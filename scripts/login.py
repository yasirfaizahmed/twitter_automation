import time

from base.base_script import BaseScript
from scripts.scripts_config import Login
from steps.selenium import selenium_steps, selenium_step


class Login(BaseScript, Login):

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

    self.driver.find_element(**Login.EMAIL_FIELD).send_keys(Login.EMAIL_KEY)
    self.driver.find_element(**Login.LOGIN_BUTTON1).click()
    time.sleep(2)

    if self._CheckExistsByXpath(Login.PASSWORD_FIELD):
      self.driver.find_element(**Login.PASSWORD_FIELD).send_keys(Login.PASSWORD_KEY)
      self.driver.find_element(**Login.LOGIN_BUTTON2).click()
      return

    elif self._CheckExistsByXpath(Login.USERNAME_FIELD):
      self.driver.find_element(**Login.USERNAME_FIELD).send_keys(Login.USERNAME_KEY)
      self.driver.find_element(**Login.NEXT_BUTTON).click()
      time.sleep(2)
      if self._CheckExistsByXpath(Login.PASSWORD_FIELD):
        self.driver.find_element(**Login.PASSWORD_FIELD).send_keys(Login.PASSWORD_KEY)
        self.driver.find_element(**Login.LOGIN_BUTTON2).click()

    time.sleep(5)

  def Teardown(self):
    self.driver.close()
    time.sleep(5)


if __name__ == '__main__':
  for _ in range(5):
    Login()()
    print("Login {} done".format(_))
