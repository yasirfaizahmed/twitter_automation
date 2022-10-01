import logging
from selenium.webdriver.common.by import By

from base.base_step import BaseStep
from steps.selenium.selenium_step import Selenium_Step


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

  def Do(self):
    try:
      self.selenium_client.find_element(by=self.by, value=self.value)
      self.response = True
    except Exception:
      logging.error("Could not find element {}".format({'by': self.value}))
      self.response = False

  def CheckCondition(self):
    return self.response


if __name__ == '__main__':
  OpenPage(url="https://twitter.com/i/flow/login")()
