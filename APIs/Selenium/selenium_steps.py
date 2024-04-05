from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import traceback
import time
import os
from datetime import date
import csv
from typing import List
from pathlib import Path as pp


from base.base_step import BaseStep
from APIs.Selenium.selenium_step import Selenium_Step
from data_handler.data_handler import BotMetadata
from data_handler.data_handler import create_data_file
from APIs.CV.cv_steps import GetIconCoordinates
from APIs.PyAutoGUI.pyautogui_steps import Click, Write
from patterns.patterns import timeout

from selenium.webdriver.remote.webelement import WebElement


class OpenPage(Selenium_Step, BaseStep):
	"""
	utility class to open the page of desired url in webdriver
	"""

	def __init__(self, url: str, **kwargs):
		super().__init__(**kwargs)
		self.url = url

	def Do(self) -> None:
		self.selenium_client.get(self.url)

	def CheckCondition(self) -> bool:
		return True


class FindBy(Selenium_Step, BaseStep):
	"""
	utility class to find element using 'By' and 'value'
	"""

	def __init__(self, by: By, value: str, **kwargs):
		super().__init__()
		self.by = by
		self.value = value
		self._kwargs = kwargs

	def Do(self) -> None:
		try:
			self.selenium_client.find_element(by=self.by, value=self.value)
			self.response.ok = True
		except Exception:
			self.logger.error("Could not find element {}".format({"by": self.value}))
			self.response.ok = False

	def CheckCondition(self) -> bool:
		return self.response.ok


class Login(Selenium_Step, BaseStep):
	"""
	A class to do a login procedure of the bot name provided

	Attributes:
	  url (str): endpoint url of twitter 'https://twitter.com/i/flow/login'
	  botname (str): the name of the bot in the METADATA
	"""

	def __init__(
		self,
		url: str = "https://twitter.com/i/flow/login",
		botname: str = "bot1",
		**kwargs,
	):
		super().__init__(**kwargs)
		self.url = url
		self.bmd = BotMetadata().GetBotMetadata(botname=botname)

	def Do(self):
		try:
			OpenPage(url=self.url)()
			sleep(15)

			self.selenium_client.find_element(**self.config.EMAIL_FIELD).send_keys(
				self.bmd.EMAIL_KEY
			)
			self.selenium_client.find_element(**self.config.LOGIN_BUTTON1).click()
			sleep(2)

			if self._CheckExistsByXpath(self.config.PASSWORD_FIELD):
				self.selenium_client.find_element(
					**self.config.PASSWORD_FIELD
				).send_keys(self.bmd.PASSWORD_KEY)
				self.selenium_client.find_element(**self.config.LOGIN_BUTTON2).click()

			elif self._CheckExistsByXpath(self.config.USERNAME_FIELD):
				self.selenium_client.find_element(
					**self.config.USERNAME_FIELD
				).send_keys(self.bmd.USERNAME_KEY)
				self.selenium_client.find_element(**self.config.NEXT_BUTTON).click()
				sleep(2)
				if self._CheckExistsByXpath(
					self.config.USERNAME_FIELD
				):  # incorrect username, using phone number instead
					self.selenium_client.find_element(
						**self.config.USERNAME_FIELD
					).send_keys(Keys.CONTROL + "a")
					self.selenium_client.find_element(
						**self.config.USERNAME_FIELD
					).send_keys(Keys.DELETE)
					self.selenium_client.find_element(
						**self.config.USERNAME_FIELD
					).send_keys(self.bmd.PHONE_NUMBER)
					self.selenium_client.find_element(**self.config.NEXT_BUTTON).click()
					sleep(2)
				if self._CheckExistsByXpath(self.config.PASSWORD_FIELD):
					self.selenium_client.find_element(
						**self.config.PASSWORD_FIELD
					).send_keys(self.bmd.PASSWORD_KEY)
					self.selenium_client.find_element(
						**self.config.LOGIN_BUTTON2
					).click()
			self.response.ok = True

			time.sleep(4)

		except Exception:
			self.logger.warning("Either Error in logging in")

	def CheckCondition(self):
		self.logger.info("Logged-in as {}".format(self.bmd.USERNAME_KEY))
		return self.response.ok


