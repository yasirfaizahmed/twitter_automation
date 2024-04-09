"""
Author: Yasir Faiz Ahmed
Contact: yasirfaizahmed.n@gmail.com
Date: April 8, 2024
Description: This is a automation script to post chron based hadith dialy.
"""

from Quote2Image import Convert, ImgObject
from pathlib import Path as pp
from pathlib import PosixPath
import time
from datetime import date
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

from utils.paths import RESOURCES, GENERATED
from log_handling.log_handling import logger

IMAGE_SET_DIR = "hadith_backgroud_image_set"
IMAGE_SET_PATH = pp(RESOURCES, IMAGE_SET_DIR)
FONT_SET_DIR = "fonts"
FONT_SET_PATH = pp(RESOURCES, FONT_SET_DIR)
BRIGHTNESS = 30  # out of 100
BLURR = 0  # out of 100
# DEFAULT_FONT = "AnotherFlight-m752"
# DEFAULT_FONT = "MemorialLane-z8XVX"
DEFAULT_FONT = "RobotoSlab-VariableFont_wght"
# DEFAULT_FONT = "Oswald-Medium"
MIN_IMAGE_WIDTH = 500
MIN_IMAGE_HEIGHT = 700
GOOD_QUOTE_HEIGHT = 0.4  # 40% of the image height
MAX_ITER_COUNT = 20


def handle_output_dir() -> bool:
	if GENERATED.exists() is False:
		logger.warning("_GENERATED dir not found, creating it...")
		GENERATED.mkdir()
	else:
		logger.warning("_GENERATED dir found, using it...")


def pick_random_image() -> PosixPath:
	all_images = list(IMAGE_SET_PATH.iterdir())
	random_image = random.choice(all_images)
	logger.info(f"chose image {random_image.absolute()} randomly")
	# width, height = Image.open(random_image)

	return random_image


def pick_first_image(image: str) -> PosixPath:
	if pp(image).exists():
		logger.info(f"using image {pp(image).absolute()}")
		return pp(image)
	first_image = list(IMAGE_SET_PATH.iterdir())[0]
	logger.info(f"using first image {first_image.absolute()}")
	return first_image


def get_font_file(font_name: str = DEFAULT_FONT) -> PosixPath:
	if pp(FONT_SET_PATH, f"{font_name}.ttf").exists() is False:
		logger.error(f"font {font_name} does not exits...")
		exit(-1)

	return pp(FONT_SET_PATH, f"{font_name}.ttf")


def custom_image_generator(
	narration,
	narrator,
	author,
	fg,
	image_path="",
	font_path="",
	font_size=20,
	size=(),
	watermark_text="",
	watermark_font_size: int = None,
	font_size_author: int = None,
):
	image_path: PosixPath = (
		pick_random_image() if image_path == "" else pick_first_image(image_path)
	)
	font_path: PosixPath = get_font_file() if font_path == "" else font_path

	bg = ImgObject(image=str(image_path.absolute()), brightness=BRIGHTNESS, blur=BLURR)
	image = Image.open(bg.image)
	width, height = image.size if size == () else size
	image.resize((width, height))  #
	enhancer = ImageEnhance.Brightness(image)
	image = enhancer.enhance(bg.brightness / 100)
	if bg.blur != 0:
		image = image.filter(ImageFilter.BoxBlur(bg.blur))
	draw = ImageDraw.Draw(image)

	quote_height = font_size  # just to initialize
	iter_count = 0
	while (quote_height < (GOOD_QUOTE_HEIGHT * height)) or (
		quote_height > (GOOD_QUOTE_HEIGHT * height)
	):
		# check what must be the font size so that the text part takes up correct % of space in middle
		font = ImageFont.truetype(str(font_path.absolute()), font_size)
		lines = []
		line = ""
		for word in narration.split():
			line_width = draw.textsize(line + " " + word, font)[0]
			if line_width > width - 40:
				lines.append(line)
				line = word
			else:
				line += " " + word

		lines.append(line)
		quote_height = sum([draw.textsize(line, font)[1] for line in lines])
		if iter_count > MAX_ITER_COUNT:
			break
		if quote_height < (GOOD_QUOTE_HEIGHT * height):
			font_size += 1  # increase font size
		elif quote_height > (GOOD_QUOTE_HEIGHT * height):
			font_size -= 1  # decreset font size
		iter_count += 1

	y = (height - quote_height - font_size) // 2

	if narrator != "":
		n_lines = []
		n_line = ""
		for word in narrator.split():
			n_line_width = draw.textsize(n_line + " " + word, font)[0]
			if n_line_width > width - 40:
				n_lines.append(n_line)
				n_line = word
			else:
				n_line += " " + word
		n_lines.append(n_line)
		for line in n_lines:
			draw.text((40, y - 50), line, fg, font=font, antialias=True)
			y += draw.textsize(line, font)[1]

	for line in lines:
		line_width = draw.textsize(line, font)[0]
		x = (width - line_width) // 2
		draw.text((x, y), line, fg, font=font, antialias=True)
		y += draw.textsize(line, font)[1]

	dash_width = draw.textsize(" - ", font)[0]
	x = (width - dash_width) // 2
	y += font_size // 2
	# draw.text((x, y), " - ", fg, font=font)

	font_author = ImageFont.truetype(
		str(font_path.absolute()), int(font_size - (0.3 * font_size))
	)
	author_width = draw.textsize(author, font_author)[0]
	x = (width - author_width) // 2
	draw.text((x, y + 20), author, fg, font=font_author, antialias=True)

	_current_time = time.strftime("%H-%M-%S", time.localtime())
	_current_date = date.today().strftime("%B-%d-%Y")
	# Save The Image as a Png file
	image.convert("RGB")
	image.save(pp(GENERATED, f"{_current_date}_{_current_time}.png"))


# Depricated
def generate_image(content: str, author: str, image: str = ""):
	if handle_output_dir() is False:
		logger.error("something went wrong while creating _GENERATED dir, exiting...")
		exit(-1)

	image_path: PosixPath = (
		pick_random_image() if image == "" else pick_first_image(image)
	)
	font_path: PosixPath = get_font_file()

	width, height = Image.open(image_path).size

	# Generate Fg and Bg Color
	bg = ImgObject(image=str(image_path.absolute()), brightness=BRIGHTNESS, blur=BLURR)

	img = Convert(
		quote=content,
		author=author,
		fg=(255, 255, 255),
		bg=bg,
		font_size=20,
		font_type=str(font_path.absolute()),
		width=width,
		height=height,
		watermark_text="",
	)

	_current_time = time.strftime("%H-%M-%S", time.localtime())
	_current_date = date.today().strftime("%B-%d-%Y")
	# Save The Image as a Png file
	img.save(pp(GENERATED, f"{_current_date}_{_current_time}.png"))
