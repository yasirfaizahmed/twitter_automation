from steps.selenium.stepsconfig import SeleniumClientConf
from patterns.patterns import Singleton


import logging
from selenium import webdriver
import pathlib


class SeleniumClient(Singleton, SeleniumClientConf):

  def __init__(self, driver_path: str = None):
    driver = self.DRIVER_PATH if driver_path is None else driver_path

    if pathlib.Path(self.DRIVER_PATH).exists():
      self.driver = webdriver.Chrome(driver)
    else:
      logging.error("passed driver_path {} is not valid".format(driver))
