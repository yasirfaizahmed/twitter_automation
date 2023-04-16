__author__ = "yasir faiz ahmed"
__authors__ = ["yasir faiz ahmed"]
__contact__ = "yasirfaizahmed.n@gmail.com"
__copyright__ = "Copyright 2022 TwitterAutomation"
__credits__ = ["yasir"]
__date__ = "28/12/2022"
__deprecated__ = False
__email__ = "yasirfaizahmed.n@gmail.com"
__license__ = ""
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.0.1"


from base.base_step import BaseStep
from steps.Selenium.selenium_step import Mail_Step
# from selenium.webdriver.common.by import By
# from steps.selenium import selenium_steps
from scripts.scripts_config import BotMetadata
from steps.mail.mail_pyautogui import mail_creation_script

import random
import invoke
import time


MAX_RANDOM_SUFFIX = 256


class MakeMailAccounts(Mail_Step, BaseStep):
  def __init__(self, suggested_names: list = ['stephenhawking', 'alberteinstein'], account_number: int = 5):
    # Selenium_Step.__init__(self)
    Mail_Step.__init__(self)
    self._bmd = BotMetadata()
    # self.selenium_client.maximize_window()
    self.account_number = account_number
    self.suggested_names = suggested_names * (account_number // len(suggested_names))
    self.__present_mails = self.__get_mails_from_bmd()

  def __get_mails_from_bmd(self):
    return [self._bmd.data.get(bot, None).get('EMAIL_KEY', None) for bot in self._bmd.data]

  def __generate_mails(self):
    mails = []
    for name in self.suggested_names:
      suffix = str(random.randint(1, MAX_RANDOM_SUFFIX))
      mail = "{}{}@post.com".format(name[0] + name[1], suffix)
      while mail in self.__present_mails:
        mail = "{}{}@post.com".format(name[0] + name[1], suffix)
      mails.append({'mail': mail, 'first': name[0], 'last': name[1]})

    return mails

  def Do(self):
    __mails = self.__generate_mails()
    # selenium_steps.OpenPage(url="https://www.mail.com/")()

    invoke.run("google-chrome https://www.mail.com/")

    time.sleep(10)
    for _mail in __mails:
      mail_creation_script(first=_mail['first'], last=_mail['last'], mail=_mail['mail'].split('@')[0])

  def CheckCondition(self):
    return True


MakeMailAccounts(suggested_names=[("rakesh", "indian"), ("rakesh", "rss")])()
