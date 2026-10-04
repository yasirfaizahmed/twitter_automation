from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

from PIL import Image

Part = str | Image.Image


@dataclass
class Message:
	"""Backend-neutral chat message: text and PIL images, in order."""

	role: Literal["system", "user", "assistant"]
	content: list[Part]

	def text(self) -> str:
		return "".join(p if isinstance(p, str) else "<image>" for p in self.content)


@dataclass
class VLMResponse:
	text: str
	reasoning: str = ""
	latency_s: float = 0.0
	usage: dict[str, Any] = field(default_factory=dict)


class VLM(ABC):
	@abstractmethod
	def complete(
		self,
		messages: list[Message],
		json_schema: dict[str, Any] | None = None,
		schema_name: str = "response",
	) -> VLMResponse:
		"""Run one chat completion. ``json_schema`` asks the backend to constrain the
		output when it can; callers still validate the result."""


def schema_for_constrained_decoding(schema: dict[str, Any]) -> dict[str, Any]:
	"""Make a pydantic JSON schema friendlier to grammar engines (xgrammar, outlines,
	llguidance): ``oneOf`` -> ``anyOf``, drop keywords some engines reject. Range checks
	are re-applied by pydantic after parsing, so nothing is lost."""
	drop = {"title", "discriminator", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"}

	def walk(node: Any) -> Any:
		if isinstance(node, dict):
			out = {}
			for k, v in node.items():
				if k in drop and not isinstance(v, dict | list) or k == "discriminator":
					continue
				out["anyOf" if k == "oneOf" else k] = walk(v)
			return out
		if isinstance(node, list):
			return [walk(v) for v in node]
		return node

	return walk(schema)
