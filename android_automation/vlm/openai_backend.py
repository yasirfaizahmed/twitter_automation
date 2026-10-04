"""Backend for any server speaking the OpenAI chat-completions API: vLLM, SGLang,
llama.cpp server, Ollama, LM Studio, TGI, or a hosted provider."""

from __future__ import annotations

import time
from typing import Any

from android_automation.config import ModelConfig
from android_automation.imaging import to_data_url
from android_automation.vlm.base import VLM, Message, VLMResponse, schema_for_constrained_decoding


class OpenAICompatibleVLM(VLM):
	def __init__(self, cfg: ModelConfig, client: Any | None = None):
		self.cfg = cfg
		if client is None:
			from openai import OpenAI

			client = OpenAI(
				base_url=cfg.base_url,
				api_key=cfg.api_key(),
				timeout=cfg.timeout,
				max_retries=cfg.max_retries,
			)
		self.client = client

	def _encode(self, messages: list[Message]) -> list[dict[str, Any]]:
		out = []
		for m in messages:
			if all(isinstance(p, str) for p in m.content):
				out.append({"role": m.role, "content": "".join(m.content)})
				continue
			parts = []
			for p in m.content:
				if isinstance(p, str):
					parts.append({"type": "text", "text": p})
				else:
					url = to_data_url(p, self.cfg.image.format)
					parts.append({"type": "image_url", "image_url": {"url": url}})
			out.append({"role": m.role, "content": parts})
		return out

	def complete(
		self,
		messages: list[Message],
		json_schema: dict[str, Any] | None = None,
		schema_name: str = "response",
	) -> VLMResponse:
		kwargs: dict[str, Any] = {
			"model": self.cfg.model,
			"messages": self._encode(messages),
			"temperature": self.cfg.temperature,
			"max_tokens": self.cfg.max_tokens,
		}
		if json_schema is not None and self.cfg.structured_output == "json_schema":
			kwargs["response_format"] = {
				"type": "json_schema",
				"json_schema": {
					"name": schema_name,
					"schema": schema_for_constrained_decoding(json_schema),
				},
			}
		elif json_schema is not None and self.cfg.structured_output == "json_object":
			kwargs["response_format"] = {"type": "json_object"}
		extra_body = dict(self.cfg.extra_body)
		if self.cfg.chat_template_kwargs:
			extra_body["chat_template_kwargs"] = {
				**extra_body.get("chat_template_kwargs", {}),
				**self.cfg.chat_template_kwargs,
			}
		if extra_body:
			kwargs["extra_body"] = extra_body

		start = time.monotonic()
		resp = self.client.chat.completions.create(**kwargs)
		latency = time.monotonic() - start
		msg = resp.choices[0].message
		reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None) or ""
		usage = resp.usage.model_dump() if getattr(resp, "usage", None) else {}
		return VLMResponse(
			text=msg.content or "", reasoning=reasoning, latency_s=latency, usage=usage
		)
