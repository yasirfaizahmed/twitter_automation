import io
import subprocess

import pytest
from PIL import Image

from android_automation.device import adb as adb_mod
from android_automation.device.adb import AdbDevice, escape_input_text, list_devices
from android_automation.device.base import DeviceError


class FakeRun:
	"""Stands in for subprocess.run; answers by matching the device shell command."""

	def __init__(self, responses=None):
		self.cmds = []
		self.responses = responses or {}

	def __call__(self, cmd, capture_output, timeout, input=None):
		self.cmds.append(cmd)
		key = cmd[-1]
		out, code = b"", 0
		for prefix, resp in self.responses.items():
			if key.startswith(prefix) or (prefix == "screencap" and "screencap" in cmd):
				out, code = resp if isinstance(resp, tuple) else (resp, 0)
				break
		return subprocess.CompletedProcess(cmd, code, stdout=out, stderr=b"boom" if code else b"")

	def shell_cmds(self):
		return [c[-1] for c in self.cmds if "shell" in c]


@pytest.fixture
def fake_run(monkeypatch):
	def install(responses=None):
		fr = FakeRun(responses)
		monkeypatch.setattr(adb_mod.subprocess, "run", fr)
		return fr

	return install


def test_gestures_build_expected_commands(fake_run):
	fr = fake_run()
	d = AdbDevice(serial="emulator-5554")
	d.tap(10, 20)
	d.long_press(1, 2, 900)
	d.swipe(1, 2, 3, 4, 250)
	d.press_key("back")
	assert fr.cmds[0] == ["adb", "-s", "emulator-5554", "shell", "input tap 10 20"]
	assert fr.shell_cmds()[1:] == [
		"input swipe 1 2 1 2 900",
		"input swipe 1 2 3 4 250",
		"input keyevent KEYCODE_BACK",
	]
	with pytest.raises(DeviceError):
		d.press_key("teleport")


def test_type_text_escaping_and_newlines(fake_run):
	fr = fake_run()
	d = AdbDevice()
	d.type_text("it's a test\nline 2")
	assert fr.shell_cmds() == [
		"input text " + escape_input_text("it's a test"),
		"input keyevent KEYCODE_ENTER",
		"input text " + escape_input_text("line 2"),
	]
	assert escape_input_text("a b") == "a%sb"
	assert escape_input_text("it's") == "'it'\"'\"'s'"


def test_non_ascii_needs_adbkeyboard(fake_run):
	fake_run({"ime list": b"com.google.android.inputmethod.latin/.LatinIME\n"})
	with pytest.raises(DeviceError, match="ADBKeyboard"):
		AdbDevice().type_text("السلام عليكم")


def test_non_ascii_via_adbkeyboard_restores_ime(fake_run, monkeypatch):
	fr = fake_run(
		{
			"ime list": b"com.android.adbkeyboard/.AdbIME\n",
			"settings get": b"com.google.android.inputmethod.latin/.LatinIME\n",
		}
	)
	monkeypatch.setattr(adb_mod.time, "sleep", lambda s: None)
	AdbDevice().type_text("سلام 👋")
	cmds = fr.shell_cmds()
	assert cmds[2] == "ime set com.android.adbkeyboard/.AdbIME"
	assert cmds[3].startswith("am broadcast -a ADB_INPUT_B64 --es msg ")
	assert cmds[4] == "ime set com.google.android.inputmethod.latin/.LatinIME"


def test_screenshot_decodes_png(fake_run):
	buf = io.BytesIO()
	Image.new("RGB", (8, 16), "red").save(buf, format="PNG")
	fake_run({"screencap": buf.getvalue()})
	img = AdbDevice().screenshot()
	assert img.size == (8, 16)


def test_screenshot_rejects_garbage(fake_run):
	fake_run({"screencap": b"not a png"})
	with pytest.raises(DeviceError):
		AdbDevice().screenshot()


