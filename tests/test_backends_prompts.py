from types import SimpleNamespace
from typing import get_args

from PIL import Image

from android_automation import prompts
from android_automation.actions import Action
from android_automation.config import ModelConfig
from android_automation.vlm.base import Message, schema_for_constrained_decoding
from android_automation.vlm.openai_backend import OpenAICompatibleVLM


class FakeClient:
	def __init__(self, content='{"x": 1}', reasoning=None):
		self.kwargs = None
		msg = SimpleNamespace(content=content, reasoning_content=reasoning)
		self._resp = SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=None)
		self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

	def _create(self, **kwargs):
		self.kwargs = kwargs
		return self._resp


def test_openai_backend_request_shape():
	cfg = ModelConfig(
		model="m",
		chat_template_kwargs={"thinking": False},
		extra_body={"top_k": 1},
		image={"format": "PNG"},
	)
	client = FakeClient(reasoning="thinking...")
	vlm = OpenAICompatibleVLM(cfg, client=client)
	msgs = [Message("system", ["sys"]), Message("user", ["look", Image.new("RGB", (4, 4))])]
	resp = vlm.complete(msgs, json_schema={"type": "object", "oneOf": []}, schema_name="s")

	kw = client.kwargs
	assert kw["model"] == "m" and kw["temperature"] == 0.0
	assert kw["messages"][0] == {"role": "system", "content": "sys"}
	parts = kw["messages"][1]["content"]
	assert parts[0] == {"type": "text", "text": "look"}
	assert parts[1]["image_url"]["url"].startswith("data:image/png;base64,")
	assert kw["response_format"]["json_schema"]["schema"] == {"type": "object", "anyOf": []}
	assert kw["extra_body"] == {"top_k": 1, "chat_template_kwargs": {"thinking": False}}
	assert resp.text == '{"x": 1}' and resp.reasoning == "thinking..."


def test_openai_backend_without_structured_output():
	client = FakeClient()
	OpenAICompatibleVLM(ModelConfig(structured_output="none"), client=client).complete(
		[Message("user", ["hi"])], json_schema={"type": "object"}
	)
	assert "response_format" not in client.kwargs and "extra_body" not in client.kwargs


def test_constrained_schema_keeps_properties_named_like_keywords():
	schema = {
		"title": "T",
		"properties": {
			"title": {"type": "string", "title": "Title"},
			"n": {"type": "integer", "minimum": 0},
		},
		"discriminator": {"propertyName": "type"},
	}
	assert schema_for_constrained_decoding(schema) == {
		"properties": {"title": {"type": "string"}, "n": {"type": "integer"}}
	}


def test_every_action_is_documented_in_the_system_prompt():
	union = get_args(get_args(Action)[0])
	kinds = [cls.model_fields["type"].default for cls in union]
	text = prompts.system_prompt("coords")
	for kind in kinds:
		assert f'"type": "{kind}"' in text, kind


def test_step_schema_requires_action_type_first():
	schema = prompts.agent_step_schema()
	assert schema["required"] == ["observation", "plan", "thought", "note", "action"]
	for d in schema["$defs"].values():
		assert list(d["properties"])[0] == "type"
		assert d["required"][0] == "type"


def test_secret_block_only_when_secrets_exist():
	assert "Secrets" not in prompts.system_prompt("c")
	assert "{{A}}, {{B}}" in prompts.system_prompt("c", ["A", "B"])
