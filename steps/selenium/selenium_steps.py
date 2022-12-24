from selenium.webdriver.common.by import By
from time import sleep

from base.base_step import BaseStep
from steps.selenium.selenium_step import Selenium_Step
from utils.util import GetBotMetadata


class OpenPage(Selenium_Step, BaseStep):

  def __init__(self, url: str, **kwargs):
    super().__init__(**kwargs)
    self.url = url

  def Do(self) -> None:
    self.selenium_client.get(self.url)

  def CheckCondition(self) -> bool:
    return True


class FindBy(Selenium_Step, BaseStep):

  def __init__(self, by: By, value: str, **kwargs):
    super().__init__()
    self.by = by
    self.value = value
    self._kwargs = kwargs

  def Do(self) -> None:
    try:
      self.selenium_client.find_element(by=self.by, value=self.value)
      self.response = True
    except Exception:
      self.logger.error("Could not find element {}".format({'by': self.value}))
      self.response = False

  def CheckCondition(self) -> bool:
    return self.response


class Login(Selenium_Step, BaseStep):
  def __init__(self,
               url: str = "https://twitter.com/i/flow/login", 
               botname: str = 'bot1', **kwargs):
    super().__init__(**kwargs)
    self.url = url
    self.bmd = GetBotMetadata(botname=botname)

  def _CheckExistsByXpath(self, element):
    try:
      self.selenium_client.find_element(**element)
    except Exception:
      return False
    return True

  def Do(self):
    OpenPage(url=self.url)()
    sleep(10)

    self.selenium_client.find_element(**self.config.EMAIL_FIELD).send_keys(self.bmd.EMAIL_KEY)
    self.selenium_client.find_element(**self.config.LOGIN_BUTTON1).click()
    sleep(2)

    if self._CheckExistsByXpath(self.config.PASSWORD_FIELD):
      self.selenium_client.find_element(**self.config.PASSWORD_FIELD).send_keys(self.bmd.PASSWORD_KEY)
      self.selenium_client.find_element(**self.config.LOGIN_BUTTON2).click()
      return

    elif self._CheckExistsByXpath(self.config.USERNAME_FIELD):
      self.selenium_client.find_element(**self.config.USERNAME_FIELD).send_keys(self.bmd.USERNAME_KEY)
      self.selenium_client.find_element(**self.config.NEXT_BUTTON).click()
      sleep(2)
      if self._CheckExistsByXpath(self.config.PASSWORD_FIELD):
        self.selenium_client.find_element(**self.config.PASSWORD_FIELD).send_keys(self.bmd.PASSWORD_KEY)
        self.selenium_client.find_element(**self.config.LOGIN_BUTTON2).click()

  def CheckCondition(self):
    self.logger.info("Logged-in as {}".format(self.bmd.USERNAME_KEY))
    return True   # TODO


class Like(Selenium_Step, BaseStep):

  def __init__(self, post_url, **kwargs):
    super().__init__(**kwargs)
    self.post_url = post_url

  def Do(self):
    OpenPage(url=self.post_url)()
    sleep(7)
    self.selenium_client.find_element(**self.config.LIKE_ICON).click()

  def CheckCondition(self):
    self.logger.info("Liked post ")
    return True


class LikePosts(Selenium_Step, BaseStep):

  def _CheckExistsByXpath(self, element):
    try:
      self.selenium_client.find_element(**element)
    except Exception:
      return False
    return True

  def __init__(self, user_profile, number_of_posts, **kwargs):
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

  def CheckCondition(self):
    return True


class RetweetPosts(Selenium_Step, BaseStep):

  def _CheckExistsByXpath(self, element):
    try:
      self.selenium_client.find_element(**element)
    except Exception:
      return False
    return True

  def __init__(self, user_profile, number_of_posts, **kwargs):
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
      if self._CheckExistsByXpath(self.config.RETWEET_ICON1):
        self.selenium_client.find_element(**self.config.RETWEET_ICON1).click()
        sleep(0.5)
        if self._CheckExistsByXpath(self.config.RETWEET_ICON2):
          self.selenium_client.find_element(**self.config.RETWEET_ICON2).click()
        liked += 1
        self.logger.info("Retweeted {} tweet of @{}".format(liked, self.user_profile.split('/')[-1]))
        if liked > self.number_of_posts:
          break
      else:
        scroll += scroll_inc
        self.selenium_client.execute_script("window.scrollTo(0, {})".format(scroll))
        self.logger.info("Already retweeted of @{}, skipping tweet".format(self.user_profile.split('/')[-1]))
        sleep(0.5)

  def CheckCondition(self):
    return True


if __name__ == '__main__':
  OpenPage(url="https://twitter.com/i/flow/login")()
