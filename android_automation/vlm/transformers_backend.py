"""In-process inference with Hugging Face transformers (``pip install -e '.[local]'``).

Works with any ``AutoModelForImageTextToText`` checkpoint (Holo, Qwen-VL, UI-TARS, ...).
There is no constrained decoding here, so output is validated and retried by the agent;
for production throughput serve the model with vLLM and use the ``openai`` backend.
"""

from __future__ import annotations

import time
from typing import Any

from PIL import Image

from android_automation.config import ModelConfig
from android_automation.vlm.base import VLM, Message, VLMResponse


class TransformersVLM(VLM):
	def __init__(self, cfg: ModelConfig):
		try:
			import torch
			import transformers
		except ImportError as e:  # pragma: no cover - depends on optional extra
			raise ImportError(
				"the transformers backend needs the 'local' extra: pip install -e '.[local]'"
			) from e
		self.cfg = cfg
		self._torch = torch
		dtype = cfg.dtype if cfg.dtype == "auto" else getattr(torch, cfg.dtype)
		self.model = None
		errors = []
		# Newer multimodal families (e.g. Qwen3.5) register under AutoModelForMultimodalLM.
		for name in ("AutoModelForImageTextToText", "AutoModelForMultimodalLM"):
			auto = getattr(transformers, name, None)
			if auto is None:
				continue
			try:
				self.model = auto.from_pretrained(cfg.model, dtype=dtype, device_map=cfg.device_map)
				break
			except ValueError as e:  # architecture not registered under this auto class
				errors.append(f"{name}: {e}")
		if self.model is None:
			raise ValueError(f"cannot load {cfg.model} as a vision-language model: {errors}")
		self.model.eval()
		self.processor = transformers.AutoProcessor.from_pretrained(cfg.model)

	def complete(
		self,
		messages: list[Message],
		json_schema: dict[str, Any] | None = None,
		schema_name: str = "response",
	) -> VLMResponse:
		hf_messages = []
		images: list[Image.Image] = []
		for m in messages:
			parts = []
			for p in m.content:
				if isinstance(p, str):
					parts.append({"type": "text", "text": p})
				else:
					parts.append({"type": "image", "image": p})
					images.append(p)
			hf_messages.append({"role": m.role, "content": parts})

		prompt = self.processor.apply_chat_template(
			hf_messages, tokenize=False, add_generation_prompt=True, **self.cfg.chat_template_kwargs
		)
		inputs = self.processor(
			text=[prompt], images=images or None, padding=True, return_tensors="pt"
		).to(self.model.device)

		gen_kwargs: dict[str, Any] = {"max_new_tokens": self.cfg.max_tokens}
		if self.cfg.temperature > 0:
			gen_kwargs.update(do_sample=True, temperature=self.cfg.temperature)
		else:
			gen_kwargs["do_sample"] = False

		start = time.monotonic()
		with self._torch.inference_mode():
			out = self.model.generate(**inputs, **gen_kwargs)
		latency = time.monotonic() - start
		prompt_len = inputs["input_ids"].shape[1]
		new_tokens = out[:, prompt_len:]
		text = self.processor.batch_decode(new_tokens, skip_special_tokens=True)[0]
		return VLMResponse(
			text=text,
			latency_s=latency,
			usage={"prompt_tokens": int(prompt_len), "completion_tokens": int(new_tokens.shape[1])},
		)
