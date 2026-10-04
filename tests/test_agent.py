import json

import pytest

from android_automation.agent import Agent
from android_automation.config import ModelConfig
from android_automation.device import DryRunDevice
from android_automation.grounding import Grounder
from tests.conftest import FakeDevice, ScriptedVLM, step


def make_agent(vlm, dev, config, **kw):
	return Agent(vlm, dev, config, sleep=lambda s: None, **kw)


def run_files_text(run_dir) -> str:
	return "\n".join(
		p.read_text() for p in run_dir.iterdir() if p.suffix in {".json", ".jsonl", ".html"}
	)


def test_tap_then_done_records_everything(config):
	dev = FakeDevice()
	vlm = ScriptedVLM(
		[
			step({"type": "tap", "target": "OK button", "x": 500, "y": 500}, observation="dialog"),
			step({"type": "done", "answer": "pressed"}),
		]
	)
	res = make_agent(vlm, dev, config).run("press OK")

	assert res.success and res.answer == "pressed" and res.steps == 2
	assert dev.gestures() == [("tap", 540, 1200)]
	second = vlm.prompt_text(1)
	assert "tap(target='OK button', x=500, y=500)" in second
	assert "done at (540, 1200)px." in second
	assert "<goal>\npress OK\n</goal>" in second
	rows = [json.loads(line) for line in (res.run_dir / "steps.jsonl").read_text().splitlines()]
	assert [r["index"] for r in rows] == [0, 1]
	assert rows[0]["device_points"] == [[540, 1200]] and rows[0]["screen_changed"] is True
	assert "system_prompt" in rows[0]
	assert (res.run_dir / "report.html").exists()
	assert (res.run_dir / "step_000_action.png").exists()


def test_schema_is_sent_for_constrained_decoding(config):
	vlm = ScriptedVLM([step({"type": "done"})])
	make_agent(vlm, FakeDevice(), config).run("x")
	schema = vlm.requests[0][1]
	assert "action" in schema["required"]


def test_parse_retry_then_success(config):
	vlm = ScriptedVLM(["I think I should tap", step({"type": "done"})])
	res = make_agent(vlm, FakeDevice(), config).run("x")
	assert res.success
	retry_msgs = vlm.requests[1][0]
	assert retry_msgs[-2].role == "assistant" and "could not be used" in retry_msgs[-1].text()


def test_gives_up_on_unparseable_output(config):
	config.agent.max_parse_retries = 1
	vlm = ScriptedVLM(["nope", "still nope"])
	res = make_agent(vlm, FakeDevice(), config).run("x")
	assert res.status == "error" and "unusable" in res.reason


def test_fail_action(config):
	vlm = ScriptedVLM([step({"type": "fail", "reason": "app not installed"})])
	res = make_agent(vlm, FakeDevice(), config).run("x")
	assert res.status == "failed" and res.reason == "app not installed"


def test_secrets_are_typed_but_never_shown_or_recorded(config):
	dev = FakeDevice()
	vlm = ScriptedVLM(
		[
			step(
				{
					"type": "type",
					"text": "{{PW}}",
					"target": "password",
					"x": 500,
					"y": 400,
					"submit": True,
				}
			),
			step({"type": "done"}),
		]
	)
	res = make_agent(vlm, dev, config, secrets={"PW": "hunter2"}).run("log in")
	assert dev.gestures() == [
		("tap", 540, 960),
		("type_text", "hunter2"),
		("press_key", "enter"),
	]
	assert "{{PW}}" in vlm.prompt_text(0)
	assert all("hunter2" not in vlm.prompt_text(i) for i in range(2))
	assert "hunter2" not in run_files_text(res.run_dir)


def test_unknown_secret_is_refused(config):
	dev = FakeDevice()
	vlm = ScriptedVLM(
		[step({"type": "type", "text": "{{AWS_SECRET_KEY}}"}), step({"type": "done"})]
	)
	make_agent(vlm, dev, config).run("x")
	assert dev.gestures() == []
	assert "FAILED: unknown secret placeholder {{AWS_SECRET_KEY}}" in vlm.prompt_text(1)


def test_stuck_detection_warns_then_stops(config):
	config.agent.stuck_threshold = 2
	dev = FakeDevice(static=True)
	tap = step({"type": "tap", "target": "dead button", "x": 10, "y": 10})
	vlm = ScriptedVLM([tap] * 4)
	res = make_agent(vlm, dev, config).run("x")
	assert res.status == "stuck" and res.steps == 4
	assert "did not visibly change" in vlm.prompt_text(1)
	assert "WARNING" not in vlm.prompt_text(1)
	assert "WARNING: the last 2 actions were identical" in vlm.prompt_text(2)


def test_external_grounder_overrides_model_coordinates(config):
	dev = FakeDevice()
	grounder = Grounder(ScriptedVLM(['{"x": 250, "y": 750}']), ModelConfig())
	vlm = ScriptedVLM(
		[step({"type": "tap", "target": "Like", "x": 1, "y": 1}), step({"type": "done"})]
	)
	make_agent(vlm, dev, config, grounder=grounder).run("like it")
	assert dev.gestures() == [("tap", 270, 1800)]
	assert "Like" in grounder.vlm.prompt_text(0)


