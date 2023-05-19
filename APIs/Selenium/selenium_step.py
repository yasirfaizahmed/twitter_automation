from APIs.Selenium.stepsconfig import SeleniumClientConf
from patterns.patterns import Singleton
from config.scripts_config import SeleniumConfigs, MailConfigs


import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pathlib

OPTIONS = Options()
OPTIONS.add_argument("--start-maximized")


class SeleniumClient(SeleniumClientConf, metaclass=Singleton):

  def __init__(self, driver_path: str = None, **kwargs):
    driver_path = self.DRIVER_PATH if driver_path is None else driver_path
    if pathlib.Path(self.DRIVER_PATH).exists():
      self.driver = webdriver.Chrome(driver_path, options=OPTIONS)
      self.driver.find_element
    else:
      logging.error("driver_path {} is not valid".format(driver_path))
    self._kwargs = kwargs


class Selenium_Step():
  # All interactive related API classes must inherite from Selenium_Step
  def __init__(self, **kwargs):
    self.selenium_client = SeleniumClient(**kwargs).driver
    self.config = SeleniumConfigs()

  def _CheckExistsByXpath(self, element):   # custom step method
    try:
      self.selenium_client.find_element(**element)
    except Exception:
      return False
    return True


class Mail_Step():
  def __init__(self):
    self.config = MailConfigs()


if __name__ == '__main__':
  a = SeleniumClient().driver
