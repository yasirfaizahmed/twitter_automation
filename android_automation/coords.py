"""Coordinate spaces used by different VLM families, and conversion to device pixels.

- ``normalized_1000``: integers 0..1000 relative to the image (Qwen3-VL / Qwen3.5 based
  models such as Holo2, Holo3.x, UI-TARS-2, GUI-Owl).
- ``normalized_1``: floats 0..1 relative to the image.
- ``pixel``: absolute pixels of the (resized) image the model was shown
  (Qwen2.5-VL based models such as Holo1/Holo1.5, UI-TARS-1.5).
"""

from __future__ import annotations

from typing import Literal

CoordinateSpace = Literal["normalized_1000", "normalized_1", "pixel"]


def describe_space(space: CoordinateSpace, image_size: tuple[int, int]) -> str:
	w, h = image_size
	if space == "normalized_1000":
		return (
			"Coordinates are integers from 0 to 1000 relative to the screenshot: "
			"(0, 0) is the top-left corner and (1000, 1000) the bottom-right corner."
		)
	if space == "normalized_1":
		return (
			"Coordinates are decimals from 0.0 to 1.0 relative to the screenshot: "
			"(0.0, 0.0) is the top-left corner and (1.0, 1.0) the bottom-right corner."
		)
	return (
		f"Coordinates are absolute pixels in the {w}x{h} screenshot: "
		f"(0, 0) is the top-left corner and ({w - 1}, {h - 1}) the bottom-right corner."
	)


def _scale(space: CoordinateSpace, image_size: tuple[int, int]) -> tuple[float, float]:
	if space == "normalized_1000":
		return 1000.0, 1000.0
	if space == "normalized_1":
		return 1.0, 1.0
	return float(image_size[0]), float(image_size[1])


def to_fraction(
	x: float, y: float, space: CoordinateSpace, image_size: tuple[int, int]
) -> tuple[float, float]:
	"""Model coordinates -> fractions of the screen in [0, 1] (clamped)."""
	sx, sy = _scale(space, image_size)
	fx = min(max(x / sx, 0.0), 1.0)
	fy = min(max(y / sy, 0.0), 1.0)
	return fx, fy


def in_bounds(x: float, y: float, space: CoordinateSpace, image_size: tuple[int, int]) -> bool:
	sx, sy = _scale(space, image_size)
	return 0 <= x <= sx and 0 <= y <= sy


def to_device(
	x: float,
	y: float,
	space: CoordinateSpace,
	image_size: tuple[int, int],
	screen_size: tuple[int, int],
) -> tuple[int, int]:
	"""Model coordinates -> device pixel coordinates (clamped to the screen)."""
	fx, fy = to_fraction(x, y, space, image_size)
	w, h = screen_size
	return min(round(fx * w), w - 1), min(round(fy * h), h - 1)


def from_fraction(
	fx: float, fy: float, space: CoordinateSpace, image_size: tuple[int, int]
) -> tuple[float, float]:
	"""Fractions of the screen -> model coordinates (used to translate grounder output)."""
	sx, sy = _scale(space, image_size)
	return fx * sx, fy * sy
