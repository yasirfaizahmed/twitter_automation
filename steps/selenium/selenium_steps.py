from base.base_step import BaseStep
from steps.selenium.selenium_step import SeleniumClient


class OpenPage(SeleniumClient, BaseStep):

  def __init__(self, driver_path: str, **kwargs):
    super().__init__(driver_path, **kwargs)

  def Do(self):
    pass

  def CheckCondition(self):
    return True


if __name__ == '__main__':
  OpenPage(driver_path="/home/xd/Documents/drivers/chromedriver_linux64/chromedriver")
