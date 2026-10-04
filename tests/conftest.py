from __future__ import annotations

import json
from typing import Any

import pytest
from PIL import Image

from android_automation.config import Config
from android_automation.device.base import Device
from android_automation.vlm.base import VLM, Message, VLMResponse

SCREEN = (1080, 2400)


class FakeDevice(Device):
	"""Records every call. The screen changes colour after each gesture unless
	``static`` is set, so change detection can be exercised both ways."""

	def __init__(self, static: bool = False, size: tuple[int, int] = SCREEN):
		self.calls: list[tuple[Any, ...]] = []
		self.static = static
		self.size = size
		self._frame = 0

	def _act(self, *call: Any) -> None:
		self.calls.append(call)
		if not self.static:
			self._frame += 1

	def screenshot(self) -> Image.Image:
		# Consecutive frames differ by 80 or 176 grey levels: always a visible change.
		shade = (self._frame * 80) % 256
		return Image.new("RGB", self.size, (shade, shade, shade))

	def current_app(self) -> str | None:
		return "com.example.app"

	def tap(self, x, y):
		self._act("tap", x, y)

	def double_tap(self, x, y):
		self._act("double_tap", x, y)

	def long_press(self, x, y, duration_ms=800):
		self._act("long_press", x, y, duration_ms)

	def swipe(self, x1, y1, x2, y2, duration_ms=300):
		self._act("swipe", x1, y1, x2, y2, duration_ms)

	def type_text(self, text):
		self._act("type_text", text)

	def clear_text(self):
		self._act("clear_text")

	def press_key(self, key):
		self._act("press_key", key)

	def open_app(self, app):
		self._act("open_app", app)
		return f"pkg.{app}"

	def force_stop(self, package):
		self._act("force_stop", package)

	def push_file(self, src, dest):
		self._act("push_file", src, dest)

	def gestures(self) -> list[tuple[Any, ...]]:
		return [c for c in self.calls if c[0] not in ("open_app", "force_stop", "push_file")]


class ScriptedVLM(VLM):
	"""Returns queued replies in order (dicts are JSON-encoded); keeps every request."""

	def __init__(self, replies: list[str | dict]):
		self.replies = list(replies)
		self.requests: list[tuple[list[Message], dict | None]] = []

	def complete(self, messages, json_schema=None, schema_name="response") -> VLMResponse:
		self.requests.append((messages, json_schema))
		if not self.replies:
			raise AssertionError("ScriptedVLM ran out of replies")
		reply = self.replies.pop(0)
		return VLMResponse(text=reply if isinstance(reply, str) else json.dumps(reply))

	def prompt_text(self, i: int) -> str:
		return "\n".join(m.text() for m in self.requests[i][0])


def step(action: dict, **extra) -> dict:
	return {
		"observation": "",
		"plan": ["do it"],
		"thought": "",
		"note": "",
		**extra,
		"action": action,
	}


@pytest.fixture
def config(tmp_path) -> Config:
	cfg = Config()
	cfg.agent.settle_seconds = 0
	cfg.agent.stable_timeout = 0
	cfg.agent.record_dir = str(tmp_path / "runs")
	return cfg
