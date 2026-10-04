"""Android device control over plain ``adb`` (USB, Wi-Fi or emulator).

Nothing has to be installed on the phone. For non-ASCII text (emoji, Arabic, Urdu...)
install ADBKeyboard (https://github.com/senzhk/ADBKeyBoard); ``adb shell input text``
only handles ASCII.
"""

from __future__ import annotations

import base64
import io
import logging
import re
import shlex
import subprocess
import time
from dataclasses import dataclass

from PIL import Image

from android_automation.device.base import Device, DeviceError

log = logging.getLogger(__name__)

KEYCODES = {
	"back": "KEYCODE_BACK",
	"home": "KEYCODE_HOME",
	"enter": "KEYCODE_ENTER",
	"app_switch": "KEYCODE_APP_SWITCH",
	"delete": "KEYCODE_DEL",
	"tab": "KEYCODE_TAB",
	"search": "KEYCODE_SEARCH",
	"volume_up": "KEYCODE_VOLUME_UP",
	"volume_down": "KEYCODE_VOLUME_DOWN",
	"power": "KEYCODE_POWER",
}

ADB_KEYBOARD_IME = "com.android.adbkeyboard/.AdbIME"

# Last-resort launch intents for system apps that some builds hide from the launcher
# (BlueStacks, for one, has no launcher entry for Android's own Settings).
SYSTEM_APP_ACTIONS = {
	"com.android.settings": "android.settings.SETTINGS",
}
_COMPONENT = re.compile(r"^\s*([A-Za-z0-9_.]+)/([A-Za-z0-9_.$]+)\s*$")
_INPUT_TEXT_CHUNK = 200


@dataclass
class AdbDeviceInfo:
	serial: str
	state: str
	description: str


def list_devices(adb_path: str = "adb") -> list[AdbDeviceInfo]:
	out = _run([adb_path, "devices", "-l"], timeout=15).decode(errors="replace")
	devices = []
	for line in out.splitlines()[1:]:
		parts = line.split()
		if len(parts) >= 2:
			devices.append(AdbDeviceInfo(parts[0], parts[1], " ".join(parts[2:])))
	return devices


def connect(address: str, adb_path: str = "adb") -> str:
	"""``adb connect host:port`` for Wi-Fi debugging or networked emulators."""
	return _run([adb_path, "connect", address], timeout=30).decode(errors="replace").strip()


def _run(cmd: list[str], timeout: float, input_bytes: bytes | None = None) -> bytes:
	try:
		proc = subprocess.run(cmd, capture_output=True, timeout=timeout, input=input_bytes)
	except FileNotFoundError as e:
		raise DeviceError(
			f"'{cmd[0]}' not found. Install Android platform-tools and put adb on PATH."
		) from e
	except subprocess.TimeoutExpired as e:
		raise DeviceError(f"timed out after {timeout}s: {' '.join(cmd)}") from e
	if proc.returncode != 0:
		err = (proc.stderr or proc.stdout).decode(errors="replace").strip()
		raise DeviceError(f"{' '.join(cmd)} failed ({proc.returncode}): {err}")
	return proc.stdout


def _short(e: Exception, limit: int = 120) -> str:
	text = " ".join(str(e).split())
	return text if len(text) <= limit else text[: limit - 3] + "..."


def escape_input_text(text: str) -> str:
	"""Escape text for ``input text``: spaces become %s, then shell-quote for the device shell."""
	return shlex.quote(text.replace(" ", "%s"))


