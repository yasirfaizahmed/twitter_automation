import pytest

from android_automation.actions import Done, Fail, OpenApp, PressKey, Scroll, Swipe, Tap, TypeText
from android_automation.parsing import ParseError, extract_json, parse_step


def test_clean_json():
	s = parse_step(
		'{"observation": "home", "plan": ["a", "b"], "thought": "t", "note": "",'
		' "action": {"type": "tap", "target": "Post", "x": 912, "y": 860}}'
	)
	assert isinstance(s.action, Tap)
	assert (s.action.x, s.action.y, s.action.target) == (912, 860, "Post")
	assert s.plan == ["a", "b"]


def test_reasoning_fences_and_prose_are_ignored():
	text = (
		"<think>the button {is} there</think>Sure! Here you go:\n"
		'```json\n{"thought": "x", "action": {"type": "press_key", "key": "back"}}\n```\nDone.'
	)
	assert isinstance(parse_step(text).action, PressKey)


def test_unclosed_think_prefix():
	text = 'reasoning with {"bogus": 1} braces</think>{"action": {"type": "wait"}}'
	assert parse_step(text).action.type == "wait"


def test_flattened_click_with_coordinate_list():
	s = parse_step('{"action": "click", "coordinate": [100, 200], "thought": "go"}')
	assert isinstance(s.action, Tap)
	assert (s.action.x, s.action.y) == (100, 200)
	assert s.thought == "go"


def test_holo_cookbook_style_action():
	s = parse_step(
		'{"thought": "t", "action": {"action": "click_element", "element": "Search", "x": 5, "y": 6}}'
	)
	assert isinstance(s.action, Tap)
	assert s.action.target == "Search"


def test_bbox_becomes_centre():
	s = parse_step('{"action": {"type": "tap", "bbox": [0, 0, 100, 50]}}')
	assert (s.action.x, s.action.y) == (50, 25)


@pytest.mark.parametrize(
	"action, expected",
	[
		({"type": "back"}, PressKey),
		({"type": "press_key", "key": "KEYCODE_HOME"}, PressKey),
		({"type": "scroll_down"}, Scroll),
		({"type": "launch", "app_name": "YouTube"}, OpenApp),
		({"type": "input_text", "content": "hello"}, TypeText),
		({"type": "terminate", "status": "success"}, Done),
		({"type": "terminate", "status": "failure", "reason": "blocked"}, Fail),
		({"type": "finished", "content": "42"}, Done),
	],
)
def test_aliases(action, expected):
	import json

	s = parse_step(json.dumps({"action": action}))
	assert isinstance(s.action, expected)


def test_key_normalisation_and_answer_alias():
	assert (
		parse_step('{"action": {"type": "press_key", "key": "KEYCODE_HOME"}}').action.key == "home"
	)
	assert parse_step('{"action": {"type": "finished", "content": "42"}}').action.answer == "42"


def test_swipe_start_end_points():
	s = parse_step('{"action": {"type": "drag", "start": [1, 2], "end": [3, 4]}}')
	assert isinstance(s.action, Swipe)
	assert (s.action.x1, s.action.y1, s.action.x2, s.action.y2) == (1, 2, 3, 4)


def test_plan_string_is_split():
	s = parse_step('{"plan": "- open app\\n- tap search", "action": {"type": "wait"}}')
	assert s.plan == ["open app", "tap search"]


def test_top_level_action_without_wrapper():
	s = parse_step('{"type": "open_app", "app": "Settings"}')
	assert isinstance(s.action, OpenApp)


def test_errors():
	with pytest.raises(ParseError, match="no JSON"):
		parse_step("I would tap the button")
	with pytest.raises(ParseError, match="schema"):
		parse_step('{"action": {"type": "teleport"}}')
	with pytest.raises(ParseError, match="schema"):
		parse_step('{"action": {"type": "scroll", "direction": "sideways"}}')


def test_extract_json_skips_non_objects():
	assert extract_json('[1, 2] then {"a": 1}') == {"a": 1}
