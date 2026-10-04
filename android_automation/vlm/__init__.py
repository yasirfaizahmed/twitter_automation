from __future__ import annotations

from android_automation.config import ModelConfig
from android_automation.vlm.base import VLM, Message, VLMResponse


def build_vlm(cfg: ModelConfig) -> VLM:
	if cfg.backend == "openai":
		from android_automation.vlm.openai_backend import OpenAICompatibleVLM

		return OpenAICompatibleVLM(cfg)
	if cfg.backend == "transformers":
		from android_automation.vlm.transformers_backend import TransformersVLM

		return TransformersVLM(cfg)
	raise ValueError(f"unknown backend {cfg.backend!r}")


__all__ = ["VLM", "Message", "VLMResponse", "build_vlm"]