class AdbDevice(Device):
	def __init__(
		self,
		serial: str | None = None,
		adb_path: str = "adb",
		text_input: str = "auto",
		app_aliases: dict[str, str] | None = None,
		timeout: float = 30.0,
	):
		"""
		Args:
		    serial: device serial (``adb devices``); required when several are attached.
		    text_input: ``auto`` (ASCII via ``input text``, otherwise ADBKeyboard),
		        ``input`` or ``adbkeyboard``.
		    app_aliases: app name -> package, consulted by ``open_app``.
		"""
		self.serial = serial
		self.adb_path = adb_path
		self.text_input = text_input
		self.app_aliases = {k.lower(): v for k, v in (app_aliases or {}).items()}
		self.timeout = timeout
		self._packages: list[str] | None = None

	# -- plumbing -------------------------------------------------------------
	def adb(self, *args: str, timeout: float | None = None) -> bytes:
		cmd = [self.adb_path]
		if self.serial:
			cmd += ["-s", self.serial]
		return _run(cmd + list(args), timeout=timeout or self.timeout)

	def shell(self, command: str, timeout: float | None = None) -> str:
		log.debug("adb shell %s", command)
		return self.adb("shell", command, timeout=timeout).decode(errors="replace")

	# -- observation ----------------------------------------------------------
	def screenshot(self) -> Image.Image:
		data = self.adb("exec-out", "screencap", "-p")
		if not data.startswith(b"\x89PNG"):
			raise DeviceError("screencap did not return a PNG (is the screen secure/locked?)")
		img = Image.open(io.BytesIO(data))
		img.load()
		return img.convert("RGB")

	def current_app(self) -> str | None:
		try:
			out = self.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
		except DeviceError:
			return None
		m = re.search(r"\s([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)/", out)
		return m.group(1) if m else None

	# -- gestures -------------------------------------------------------------
	def tap(self, x: int, y: int) -> None:
		self.shell(f"input tap {x} {y}")

	def double_tap(self, x: int, y: int) -> None:
		# One shell round trip so the two taps land inside the double-tap timeout.
		self.shell(f"input tap {x} {y}; input tap {x} {y}")

	def long_press(self, x: int, y: int, duration_ms: int = 800) -> None:
		self.shell(f"input swipe {x} {y} {x} {y} {duration_ms}")

	def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
		self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

	def press_key(self, key: str) -> None:
		code = KEYCODES.get(key)
		if code is None:
			raise DeviceError(f"unknown key {key!r}; expected one of {sorted(KEYCODES)}")
		self.shell(f"input keyevent {code}")

	def wake(self) -> None:
		self.shell("input keyevent KEYCODE_WAKEUP")

	# -- text -----------------------------------------------------------------
	def type_text(self, text: str) -> None:
		mode = self.text_input
		if mode == "auto":
			mode = "input" if text.isascii() else "adbkeyboard"
		if mode == "adbkeyboard":
			self._type_adbkeyboard(text)
			return
		if not text.isascii():
			raise DeviceError("non-ASCII text needs text_input=adbkeyboard (install ADBKeyboard)")
		for i, line in enumerate(text.split("\n")):
			if i:
				self.press_key("enter")
			for start in range(0, len(line), _INPUT_TEXT_CHUNK):
				self.shell(
					f"input text {escape_input_text(line[start : start + _INPUT_TEXT_CHUNK])}"
				)

	def _type_adbkeyboard(self, text: str) -> None:
		if ADB_KEYBOARD_IME not in self.shell("ime list -s"):
			raise DeviceError(
				"non-ASCII text needs ADBKeyboard: install "
				"https://github.com/senzhk/ADBKeyBoard and enable it in keyboard settings"
			)
		previous = self.shell("settings get secure default_input_method").strip()
		if previous != ADB_KEYBOARD_IME:
			self.shell(f"ime set {ADB_KEYBOARD_IME}")
			time.sleep(0.5)
		try:
			b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
			self.shell(f"am broadcast -a ADB_INPUT_B64 --es msg {b64}")
		finally:
			if previous and previous != ADB_KEYBOARD_IME and previous != "null":
				self.shell(f"ime set {shlex.quote(previous)}")

	def clear_text(self) -> None:
		try:  # select-all (Android 13+), then delete
			self.shell("input keycombination KEYCODE_CTRL_LEFT KEYCODE_A")
			self.shell("input keyevent KEYCODE_DEL")
		except DeviceError:
			pass
		self.shell("input keyevent KEYCODE_MOVE_END " + " ".join(["KEYCODE_DEL"] * 80))

	# -- apps -----------------------------------------------------------------
	def packages(self, refresh: bool = False) -> list[str]:
		if self._packages is None or refresh:
			out = self.shell("pm list packages")
			self._packages = sorted(
				line.removeprefix("package:").strip()
				for line in out.splitlines()
				if line.startswith("package:")
			)
		return self._packages

	def resolve_package(self, app: str) -> str:
		name = app.strip()
		key = name.lower()
		if key in self.app_aliases:
			return self.app_aliases[key]
		installed = self.packages()
		if name in installed:
			return name
		compact = re.sub(r"[^a-z0-9]", "", key)
		if not compact:
			raise DeviceError(f"cannot resolve app {app!r}")
		scored = []
		for pkg in installed:
			segments = pkg.lower().split(".")
			if compact in segments:
				score = 0 if segments[-1] == compact else 1
			elif any(compact in seg for seg in segments[1:]):
				score = 2
			else:
				continue
			scored.append((score, len(pkg), pkg))
		if not scored:
			raise DeviceError(
				f"no installed package matches {app!r}; add it under `apps:` in the config"
			)
		return min(scored)[2]

	def open_app(self, app: str) -> str:
		"""Launch ``app`` and return its package. Tries, in order: the launcher entry
		(monkey), the resolved launcher activity, any exported MAIN activity of the
		package, and a well-known system intent."""
		package = self.resolve_package(app)
		pkg = shlex.quote(package)
		tried = []

		try:
			out = self.shell(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1 2>&1")
			if "No activities found" not in out and "monkey aborted" not in out.lower():
				return package
			tried.append("monkey: no launcher activity")
		except DeviceError as e:  # exit 252 (-4): no launchable activity
			tried.append(f"monkey: {_short(e)}")

		queries = (
			"cmd package resolve-activity --brief -a android.intent.action.MAIN "
			f"-c android.intent.category.LAUNCHER {pkg}",
			f"cmd package query-activities --brief -a android.intent.action.MAIN {pkg}",
		)
		for query in queries:
			for component in self._components(query, package):
				try:
					self._am_start(f"-n {shlex.quote(component)}")
					return package
				except DeviceError as e:
					tried.append(f"{component}: {_short(e)}")

		action = SYSTEM_APP_ACTIONS.get(package)
		if action:
			try:
				self._am_start(f"-a {action}")
				return package
			except DeviceError as e:
				tried.append(f"{action}: {_short(e)}")

		raise DeviceError(
			f"could not launch {package} ({'; '.join(tried)}); open it from the home screen instead"
		)

	def _components(self, query: str, package: str) -> list[str]:
		"""Activity components of ``package`` printed by a ``cmd package`` query."""
		try:
			out = self.shell(f"{query} 2>&1")
		except DeviceError:  # `cmd package` is missing before Android 7
			return []
		found = []
		for line in out.splitlines():
			m = _COMPONENT.match(line)
			if m and m.group(1) == package and m.group(0).strip() not in found:
				found.append(m.group(0).strip())
		return found[:3]

	def _am_start(self, args: str) -> None:
		out = self.shell(f"am start {args} 2>&1")
		if "Error" in out or "Exception" in out:
			raise DeviceError(out.strip().splitlines()[-1])

	def force_stop(self, package: str) -> None:
		self.shell(f"am force-stop {shlex.quote(package)}")

	def push_file(self, src: str, dest: str) -> None:
		self.adb("push", src, dest, timeout=max(self.timeout, 120))
		# Make it show up in gallery/file pickers.
		self.shell(
			"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
			f"-d {shlex.quote('file://' + dest)}"
		)
