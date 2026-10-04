"""Device abstraction. The agent only ever talks to this interface, so a different
transport (uiautomator2, Appium, a cloud device farm) is one new subclass away."""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image


class DeviceError(RuntimeError):
	pass


class Device(ABC):
	@abstractmethod
	def screenshot(self) -> Image.Image:
		"""Current screen at native resolution. Input coordinates match this image."""

	@abstractmethod
	def tap(self, x: int, y: int) -> None: ...

	@abstractmethod
	def double_tap(self, x: int, y: int) -> None: ...

	@abstractmethod
	def long_press(self, x: int, y: int, duration_ms: int = 800) -> None: ...

	@abstractmethod
	def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None: ...

	@abstractmethod
	def type_text(self, text: str) -> None: ...

	@abstractmethod
	def clear_text(self) -> None:
		"""Clear the focused text field."""

	@abstractmethod
	def press_key(self, key: str) -> None:
		"""``key`` is one of ``actions.Key``."""

	@abstractmethod
	def open_app(self, app: str) -> str:
		"""Launch an app by name or package. Returns the package launched."""

	def force_stop(self, package: str) -> None:
		raise NotImplementedError

	def push_file(self, src: str, dest: str) -> None:
		raise NotImplementedError

	def current_app(self) -> str | None:
		"""Package of the foreground app, if the transport can tell."""
		return None

	def wake(self) -> None:
		"""Turn the screen on if it is off."""
		return None
