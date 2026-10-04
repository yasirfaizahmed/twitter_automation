"""The JSON contract between the VLM and the executor.

Every turn the model returns one ``AgentStep``: what it sees, its updated plan
(the goal broken down into remaining sub-steps), and exactly one ``Action`` to
run next. Coordinates are in the model's coordinate space (see ``coords.py``),
never in device pixels.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class _Action(BaseModel):
	model_config = ConfigDict(extra="ignore")


class _Pointed(_Action):
	target: str = Field(
		default="",
		description="Short visual description of the UI element, e.g. 'blue Post button, top right'.",
	)
	x: float | None = Field(default=None, description="Horizontal position of the element centre.")
	y: float | None = Field(default=None, description="Vertical position of the element centre.")


class Tap(_Pointed):
	"""Tap a UI element."""

	type: Literal["tap"] = "tap"


class DoubleTap(_Pointed):
	"""Double-tap a UI element (e.g. like a photo)."""

	type: Literal["double_tap"] = "double_tap"


class LongPress(_Pointed):
	"""Press and hold a UI element (context menus, selection)."""

	type: Literal["long_press"] = "long_press"
	duration_ms: int = Field(default=800, ge=100, le=10_000)


class TypeText(_Action):
	"""Type text. If x/y or target is given the field is tapped first."""

	type: Literal["type"] = "type"
	text: str = Field(description="Text to type. Use {{NAME}} to type a declared secret.")
	target: str = ""
	x: float | None = None
	y: float | None = None
	clear: bool = Field(default=False, description="Clear the field before typing.")
	submit: bool = Field(default=False, description="Press Enter after typing.")


class Swipe(_Action):
	"""Drag from (x1, y1) to (x2, y2). Use for sliders, drag-and-drop, precise gestures."""

	type: Literal["swipe"] = "swipe"
	x1: float
	y1: float
	x2: float
	y2: float
	duration_ms: int = Field(default=300, ge=50, le=10_000)


class Scroll(_Action):
	"""Scroll content. 'down' reveals content further down (the finger moves up)."""

	type: Literal["scroll"] = "scroll"
	direction: Literal["up", "down", "left", "right"]
	distance: Literal["short", "medium", "long"] = "medium"
	target: str = Field(default="", description="Optional scrollable area to scroll inside.")
	x: float | None = None
	y: float | None = None


Key = Literal[
	"back",
	"home",
	"enter",
	"app_switch",
	"delete",
	"tab",
	"search",
	"volume_up",
	"volume_down",
	"power",
]


class PressKey(_Action):
	"""Press a hardware/system key."""

	type: Literal["press_key"] = "press_key"
	key: Key


class OpenApp(_Action):
	"""Launch an app by name ('YouTube') or package ('com.google.android.youtube')."""

	type: Literal["open_app"] = "open_app"
	app: str


class Wait(_Action):
	"""Wait for loading/animations."""

	type: Literal["wait"] = "wait"
	seconds: float = Field(default=2.0, ge=0.0, le=30.0)


class AskUser(_Action):
	"""Ask the human for information only they have (OTP code, a choice)."""

	type: Literal["ask_user"] = "ask_user"
	question: str


class Done(_Action):
	"""The goal is achieved. Put any requested information in ``answer``."""

	type: Literal["done"] = "done"
	answer: str = ""


class Fail(_Action):
	"""The goal cannot be achieved; explain why."""

	type: Literal["fail"] = "fail"
	reason: str


Action = Annotated[
	Tap
	| DoubleTap
	| LongPress
	| TypeText
	| Swipe
	| Scroll
	| PressKey
	| OpenApp
	| Wait
	| AskUser
	| Done
	| Fail,
	Field(discriminator="type"),
]

ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)
POINTED_ACTIONS = (Tap, DoubleTap, LongPress)
TERMINAL_ACTIONS = (Done, Fail)


class AgentStep(BaseModel):
	"""One model turn: observation, the broken-down plan, and the next action."""

	model_config = ConfigDict(extra="ignore")

	observation: str = Field(
		default="", description="What is on screen that matters for the goal (1-2 sentences)."
	)
	plan: list[str] = Field(
		default_factory=list,
		description="Remaining sub-steps to reach the goal, next one first. Revise it every turn.",
	)
	thought: str = Field(default="", description="Why the action below is the right next move.")
	note: str = Field(
		default="",
		description="Facts to remember for later steps (values read from screen, etc). Empty if none.",
	)
	action: Action


def describe(action: _Action) -> str:
	"""One-line, human readable summary used in history and logs."""
	data = action.model_dump(exclude_none=True, exclude_defaults=True)
	kind = getattr(action, "type", type(action).__name__)
	args = ", ".join(
		f"{k}={int(v) if isinstance(v, float) and v.is_integer() else v!r}"
		for k, v in data.items()
		if k != "type"
	)
	return f"{kind}({args})"
