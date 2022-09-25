from selenium import webdriver
import pathlib
import logging

from patterns.patterns import Singleton


class SeleniumClient(Singleton):

  def __init__(self, driver_path: str):
    if pathlib.Path(driver_path).exists():
      self.driver = webdriver.Chrome(driver_path)
    else:
      logging.error("passed driver_path {} is not valid".format(driver_path))