def test_resolve_package(fake_run):
	fake_run(
		{
			"pm list packages": b"package:com.google.android.youtube\npackage:com.whatsapp\n"
			b"package:com.android.settings\npackage:com.google.android.apps.youtube.music\n"
		}
	)
	d = AdbDevice(app_aliases={"X": "com.twitter.android"})
	assert d.resolve_package("x") == "com.twitter.android"
	assert d.resolve_package("YouTube") == "com.google.android.youtube"
	assert d.resolve_package("WhatsApp") == "com.whatsapp"
	assert d.resolve_package("com.android.settings") == "com.android.settings"
	with pytest.raises(DeviceError, match="no installed package"):
		d.resolve_package("Nonexistent")


# What monkey prints on BlueStacks for a package without a launcher entry (exit 252 = -4).
MONKEY_NO_LAUNCHER = (
	b'args: [-p, com.android.settings, -c, android.intent.category.LAUNCHER, 1]\n arg: "-p"\n',
	252,
)


def test_open_app_uses_monkey_first(fake_run):
	fr = fake_run({"pm list": b"package:com.foo\n", "monkey": b"Events injected: 1\n"})
	assert AdbDevice().open_app("com.foo") == "com.foo"
	assert [c for c in fr.shell_cmds() if c.startswith("am start")] == []


def test_open_app_falls_back_to_the_resolved_launcher_activity(fake_run):
	fr = fake_run(
		{
			"pm list": b"package:com.foo\n",
			"monkey": MONKEY_NO_LAUNCHER,
			"cmd package resolve-activity": b"priority=0 preferredOrder=0 match=0x108000\ncom.foo/.Main\n",
			"am start -n": b"Starting: Intent { cmp=com.foo/.Main }\n",
		}
	)
	assert AdbDevice().open_app("com.foo") == "com.foo"
	assert "am start -n com.foo/.Main 2>&1" in fr.shell_cmds()


def test_open_settings_on_bluestacks_uses_the_settings_intent(fake_run):
	fr = fake_run(
		{
			"pm list": b"package:com.android.settings\n",
			"monkey": MONKEY_NO_LAUNCHER,
			"cmd package resolve-activity": b"No activity found\n",
			"cmd package query-activities": b"1 activities found:\n  com.android.settings/.Hidden\n",
			"am start -n": b"Error: Activity class {com.android.settings/.Hidden} does not exist.\n",
			"am start -a": b"Starting: Intent { act=android.settings.SETTINGS }\n",
		}
	)
	assert AdbDevice().open_app("settings") == "com.android.settings"
	starts = [c for c in fr.shell_cmds() if c.startswith("am start")]
	assert starts == [
		"am start -n com.android.settings/.Hidden 2>&1",
		"am start -a android.settings.SETTINGS 2>&1",
	]


def test_open_app_gives_up_with_advice(fake_run):
	fake_run(
		{
			"pm list": b"package:com.foo\n",
			"monkey": b"** No activities found to run, monkey aborted.",
			"cmd package": (b"", 1),  # e.g. Android 6 without `cmd package`
		}
	)
	with pytest.raises(
		DeviceError, match="could not launch com.foo .*open it from the home screen"
	):
		AdbDevice().open_app("com.foo")


def test_failed_command_raises(fake_run):
	fake_run({"input tap": (b"", 1)})
	with pytest.raises(DeviceError, match="boom"):
		AdbDevice().tap(1, 1)


def test_current_app_parses_focus(fake_run):
	fake_run(
		{
			"dumpsys": b"  mCurrentFocus=Window{1a2b u0 com.twitter.android/com.twitter.app.main.MainActivity}\n"
		}
	)
	assert AdbDevice().current_app() == "com.twitter.android"


def test_list_devices(fake_run):
	fake_run({"-l": b"List of devices attached\nR58M123 device usb:1-1 model:SM_G973F\n\n"})
	devs = list_devices()
	assert devs[0].serial == "R58M123" and devs[0].state == "device"


def test_missing_adb_binary(monkeypatch):
	def boom(*a, **k):
		raise FileNotFoundError

	monkeypatch.setattr(adb_mod.subprocess, "run", boom)
	with pytest.raises(DeviceError, match="platform-tools"):
		AdbDevice().tap(1, 1)
