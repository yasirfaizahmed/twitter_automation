"""The observe -> think -> act -> verify loop.

screenshot ──► VLM ──► JSON {observation, plan, thought, action}
    ▲                                    │
    │                       (optional grounder: target -> x, y)
    │                                    ▼
wait until the screen settles ◄── execute on device (ADB)
    └── feedback: what ran, did the screen change, errors ──► next prompt
"""

from __future__ import annotations

import logging
import re
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from PIL import Image

from android_automation import coords, imaging, prompts
from android_automation.actions import (
	AgentStep,
	AskUser,
	Done,
	DoubleTap,
	Fail,
	LongPress,
	OpenApp,
	PressKey,
	Scroll,
	Swipe,
	Tap,
	TypeText,
	Wait,
	describe,
)
from android_automation.config import Config
from android_automation.device.base import Device, DeviceError
from android_automation.grounding import Grounder, GroundingError
from android_automation.parsing import ParseError, parse_step
from android_automation.recorder import Recorder
from android_automation.vlm.base import VLM, Message, VLMResponse

log = logging.getLogger(__name__)

Status = Literal["success", "failed", "max_steps", "stuck", "error", "aborted"]
_SECRET = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
_SCROLL_DISTANCE = {"short": 0.2, "medium": 0.4, "long": 0.6}


class ActionError(RuntimeError):
	"""The action was well-formed JSON but cannot be carried out as given."""


class Aborted(RuntimeError):
	"""Raised from a callback to stop the run."""


@dataclass
class RunResult:
	status: Status
	steps: int
	answer: str = ""
	reason: str = ""
	plan: list[str] = field(default_factory=list)
	notes: list[str] = field(default_factory=list)
	run_dir: Path | None = None

	@property
	def success(self) -> bool:
		return self.status == "success"


@dataclass
class StepEvent:
	index: int
	step: AgentStep
	action: str
	feedback: str
	points: list[tuple[int, int]]
	response: VLMResponse