def test_self_grounding_when_coordinates_missing(config):
	dev = FakeDevice()
	vlm = ScriptedVLM(
		[step({"type": "tap", "target": "Like"}), "Click(250, 750)", step({"type": "done"})]
	)
	make_agent(vlm, dev, config).run("like it")
	assert dev.gestures() == [("tap", 270, 1800)]
	assert vlm.requests[1][1]["required"] == ["x", "y"]


def test_tap_without_position_or_target_is_reported(config):
	dev = FakeDevice()
	vlm = ScriptedVLM([step({"type": "tap"}), step({"type": "done"})])
	make_agent(vlm, dev, config).run("x")
	assert dev.gestures() == []
	assert "FAILED: tap needs x/y or a target" in vlm.prompt_text(1)


def test_out_of_bounds_coordinates_are_clamped_with_warning(config):
	dev = FakeDevice()
	vlm = ScriptedVLM([step({"type": "tap", "x": 1500, "y": 500}), step({"type": "done"})])
	make_agent(vlm, dev, config).run("x")
	assert dev.gestures() == [("tap", 1079, 1200)]
	assert "outside the screen" in vlm.prompt_text(1)


@pytest.mark.parametrize(
	"direction, expected",
	[
		("down", ("swipe", 540, 1680, 540, 720, 400)),
		("up", ("swipe", 540, 720, 540, 1680, 400)),
		("right", ("swipe", 756, 1200, 324, 1200, 400)),
	],
)
def test_scroll_direction(config, direction, expected):
	dev = FakeDevice()
	vlm = ScriptedVLM([step({"type": "scroll", "direction": direction}), step({"type": "done"})])
	make_agent(vlm, dev, config).run("x")
	assert dev.gestures() == [expected]


def test_other_actions_reach_the_device(config):
	dev = FakeDevice()
	vlm = ScriptedVLM(
		[
			step({"type": "open_app", "app": "YouTube"}),
			step({"type": "press_key", "key": "back"}),
			step({"type": "long_press", "x": 0, "y": 0, "duration_ms": 1000}),
			step({"type": "swipe", "x1": 0, "y1": 1000, "x2": 1000, "y2": 0}),
			step({"type": "wait", "seconds": 1}),
			step({"type": "done"}),
		]
	)
	res = make_agent(vlm, dev, config).run("x")
	assert res.success
	assert dev.calls == [
		("open_app", "YouTube"),
		("press_key", "back"),
		("long_press", 0, 0, 1000),
		("swipe", 0, 2399, 1079, 0, 300),
	]
	assert "launched pkg.YouTube." in vlm.prompt_text(1)


def test_confirm_can_reject(config):
	dev = FakeDevice()
	vlm = ScriptedVLM([step({"type": "tap", "x": 1, "y": 1}), step({"type": "done"})])
	make_agent(vlm, dev, config, confirm=lambda i, s: False).run("x")
	assert dev.gestures() == []
	assert "SKIPPED" in vlm.prompt_text(1)


def test_ask_user_answer_reaches_the_model(config):
	vlm = ScriptedVLM([step({"type": "ask_user", "question": "OTP?"}), step({"type": "done"})])
	make_agent(vlm, FakeDevice(), config, ask_user=lambda q: "123456").run("x")
	assert "The user answered: '123456'" in vlm.prompt_text(1)


def test_max_steps(config):
	config.agent.max_steps = 2
	vlm = ScriptedVLM([step({"type": "wait"})] * 2)
	res = make_agent(vlm, FakeDevice(), config).run("x")
	assert res.status == "max_steps" and res.steps == 2


def test_backend_errors_end_the_run_cleanly(config):
	class Broken(ScriptedVLM):
		def complete(self, *a, **k):
			raise ConnectionError("server down")

	res = make_agent(Broken([]), FakeDevice(), config).run("x")
	assert res.status == "error" and "server down" in res.reason
	assert (res.run_dir / "result.json").exists()


def test_dry_run_never_touches_the_device(config):
	inner = FakeDevice()
	vlm = ScriptedVLM([step({"type": "tap", "x": 1, "y": 1}), step({"type": "done"})])
	make_agent(vlm, DryRunDevice(inner), config).run("x")
	assert inner.calls == []


def test_history_images_sends_previous_screens(config):
	config.agent.history_images = 2
	vlm = ScriptedVLM([step({"type": "tap", "x": 1, "y": 1}), step({"type": "done"})])
	make_agent(vlm, FakeDevice(), config).run("x")
	from PIL import Image

	def n_images(i):
		return sum(isinstance(p, Image.Image) for m in vlm.requests[i][0] for p in m.content)

	assert (n_images(0), n_images(1)) == (1, 2)


def test_plan_and_notes_carry_forward(config):
	vlm = ScriptedVLM(
		[
			step({"type": "wait"}, plan=["open search", "type query"], note="price is 10"),
			step({"type": "done"}, plan=[]),
		]
	)
	res = make_agent(vlm, FakeDevice(), config).run("x")
	second = vlm.prompt_text(1)
	assert "1. open search\n2. type query" in second and "- price is 10" in second
	assert res.plan == ["open search", "type query"] and res.notes == ["price is 10"]