class Like(Selenium_Step, BaseStep):
	"""
	A class to automate a tweek like

	Attributes:
	  post_url (str): url of the tweet
	  by_all_bots (bool): if True iterate through the METADATA of bots to like the post.
	      False(default) will only use the METADATA of the first bot.
	"""

	def __init__(self, post_url: str, by_all_bots: bool = False, **kwargs):
		super().__init__(**kwargs)
		self.post_url = post_url
		self.by_all_bots = by_all_bots

	def Do(self):
		if self.by_all_bots is False:
			__bmd = BotMetadata()
			bot, val = next(iter(__bmd.data.items()))
			try:
				Login(botname=bot)()
				sleep(5)
				OpenPage(url=self.post_url)()
				sleep(7)
				if self._CheckExistsByXpath(self.config.LIKE_ICON):
					self.selenium_client.find_element(**self.config.LIKE_ICON).click()
				self.logger.info("Liked post {} with bot {}".format(self.post_url, bot))
			except Exception:
				self.logger.error(
					"Exception caught while liking post {} with bot {}".format(
						self.post_url, bot
					)
				)
		else:
			__bmd = BotMetadata()
			for bot in __bmd.data:
				try:
					Login(botname=bot)()
					sleep(5)
					OpenPage(url=self.post_url)()
					sleep(7)
					if self._CheckExistsByXpath(self.config.LIKE_ICON):
						self.selenium_client.find_element(
							**self.config.LIKE_ICON
						).click()
						self.logger.info(
							"Liked post {} with bot {}".format(self.post_url, bot)
						)
					else:  # TODO
						pass
				except Exception:
					self.logger.error(
						"Exception caught while liking post {} with bot {}".format(
							self.post_url, bot
						)
					)

	def CheckCondition(self):
		self.logger.info("Liked post {}".format(self.post_url))
		return True


class Retweet(Selenium_Step, BaseStep):
	"""
	A class to automate a retweet of tweet

	Attributes:
	  post_url (str): url of the tweet
	  by_all_bots (bool): if True iterate through the METADATA of bots to Retweet the post.
	      False(default) will only use the METADATA of the first bot.
	"""

	def __init__(self, post_url: str, by_all_bots: bool = False, **kwargs):
		super().__init__(**kwargs)
		self.post_url = post_url
		self.by_all_bots = by_all_bots

	def Do(self):
		if self.by_all_bots is False:
			__bmd = BotMetadata()
			bot, val = next(iter(__bmd.data.items()))
			try:
				Login(botname=bot)()
				sleep(5)
				if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
					self.selenium_client.find_element(
						**self.config.RETWEET_ICON1
					).click()
					sleep(0.5)
					if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
						self.selenium_client.find_element(
							**self.config.RETWEET_ICON2
						).click()
						self.logger.info(
							"Retweeted post {} with bot {}".format(self.post_url, bot)
						)
			except Exception:
				self.logger.error(
					"Exception caught while Retweeting post {} with bot {}".format(
						self.post_url, bot
					)
				)
		else:
			__bmd = BotMetadata()
			for bot in __bmd.data:
				try:
					Login(botname=bot)()
					sleep(5)
					OpenPage(url=self.post_url)()
					sleep(7)
					if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
						self.selenium_client.find_element(
							**self.config.RETWEET_ICON1
						).click()
						sleep(0.5)
						if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
							self.selenium_client.find_element(
								**self.config.RETWEET_ICON2
							).click()
							self.logger.info(
								"Liked post {} with bot {}".format(self.post_url, bot)
							)
					else:  # TODO
						pass
				except Exception:
					self.logger.error(
						"Exception caught while liking post {} with bot {}".format(
							self.post_url, bot
						)
					)

	def CheckCondition(self):
		self.logger.info("Liked post {}".format(self.post_url))
		return True


class comment(Selenium_Step, BaseStep):
	"""
	(WIP)
	"""

	def __init__(self, post_url: str, by_all_bots: bool = False, **kwargs):
		super().__init__(**kwargs)
		self.post_url = post_url
		self.by_all_bots = by_all_bots

	def __get_context(self):
		pass

	def Do(self):
		if self.by_all_bots is False:
			OpenPage(url=self.post_url)()
			sleep(7)
			if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
				self.selenium_client.find_element(**self.config.RETWEET_ICON1).click()
				sleep(0.5)
				if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
					self.selenium_client.find_element(
						**self.config.RETWEET_ICON2
					).click()
					self.logger.info("Liked post {}".format(self.post_url))
		else:
			__bmd = BotMetadata()
			for bot in __bmd.data:
				try:
					Login(botname=bot)()
					sleep(5)
					OpenPage(url=self.post_url)()
					sleep(7)
					if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
						self.selenium_client.find_element(
							**self.config.RETWEET_ICON1
						).click()
						sleep(0.5)
						if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
							self.selenium_client.find_element(
								**self.config.RETWEET_ICON2
							).click()
							self.logger.info(
								"Liked post {} with bot {}".format(self.post_url, bot)
							)
					else:  # TODO
						pass
				except Exception:
					self.logger.error(
						"Exception caught while liking post {} with bot {}".format(
							self.post_url, bot
						)
					)

	def CheckCondition(self):
		self.logger.info("Liked post {}".format(self.post_url))
		return True


