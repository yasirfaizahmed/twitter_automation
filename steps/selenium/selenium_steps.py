from selenium.webdriver.common.by import By
from time import sleep

from base.base_step import BaseStep
from steps.selenium.selenium_step import Selenium_Step
from utils.util import GetBotMetadata
from scripts.scripts_config import BotMetadata


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
      self.response.ok = True
    except Exception:
      self.logger.error("Could not find element {}".format({'by': self.value}))
      self.response.ok = False

  def CheckCondition(self) -> bool:
    return self.response.ok


class Login(Selenium_Step, BaseStep):
  def __init__(self,
               url: str = "https://twitter.com/i/flow/login",
               botname: str = 'bot1', **kwargs):
    super().__init__(**kwargs)
    self.url = url
    self.bmd = GetBotMetadata(botname=botname)

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

  def __init__(self, post_url: str, by_all_bots: bool = False, **kwargs):
    super().__init__(**kwargs)
    self.post_url = post_url
    self.by_all_bots = by_all_bots

  def Do(self):
    if self.by_all_bots is False:
      OpenPage(url=self.post_url)()
      sleep(7)
      if self._CheckExistsByXpath(self.config.LIKE_ICON):
        self.selenium_client.find_element(**self.config.LIKE_ICON).click()
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

  def __init__(self, post_url: str, by_all_bots: bool = False, **kwargs):
    super().__init__(**kwargs)
    self.post_url = post_url
    self.by_all_bots = by_all_bots

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


class comment(Selenium_Step, BaseStep):

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
  def __init__(self, user_prompt: str, by_all_bots: bool = False, tags: list = [], **kwargs):
    super().__init__(**kwargs)
    self.prompt = user_prompt
    self.by_all_bots = by_all_bots
    self.tags = tags

  def _form_quotes_from_tags(self):
    tags = ''
    for tag in self.tags:
      tags += tag + ', '
    return "Generate a inspirational quote using tags like{}".format(tags)

  def _generate_text(self):
    from steps.gpt.respond import generate_gpt3_response
    response = generate_gpt3_response(user_prompt=self._form_quotes_from_tags())
    return response.choices[0].text.strip()

  def Do(self):
    genrated_text: str = self._generate_text()

  def CheckCondition(self):
    return True


class LikePosts(Selenium_Step, BaseStep):

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
