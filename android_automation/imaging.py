"""Screenshot preprocessing, encoding, change detection and annotation."""

from __future__ import annotations

import base64
import io
import math

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


def smart_resize(
	height: int,
	width: int,
	factor: int = 32,
	min_pixels: int = 64 * 32 * 32,
	max_pixels: int = 1568 * 32 * 32,
) -> tuple[int, int]:
	"""Qwen-VL style resize: both sides divisible by ``factor``, area within bounds,
	aspect ratio preserved. Returns ``(height, width)``.

	Feeding the model an image that is already at this size means the server does
	not resize it again, so ``pixel`` coordinates line up with what we sent.
	"""
	if height < factor or width < factor:
		scale = factor / min(height, width)
		height, width = math.ceil(height * scale), math.ceil(width * scale)
	h_bar = max(factor, round(height / factor) * factor)
	w_bar = max(factor, round(width / factor) * factor)
	if h_bar * w_bar > max_pixels:
		beta = math.sqrt((height * width) / max_pixels)
		h_bar = max(factor, math.floor(height / beta / factor) * factor)
		w_bar = max(factor, math.floor(width / beta / factor) * factor)
	elif h_bar * w_bar < min_pixels:
		beta = math.sqrt(min_pixels / (height * width))
		h_bar = math.ceil(height * beta / factor) * factor
		w_bar = math.ceil(width * beta / factor) * factor
	return h_bar, w_bar


def prepare_for_model(
	image: Image.Image, factor: int, min_pixels: int, max_pixels: int
) -> Image.Image:
	image = image.convert("RGB")
	h, w = smart_resize(image.height, image.width, factor, min_pixels, max_pixels)
	if (w, h) == image.size:
		return image
	return image.resize((w, h), Image.Resampling.LANCZOS)


def to_data_url(image: Image.Image, fmt: str = "PNG", jpeg_quality: int = 90) -> str:
	buf = io.BytesIO()
	fmt = fmt.upper()
	if fmt in ("JPG", "JPEG"):
		image.convert("RGB").save(buf, format="JPEG", quality=jpeg_quality)
		mime = "image/jpeg"
	else:
		image.save(buf, format="PNG")
		mime = "image/png"
	return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"


def screen_diff(a: Image.Image, b: Image.Image) -> float:
	"""Fraction of the screen (0..1) that visibly changed between two screenshots.

	Counting changed pixels, rather than averaging the difference, keeps small but real
	changes (a typed word, a toggled switch) detectable while a blinking cursor or the
	status-bar clock stay below typical thresholds."""
	size = (180, 320) if a.height >= a.width else (320, 180)
	ta = a.convert("L").resize(size, Image.Resampling.BILINEAR)
	tb = b.convert("L").resize(size, Image.Resampling.BILINEAR)
	mask = ImageChops.difference(ta, tb).point(lambda p: 255 if p > 24 else 0)
	return ImageStat.Stat(mask).mean[0] / 255.0


def annotate(
	image: Image.Image,
	points: list[tuple[int, int]],
	label: str = "",
	color: str = "#ff1f4b",
) -> Image.Image:
	"""Draw the executed gesture on a copy of the screenshot: a ring for one point,
	an arrow for a swipe."""
	out = image.convert("RGB").copy()
	draw = ImageDraw.Draw(out)
	r = max(12, out.width // 24)
	width = max(3, out.width // 120)
	for x, y in points[:1]:
		draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=width)
		draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)
	if len(points) >= 2:
		(x1, y1), (x2, y2) = points[0], points[-1]
		draw.line((x1, y1, x2, y2), fill=color, width=width)
		ang = math.atan2(y2 - y1, x2 - x1)
		for da in (2.6, -2.6):
			draw.line(
				(x2, y2, x2 + r * math.cos(ang + da), y2 + r * math.sin(ang + da)),
				fill=color,
				width=width,
			)
	if label:
		size = max(12, out.width // 28)
		try:
			font = ImageFont.load_default(size=size)
		except TypeError:  # Pillow < 10.1 has no sized default font
			font = ImageFont.load_default()
		pad = size // 2
		box = draw.textbbox((pad, pad), label, font=font)
		draw.rectangle((0, 0, box[2] + pad, box[3] + pad), fill="#000000")
		draw.text((pad, pad), label, fill="#ffffff", font=font)
	return out
