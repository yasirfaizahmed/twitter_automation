from base.base_step import BaseStep
from steps.selenium.selenium_step import SeleniumClient


class OpenPage(SeleniumClient, BaseStep):

  def __init__(self, url: str, **kwargs):
    super().__init__(**kwargs)
    self.url = url

  def Do(self) -> None:
    self.driver.get(self.url)

  def CheckCondition(self) -> bool:
    return True


if __name__ == '__main__':
  OpenPage(url="https://twitter.com/i/flow/login")()
