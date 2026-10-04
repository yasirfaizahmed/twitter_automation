"""Reusable task files (YAML).

name: like-latest-post
app: x                      # launched (and optionally force-stopped) before the agent starts
reset_app: true
goal: Open the profile of {{handle}} and like their most recent post.
params:
  handle: "@NASA"
secrets: [X_PASSWORD]       # read from the environment, typed via {{X_PASSWORD}}
push_files:                 # src is relative to the task file; params work here too
  - {src: "{{image}}", dest: /sdcard/Pictures/post.png}
max_steps: 25
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from android_automation.device.base import DeviceError

if TYPE_CHECKING:
	from android_automation.agent import Agent, RunResult

log = logging.getLogger(__name__)

_PARAM = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class PushFile(BaseModel):
	src: str
	dest: str


class Task(BaseModel):
	model_config = ConfigDict(extra="forbid")

	name: str = ""
	goal: str
	app: str | None = None
	reset_app: bool = False
	params: dict[str, str] = Field(default_factory=dict)
	secrets: list[str] = Field(default_factory=list)
	push_files: list[PushFile] = Field(default_factory=list)
	max_steps: int | None = None
	_base_dir: Path | None = PrivateAttr(default=None)

	def render(self, text: str, overrides: dict[str, str] | None = None) -> str:
		"""Fill ``{{param}}`` placeholders. Secret placeholders are left for the model to
		type; anything else unresolved is an error."""
		params = {**self.params, **(overrides or {})}

		def sub(m: re.Match[str]) -> str:
			name = m.group(1)
			if name in params:
				return str(params[name])
			if name in self.secrets:
				return m.group(0)
			raise KeyError(f"task {self.name or '<unnamed>'}: no value for {{{{{name}}}}}")

		return _PARAM.sub(sub, text)

	def render_goal(self, overrides: dict[str, str] | None = None) -> str:
		return self.render(self.goal, overrides)

	def files_to_push(self, overrides: dict[str, str] | None = None) -> list[PushFile]:
		out = []
		for f in self.push_files:
			src = Path(self.render(f.src, overrides)).expanduser()
			if not src.is_absolute() and not src.exists() and self._base_dir is not None:
				src = self._base_dir / src
			out.append(PushFile(src=str(src), dest=self.render(f.dest, overrides)))
		return out

	def resolve_secrets(self) -> dict[str, str]:
		# Empty counts as missing: compose passes unset variables through as "".
		missing = [s for s in self.secrets if not os.environ.get(s)]
		if missing:
			raise KeyError(f"set these environment variables first: {', '.join(missing)}")
		return {s: os.environ[s] for s in self.secrets}


def load_task(path: str | Path) -> Task:
	path = Path(path)
	data = yaml.safe_load(path.read_text()) or {}
	if not isinstance(data, dict):
		raise ValueError(f"{path}: a task file must be a mapping")
	data.setdefault("name", path.stem)
	task = Task.model_validate(data)
	task._base_dir = path.parent
	return task


def run_task(
	agent: Agent,
	task: Task,
	params: dict[str, str] | None = None,
	extra_secrets: dict[str, str] | None = None,
) -> RunResult:
	"""Prepare the device for ``task`` (push files, launch the app) and run the agent."""
	goal = task.render_goal(params)
	files = task.files_to_push(params)
	for f in files:
		if not Path(f.src).is_file():
			raise FileNotFoundError(f"push_files: {f.src} does not exist")
	secrets = {**task.resolve_secrets(), **(extra_secrets or {})}
	device = agent.device
	for f in files:
		device.push_file(f.src, f.dest)
	hints = []
	if task.app:
		try:
			if task.reset_app:
				resolve = getattr(device, "resolve_package", None)
				device.force_stop(resolve(task.app) if resolve else task.app)
			device.open_app(task.app)
			agent.sleep(max(agent.config.agent.settle_seconds, 1.5))
		except DeviceError as e:
			# Not fatal: the agent can still find the app on the home screen or app drawer.
			log.warning("could not open %s up front: %s", task.app, e)
			hints.append(
				f"The app '{task.app}' could not be opened automatically ({e}). "
				"Open it yourself, e.g. from the home screen, the app drawer or search."
			)

	# Task-specific settings apply to this run only; the agent can be reused afterwards.
	saved_config, saved_secrets = agent.config, agent.secrets
	agent.secrets = {**saved_secrets, **secrets}
	if task.max_steps:
		agent.config = saved_config.model_copy(
			update={"agent": saved_config.agent.model_copy(update={"max_steps": task.max_steps})}
		)
	try:
		return agent.run(goal, hints=hints)
	finally:
		agent.config, agent.secrets = saved_config, saved_secrets
