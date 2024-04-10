"""
Author: Yasir Faiz Ahmed
Contact: yasirfaizahmed.n@gmail.com
Date: April 6, 2024
Description: This is a automation script to post chron based hadith dialy.
"""

import requests
from urllib.parse import urlencode, urljoin
import json
import os
from pathlib import Path as pp
from datetime import datetime
from datetime import timedelta
import nltk
import random
from typing import List
import traceback

from create_image import custom_image_generator
from log_handling.log_handling import logger
from utils.paths import RESOURCES
from APIs.Selenium import selenium_steps


BASE_URL = "https://api.sunnah.com/v1/"

# Bot name
BOT_NAME = "default_bot"

# Hadith constants
BUKHARI = "bukhari"
MUSLIM = "muslim"
NASAI = "nasai"
ABUDAWUD = "abudawud"
TIRMIDHI = "tirmidhi"
IBNMIDHI = "ibnmidhi"
MALIK = "malik"
AHMAD = "ahmad"
DARIMI = "darimi"
FORTY = "forty"
NAWAWI40 = "nawawi40"
RIADUSSALIHIN = "riadussalihin"
MISHKAT = "mishkat"
ADAB = "adab"
BULUGH = "bulugh"
HISN = "hisn"
VIRTUES = "virtues"
CURRENT_COLLECTION_UNDER_USE = BUKHARI

# Cron constants
DAY_IT_ALL_STARTED = datetime(2024, 4, 7).date()  # Monday, 7th of Apr, 2024
TODAY = datetime.now().date()  # current day
SUNNAH_KEY = os.environ.get("SUNNAH_KEY", "")
if SUNNAH_KEY == "":
	logger.error("key SUNNAH_KEY not set in env, exiting")
	exit(-1)

# Image generation constants
MAX_WORDS_IN_HADITH = 250
GOOD_NUMBER_OF_WORDS_IN_ONE_IMAGE = 150
IMAGE_SET_DIR = "hadith_backgroud_image_set"
IMAGE_SET_PATH = pp(RESOURCES, IMAGE_SET_DIR)


def _get_largest_files(
	directory, n=10
):  # Get list of n largest files in IMAGE_SET_PATH
	dir_path = pp(directory)
	files = [
		(file, file.stat().st_size) for file in dir_path.iterdir() if file.is_file()
	]
	sorted_files = sorted(files, key=lambda x: x[1], reverse=True)
	largest_files = sorted_files[:n]
	return largest_files


NUMBER_OF_BIGGEST_IMAGE_FILES = 10
BIGGEST_IMAGE_FILE = random.choice(
	_get_largest_files(IMAGE_SET_PATH, NUMBER_OF_BIGGEST_IMAGE_FILES)
)[0]
MAX_NUMBER_OF_PAGES = 4


# GET available collections
def get_collections(collection_name: str) -> dict:
	collections_endpoint = "collections"
	collections_params = {"limit": 50, "page": 1}
	headers = {"Accept": "application/json", "X-API-Key": SUNNAH_KEY}
	url = form_url(endpoint=collections_endpoint, params=collections_params)
	logger.info(f"GET request with url {url}")
	response = requests.get(url, headers=headers)

	# Simple response handler
	if response.status_code < 200 and response.status_code >= 300:
		logger.error(
			f"something went wrong in {get_collections.__name__}'s GET request, exiting"
		)
		exit(-1)
	logger.info(f"Response OK - {response.status_code}")
	data = json.loads(response.content)

	for collection in data.get("data", ""):
		if collection.get("name", "") == collection_name:
			return collection


# Calibrate the delta date difference
def calibrate_time_difference() -> timedelta:
	return TODAY - DAY_IT_ALL_STARTED


# GET hadith from collection data and hadith number
def get_hadith(collection_data: dict, hadith_number: int) -> dict:
	collection_name = collection_data.get("name", CURRENT_COLLECTION_UNDER_USE)
	hadith_endpoint = f"collections/{collection_name}/hadiths/{hadith_number}"
	headers = {"Accept": "application/json", "X-API-Key": os.environ["SUNNAH_KEY"]}
	url = form_url(endpoint=hadith_endpoint, params={})
	logger.info(f"GET request with url {url}")
	response = requests.get(url, headers=headers)

	# Simple response handler
	if response.status_code < 200 and response.status_code >= 300:
		logger.error(
			f"something went wrong in {get_collections.__name__}'s GET request, exiting"
		)
		exit(-1)
	logger.info(f"Response OK - {response.status_code}")
	data = json.loads(response.text)
	return data


# GET random hadith if current hadith is too big to post
def get_random_hadith():
	random_hadith_endpoint = "hadiths/random"
	headers = {"Accept": "application/json", "X-API-Key": os.environ["SUNNAH_KEY"]}
	url = form_url(endpoint=random_hadith_endpoint, params={})
	logger.info(f"GET request with url {url}")
	response = requests.get(url, headers=headers)

	# Simple response handler
	if response.status_code < 200 and response.status_code >= 300:
		logger.error(
			f"something went wrong in {get_collections.__name__}'s GET request, exiting"
		)
		exit(-1)
	logger.info(f"Response OK - {response.status_code}")
	data = json.loads(response.text)
	return data


# URL maker utility
def form_url(endpoint: str, params: dict) -> str:
	logger.info("Forming url")
	non_null_params = {}
	for key, value in params.items():
		if value is None or value == "":
			continue
		value = ";".join(value) if isinstance(value, list) else value  # tagged

		non_null_params.update({key: value})
	url_with_enpoint = urljoin(BASE_URL, endpoint)
	url = f"{url_with_enpoint}?{urlencode(non_null_params)}"
	logger.info(f"formed url: {url}")
	return url


