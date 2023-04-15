import time

from base.base_script import BaseScript
from scripts.scripts_config import Configs as Config
from steps.Selenium import selenium_steps, selenium_step


class Login(BaseScript, Config):

  def _CheckExistsByXpath(self, element):
    try:
      self.driver.find_element(**element)
    except Exception:
      return False
    return True

  def Setup(self):
    self.driver = selenium_step.Selenium_Step(need_new_client=True).selenium_client

  def Run(self):
    selenium_steps.OpenPage(url="https://twitter.com/i/flow/login")()
    time.sleep(8)

    self.driver.find_element(**Config.EMAIL_FIELD).send_keys(Config.EMAIL_KEY)
    self.driver.find_element(**Config.LOGIN_BUTTON1).click()
    time.sleep(2)

    if self._CheckExistsByXpath(Config.PASSWORD_FIELD):
      self.driver.find_element(**Config.PASSWORD_FIELD).send_keys(Config.PASSWORD_KEY)
      self.driver.find_element(**Config.LOGIN_BUTTON2).click()
      return

    elif self._CheckExistsByXpath(Config.USERNAME_FIELD):
      self.driver.find_element(**Config.USERNAME_FIELD).send_keys(Config.USERNAME_KEY)
      self.driver.find_element(**Config.NEXT_BUTTON).click()
      time.sleep(2)
      if self._CheckExistsByXpath(Config.PASSWORD_FIELD):
        self.driver.find_element(**Config.PASSWORD_FIELD).send_keys(Config.PASSWORD_KEY)
        self.driver.find_element(**Config.LOGIN_BUTTON2).click()

    time.sleep(5)

  def Teardown(self):
    self.driver.close()
    time.sleep(5)


if __name__ == '__main__':
  Login()()
  # Like()()
