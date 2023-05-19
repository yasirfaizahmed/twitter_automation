from selenium.webdriver.common.by import By
from time import sleep
import traceback
import time

from base.base_step import BaseStep
from APIs.Selenium.selenium_step import Selenium_Step
from utils.util import GetBotMetadata
from config.scripts_config import BotMetadata
from APIs.CV.cv_steps import GetIconCoordinates
from APIs.PyAutoGUI.pyautogui_steps import Click, Write


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
      self.logger.error("Could not find element {}".format({'by': self.value}))
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
  def __init__(self,
               url: str = "https://twitter.com/i/flow/login",
               botname: str = 'bot1', **kwargs):
    super().__init__(**kwargs)
    self.url = url
    self.bmd = GetBotMetadata(botname=botname)

  def Do(self):
    try:
      OpenPage(url=self.url)()
      sleep(15)

      self.selenium_client.find_element(**self.config.EMAIL_FIELD).send_keys(self.bmd.EMAIL_KEY)
      self.selenium_client.find_element(**self.config.LOGIN_BUTTON1).click()
      sleep(2)

      if self._CheckExistsByXpath(self.config.PASSWORD_FIELD):
        self.selenium_client.find_element(**self.config.PASSWORD_FIELD).send_keys(self.bmd.PASSWORD_KEY)
        self.selenium_client.find_element(**self.config.LOGIN_BUTTON2).click()

      elif self._CheckExistsByXpath(self.config.USERNAME_FIELD):
        self.selenium_client.find_element(**self.config.USERNAME_FIELD).send_keys(self.bmd.USERNAME_KEY)
        self.selenium_client.find_element(**self.config.NEXT_BUTTON).click()
        sleep(2)
        if self._CheckExistsByXpath(self.config.PASSWORD_FIELD):
          self.selenium_client.find_element(**self.config.PASSWORD_FIELD).send_keys(self.bmd.PASSWORD_KEY)
          self.selenium_client.find_element(**self.config.LOGIN_BUTTON2).click()
      self.response.ok = True

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
        self.logger.error("Exception caught while liking post {} with bot {}".format(self.post_url, bot))
    else:
      __bmd = BotMetadata()
      for bot in __bmd.data:
        try:
          Login(botname=bot)()
          sleep(5)
          OpenPage(url=self.post_url)()
          sleep(7)
          if self._CheckExistsByXpath(self.config.LIKE_ICON):
            self.selenium_client.find_element(**self.config.LIKE_ICON).click()
            self.logger.info("Liked post {} with bot {}".format(self.post_url, bot))
          else:   # TODO
            pass
        except Exception:
          self.logger.error("Exception caught while liking post {} with bot {}".format(self.post_url, bot))

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
          self.selenium_client.find_element(**self.config.RETWEET_ICON1).click()
          sleep(0.5)
          if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
            self.selenium_client.find_element(**self.config.RETWEET_ICON2).click()
            self.logger.info("Retweeted post {} with bot {}".format(self.post_url, bot))
      except Exception:
        self.logger.error("Exception caught while Retweeting post {} with bot {}".format(self.post_url, bot))
    else:
      __bmd = BotMetadata()
      for bot in __bmd.data:
        try:
          Login(botname=bot)()
          sleep(5)
          OpenPage(url=self.post_url)()
          sleep(7)
          if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
            self.selenium_client.find_element(**self.config.RETWEET_ICON1).click()
            sleep(0.5)
            if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
              self.selenium_client.find_element(**self.config.RETWEET_ICON2).click()
              self.logger.info("Liked post {} with bot {}".format(self.post_url, bot))
          else:   # TODO
            pass
        except Exception:
          self.logger.error("Exception caught while liking post {} with bot {}".format(self.post_url, bot))

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
          self.selenium_client.find_element(**self.config.RETWEET_ICON2).click()
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
            self.selenium_client.find_element(**self.config.RETWEET_ICON1).click()
            sleep(0.5)
            if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
              self.selenium_client.find_element(**self.config.RETWEET_ICON2).click()
              self.logger.info("Liked post {} with bot {}".format(self.post_url, bot))
          else:   # TODO
            pass
        except Exception:
          self.logger.error("Exception caught while liking post {} with bot {}".format(self.post_url, bot))

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
  def __init__(self, tweet_content: str = 'hello, this is a automated tweet',
               by_all_bots: bool = False, **kwargs):
    super().__init__(**kwargs)
    self.tweet_content = tweet_content
    self.by_all_bots = by_all_bots

  def Do(self):
    __bmd = BotMetadata()
    for bot in __bmd.data:
      try:
        Login(botname=bot)()
        sleep(5)

        try:
          # check if already logged in
          result1 = GetIconCoordinates(icon_name='next_button_already_logged_in')().data
          Click(*result1.get('center'))()
          self.logger.warning("Already logged in..")
          time.sleep(3)
        except Exception:
          pass

        result1 = GetIconCoordinates(icon_name='start_tweet_small')().data
        Click(*result1.get('center'))()
        time.sleep(3)

        Write(self.tweet_content)()
        time.sleep(3)

        result2 = GetIconCoordinates(icon_name='tweet_button')().data
        Click(*result2.get('center'))()
        time.sleep(3)

        self.logger.info("Tweeted {}".format(self.tweet_content))
      except Exception:
        self.logger.error(traceback.format_exc())
        self.logger.error("Error occured while tweeting with bot {}".format(bot))

      if self.by_all_bots is False:
        break

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
  """
  def __init__(self, user_prompt: str = 'Generate a inspirational quote using tags like',
               tags: list = [], bot_username: str = '', by_all_bots: bool = False, **kwargs):
    super().__init__(**kwargs)
    self.prompt = user_prompt
    self.by_all_bots = by_all_bots
    self.tags = tags

  def _form_question_from_tags(self):
    tags = ''
    for tag in self.tags:
      tags += tag + ', '
    return "{} {}".format(self.prompt, tags)

  def _generate_text(self):
    from APIs.GPT.respond import generate_gpt3_response
    response = generate_gpt3_response(user_prompt=self._form_question_from_tags())().data
    return response.choices[0].text.strip()

  def Do(self):
    generated_text: str = self._generate_text()
    __bmd = BotMetadata()
    for bot in __bmd.data:
      try:
        Login(botname=bot)()
        sleep(5)
        result1 = GetIconCoordinates(icon_name='start_tweet_small')().data
        Click(*result1.get('center'))()
        time.sleep(3)

        Write(generated_text)()
        time.sleep(3)

        result2 = GetIconCoordinates(icon_name='tweet_button')().data
        Click(*result2.get('center'))()
        time.sleep(3)

        self.logger.info("Tweeted on tags {}".format(self.tags))
      except Exception:
        self.logger.error(traceback.format_exc())
        self.logger.error("Error occured while tweeting with bot {}".format(bot))

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
          Click(*result.get('center'))()

        self.logger.info("Reporting completed for profile {} with bot {}".format(self.user_profile.split('/')[-1], bot))

      except Exception:
        self.logger.error(traceback.format_exc())
        self.logger.error("Error occured while reporting a profile with bot {}".format(bot))

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
          self.logger.info("Retweeted {} tweet of @{}".format(liked, self.user_profile.split('/')[-1]))
          if liked > self.number_of_posts:
            break
        else:
          scroll += scroll_inc
          self.selenium_client.execute_script("window.scrollTo(0, {})".format(scroll))
          self.logger.info("Already liked of @{}, skipping tweet".format(self.user_profile.split('/')[-1]))
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
          self.selenium_client.find_element(**self.config.RETWEET_ICON1).click()
          sleep(0.5)
          if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
            self.selenium_client.find_element(**self.config.RETWEET_ICON2).click()
          retweet += 1
          self.logger.info("Retweeted {} tweet of @{}".format(retweet, self.user_profile.split('/')[-1]))
          if retweet > self.number_of_posts:
            break
        else:
          scroll += scroll_inc
          self.selenium_client.execute_script("window.scrollTo(0, {})".format(scroll))
          self.logger.info("Already retweeted of @{}, skipping tweet".format(self.user_profile.split('/')[-1]))
          sleep(0.5)
      except Exception:
        self.logger.error("Exception caught while liking post{}".format(retweet))
        self.logger.error("Continuing to the next post.")

  def CheckCondition(self):
    return True


if __name__ == '__main__':
  OpenPage(url="https://twitter.com/i/flow/login")()
