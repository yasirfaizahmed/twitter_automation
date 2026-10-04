import pytest
from PIL import Image, ImageDraw

from android_automation import coords, imaging


@pytest.mark.parametrize(
	"space, x, y, image_size, expected",
	[
		("normalized_1000", 500, 500, (480, 1056), (540, 1200)),
		("normalized_1", 0.25, 0.75, (480, 1056), (270, 1800)),
		("pixel", 240, 528, (480, 1056), (540, 1200)),
		("normalized_1000", 1000, 1000, (480, 1056), (1079, 2399)),
		("normalized_1000", -50, 2000, (480, 1056), (0, 2399)),
	],
)
def test_to_device(space, x, y, image_size, expected):
	assert coords.to_device(x, y, space, image_size, (1080, 2400)) == expected


def test_in_bounds_and_round_trip():
	assert coords.in_bounds(1000, 0, "normalized_1000", (1, 1))
	assert not coords.in_bounds(1001, 0, "normalized_1000", (1, 1))
	assert coords.from_fraction(0.5, 0.25, "pixel", (200, 400)) == (100, 100)


@pytest.mark.parametrize("w, h", [(1080, 2400), (720, 1600), (2400, 1080), (20, 20)])
def test_smart_resize_constraints(w, h):
	factor, lo, hi = 32, 64 * 32 * 32, 1568 * 32 * 32
	rh, rw = imaging.smart_resize(h, w, factor, lo, hi)
	assert rh % factor == 0 and rw % factor == 0
	assert lo <= rh * rw <= hi
	if min(w, h) > factor:
		assert abs(rw / rh - w / h) < 0.1


def test_screen_diff_and_annotate():
	a = Image.new("RGB", (100, 200), "white")
	b = Image.new("RGB", (100, 200), "black")
	assert imaging.screen_diff(a, a) == 0
	assert imaging.screen_diff(a, b) > 0.9
	# A typed word on a phone-sized screen counts as a change; a blinking cursor does not.
	screen = Image.new("RGB", (1080, 2400), "white")
	typed = screen.copy()
	ImageDraw.Draw(typed).rectangle((100, 600, 400, 650), fill="black")
	cursor = screen.copy()
	ImageDraw.Draw(cursor).rectangle((100, 600, 103, 650), fill="black")
	assert imaging.screen_diff(screen, typed) > 0.001
	assert imaging.screen_diff(screen, cursor) < 0.001
	out = imaging.annotate(a, [(10, 10), (50, 150)], "swipe")
	assert out.size == a.size and out is not a


def test_data_url():
	url = imaging.to_data_url(Image.new("RGB", (4, 4)), "JPEG")
	assert url.startswith("data:image/jpeg;base64,")
