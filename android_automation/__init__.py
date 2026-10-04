"""Automate any Android app with vision-language models.

from android_automation import Agent, load_config

agent = Agent.from_config(load_config())
result = agent.run("Open YouTube and search for 'Surah Al-Kahf recitation'")
print(result.status, result.answer, result.run_dir)
"""

from android_automation.actions import AgentStep
from android_automation.agent import Agent, RunResult, StepEvent
from android_automation.config import Config, load_config
from android_automation.device import AdbDevice, Device, DryRunDevice
from android_automation.grounding import Grounder
from android_automation.tasks import Task, load_task, run_task
from android_automation.vlm import VLM, Message, build_vlm

__version__ = "0.1.0"

__all__ = [
	"AdbDevice",
	"Agent",
	"AgentStep",
	"Config",
	"Device",
	"DryRunDevice",
	"Grounder",
	"Message",
	"RunResult",
	"StepEvent",
	"Task",
	"VLM",
	"build_vlm",
	"load_config",
	"load_task",
	"run_task",
]
