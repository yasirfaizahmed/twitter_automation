"""End to end through the real CLI, the real OpenAI SDK and a real subprocess, with a
fake OpenAI-compatible server and a fake ``adb`` executable standing in for vLLM and
the phone."""

import io
import json
import stat
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from android_automation.cli import app

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "default.yaml"

FAKE_ADB = """#!{python}
import sys, pathlib
args = sys.argv[1:]
pathlib.Path({log!r}).open("a").write(" ".join(args) + "\\n")
if "screencap" in args:
    sys.stdout.buffer.write(pathlib.Path({png!r}).read_bytes())
elif args[-1].startswith("dumpsys"):
    print("mCurrentFocus=Window{{1 u0 com.android.settings/.Settings}}")
elif args[:1] == ["devices"]:
    print("List of devices attached\\nemulator-5554\\tdevice product:sdk\\n")
"""


class FakeVLMServer(BaseHTTPRequestHandler):
	replies: list[dict] = []
	requests: list[dict] = []

	def do_POST(self):  # noqa: N802
		body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
		FakeVLMServer.requests.append(body)
		content = json.dumps(FakeVLMServer.replies.pop(0))
		payload = {
			"id": "x",
			"object": "chat.completion",
			"created": 0,
			"model": body["model"],
			"choices": [
				{
					"index": 0,
					"finish_reason": "stop",
					"message": {"role": "assistant", "content": content},
				}
			],
			"usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
		}
		data = json.dumps(payload).encode()
		self.send_response(200)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def log_message(self, *args):
		pass


@pytest.fixture
def server():
	httpd = HTTPServer(("127.0.0.1", 0), FakeVLMServer)
	thread = threading.Thread(target=httpd.serve_forever, daemon=True)
	thread.start()
	yield f"http://127.0.0.1:{httpd.server_port}/v1"
	httpd.shutdown()


@pytest.fixture
def fake_adb(tmp_path):
	png = tmp_path / "screen.png"
	buf = io.BytesIO()
	Image.new("RGB", (1080, 2400), "white").save(buf, format="PNG")
	png.write_bytes(buf.getvalue())
	log = tmp_path / "adb.log"
	script = tmp_path / "adb"
	script.write_text(FAKE_ADB.format(python=sys.executable, log=str(log), png=str(png)))
	script.chmod(script.stat().st_mode | stat.S_IEXEC)
	return script, log


@pytest.mark.skipif(sys.platform == "win32", reason="shebang-based fake adb")
def test_cli_run_end_to_end(server, fake_adb, tmp_path):
	adb, log = fake_adb
	FakeVLMServer.requests = []
	FakeVLMServer.replies = [
		{
			"observation": "Settings home",
			"plan": ["open Display", "toggle dark theme"],
			"thought": "Display is listed",
			"note": "",
			"action": {"type": "tap", "target": "Display", "x": 500, "y": 500},
		},
		{
			"observation": "",
			"plan": [],
			"thought": "",
			"note": "",
			"action": {"type": "done", "answer": "ok"},
		},
	]
	result = CliRunner().invoke(
		app,
		[
			"run",
			"Open display settings",
			"-c",
			str(DEFAULT_CONFIG),
			"--base-url",
			server,
			"--model",
			"test-model",
			"-s",
			f"device.adb_path={adb}",
			"-s",
			"agent.settle_seconds=0",
			"-s",
			"agent.stable_timeout=0",
			"-s",
			f"agent.record_dir={tmp_path / 'runs'}",
		],
	)
	assert result.exit_code == 0, result.output
	adb_calls = log.read_text().splitlines()
	assert "shell input keyevent KEYCODE_WAKEUP" in adb_calls
	assert "shell input tap 540 1200" in adb_calls

	first = FakeVLMServer.requests[0]
	assert first["model"] == "test-model"
	assert first["response_format"]["type"] == "json_schema"
	assert first["chat_template_kwargs"] == {"thinking": False, "enable_thinking": False}
	user_parts = first["messages"][1]["content"]
	image_urls = [p["image_url"]["url"] for p in user_parts if p["type"] == "image_url"]
	assert len(image_urls) == 1 and image_urls[0].startswith("data:image/jpeg;base64,")
	assert "Foreground app package: com.android.settings" in json.dumps(user_parts)
	assert list((tmp_path / "runs").glob("*/report.html"))


def test_cli_devices(fake_adb):
	adb, _ = fake_adb
	result = CliRunner().invoke(app, ["devices", "--adb-path", str(adb)])
	assert result.exit_code == 0 and "emulator-5554" in result.output
