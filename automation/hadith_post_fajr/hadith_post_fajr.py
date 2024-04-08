"""
Author: Yasir Faiz Ahmed
Contact: yasirfaizahmed.n@gmail.com
Date: April 6, 2024
Description: This is a automation script to post chron based Quran.
"""

import requests
from urllib.parse import urlencode, urljoin
import json
import os

from log_handling.log_handling import logger

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


def get_collections(collection_name: str) -> dict:
	collections_endpoint = "collections"
	collections_params = {"limit": 50, "page": 1}
	headers = {"Accept": "application/json", "X-API-Key": os.environ["SUNNAH_KEY"]}
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


def main():
	get_collections(CURRENT_COLLECTION_UNDER_USE)


if __name__ == "__main__":
	main()
