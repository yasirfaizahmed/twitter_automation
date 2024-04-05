"""
Author: Yasir Faiz Ahmed
Contact: yasirfaizahmed.n@gmail.com
Date: April 4, 2024
Description: This is a automation script to post chron based Ramazan progress bar on twitter.
"""

from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageDraw
import traceback

from APIs.Selenium import selenium_steps
from log_handling.log_handling import logger
from ascii_progress import progress


NUMBER_OF_DAYS_IN_ISLAMIC_CALENDER = 355
# NEXT_EID_AL_FITR = datetime(2025, 3, 30).date()  # 30th of mar
NEXT_EID_AL_FITR = datetime(2024, 4, 10).date()
NEXT_FIRST_ROZA = datetime(2025, 2, 28).date()  # 28th of feb

BOT_NAME = "default_bot"


def drawProgressBar(d, x, y, w, h, progress, bg="white", fg="green"):
	# draw background
	d.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=bg)
	# draw progress bar
	w *= progress
	d.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=fg)
	return d


def calibrate_time_difference() -> timedelta:
	today = datetime.now().date()
	day_difference = NEXT_EID_AL_FITR - today
	return NUMBER_OF_DAYS_IN_ISLAMIC_CALENDER - day_difference.days  # days completed


# Depricated
def create_image():
	days_remaining = calibrate_time_difference()
	completion_ration = days_remaining.days / NUMBER_OF_DAYS_IN_ISLAMIC_CALENDER

	# create image or load your existing image with out=Image.open(path)
	out = Image.new("RGB", (500, 75), (50, 50, 50))
	d = ImageDraw.Draw(out)
	# draw the progress bar to given location, width, progress and color
	d = drawProgressBar(d, 20, 10, 400, 55, abs(1 - completion_ration))
	out.save("output.jpg")

	return True, days_remaining.days


def create_progress(days_completed: int):
	progress_ascii = progress(
		min=1,
		max=NUMBER_OF_DAYS_IN_ISLAMIC_CALENDER,
		current=days_completed,
		width=20,
		style=1,
	)
	return True, progress_ascii


def main():
	try:
		days_completed = calibrate_time_difference()
		status, progress_ascii = create_progress(days_completed=days_completed)
		# status, days_remaining = create_image()
		if status:
			selenium_steps.Login(botname=BOT_NAME)()

			tweet_content = f"{NUMBER_OF_DAYS_IN_ISLAMIC_CALENDER - days_completed} Days remaining for Eid al-Fitr\n \n{progress_ascii}"

			selenium_steps.Tweet(
				tweet_content=tweet_content, bot_name="default_bot", use_pyautogui=False
			)()
		else:
			logger.error("something went wrong...")
			exit(1)
	except Exception:
		logger.error("exception caught...")
		logger.error(traceback.format_exc())
		exit(-1)


if __name__ == "__main__":
	main()