class Tweet(Selenium_Step, BaseStep):
	"""
	A class to automate a tweet

	Attributes:
	  tweet_content (str): message of what to tweet
	  by_all_bots (bool): if True iterate through the METADATA of bots to tweet.
	      False(default) will only use the METADATA of the first bot.
	"""

	def __init__(
		self,
		tweet_content: str = "hello, this is a automated tweet",
		bot_name: str = "default_bot",
		use_pyautogui: bool = False,
		**kwargs,
	):
		super().__init__(**kwargs)
		self.tweet_content = tweet_content
		self.bot_name = bot_name
		self.use_pyautogui = use_pyautogui

	def Do(self):
		__bmd = BotMetadata().data
		bot = __bmd.get(self.bot_name, "").get("USERNAME_KEY", "")
		if self.use_pyautogui:
			try:
				try:
					# check if already logged in
					result1 = GetIconCoordinates(
						icon_name="next_button_already_logged_in"
					)().data
					Click(*result1.get("center"))()
					self.logger.warning("Already logged in..")
					time.sleep(3)
				except Exception:
					pass

				result1 = GetIconCoordinates(icon_name="start_tweet_small")().data
				Click(*result1.get("center"))()
				time.sleep(3)

				Write(self.tweet_content)()
				time.sleep(3)

				result2 = GetIconCoordinates(icon_name="tweet_button")().data
				Click(*result2.get("center"))()
				time.sleep(3)

				self.logger.info("Tweeted {}".format(self.tweet_content))
			except Exception:
				self.logger.error(traceback.format_exc())
				self.logger.error(
					"Error occured while tweeting with bot {}".format(bot)
				)

		else:
			if self._CheckExistsByXpath(
				{
					"by": By.XPATH,
					"value": "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[3]/a/div",
				}
			):
				self.selenium_client.find_element(
					**{
						"by": By.XPATH,
						"value": "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[3]/a/div",
					}
				).click()
				sleep(5)
			if self._CheckExistsByXpath(
				{
					"by": By.XPATH,
					"value": "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div",
				}
			):
				self.selenium_client.find_element(
					**{
						"by": By.XPATH,
						"value": "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div",
					}
				).send_keys(self.tweet_content)
				sleep(5)
			if self._CheckExistsByXpath(
				{
					"by": By.XPATH,
					"value": "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[2]/div[2]/div/div/div/div[4]/div/span/span",
				}
			):
				self.selenium_client.find_element(
					**{
						"by": By.XPATH,
						"value": "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[2]/div[2]/div/div/div/div[4]/div/span/span",
					}
				).click()
				sleep(5)
		self.response.ok = True

	def CheckCondition(self):
		return self.response.ok


