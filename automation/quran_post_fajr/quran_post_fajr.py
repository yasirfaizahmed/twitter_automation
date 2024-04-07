"""
Author: Yasir Faiz Ahmed
Contact: yasirfaizahmed.n@gmail.com
Date: April 6, 2024
Description: This is a automation script to post chron based Quran.
"""

import requests

BASE_URL = ""


def get_response():
	pass


def main():
	get_response()

	url = "https://api.quran.com/api/v4/verses/by_key/1:1?words=true"

	payload = {}
	headers = {"Accept": "application/json"}

	response = requests.request("GET", url, headers=headers, data=payload)

	print(response.text)


if __name__ == "__main__":
	main()