class Agent:
	def __init__(
		self,
		vlm: VLM,
		device: Device,
		config: Config | None = None,
		*,
		grounder: Grounder | None = None,
		secrets: dict[str, str] | None = None,
		on_step: Callable[[StepEvent], None] | None = None,
		confirm: Callable[[int, AgentStep], bool] | None = None,
		ask_user: Callable[[str], str] | None = None,
		sleep: Callable[[float], None] = time.sleep,
	):
		"""
		Args:
		    grounder: resolves element descriptions to positions. When set, it is used
		        for every targeted action and the main model's own x/y are ignored.
		    secrets: placeholder name -> value. The model only ever sees the names.
		    on_step: called after every executed step (for UIs / logging).
		    confirm: called before each device action; return False to skip it.
		    ask_user: answers the model's ``ask_user`` questions (e.g. an OTP).
		"""
		self.vlm = vlm
		self.device = device
		self.config = config or Config()
		self.grounder = grounder
		self.secrets = dict(secrets or {})
		self.on_step = on_step
		self.confirm = confirm
		self.ask_user = ask_user
		self.sleep = sleep
		self._self_grounder: Grounder | None = None
		self._warnings: list[str] = []

	@classmethod
	def from_config(
		cls,
		config: Config,
		*,
		device: Device | None = None,
		dry_run: bool = False,
		**kwargs: Any,
	) -> Agent:
		from android_automation.device import AdbDevice, DryRunDevice
		from android_automation.vlm import build_vlm

		if device is None:
			d = config.device
			device = AdbDevice(
				serial=d.serial,
				adb_path=d.adb_path,
				text_input=d.text_input,
				app_aliases=config.app_aliases(),
				timeout=d.timeout,
			)
		if dry_run:
			device = DryRunDevice(device)
		grounder = None
		if config.grounder is not None:
			grounder = Grounder(build_vlm(config.grounder), config.grounder)
		return cls(build_vlm(config.model), device, config, grounder=grounder, **kwargs)

	# ------------------------------------------------------------------ run
	def run(self, goal: str) -> RunResult:
		acfg = self.config.agent
		mcfg = self.config.model
		recorder = None
		if acfg.record_dir:
			recorder = Recorder(
				acfg.record_dir,
				goal,
				meta={
					"config": self.config.model_dump(mode="json"),
					"secrets": sorted(self.secrets),
				},
			)

		plan: list[str] = []
		notes: list[str] = []
		history: list[prompts.HistoryEntry] = []
		images: deque[Image.Image] = deque(maxlen=acfg.history_images)
		last_sig, streak = "", 0
		result: RunResult | None = None
		shot: Image.Image | None = None

		try:
			self.device.wake()
			shot = self.device.screenshot()
			for index in range(acfg.max_steps):
				model_img = imaging.prepare_for_model(
					shot, mcfg.image.factor, mcfg.image.min_pixels, mcfg.image.max_pixels
				)
				images.append(model_img)
				coord_note = coords.describe_space(mcfg.coordinate_space, model_img.size)
				warnings, self._warnings = self._warnings, []
				if streak >= acfg.stuck_threshold:
					warnings.append(
						f"the last {streak} actions were identical and changed nothing. "
						"Do something different: another element, scroll, go back, or fail."
					)
				messages = prompts.step_messages(
					goal=goal,
					coordinates=coord_note,
					screenshots=list(images),
					plan=plan,
					notes=notes,
					history=history[-acfg.history_actions :],
					step_index=index,
					max_steps=acfg.max_steps,
					current_app=self.device.current_app(),
					warnings=warnings,
					secret_names=sorted(self.secrets),
				)
				step, responses, parse_error = self._decide(messages)
				resp = responses[-1]
				record: dict[str, Any] = {
					"prompt": messages[1].text(),
					"raw": resp.text,
					"reasoning": resp.reasoning,
					"latency_s": round(sum(r.latency_s for r in responses), 3),
					"usage": resp.usage,
					"attempts": len(responses),
					"model_image_size": model_img.size,
					"screen_size": shot.size,
				}
				if index == 0:
					record["system_prompt"] = messages[0].text()
				if step is None:
					result = RunResult(
						"error", index + 1, reason=f"unusable model output: {parse_error}"
					)
					if recorder:
						recorder.step(index, shot, None, {**record, "feedback": result.reason})
					break

				if step.plan:
					plan = step.plan
				if step.note.strip():
					notes = (notes + [step.note.strip()])[-20:]
				action = step.action
				action_text = describe(action)
				record.update(step=step.model_dump(mode="json"), action=action_text)

				if isinstance(action, Done | Fail):
					status: Status = "success" if isinstance(action, Done) else "failed"
					result = RunResult(
						status,
						index + 1,
						answer=action.answer if isinstance(action, Done) else "",
						reason=action.reason if isinstance(action, Fail) else "",
					)
					if recorder:
						recorder.step(index, shot, None, {**record, "feedback": status})
					self._emit(index, step, action_text, status, [], resp)
					break

				points: list[tuple[int, int]] = []
				if isinstance(action, AskUser):
					feedback = self._ask(action.question)
				elif self.confirm is not None and not self.confirm(index, step):
					feedback = "SKIPPED: the user rejected this action. Choose another."
				else:
					try:
						points, feedback = self._execute(action, shot, model_img)
					except (ActionError, DeviceError, GroundingError, ParseError) as e:
						feedback = f"FAILED: {e}"

				new_shot = self._observe_after_action()
				changed = imaging.screen_diff(shot, new_shot) >= acfg.change_threshold
				if not changed and not isinstance(action, Wait | AskUser):
					feedback += " The screen did not visibly change."
				if changed:
					streak = 0
				else:
					streak = streak + 1 if action_text == last_sig else 1
				last_sig = action_text

				history.append(prompts.HistoryEntry(index, action_text, feedback))
				record.update(feedback=feedback, device_points=points, screen_changed=changed)
				if recorder:
					annotated = imaging.annotate(shot, points, action_text) if points else None
					recorder.step(index, shot, annotated, record)
				self._emit(index, step, action_text, feedback, points, resp)
				shot = new_shot

				if streak >= 2 * acfg.stuck_threshold:
					result = RunResult(
						"stuck",
						index + 1,
						reason=f"repeated {action_text} {streak}x with no effect",
					)
					break
			else:
				result = RunResult("max_steps", acfg.max_steps, reason="step budget exhausted")
		except (KeyboardInterrupt, Aborted):
			result = RunResult("aborted", len(history), reason="stopped by user")
		except Exception as e:  # network errors, device unplugged, ...
			log.exception("run failed")
			result = RunResult("error", len(history), reason=f"{type(e).__name__}: {e}")

		assert result is not None
		result.plan, result.notes = plan, notes
		if recorder:
			result.run_dir = recorder.dir
			recorder.finish(
				{k: v for k, v in result.__dict__.items() if k != "run_dir"}, final_screenshot=shot
			)
		return result

	# ------------------------------------------------------------ decision
	def _decide(self, messages: list[Message]) -> tuple[AgentStep | None, list[VLMResponse], str]:
		schema = prompts.agent_step_schema()
		convo = list(messages)
		responses: list[VLMResponse] = []
		error = ""
		for _ in range(self.config.agent.max_parse_retries + 1):
			resp = self.vlm.complete(convo, json_schema=schema, schema_name="agent_step")
			responses.append(resp)
			try:
				return parse_step(resp.text), responses, ""
			except ParseError as e:
				error = str(e)
				log.warning("unparseable model output (%s): %.200s", error, resp.text)
				convo = list(messages) + [
					Message("assistant", [resp.text or "(empty reply)"]),
					Message(
						"user",
						[
							f"That reply could not be used: {error}. Reply again with ONLY the "
							"JSON object described in the instructions."
						],
					),
				]
		return None, responses, error

	def _ask(self, question: str) -> str:
		if self.ask_user is None:
			return "No user is available to answer. Continue without it, or fail."
		answer = self.ask_user(question)
		return f"The user answered: {answer!r}"

	def _emit(self, index, step, action_text, feedback, points, resp) -> None:
		log.info("step %d: %s -> %s", index + 1, action_text, feedback)
		if self.on_step:
			self.on_step(StepEvent(index, step, action_text, feedback, points, resp))

	def _observe_after_action(self) -> Image.Image:
		acfg = self.config.agent
		if acfg.settle_seconds > 0:
			self.sleep(acfg.settle_seconds)
		shot = self.device.screenshot()
		deadline = time.monotonic() + acfg.stable_timeout
		while time.monotonic() < deadline:
			nxt = self.device.screenshot()
			if imaging.screen_diff(shot, nxt) < acfg.change_threshold:
				return nxt
			shot = nxt
		return shot

	# ----------------------------------------------------------- execution
	def _fraction(
		self, action: Any, shot: Image.Image, model_img: Image.Image
	) -> tuple[float, float] | None:
		target = getattr(action, "target", "") or ""
		x, y = getattr(action, "x", None), getattr(action, "y", None)
		space = self.config.model.coordinate_space
		if self.grounder is not None and target:
			return self.grounder.locate(shot, target)
		if x is not None and y is not None:
			if not coords.in_bounds(x, y, space, model_img.size):
				self._warnings.append(f"({x}, {y}) was outside the screen and got clamped.")
			return coords.to_fraction(x, y, space, model_img.size)
		if target:
			if self._self_grounder is None:
				self._self_grounder = Grounder(self.vlm, self.config.model)
			return self._self_grounder.locate(shot, target)
		return None

	def _fill_secrets(self, text: str) -> str:
		def sub(m: re.Match[str]) -> str:
			name = m.group(1)
			if name not in self.secrets:
				raise ActionError(f"unknown secret placeholder {{{{{name}}}}}")
			return self.secrets[name]

		return _SECRET.sub(sub, text)

	def _execute(
		self, action: Any, shot: Image.Image, model_img: Image.Image
	) -> tuple[list[tuple[int, int]], str]:
		w, h = shot.size
		space = self.config.model.coordinate_space

		def px(frac: tuple[float, float]) -> tuple[int, int]:
			return min(round(frac[0] * w), w - 1), min(round(frac[1] * h), h - 1)

		dev = self.device
		if isinstance(action, Tap | DoubleTap | LongPress):
			frac = self._fraction(action, shot, model_img)
			if frac is None:
				raise ActionError(f"{action.type} needs x/y or a target description")
			x, y = px(frac)
			if isinstance(action, Tap):
				dev.tap(x, y)
			elif isinstance(action, DoubleTap):
				dev.double_tap(x, y)
			else:
				dev.long_press(x, y, action.duration_ms)
			return [(x, y)], f"done at ({x}, {y})px."

		if isinstance(action, TypeText):
			text = self._fill_secrets(action.text)
			points = []
			if action.target or (action.x is not None and action.y is not None):
				frac = self._fraction(action, shot, model_img)
				if frac is not None:
					points.append(px(frac))
					dev.tap(*points[0])
					self.sleep(0.4)
			if action.clear:
				dev.clear_text()
			if text:
				dev.type_text(text)
			if action.submit:
				dev.press_key("enter")
			return points, f"typed {len(action.text)} characters."

		if isinstance(action, Swipe):
			a = px(coords.to_fraction(action.x1, action.y1, space, model_img.size))
			b = px(coords.to_fraction(action.x2, action.y2, space, model_img.size))
			dev.swipe(*a, *b, action.duration_ms)
			return [a, b], f"swiped {a} -> {b}."

		if isinstance(action, Scroll):
			ax, ay = 0.5, 0.5
			if action.target or (action.x is not None and action.y is not None):
				ax, ay = self._fraction(action, shot, model_img) or (ax, ay)
			d = _SCROLL_DISTANCE[action.distance] / 2
			# Content moves with the finger: to reveal what is below, drag upwards.
			dx, dy = {"down": (0, -d), "up": (0, d), "right": (-d, 0), "left": (d, 0)}[
				action.direction
			]

			def clamp(v: float, lo: float, hi: float) -> float:
				return min(max(v, lo), hi)

			start = (clamp(ax - dx, 0.05, 0.95), clamp(ay - dy, 0.15, 0.85))
			end = (clamp(ax + dx, 0.05, 0.95), clamp(ay + dy, 0.15, 0.85))
			a, b = px(start), px(end)
			dev.swipe(*a, *b, 400)
			return [a, b], f"scrolled {action.direction}."

		if isinstance(action, PressKey):
			dev.press_key(action.key)
			return [], f"pressed {action.key}."

		if isinstance(action, OpenApp):
			package = dev.open_app(action.app)
			return [], f"launched {package}."

		if isinstance(action, Wait):
			self.sleep(action.seconds)
			return [], f"waited {action.seconds:g}s."

		raise ActionError(f"unsupported action {type(action).__name__}")