class OpenaiTweet(Selenium_Step, BaseStep):
	"""
	(WIP)
	A class to automate a tweet using openai API to generate the tweet text

	Attributes:
	  user_prompt (str): message of waht to tweet (WIP)
	  tags (list of strings): tags on waht the tweet must be so that it can be used by Openai API to generate a reposne.
	  by_all_bots (bool): if True iterate through the METADATA of bots to tweet.
	      False(default) will only use the METADATA of the first bot.
	  as_image (bool): if True, the tweet text will be converted to an image and gets tweeted
	"""

	JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""

	def __init__(
		self,
		user_prompt: str = "Generate a inspirational quote using tags like",
		tags: list = [],
		bot_username: str = "",
		by_all_bots: bool = False,
		as_image=False,
		**kwargs,
	):
		super().__init__(**kwargs)
		self.prompt = user_prompt
		self.by_all_bots = by_all_bots
		self.tags = tags
		self.as_image = as_image

	def _form_question_from_tags(self):
		tags = ""
		for tag in self.tags:
			tags += tag + ", "
		return "{} {}".format(self.prompt, tags)

	def _generate_text(self):
		from APIs.GPT.respond import generate_gpt3_response

		response = generate_gpt3_response(
			user_prompt=self._form_question_from_tags()
		)().data
		return response.choices[0].text.strip()

	def _form_image_from_text(self, text: str):
		font_size = 24
		from PIL import Image, ImageDraw, ImageFont

		# Set the font style and size
		font = ImageFont.truetype("resources/fonts/MemorialLane-z8XVX.ttf", font_size)

		# Determine the image size based on the text length and font size
		text_width, text_height = font.getsize(text)
		image_width = text_width + 200  # Adding padding
		image_height = text_height + 200  # Adding padding

		# Create a blank image with a white background
		image = Image.new("RGB", (image_width, image_height), (196, 196, 53))
		image.info["dpi"] = (1200, 1200)
		draw = ImageDraw.Draw(image)

		# Calculate the position to center the text
		x = (image_width - text_width) // 2
		y = (image_height - text_height) // 2

		# Draw the text on the image
		draw.text((x, y), text, font=font, fill="black")

		_current_time = time.strftime("%H-%M-%S", time.localtime())
		_current_date = date.today().strftime("%B-%d-%Y")

		if os.path.exists("_IMAGEs") is False:
			self.logger.info("_IMAGEs dir was not found in workspace, creating it...")
			os.mkdir("_IMAGEs")
		image_path = os.path.join(
			"_IMAGEs/", "{}_{}.png".format(_current_date, _current_time)
		)
		image.save(image_path)

		return os.path.abspath(image_path)

	def _drag_and_drop_file(self, drop_target, path):
		file_input = self.selenium_client.execute_script(
			OpenaiTweet.JS_DROP_FILE, drop_target, 0, 0
		)
		file_input.send_keys(path)

	def Do(self):
		generated_text: str = self._generate_text()
		__bmd = BotMetadata()
		for bot in __bmd.data:
			try:
				Login(botname=bot)()
				sleep(5)
				if self.as_image is False:
					result1 = GetIconCoordinates(icon_name="start_tweet_small")().data
					Click(*result1.get("center"))()
					time.sleep(3)

					Write(generated_text)()
					time.sleep(3)
				else:
					image_path = self._form_image_from_text(text=generated_text)
					tweet_element = self.selenium_client.find_element(
						**self.config.TWEET_FIELD
					)
					self._drag_and_drop_file(tweet_element, image_path)

				result2 = GetIconCoordinates(icon_name="tweet_button")().data
				Click(*result2.get("center"))()
				time.sleep(3)

				self.logger.info("Tweeted on tags {}".format(self.tags))
			except Exception:
				self.logger.error(traceback.format_exc())
				self.logger.error(
					"Error occured while tweeting with bot {}".format(bot)
				)

			if self.by_all_bots is False:
				break

		self.response.ok = True

	def CheckCondition(self):
		return self.response.ok


class ReportProfile(Selenium_Step, BaseStep):
	"""
	(WIP)
	"""

	def __init__(self, user_profile: str, report_category: str, **kwargs):
		super().__init__(**kwargs)
		self.user_profile = user_profile
		self.report_category = report_category

	def Do(self):
		_bmd = BotMetadata()
		for bot in _bmd.data:
			try:
				Login(botname=bot)()
				sleep(5)
				OpenPage(url=self.user_profile)()
				sleep(7)

				from config.scripts_config import ReportingIconWorkflow as r

				for icon in r.workflow:
					# click icon
					result = GetIconCoordinates(icon_name=icon)().data
					Click(*result.get("center"))()

				self.logger.info(
					"Reporting completed for profile {} with bot {}".format(
						self.user_profile.split("/")[-1], bot
					)
				)

			except Exception:
				self.logger.error(traceback.format_exc())
				self.logger.error(
					"Error occured while reporting a profile with bot {}".format(bot)
				)

	def CheckCondition(self):
		return True


class LikePosts(Selenium_Step, BaseStep):
	"""
	A class to automate a Like of posts under a profile

	Attributes:
	  user_profile (str): url of the profile
	  number_of_posts (int): Like a 'number_of_posts' posts of profile
	"""

	def __init__(self, user_profile: str, number_of_posts: int, **kwargs):
		super().__init__(**kwargs)
		self.user_profile = user_profile
		self.number_of_posts = number_of_posts

	def Do(self):
		OpenPage(url=self.user_profile)()
		sleep(5)
		liked = 0
		scroll = 0
		scroll_inc = 300
		while True:
			try:
				if self._CheckExistsByXpath(self.config.LIKE_ICON):
					self.selenium_client.find_element(**self.config.LIKE_ICON).click()
					sleep(3)
					liked += 1
					self.logger.info(
						"Liked {} tweet of @{}".format(
							liked, self.user_profile.split("/")[-1]
						)
					)
					if liked > self.number_of_posts:
						break
				else:
					scroll += scroll_inc
					self.selenium_client.execute_script(
						"window.scrollTo(0, {})".format(scroll)
					)
					self.logger.info(
						"Already liked of @{}, skipping tweet".format(
							self.user_profile.split("/")[-1]
						)
					)
					sleep(3)
			except Exception:
				self.logger.error("Exception caught while liking post{}".format(liked))
				self.logger.error("Continuing to the next post.")

	def CheckCondition(self):
		return True