# Hadith data extractor utility
def extract_hadith_data(hadith_data: dict) -> dict:
	logger.info("Extracting Hadith data")
	hadith_english: dict = hadith_data.get("hadith", "")[0]
	hadith_arabic: dict = hadith_data.get("hadith", "")[1]  # noqa: F841

	# Extracting data
	collection: str = hadith_data.get("collection")
	book: str = hadith_data.get("bookNumber")
	hadith_number: str = hadith_data.get("hadithNumber")
	prefix = "Sahih" if collection.upper() in [BUKHARI, MUSLIM] else ""
	hadith_source = f"{prefix} al-{collection.upper()} {book} : {hadith_number}"

	raw_hadith = hadith_english.get("body")

	# Replacing non-renderable symbols, and removing junk chars
	replace = {"ﷺ": "PBUH"}
	remove = ["<p>", "</p>", "<b>", "</b>", "<br>", "</br>", "<br/>"]
	for key, value in replace.items():
		raw_hadith = raw_hadith.replace(key, value)
	for rem in remove:
		raw_hadith = raw_hadith.replace(rem, "")

	narrator = raw_hadith.split(":")[0]
	narration = " ".join(raw_hadith.split(":")[1:])

	return {
		"narrator": narrator,
		"narration": narration,
		"hadith_source": hadith_source,
	}


# Utility splits the big Hadith into n equal paragraphs
def split_into_paragraphs(text, n):
	logger.info(f"Splitting the Hadith into {n} parts")
	nltk.download("punkt")
	# Tokenize the text into sentences
	sentences = nltk.sent_tokenize(text)

	# Calculate the number of sentences per paragraph
	sentences_per_paragraph = len(sentences) // n

	# Split the sentences into N paragraphs
	paragraphs = []
	for i in range(0, len(sentences), sentences_per_paragraph):
		paragraph = " ".join(sentences[i : i + sentences_per_paragraph])
		paragraphs.append(paragraph)

	# After
	if (
		len(paragraphs[-1].split()) < 0.3 * len(paragraphs[-2].split())
		and len(paragraphs) > 1
	):
		paragraphs[-2] += paragraphs[-1]
		paragraphs.pop()

	return paragraphs


# Generate Hadith image
def generate_hadith_images() -> List:
	# GET collections
	collection_data = get_collections(CURRENT_COLLECTION_UNDER_USE)
	# Calibrate the delta date difference
	hadith_number = calibrate_time_difference().days
	# GET hadith
	hadith_data = get_hadith(
		collection_data=collection_data, hadith_number=10
	)

	# Extract Hadith
	extracted_hadith_data = extract_hadith_data(hadith_data)

	# Logic to create images depending on the size of Hadith
	number_of_words_in_hadith = len(extracted_hadith_data.get("narration").split())
	if number_of_words_in_hadith > MAX_WORDS_IN_HADITH:  # If cant fit it one page
		logger.info(
			f"Number of words in Hadith {number_of_words_in_hadith} > {MAX_WORDS_IN_HADITH}"
		)
		if (
			number_of_words_in_hadith > MAX_NUMBER_OF_PAGES * MAX_WORDS_IN_HADITH
		):  # If cant fit in 4 pages
			logger.info(
				f"Number of words in Hadith {number_of_words_in_hadith} cant fit in {MAX_NUMBER_OF_PAGES} Pages"
			)
			hadith_data = get_random_hadith()
			extracted_hadith_data = extract_hadith_data(hadith_data)
		else:
			narrator = extracted_hadith_data.get("narrator")
			narration = extracted_hadith_data.get("narration")
			number_of_pages = len(narration.split(" ")) // MAX_WORDS_IN_HADITH  # <= 4
			logger.info(
				f"Number of words in Hadith {number_of_words_in_hadith} can fit into {number_of_pages} pages"
			)
			# Splitting the Hadith into paragraphs
			list_of_paragraphs = split_into_paragraphs(narration, number_of_pages)
			response_list = []
			for i, paragraph in enumerate(list_of_paragraphs):
				if i != 0:
					narrator = ""
				response = custom_image_generator(
					narrator=narrator,
					narration=paragraph,
					image_path=BIGGEST_IMAGE_FILE,
					author=extracted_hadith_data.get("hadith_source"),
					fg=(255, 255, 255),
				)
				response_list.append(response)
				logger.info(paragraph)
			return response_list

	response = custom_image_generator(
		narrator=extracted_hadith_data.get("narrator"),
		narration=extracted_hadith_data.get("narration"),
		# image_path="/home/xd/Documents/python_codes/twitter_automation/resources/hadith_backgroud_image_set/pinterest_2040762320649080.jpg",
		author=extracted_hadith_data.get("hadith_source"),
		fg=(255, 255, 255),
	)
	return [response]


# main
def main():
	try:
		response_list = generate_hadith_images()  # noqa: F841L
		if all([response.get("status", False) for response in response_list]):
			logger.info("All status OK")
			selenium_steps.Login(botname=BOT_NAME)()

			tweet_text = ""

			selenium_steps.Tweet(
				tweet_content=tweet_text,
				media_files=[
					str(response.get("saved_image_path")) for response in response_list
				],
				bot_name="default_bot",
				use_pyautogui=False,
			)()
			exit(0)
	except Exception:
		logger.error("Something went wrong")
		logger.error(traceback.format_exc())
		exit(-1)


# Entry point
if __name__ == "__main__":
	main()
