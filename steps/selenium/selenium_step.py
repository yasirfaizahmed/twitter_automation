from steps.selenium.stepsconfig import SeleniumClientConf
from patterns.patterns import Singleton


import logging
from selenium import webdriver
import pathlib


class SeleniumClient(Singleton, SeleniumClientConf):

  def __init__(self, driver_path: str = None, need_new_client=False, **kwargs):
    driver_path = self.DRIVER_PATH if driver_path is None else driver_path
    if need_new_client is True:
      if hasattr(self, 'driver') is True:
        del self.driver
    self._kwargs = kwargs

    if hasattr(self, 'driver') is not True:
      if pathlib.Path(self.DRIVER_PATH).exists():
        self.driver = webdriver.Chrome(driver_path)
        self.driver.find_element
      else:
        logging.error("passed driver_path {} is not valid".format(driver_path))


class Selenium_Step():

  def __init__(self, **kwargs):
    self.selenium_client = SeleniumClient(**kwargs).driver