class RetweetPosts(Selenium_Step, BaseStep):
	"""
	A class to automate a retweet of posts under a profile

	Attributes:
	  user_profile (str): url of the profile
	  number_of_posts (int): retweet a 'number_of_posts' posts of profile
	"""

	def __init__(self, user_profile, number_of_posts, **kwargs):
		super().__init__(**kwargs)
		self.user_profile = user_profile
		self.number_of_posts = number_of_posts

	def Do(self):
		OpenPage(url=self.user_profile)()
		sleep(5)
		retweet = 0
		scroll = 0
		scroll_inc = 300
		while True:
			try:
				if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
					self.selenium_client.find_element(
						**self.config.RETWEET_ICON1
					).click()
					sleep(0.5)
					if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
						self.selenium_client.find_element(
							**self.config.RETWEET_ICON2
						).click()
					retweet += 1
					self.logger.info(
						"Retweeted {} tweet of @{}".format(
							retweet, self.user_profile.split("/")[-1]
						)
					)
					if retweet > self.number_of_posts:
						break
				else:
					scroll += scroll_inc
					self.selenium_client.execute_script(
						"window.scrollTo(0, {})".format(scroll)
					)
					self.logger.info(
						"Already retweeted of @{}, skipping tweet".format(
							self.user_profile.split("/")[-1]
						)
					)
					sleep(0.5)
			except Exception:
				self.logger.error(
					"Exception caught while liking post{}".format(retweet)
				)
				self.logger.error("Continuing to the next post.")

	def CheckCondition(self):
		return True


class CollectUserTweetData(Selenium_Step, BaseStep):
	def __init__(
		self,
		user_profile: str,
		number_of_tweets: int,
		recursive_levels: int = 0,
		file_format: str = "csv",
		file_name: str = "default",
		**kwargs,
	):
		super().__init__(**kwargs)
		self.user_profile = user_profile
		self.number_of_tweets = number_of_tweets
		self.recursive_levels = recursive_levels
		self.file_format = file_format
		self.file_name = file_name

		self.data = {}
		self.writer: csv.DictWriter
		self.data_file: pp
		self.writer, self.data_file = create_data_file(
			file_name, format=file_format, fieldnames=["index", "content"]
		)

	@timeout(5 * 60)  # 300 seconds
	def Do(self):
		sleep(5)
		OpenPage(url=self.user_profile)()
		sleep(5)
		tweets = 0
		current_screen_data: list = None
		last_element = None
		scroll = 0
		scroll_inc = 300
		idx = 0
		max_consicutive_scroll_count = 50

		# main loop
		while tweets < self.number_of_tweets:
			try:
				# collect all the tweets visible in current screen
				current_screen_data: List[WebElement] = (
					self.selenium_client.find_elements(**self.config.TWEET_FIELD_LATEST)
				)
				last_element = current_screen_data[-1]
				# add all available tweets to a file
				for tweet in current_screen_data:
					self.data.update({idx: tweet.text})
					self.logger.info(
						"{} has tweeted {}".format(
							self.user_profile.split("/")[-1], tweet.text
						)
					)
					with open(self.data_file, "a", newline="") as f:
						if self.file_format == "csv":
							self.writer.writerow({"index": idx, "content": tweet.text})
						else:
							f.write("{}, {}\n".format(idx, tweet.text))
						self.logger.info("wrote to the file {}".format(self.data_file))
					idx += 1
				tweets += len(current_screen_data)
				# till last_element is still in the current screen keep scrolling
				consicutive_scroll_count = 0
				while last_element in self.selenium_client.find_elements(
					**self.config.TWEET_FIELD_LATEST
				):
					if consicutive_scroll_count > max_consicutive_scroll_count:
						self.logger.warning(
							f"maximum consicutive scroll count: {max_consicutive_scroll_count} reached, maybe you reached the max twitter's tweet view quota"
						)
						return
					scroll += scroll_inc
					self.selenium_client.execute_script(
						"window.scrollTo(0, {})".format(scroll)
					)
					consicutive_scroll_count += 1
					sleep(0.5)
					self.logger.info("scrolling {}px ...".format(scroll_inc))
			except Exception:
				self.logger.error(traceback.format_exc())
				self.logger.error("Exception caught while...")

	def CheckCondition(self):
		return True


if __name__ == "__main__":
	OpenPage(url="https://twitter.com/i/flow/login")()
