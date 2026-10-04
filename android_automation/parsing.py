"""Turn raw model text into a validated ``AgentStep``.

Constrained decoding usually yields clean JSON, but backends without it (transformers,
some hosted APIs) and models trained on other action vocabularies (``click``,
``coordinate: [x, y]``, ``terminate``...) are common, so the parser is forgiving: it
strips reasoning, finds the JSON object, and maps well-known aliases onto our schema.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from android_automation.actions import AgentStep


class ParseError(ValueError):
	pass


_THINK = re.compile(r"<think>.*?</think>", re.S | re.I)
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S | re.I)

_TYPE_ALIASES = {
	"click": "tap",
	"click_element": "tap",
	"press": "tap",
	"touch": "tap",
	"double_click": "double_tap",
	"doubletap": "double_tap",
	"long_click": "long_press",
	"longpress": "long_press",
	"long_tap": "long_press",
	"input": "type",
	"input_text": "type",
	"type_text": "type",
	"write": "type",
	"write_element": "type",
	"write_element_abs": "type",
	"drag": "swipe",
	"key": "press_key",
	"keyevent": "press_key",
	"press_button": "press_key",
	"system_button": "press_key",
	"open": "open_app",
	"launch": "open_app",
	"launch_app": "open_app",
	"open_application": "open_app",
	"sleep": "wait",
	"ask": "ask_user",
	"call_user": "ask_user",
	"answer": "done",
	"finish": "done",
	"finished": "done",
	"complete": "done",
	"completed": "done",
	"success": "done",
	"stop": "done",
	"failed": "fail",
	"failure": "fail",
	"impossible": "fail",
	"infeasible": "fail",
}
_KEY_SHORTCUTS = {
	"back": "back",
	"go_back": "back",
	"navigate_back": "back",
	"home": "home",
	"go_home": "home",
	"navigate_home": "home",
	"enter": "enter",
	"recent": "app_switch",
	"recents": "app_switch",
	"app_switch": "app_switch",
}
_KEY_ALIASES = {
	"return": "enter",
	"recent": "app_switch",
	"recents": "app_switch",
	"del": "delete",
	"backspace": "delete",
}
_FIELD_ALIASES = {
	"type": {"action_type", "action", "name", "kind"},
	"text": {"content", "value", "input", "input_text"},
	"app": {"app_name", "package", "package_name", "name"},
	"key": {"button", "keycode", "key_name", "name"},
	"answer": {"content", "message", "text", "summary", "result", "return"},
	"reason": {"message", "content", "text", "why"},
	"question": {"content", "message", "text"},
	"target": {"element", "description", "element_description"},
}
_POINT_KEYS = (
	"coordinate",
	"coordinates",
	"point",
	"position",
	"center",
	"start_box",
	"box",
	"bbox",
)
_STEP_FIELDS = {"observation", "plan", "thought", "note", "action", "reasoning", "memory"}


def strip_reasoning(text: str) -> str:
	text = _THINK.sub("", text)
	if "</think>" in text:  # opening tag consumed by the chat template
		text = text.rsplit("</think>", 1)[1]
	return text.strip()


def extract_json(text: str) -> dict[str, Any]:
	"""Return the first JSON object found in ``text``."""
	text = strip_reasoning(text)
	candidates = [m.group(1) for m in _FENCE.finditer(text)] + [text]
	decoder = json.JSONDecoder()
	for cand in candidates:
		for i, ch in enumerate(cand):
			if ch != "{":
				continue
			try:
				obj, _ = decoder.raw_decode(cand[i:])
			except json.JSONDecodeError:
				continue
			if isinstance(obj, dict):
				return obj
	raise ParseError("no JSON object found in the reply")


def _as_point(value: Any) -> tuple[float, float] | None:
	if isinstance(value, str):
		nums = re.findall(r"-?\d+(?:\.\d+)?", value)
		value = [float(n) for n in nums]
	if isinstance(value, dict) and "x" in value and "y" in value:
		return float(value["x"]), float(value["y"])
	if isinstance(value, list | tuple) and all(isinstance(v, int | float) for v in value):
		if len(value) == 2:
			return float(value[0]), float(value[1])
		if len(value) == 4:  # bounding box -> centre
			return (value[0] + value[2]) / 2, (value[1] + value[3]) / 2
	return None


def normalize_action(action: dict[str, Any]) -> dict[str, Any]:
	a = dict(action)
	if "type" not in a:
		for alias in _FIELD_ALIASES["type"]:
			if isinstance(a.get(alias), str):
				a["type"] = a.pop(alias)
				break
	kind = str(a.get("type", "")).strip().lower().replace("-", "_").replace(" ", "_")

	if kind in _KEY_SHORTCUTS:
		a.setdefault("key", _KEY_SHORTCUTS[kind])
		kind = "press_key"
	elif kind.startswith("scroll_") and "direction" not in a:
		a["direction"] = kind.removeprefix("scroll_")
		kind = "scroll"
	elif kind == "terminate":
		status = str(a.get("status", "success")).lower()
		kind = "fail" if status in {"failure", "fail", "failed", "infeasible"} else "done"
	kind = _TYPE_ALIASES.get(kind, kind)
	a["type"] = kind

	for field, aliases in _FIELD_ALIASES.items():
		if field == "type" or field in a:
			continue
		for alias in aliases:
			if alias in a and alias != "type":
				a[field] = a[alias]
				break

	if a.get("x") is None or a.get("y") is None:
		for key in _POINT_KEYS:
			point = _as_point(a.get(key))
			if point:
				a["x"], a["y"] = point
				break

	if kind == "swipe":
		for keys, (fx, fy) in (
			(("start", "from", "start_point", "start_coordinate"), ("x1", "y1")),
			(("end", "to", "end_point", "end_coordinate", "end_box"), ("x2", "y2")),
		):
			if a.get(fx) is None:
				for key in keys:
					point = _as_point(a.get(key))
					if point:
						a[fx], a[fy] = point
						break
		if a.get("x1") is None and a.get("x") is not None:
			a["x1"], a["y1"] = a["x"], a["y"]

	if kind == "press_key" and isinstance(a.get("key"), str):
		key = a["key"].strip().lower().removeprefix("keycode_")
		a["key"] = _KEY_ALIASES.get(key, key)
	if kind == "scroll" and isinstance(a.get("direction"), str):
		a["direction"] = a["direction"].strip().lower()
	return a


def normalize_step(data: dict[str, Any]) -> dict[str, Any]:
	d = dict(data)
	action = d.get("action")
	if isinstance(action, str):
		# Flattened: {"action": "tap", "x": .., "y": ..}
		extras = {k: v for k, v in d.items() if k not in _STEP_FIELDS}
		action = {"type": action, **extras}
	elif action is None and any(k in d for k in ("type", "action_type")):
		action = {k: v for k, v in d.items() if k not in _STEP_FIELDS}
	elif isinstance(action, list) and action and isinstance(action[0], dict):
		action = action[0]  # one action per turn; the rest belongs in the plan
	if isinstance(action, dict):
		d["action"] = normalize_action(action)
	if "thought" not in d and isinstance(d.get("reasoning"), str):
		d["thought"] = d["reasoning"]
	if "note" not in d and isinstance(d.get("memory"), str):
		d["note"] = d["memory"]
	plan = d.get("plan")
	if isinstance(plan, str):
		d["plan"] = [s.strip(" -*\t") for s in plan.splitlines() if s.strip(" -*\t")]
	elif isinstance(plan, list):
		d["plan"] = [p if isinstance(p, str) else json.dumps(p) for p in plan]
	for key in ("observation", "thought", "note"):
		if d.get(key) is None:
			d.pop(key, None)
	return d


def parse_step(text: str) -> AgentStep:
	data = extract_json(text)
	try:
		return AgentStep.model_validate(normalize_step(data))
	except ValidationError as e:
		problems = "; ".join(
			f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in e.errors()[:5]
		)
		raise ParseError(f"JSON does not match the schema: {problems}") from e
