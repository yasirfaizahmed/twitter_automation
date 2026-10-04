"""Prompt construction. Each turn is built from scratch (system + one user message) so
context stays bounded no matter how long the run is; continuity comes from the plan,
notes and action history the agent carries forward."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from PIL import Image

from android_automation.actions import AgentStep
from android_automation.vlm.base import Message

SYSTEM_PROMPT = """\
You are an expert agent that operates an Android phone to accomplish a user's goal, \
like a careful human would. Each turn you get the goal, your previous plan and notes, \
the actions already executed (with what happened), and a screenshot of the current screen.

Work in a loop: look at the screenshot, update the plan (the goal broken down into the \
remaining concrete sub-steps), then choose exactly ONE action to do next. After it runs \
you will see the new screen and can correct course.

{coordinates}

Actions (the "type" field selects one):
- tap: {{"type": "tap", "target": "<element description>", "x": X, "y": Y}}
- double_tap: {{"type": "double_tap", "target": "...", "x": X, "y": Y}}
- long_press: {{"type": "long_press", "target": "...", "x": X, "y": Y, "duration_ms": 800}}
- type: {{"type": "type", "text": "...", "target": "<field>", "x": X, "y": Y, "clear": false, "submit": false}} \
types into the field at x/y (tapping it first); omit x/y if the field is already focused. \
"clear" empties the field first, "submit" presses Enter afterwards.
- scroll: {{"type": "scroll", "direction": "up|down|left|right", "distance": "short|medium|long"}} \
"down" reveals content further down. Add x/y to scroll inside a specific area.
- swipe: {{"type": "swipe", "x1": X, "y1": Y, "x2": X, "y2": Y, "duration_ms": 300}} for precise drags.
- press_key: {{"type": "press_key", "key": "back|home|enter|app_switch|delete|tab|search|volume_up|volume_down|power"}}
- open_app: {{"type": "open_app", "app": "<app name or package>"}} faster than finding the icon.
- wait: {{"type": "wait", "seconds": 2}} when the screen is loading.
- ask_user: {{"type": "ask_user", "question": "..."}} only for information only the user has \
(a one-time code, a choice between options).
- done: {{"type": "done", "answer": "..."}} when the goal is fully achieved and visible on \
screen; put any requested information in "answer".
- fail: {{"type": "fail", "reason": "..."}} when the goal is impossible.

Guidelines:
- Always give "target" for actions on an element: a short visual description \
(text, icon, colour, position) that identifies it uniquely.
- Aim at the centre of the element. Prefer visible text labels over guesses.
- If an action had no visible effect, do not repeat it blindly: try another element, \
scroll, wait, or go back.
- Dismiss pop-ups, permission dialogs and onboarding screens that block the goal.
- Never claim "done" before the result is visible on screen. Never invent information.
- Do not perform purchases, payments, deletions or messages beyond what the goal asks.{secrets}

Reply with ONLY a JSON object, no prose, in exactly this shape:
{{"observation": "...", "plan": ["next sub-step", "..."], "thought": "...", "note": "", "action": {{...}}}}
"""

SECRETS_BLOCK = """
- Secrets: to type a secret value, write its placeholder exactly as shown, e.g. \
{{"type": "type", "text": "{{{{{example}}}}}"}}. The real value is filled in for you. \
Available placeholders: {names}."""

LOCALIZE_PROMPT = """\
Localize an element on the GUI image according to the provided target and output a click position.
 * {coordinates}
 * You must output a valid JSON following the format: {schema}
 Your target is:
{target}"""


@dataclass
class HistoryEntry:
	index: int
	action: str
	feedback: str


def system_prompt(coordinates: str, secret_names: list[str] | None = None) -> str:
	secrets = ""
	if secret_names:
		names = ", ".join("{{" + n + "}}" for n in secret_names)
		secrets = SECRETS_BLOCK.format(example=secret_names[0], names=names)
	return SYSTEM_PROMPT.format(coordinates=coordinates, secrets=secrets)


def step_messages(
	*,
	goal: str,
	coordinates: str,
	screenshots: list[Image.Image],
	plan: list[str],
	notes: list[str],
	history: list[HistoryEntry],
	step_index: int,
	max_steps: int,
	current_app: str | None = None,
	warnings: list[str] | None = None,
	secret_names: list[str] | None = None,
) -> list[Message]:
	lines = [f"<goal>\n{goal}\n</goal>"]
	lines.append(
		f"Step {step_index + 1} of at most {max_steps}. Time: {datetime.now():%Y-%m-%d %H:%M}."
	)
	if plan:
		lines.append(
			"<previous_plan>\n"
			+ "\n".join(f"{i + 1}. {p}" for i, p in enumerate(plan))
			+ "\n</previous_plan>"
		)
	if notes:
		lines.append("<notes>\n" + "\n".join(f"- {n}" for n in notes) + "\n</notes>")
	if history:
		rows = [f"{h.index + 1}. {h.action} -> {h.feedback}" for h in history]
		lines.append("<executed_actions>\n" + "\n".join(rows) + "\n</executed_actions>")
	else:
		lines.append("<executed_actions>\nnone yet\n</executed_actions>")
	for w in warnings or []:
		lines.append(f"WARNING: {w}")
	if current_app:
		lines.append(f"Foreground app package: {current_app}")

	content: list[str | Image.Image] = ["\n\n".join(lines) + "\n\n"]
	if len(screenshots) > 1:
		for i, shot in enumerate(screenshots[:-1]):
			content += [
				f"<earlier_screenshot t=-{len(screenshots) - 1 - i}>\n",
				shot,
				"\n</earlier_screenshot>\n",
			]
	content += ["<current_screenshot>\n", screenshots[-1], "\n</current_screenshot>\n"]
	content.append("Reply with the JSON object for your next action.")
	return [
		Message("system", [system_prompt(coordinates, secret_names)]),
		Message("user", content),
	]


def localize_schema(coordinate_note: str) -> dict:
	return {
		"type": "object",
		"properties": {
			"x": {"type": "number", "description": f"Horizontal position. {coordinate_note}"},
			"y": {"type": "number", "description": f"Vertical position. {coordinate_note}"},
		},
		"required": ["x", "y"],
	}


def localize_messages(target: str, coordinates: str, screenshot: Image.Image) -> list[Message]:
	text = LOCALIZE_PROMPT.format(
		coordinates=coordinates,
		schema=json.dumps(localize_schema(coordinates)),
		target=target,
	)
	return [Message("user", [screenshot, text])]


def agent_step_schema() -> dict:
	"""JSON schema sent for constrained decoding. Stricter than the parser: every step
	field is required, and each action's ``type`` is required and generated first (grammar
	engines emit properties in schema order), so the model commits to the action kind
	before filling in its arguments."""
	schema = AgentStep.model_json_schema()
	schema["required"] = list(schema["properties"])
	for definition in schema.get("$defs", {}).values():
		props = definition.get("properties", {})
		if "const" not in props.get("type", {}):
			continue
		definition["properties"] = {
			"type": props["type"],
			**{k: v for k, v in props.items() if k != "type"},
		}
		definition["required"] = [
			"type",
			*[r for r in definition.get("required", []) if r != "type"],
		]
	return schema
