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

from create_image import custom_image_generator
from log_handling.log_handling import logger
from utils.paths import RESOURCES

BASE_URL = "https://api.sunnah.com/v1/"

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


DAY_IT_ALL_STARTED = datetime(2024, 4, 7).date()  # Monday, 7th of Apr, 2024
TODAY = datetime.now().date()  # current day
SUNNAH_KEY = os.environ.get("SUNNAH_KEY", "")
if SUNNAH_KEY == "":
	logger.error("key SUNNAH_KEY not set in env, exiting...")
	exit(-1)

MAX_WORDS_IN_HADITH = 400
GOOD_NUMBER_OF_WORDS_IN_ONE_IMAGE = 150
IMAGE_SET_DIR = "hadith_backgroud_image_set"
IMAGE_SET_PATH = pp(RESOURCES, IMAGE_SET_DIR)
BIGGEST_IMAGE_FILE = pp(IMAGE_SET_PATH, "pinterest_806425877043089332.png")
MAX_NUMBER_OF_PAGES = 4


def get_collections(collection_name: str) -> dict:
	collections_endpoint = "collections"
	collections_params = {"limit": 50, "page": 1}
	headers = {"Accept": "application/json", "X-API-Key": SUNNAH_KEY}
	url = form_url(endpoint=collections_endpoint, params=collections_params)
	response = requests.get(url, headers=headers)

	if response.status_code < 200 and response.status_code >= 300:
		logger.error(
			f"something went wrong in {get_collections.__name__}'s GET request, exiting..."
		)
		exit(-1)
	data = json.loads(response.content)

	for collection in data.get("data", ""):
		if collection.get("name", "") == collection_name:
			return collection


def calibrate_time_difference() -> timedelta:
	return TODAY - DAY_IT_ALL_STARTED


def get_hadith(collection_data: dict, hadith_number: int) -> dict:
	collection_name = collection_data.get("name", CURRENT_COLLECTION_UNDER_USE)
	hadith_endpoint = f"collections/{collection_name}/hadiths/{hadith_number}"
	headers = {"Accept": "application/json", "X-API-Key": os.environ["SUNNAH_KEY"]}
	url = form_url(endpoint=hadith_endpoint, params={})
	response = requests.get(url, headers=headers)

	if response.status_code < 200 and response.status_code >= 300:
		logger.error(
			f"something went wrong in {get_collections.__name__}'s GET request, exiting..."
		)
		exit(-1)
	data = json.loads(response.text)
	return data


def get_random_hadith():
	random_hadith_endpoint = "hadiths/random"
	headers = {"Accept": "application/json", "X-API-Key": os.environ["SUNNAH_KEY"]}
	url = form_url(endpoint=random_hadith_endpoint, params={})
	response = requests.get(url, headers=headers)

	if response.status_code < 200 and response.status_code >= 300:
		logger.error(
			f"something went wrong in {get_collections.__name__}'s GET request, exiting..."
		)
		exit(-1)
	data = json.loads(response.text)
	return data


def form_url(endpoint: str, params: dict):
	non_null_params = {}
	for key, value in params.items():
		if value is None or value == "":
			continue
		value = ";".join(value) if isinstance(value, list) else value  # tagged

		non_null_params.update({key: value})
	url_with_enpoint = urljoin(BASE_URL, endpoint)
	url = f"{url_with_enpoint}?{urlencode(non_null_params)}"
	return url


def extract_hadith_data(hadith_data: dict) -> str:
	hadith_english: dict = hadith_data.get("hadith", "")[0]
	hadith_arabic: dict = hadith_data.get("hadith", "")[1]  # noqa: F841

	collection: str = hadith_data.get("collection")
	book: str = hadith_data.get("bookNumber")
	hadith_number: str = hadith_data.get("hadithNumber")
	hadith_source = f"{collection.upper()} {book} : {hadith_number}"
	raw_hadith = hadith_english.get("body")

	replace = {"ﷺ": "PBUH"}
	remove = ["<p>", "</p>", "<b>", "</b>", "<br>", "</br>", "<br/>"]
	for key, value in replace.items():
		raw_hadith = raw_hadith.replace(key, value)
	for rem in remove:
		raw_hadith = raw_hadith.replace(rem, "")

	return {"hadith": raw_hadith, "hadith_source": hadith_source}


def main():
	collection_data = get_collections(CURRENT_COLLECTION_UNDER_USE)
	hadith_number = calibrate_time_difference().days
	hadith_data = get_hadith(
		collection_data=collection_data, hadith_number=hadith_number
	)

	extracted_hadith_data = extract_hadith_data(hadith_data)
	number_of_words_in_hadith = len(extracted_hadith_data.get("hadith").split())
	if number_of_words_in_hadith > MAX_WORDS_IN_HADITH:
		if number_of_words_in_hadith > 4 * MAX_WORDS_IN_HADITH:
			hadith_data = get_random_hadith()
			extracted_hadith_data = extract_hadith_data(hadith_data)
		else:
			words_in_each_page = number_of_words_in_hadith // MAX_NUMBER_OF_PAGES
			word_list = extracted_hadith_data.get("hadith").split()
			for i, index in enumerate(
				range(
					0,
					number_of_words_in_hadith - words_in_each_page,
					words_in_each_page,
				)
			):
				if i == 3:
					hadith_for_page = " ".join(word_list[index:])
				else:
					hadith_for_page = " ".join(
						word_list[index : index + words_in_each_page]
					)
				custom_image_generator(
					quote=hadith_for_page,
					image_path=BIGGEST_IMAGE_FILE,
					author=extracted_hadith_data.get("hadith_source"),
					fg=(255, 255, 255),
				)
			return

	custom_image_generator(
		quote=extracted_hadith_data.get("hadith"),
		# image_path="/home/xd/Documents/python_codes/twitter_automation/resources/hadith_backgroud_image_set/pinterest_2040762320649080.jpg",
		author=extracted_hadith_data.get("hadith_source"),
		fg=(255, 255, 255),
	)

	# # Depricated
	# generate_image(content=pre_processed_hadith,
	# 							author=CURRENT_COLLECTION_UNDER_USE,
	# 							image="/home/xd/Documents/python_codes/twitter_automation/resources/hadith_backgroud_image_set/pinterest_842876886503797396.jpg")

	# # to test stability
	# for i in range(1, 50):
	# 	hadith_data = get_hadith(
	# 	collection_data=collection_data, hadith_number=i
	# 	)
	# 	extracted_hadith_data = extract_hadith_data(hadith_data)
	# 	custom_image_generator(quote=extracted_hadith_data.get("hadith"),
	# 												image_path="/home/xd/Documents/python_codes/twitter_automation/resources/hadith_backgroud_image_set/pinterest_2040762320649080.jpg",
	# 												author=extracted_hadith_data.get("hadith_source"),
	# 												fg=(255,255,255))


if __name__ == "__main__":
	main()
