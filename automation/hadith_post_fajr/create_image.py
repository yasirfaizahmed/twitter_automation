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
from PIL import Image

from utils.paths import RESOURCES, GENERATED
from log_handling.log_handling import logger

IMAGE_SET_DIR = "hadith_backgroud_image_set"
IMAGE_SET_PATH = pp(RESOURCES, IMAGE_SET_DIR)
FONT_SET_DIR = "fonts"
FONT_SET_PATH = pp(RESOURCES, FONT_SET_DIR)
BRIGHTNESS = 40  # out of 100
BLURR = 0  # out of 100
# DEFAULT_FONT = "AnotherFlight-m752"
# DEFAULT_FONT = "MemorialLane-z8XVX"
DEFAULT_FONT = "RobotoSlab-VariableFont_wght"


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
	return random_image


def pick_first_image() -> PosixPath:
	first_image = list(IMAGE_SET_PATH.iterdir())[0]
	logger.info(f"using image {first_image.absolute()}")
	return first_image


def get_font_file(font_name: str = DEFAULT_FONT) -> PosixPath:
	if pp(FONT_SET_PATH, f"{font_name}.ttf").exists() is False:
		logger.error(f"font {font_name} does not exits...")
		exit(-1)

	return pp(FONT_SET_PATH, f"{font_name}.ttf")


def generate_image(content: str, author: str, random: bool = True):
	if handle_output_dir() is False:
		logger.error("something went wrong while creating _GENERATED dir, exiting...")
		exit(-1)

	image_path: PosixPath = (
		pick_random_image() if random is True else pick_first_image()
	)
	font_path: PosixPath = get_font_file()

	width, height = Image.open(image_path).size

	# Generate Fg and Bg Color
	bg = ImgObject(image=str(image_path.absolute()), brightness=BRIGHTNESS, blur=BLURR)

	img = Convert(
		quote=content,
		author=author,
		fg=(200, 200, 200),
		bg=bg,
		font_size=32,
		font_type=str(font_path.absolute()),
		width=width,
		height=height,
		watermark_text="",
	)

	_current_time = time.strftime("%H-%M-%S", time.localtime())
	_current_date = date.today().strftime("%B-%d-%Y")
	# Save The Image as a Png file
	img.save(pp(GENERATED, f"{_current_date}_{_current_time}.png"))
