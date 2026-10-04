from pathlib import Path

import pytest
from pydantic import ValidationError

from android_automation.agent import Agent
from android_automation.config import load_config
from android_automation.tasks import Task, load_task, run_task
from tests.conftest import FakeDevice, ScriptedVLM, step

ROOT = Path(__file__).resolve().parents[1]


def test_render_goal():
	t = Task(
		name="t",
		goal="Reply to {{ handle }} and log in with {{PW}}",
		params={"handle": "@a"},
		secrets=["PW"],
	)
	assert t.render_goal() == "Reply to @a and log in with {{PW}}"
	assert t.render_goal({"handle": "@b"}).startswith("Reply to @b")
	with pytest.raises(KeyError, match="missing"):
		Task(goal="hi {{missing}}").render_goal()


def test_resolve_secrets(monkeypatch):
	t = Task(goal="g", secrets=["TOK"])
	with pytest.raises(KeyError, match="TOK"):
		t.resolve_secrets()
	monkeypatch.setenv("TOK", "")  # compose passes unset variables as ""
	with pytest.raises(KeyError, match="TOK"):
		t.resolve_secrets()
	monkeypatch.setenv("TOK", "s3cret")
	assert t.resolve_secrets() == {"TOK": "s3cret"}


def test_push_paths_are_rendered_and_relative_to_the_task_file(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path.parent)
	(tmp_path / "img.png").write_bytes(b"x")
	f = tmp_path / "post.yaml"
	f.write_text(
		"goal: post it\napp: x\nparams: {image: img.png}\n"
		"push_files:\n  - {src: '{{image}}', dest: '/sdcard/Pictures/{{image}}'}\n"
	)
	t = load_task(f)
	assert t.name == "post"
	[pf] = t.files_to_push()
	assert (pf.src, pf.dest) == (str(tmp_path / "img.png"), "/sdcard/Pictures/img.png")
	[pf] = t.files_to_push({"image": str(tmp_path / "img.png")})
	assert pf.src == str(tmp_path / "img.png")


def test_unknown_task_keys_are_rejected(tmp_path):
	f = tmp_path / "bad.yaml"
	f.write_text("goal: g\nappp: typo\n")
	with pytest.raises(ValidationError):
		load_task(f)


def test_run_task_prepares_device(config, monkeypatch, tmp_path):
	monkeypatch.setenv("PW", "pw")
	monkeypatch.chdir(tmp_path)
	(tmp_path / "a.png").write_bytes(b"x")
	dev = FakeDevice()
	vlm = ScriptedVLM([step({"type": "done"})])
	agent = Agent(vlm, dev, config, sleep=lambda s: None)
	t = Task(
		goal="do {{thing}}",
		app="x",
		reset_app=True,
		params={"thing": "it"},
		secrets=["PW"],
		push_files=[{"src": "a.png", "dest": "/sdcard/a.png"}],
		max_steps=3,
	)
	res = run_task(agent, t)
	assert res.success
	assert dev.calls == [
		("push_file", "a.png", "/sdcard/a.png"),
		("force_stop", "x"),
		("open_app", "x"),
	]
	with pytest.raises(FileNotFoundError):
		run_task(
			agent, Task(goal="g", push_files=[{"src": "missing.png", "dest": "/sdcard/m.png"}])
		)
	assert "<goal>\ndo it\n</goal>" in vlm.prompt_text(0)
	assert "{{PW}}" in vlm.prompt_text(0) and "at most 3" in vlm.prompt_text(0)
	# task settings do not leak into the next run with the same agent
	assert agent.secrets == {} and agent.config.agent.max_steps == 30


@pytest.mark.parametrize("path", sorted((ROOT / "examples" / "tasks").glob("*.yaml")))
def test_example_tasks_are_valid(path):
	t = load_task(path)
	assert t.goal
	t.render_goal()
	t.files_to_push()


@pytest.mark.parametrize("path", sorted((ROOT / "configs").glob("*.yaml")))
def test_shipped_configs_load(path):
	cfg = load_config(path)
	assert cfg.model.model


def test_overrides_and_sets(tmp_path):
	f = tmp_path / "c.yaml"
	f.write_text("model:\n  model: a\n  base_url: http://h:1/v1\napps:\n  Foo: com.foo\n")
	cfg = load_config(
		f,
		overrides={"model.model": "b", "device.serial": None},
		sets=[
			"agent.max_steps=7",
			"grounder.model=g",
			"model.chat_template_kwargs={thinking: false}",
		],
	)
	assert cfg.model.model == "b" and cfg.model.base_url == "http://h:1/v1"
	assert cfg.agent.max_steps == 7 and cfg.grounder.model == "g"
	assert cfg.model.chat_template_kwargs == {"thinking": False}
	assert cfg.device.serial is None
	assert cfg.app_aliases()["foo"] == "com.foo" and cfg.app_aliases()["x"] == "com.twitter.android"


def test_typos_in_config_are_errors(tmp_path):
	f = tmp_path / "c.yaml"
	f.write_text("agent:\n  max_step: 3\n")
	with pytest.raises(ValidationError):
		load_config(f)


def test_environment_overrides(tmp_path, monkeypatch):
	f = tmp_path / "c.yaml"
	f.write_text("model:\n  model: from-file\n")
	monkeypatch.setenv("ANDROID_AUTOMATION__MODEL__BASE_URL", "http://vllm:8000/v1")
	monkeypatch.setenv("ANDROID_AUTOMATION__AGENT__MAX_STEPS", "12")
	monkeypatch.setenv("ANDROID_AUTOMATION__MODEL__MODEL", "from-env")
	monkeypatch.setenv("ANDROID_AUTOMATION__AGENT__STUCK_THRESHOLD", "")  # empty = unset
	cfg = load_config(f)
	assert cfg.agent.stuck_threshold == 3
	assert cfg.model.base_url == "http://vllm:8000/v1" and cfg.agent.max_steps == 12
	assert cfg.model.model == "from-env"
	assert load_config(f, overrides={"model.model": "from-cli"}).model.model == "from-cli"
