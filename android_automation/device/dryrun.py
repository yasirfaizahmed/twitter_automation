from __future__ import annotations

import logging

from PIL import Image

from android_automation.device.base import Device

log = logging.getLogger(__name__)


class DryRunDevice(Device):
	"""Observes the real device but only logs gestures. Useful to watch what a model
	would do without letting it touch anything."""

	def __init__(self, inner: Device):
		self.inner = inner

	def screenshot(self) -> Image.Image:
		return self.inner.screenshot()

	def current_app(self) -> str | None:
		return self.inner.current_app()

	def _log(self, what: str, *args: object) -> None:
		log.info("[dry-run] %s %s", what, " ".join(map(str, args)))

	def tap(self, x: int, y: int) -> None:
		self._log("tap", x, y)

	def double_tap(self, x: int, y: int) -> None:
		self._log("double_tap", x, y)

	def long_press(self, x: int, y: int, duration_ms: int = 800) -> None:
		self._log("long_press", x, y, duration_ms)

	def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
		self._log("swipe", x1, y1, x2, y2, duration_ms)

	def type_text(self, text: str) -> None:
		self._log("type", f"<{len(text)} chars>")

	def clear_text(self) -> None:
		self._log("clear_text")

	def press_key(self, key: str) -> None:
		self._log("press_key", key)

	def open_app(self, app: str) -> str:
		self._log("open_app", app)
		return app

	def force_stop(self, package: str) -> None:
		self._log("force_stop", package)

	def push_file(self, src: str, dest: str) -> None:
		self._log("push_file", src, dest)
