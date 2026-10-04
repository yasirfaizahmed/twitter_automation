"""Element grounding: natural-language description -> screen position.

Used when a separate grounder model is configured (planner/grounder split) or when the
main model named a target but gave no coordinates.
"""

from __future__ import annotations

import re

from PIL import Image

from android_automation import coords, imaging, prompts
from android_automation.config import ModelConfig
from android_automation.parsing import ParseError, extract_json
from android_automation.vlm.base import VLM


class GroundingError(RuntimeError):
	pass


def parse_point(text: str) -> tuple[float, float]:
	try:
		data = extract_json(text)
		return float(data["x"]), float(data["y"])
	except (ParseError, KeyError, TypeError, ValueError):
		pass
	m = re.search(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", text)
	if m:  # Click(x, y), (x, y), [x, y]
		return float(m.group(1)), float(m.group(2))
	raise GroundingError(f"could not read a point from grounder output: {text[:200]!r}")


class Grounder:
	def __init__(self, vlm: VLM, cfg: ModelConfig):
		self.vlm = vlm
		self.cfg = cfg

	def locate(self, screenshot: Image.Image, target: str) -> tuple[float, float]:
		"""Returns the position as fractions of the screen, (0..1, 0..1)."""
		img = imaging.prepare_for_model(
			screenshot, self.cfg.image.factor, self.cfg.image.min_pixels, self.cfg.image.max_pixels
		)
		space = self.cfg.coordinate_space
		note = coords.describe_space(space, img.size)
		resp = self.vlm.complete(
			prompts.localize_messages(target, note, img),
			json_schema=prompts.localize_schema(note),
			schema_name="click_position",
		)
		x, y = parse_point(resp.text)
		return coords.to_fraction(x, y, space, img.size)
