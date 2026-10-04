"""The container entrypoint (deploy/entrypoint.sh), run with fake adb / CLI binaries."""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

ENTRYPOINT = Path(__file__).resolve().parents[1] / "deploy" / "entrypoint.sh"

FAKE_ADB = """#!/bin/sh
echo "adb $*" >> "$LOG"
case "$*" in
  *wait-for-device*) exit "${FAKE_WAIT_RC:-0}" ;;
  *get-state*) echo device ;;
  *"pm list packages"*) echo "package:com.android.settings" ;;
esac
exit 0
"""
FAKE_CLI = """#!/bin/sh
echo "cli $*" >> "$LOG"
"""

pytestmark = pytest.mark.skipif(shutil.which("sh") is None, reason="needs a POSIX shell")


@pytest.fixture
def run_entrypoint(tmp_path):
	bin_dir = tmp_path / "bin"
	bin_dir.mkdir()
	for name, body in (("adb", FAKE_ADB), ("android-automation", FAKE_CLI)):
		script = bin_dir / name
		script.write_text(body)
		script.chmod(script.stat().st_mode | stat.S_IEXEC)
	log = tmp_path / "log"

	def run(*args, **env):
		full_env = {
			"PATH": f"{bin_dir}:{os.environ['PATH']}",
			"LOG": str(log),
			**{k: str(v) for k, v in env.items()},
		}
		proc = subprocess.run(
			["sh", str(ENTRYPOINT), *args], env=full_env, capture_output=True, text=True, timeout=30
		)
		lines = log.read_text().splitlines() if log.exists() else []
		log.unlink(missing_ok=True)
		return proc, lines

	return run


def test_connects_wireless_devices_and_runs_cli(run_entrypoint):
	proc, lines = run_entrypoint(
		"devices", ADB_CONNECT="1.2.3.4:5555, 5.6.7.8:5555", ADB_WAIT_FOR_DEVICE=1
	)
	assert proc.returncode == 0, proc.stderr
	assert lines == [
		"adb start-server",
		"adb connect 1.2.3.4:5555",
		"adb connect 5.6.7.8:5555",
		"cli devices",
	]


def test_waits_for_the_device_only_when_needed(run_entrypoint):
	proc, lines = run_entrypoint(
		"run", "open settings", ADB_WAIT_FOR_DEVICE=1, ANDROID_AUTOMATION__DEVICE__SERIAL="R58M"
	)
	assert proc.returncode == 0, proc.stderr
	assert "adb -s R58M wait-for-device" in lines
	assert lines[-1] == "cli run open settings"


def test_missing_device_fails_with_a_hint(run_entrypoint):
	proc, lines = run_entrypoint(
		"task", "x.yaml", ADB_WAIT_FOR_DEVICE=1, ADB_WAIT_TIMEOUT=5, FAKE_WAIT_RC=1
	)
	assert proc.returncode == 1
	assert "adb kill-server" in proc.stderr
	assert not any(line.startswith("cli") for line in lines)


def test_installs_adbkeyboard_when_missing(run_entrypoint, tmp_path):
	apk = tmp_path / "ADBKeyboard.apk"
	apk.write_bytes(b"apk")
	proc, lines = run_entrypoint("check", INSTALL_ADBKEYBOARD=1, ADBKEYBOARD_APK=apk)
	assert proc.returncode == 0, proc.stderr
	assert f"adb install -r {apk}" in lines
	assert "adb shell ime enable com.android.adbkeyboard/.AdbIME" in lines


def test_adb_and_shell_commands_pass_through(run_entrypoint):
	proc, lines = run_entrypoint("adb", "pair", "1.2.3.4:37099", "123456")
	assert proc.returncode == 0
	assert lines == ["adb pair 1.2.3.4:37099 123456"]
