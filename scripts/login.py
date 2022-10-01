import time
from selenium.webdriver.common.by import By

from base.base_script import BaseScript
from scripts.scripts_config import Login
from steps.selenium import selenium_step, selenium_steps

class Login(BaseScript, Login):

  def Setup(self):
    # self.driver = selenium_step.SeleniumClient().driver
    pass

  def Run(self):
    selenium_steps.OpenPage(url="https://twitter.com/i/flow/login")()

    time.sleep(4)

    selenium_steps.FindBy(**Login.EMAIL_FIELD)()

  def Teardown(self):
    pass


Login()()
