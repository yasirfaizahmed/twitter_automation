import time
import os
import pandas as pd
import random

from base.base_step import BaseStep
from APIs.Selenium.selenium_step import Selenium_Step
from selenium.webdriver.support.ui import Select
from APIs.Selenium.selenium_steps import OpenPage
from config.scripts_config import MailConfigs


class CreateMainAccounts(Selenium_Step, BaseStep):
  """
  A dirty way to create accounts in mail.com, usage of this as an exploit is not suggested
  and might come outside legal restrictions. and I'm not responsible for how you
  will use this API as and this is totally for educational or for fun purpose.

  dependencies:
    install chrome extension 'Buster:Caption helper' along with its local app bins by
    visiting the official page of the extension.
  """

  def __init__(self, number: int = 1, **kwargs):
    super().__init__(**kwargs)
    self.number = number
    self.names_dataset_path = os.environ['NAMESDATASETFILEPATH']

  def _generate_mail_id(self):
    df = pd.read_csv(self.names_dataset_path)
    i = 0
    while df.loc[i, 'used?'] == 'yes':
      i += 1

    name: str = df.loc[i, 'name']
    mail = name.replace(' ', '_')
    mail += str(random.randint(1, 50000))
    # adding a used value to this sample in dataset
    df.loc[i, 'used?'] = 'yes'
    df.to_csv(self.names_dataset_path, header=True, index=False)
    return name.split(' '), mail, i

  def _select_dropdown(self, element, visible_text: str):
    select = Select(self.selenium_client.find_element(**element))
    i = 0
    while i < 2:
      try:
        select.select_by_visible_text(visible_text)
        i += 1
      except Exception:
        self.logger.warning("reselecting email domain as @post.com")
      time.sleep(0.2)
    return True

  def Do(self) -> None:
    OpenPage(url='https://mail.com')()
    time.sleep(8)

    self.selenium_client.find_element(**MailConfigs.SIGN_UP).click()
    time.sleep(4)
    name, mail, index = self._generate_mail_id()
    self.selenium_client.find_element(**MailConfigs.EMAIL_FIELD).send_keys(mail)
    time.sleep(1)

    self._select_dropdown(element=MailConfigs.EMAIL_DOMAIN, visible_text="@post.com")
    time.sleep(1)

    self.selenium_client.find_element(**MailConfigs.GENDER_OPT).click()
    time.sleep(1)

    self.selenium_client.find_element(**MailConfigs.FIRSTNAME_FIELD).send_keys(name[0])
    time.sleep(1)
    self.selenium_client.find_element(**MailConfigs.lASTNAME_FIELD).send_keys(name[0])
    time.sleep(1)

    self._select_dropdown(element=MailConfigs.COUNTRY_DROPDOWN, visible_text="India")
    time.sleep(1)

    month = day = 4
    year = 2000
    self.selenium_client.find_element(**MailConfigs.MONTH_FIELD).send_keys(month)
    time.sleep(1)
    self.selenium_client.find_element(**MailConfigs.DAY_FIELD).send_keys(day)
    time.sleep(1)
    self.selenium_client.find_element(**MailConfigs.YEAR_FIELD).send_keys(year)
    time.sleep(1)

    password = "Password@123"
    self.selenium_client.find_element(**MailConfigs.CHOOSE_PASSWORD).send_keys(password)
    time.sleep(1)
    self.selenium_client.find_element(**MailConfigs.CONFIRM_PASSWORD).send_keys(password)
    time.sleep(1)



CreateMainAccounts(number=1)()