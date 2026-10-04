"""Command line interface: ``android-automation --help``."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from android_automation.actions import AgentStep, describe
from android_automation.agent import Aborted, Agent, RunResult, StepEvent
from android_automation.config import Config, load_config

app = typer.Typer(
	help="Drive any Android app with a vision-language model over ADB.",
	no_args_is_help=True,
	add_completion=False,
)
console = Console()

ConfigOpt = Annotated[
	Path | None,
	typer.Option("--config", "-c", help="YAML config (default: ./configs/default.yaml)."),
]
SetOpt = Annotated[
	list[str] | None,
	typer.Option("--set", "-s", help="Override any config key, e.g. -s agent.max_steps=50."),
]
ModelOpt = Annotated[str | None, typer.Option(help="Model name (model.model).")]
BaseUrlOpt = Annotated[
	str | None, typer.Option(help="OpenAI-compatible base URL (model.base_url).")
]
BackendOpt = Annotated[str | None, typer.Option(help="openai | transformers (model.backend).")]
SerialOpt = Annotated[str | None, typer.Option(help="ADB device serial (device.serial).")]
MaxStepsOpt = Annotated[int | None, typer.Option(help="Step budget (agent.max_steps).")]
SecretOpt = Annotated[
	list[str] | None,
	typer.Option("--secret", help="Env var the model may type as {{NAME}} without seeing it."),
]
DryRunOpt = Annotated[bool, typer.Option("--dry-run", help="Observe only, never touch the device.")]
ConfirmOpt = Annotated[bool, typer.Option("--confirm", help="Ask before every device action.")]
NoRecordOpt = Annotated[bool, typer.Option("--no-record", help="Do not save a run folder.")]
VerboseOpt = Annotated[bool, typer.Option("--verbose", "-v", help="Debug logging.")]


def _setup_logging(verbose: bool) -> None:
	logging.basicConfig(
		level=logging.DEBUG if verbose else logging.WARNING,
		format="%(message)s",
		handlers=[RichHandler(console=console, show_path=False)],
	)


def _config(
	config: Path | None,
	sets: list[str] | None,
	*,
	model: str | None = None,
	base_url: str | None = None,
	backend: str | None = None,
	serial: str | None = None,
	max_steps: int | None = None,
	no_record: bool = False,
) -> Config:
	overrides: dict[str, object] = {
		"model.model": model,
		"model.base_url": base_url,
		"model.backend": backend,
		"device.serial": serial,
		"agent.max_steps": max_steps,
	}
	cfg = load_config(config, overrides, sets)
	if no_record:
		cfg.agent.record_dir = None
	return cfg


def _secrets(names: list[str] | None) -> dict[str, str]:
	out = {}
	for name in names or []:
		if not os.environ.get(name):
			raise typer.BadParameter(
				f"environment variable {name} is not set or empty", param_hint="--secret"
			)
		out[name] = os.environ[name]
	return out


def _print_step(ev: StepEvent) -> None:
	s = ev.step
	body = []
	if s.observation:
		body.append(f"[bold]Sees[/] {s.observation}")
	if s.plan:
		body.append("[bold]Plan[/]\n" + "\n".join(f"  {i + 1}. {p}" for i, p in enumerate(s.plan)))
	if s.thought:
		body.append(f"[bold]Thinks[/] {s.thought}")
	if s.note:
		body.append(f"[bold]Notes[/] {s.note}")
	body.append(f"[bold cyan]Action[/] {ev.action}")
	body.append(f"[bold]Result[/] {ev.feedback}  [dim]({ev.response.latency_s:.1f}s)[/]")
	console.print(Panel("\n".join(body), title=f"Step {ev.index + 1}", title_align="left"))


def _confirm(index: int, step: AgentStep) -> bool:
	answer = Prompt.ask(
		f"Execute [cyan]{describe(step.action)}[/]?", choices=["y", "n", "q"], default="y"
	)
	if answer == "q":
		raise Aborted()
	return answer == "y"


def _ask_user(question: str) -> str:
	return Prompt.ask(f"[yellow]The agent asks:[/] {question}")


def _make_agent(cfg: Config, dry_run: bool, confirm: bool, secrets: dict[str, str]) -> Agent:
	return Agent.from_config(
		cfg,
		dry_run=dry_run,
		secrets=secrets,
		on_step=_print_step,
		confirm=_confirm if confirm else None,
		ask_user=_ask_user,
	)


def _report(result: RunResult) -> None:
	style = "green" if result.success else "red"
	lines = [f"[bold {style}]{result.status}[/] after {result.steps} step(s)"]
	if result.answer:
		lines.append(f"[bold]Answer[/] {result.answer}")
	if result.reason:
		lines.append(f"[bold]Reason[/] {result.reason}")
	if result.run_dir:
		lines.append(f"[dim]Run saved to {result.run_dir}/report.html[/]")
	console.print(Panel("\n".join(lines), border_style=style))


@app.command()
def run(
	goal: Annotated[str, typer.Argument(help="What to achieve, in plain language.")],
	app_name: Annotated[
		str | None, typer.Option("--app", help="Launch this app (name or package) first.")
	] = None,
	config: ConfigOpt = None,
	set_: SetOpt = None,
	model: ModelOpt = None,
	base_url: BaseUrlOpt = None,
	backend: BackendOpt = None,
	serial: SerialOpt = None,
	max_steps: MaxStepsOpt = None,
	secret: SecretOpt = None,
	dry_run: DryRunOpt = False,
	confirm: ConfirmOpt = False,
	no_record: NoRecordOpt = False,
	verbose: VerboseOpt = False,
) -> None:
	"""Run the agent on a free-form GOAL."""
	from android_automation.tasks import Task, run_task

	_setup_logging(verbose)
	cfg = _config(
		config,
		set_,
		model=model,
		base_url=base_url,
		backend=backend,
		serial=serial,
		max_steps=max_steps,
		no_record=no_record,
	)
	agent = _make_agent(cfg, dry_run, confirm, _secrets(secret))
	console.print(f"[bold]Goal[/] {goal}  [dim]model={cfg.model.model}[/]")
	result = run_task(agent, Task(goal=goal, app=app_name))
	_report(result)
	raise typer.Exit(0 if result.success else 1)


@app.command()
def task(
	files: Annotated[list[Path], typer.Argument(help="Task YAML file(s), run in order.")],
	param: Annotated[
		list[str] | None, typer.Option("--param", "-p", help="Task parameter key=value.")
	] = None,
	config: ConfigOpt = None,
	set_: SetOpt = None,
	model: ModelOpt = None,
	base_url: BaseUrlOpt = None,
	backend: BackendOpt = None,
	serial: SerialOpt = None,
	max_steps: MaxStepsOpt = None,
	secret: SecretOpt = None,
	dry_run: DryRunOpt = False,
	confirm: ConfirmOpt = False,
	no_record: NoRecordOpt = False,
	verbose: VerboseOpt = False,
) -> None:
	"""Run task file(s). Stops at the first task that does not succeed."""
	from android_automation.tasks import load_task, run_task

	_setup_logging(verbose)
	params = dict(p.split("=", 1) for p in (param or []) if "=" in p)
	cfg = _config(
		config,
		set_,
		model=model,
		base_url=base_url,
		backend=backend,
		serial=serial,
		max_steps=max_steps,
		no_record=no_record,
	)
	tasks = [load_task(path) for path in files]
	agent = _make_agent(cfg, dry_run, confirm, _secrets(secret))
	for t in tasks:
		console.rule(f"[bold]{t.name}")
		console.print(f"[bold]Goal[/] {t.render_goal(params)}")
		result = run_task(agent, t, params)
		_report(result)
		if not result.success:
			raise typer.Exit(1)


@app.command()
def devices(adb_path: str = "adb") -> None:
	"""List devices visible to adb."""
	from android_automation.device import list_devices

	table = Table("serial", "state", "details")
	for d in list_devices(adb_path):
		table.add_row(d.serial, d.state, d.description)
	console.print(table)


@app.command()
def connect(address: str, adb_path: str = "adb") -> None:
	"""adb connect HOST:PORT (wireless debugging / networked emulator)."""
	from android_automation.device import connect as adb_connect

	console.print(adb_connect(address, adb_path))


@app.command()
def screenshot(
	out: Annotated[Path, typer.Argument()] = Path("screen.png"),
	config: ConfigOpt = None,
	serial: SerialOpt = None,
) -> None:
	"""Save the current screen."""
	cfg = _config(config, None, serial=serial)
	from android_automation.device import AdbDevice

	dev = AdbDevice(serial=cfg.device.serial, adb_path=cfg.device.adb_path)
	img = dev.screenshot()
	img.save(out)
	console.print(f"saved {out} ({img.width}x{img.height}), foreground app: {dev.current_app()}")


@app.command()
def ground(
	target: Annotated[str, typer.Argument(help="Element description, e.g. 'the search icon'.")],
	tap: Annotated[bool, typer.Option(help="Also tap the located point.")] = False,
	out: Annotated[Path, typer.Option(help="Annotated screenshot path.")] = Path("ground.png"),
	config: ConfigOpt = None,
	set_: SetOpt = None,
	model: ModelOpt = None,
	base_url: BaseUrlOpt = None,
	serial: SerialOpt = None,
) -> None:
	"""Locate one element with the grounder (or main model) — handy for testing a model."""
	from android_automation.device import AdbDevice
	from android_automation.grounding import Grounder
	from android_automation.imaging import annotate
	from android_automation.vlm import build_vlm

	cfg = _config(config, set_, model=model, base_url=base_url, serial=serial)
	mcfg = cfg.grounder or cfg.model
	dev = AdbDevice(serial=cfg.device.serial, adb_path=cfg.device.adb_path)
	shot = dev.screenshot()
	fx, fy = Grounder(build_vlm(mcfg), mcfg).locate(shot, target)
	x, y = round(fx * (shot.width - 1)), round(fy * (shot.height - 1))
	annotate(shot, [(x, y)], target).save(out)
	console.print(f"{target!r} -> ({x}, {y})px; saved {out}")
	if tap:
		dev.tap(x, y)


@app.command()
def check(config: ConfigOpt = None, set_: SetOpt = None) -> None:
	"""Check adb, the device and the model endpoint."""
	from android_automation.device import AdbDevice, DeviceError, list_devices

	cfg = _config(config, set_)
	ok = True
	try:
		devs = [d for d in list_devices(cfg.device.adb_path) if d.state == "device"]
		console.print(f"[green]adb ok[/], {len(devs)} device(s) ready")
		if devs:
			dev = AdbDevice(serial=cfg.device.serial, adb_path=cfg.device.adb_path)
			img = dev.screenshot()
			console.print(f"[green]screenshot ok[/] {img.width}x{img.height}")
		else:
			ok = False
			console.print("[red]no device[/]: enable USB debugging, then `adb devices`")
	except DeviceError as e:
		ok = False
		console.print(f"[red]adb problem[/]: {e}")

	for role, mcfg in (("model", cfg.model), ("grounder", cfg.grounder)):
		if mcfg is None:
			continue
		if mcfg.backend != "openai":
			console.print(f"{role}: transformers backend, loads {mcfg.model} in-process")
			continue
		try:
			from openai import OpenAI

			client = OpenAI(base_url=mcfg.base_url, api_key=mcfg.api_key(), timeout=10)
			served = [m.id for m in client.models.list()]
			if mcfg.model in served:
				console.print(f"[green]{role} ok[/] {mcfg.model} @ {mcfg.base_url}")
			else:
				console.print(
					f"[yellow]{role}[/]: {mcfg.base_url} serves {served}, not {mcfg.model}"
				)
		except Exception as e:
			ok = False
			console.print(f"[red]{role} endpoint unreachable[/] {mcfg.base_url}: {e}")
	raise typer.Exit(0 if ok else 1)


if __name__ == "__main__":
	app()
