import time
import os
import pandas as pd

from base.base_step import BaseStep
from APIs.Selenium.selenium_step import Selenium_Step
from APIs.Selenium.selenium_steps import OpenPage
from config.scripts_config import MailConfigs


class CreateMainAccounts(Selenium_Step, BaseStep):
  """
  A dirty way to create accounts in mail.com, usage of this as an exploit is not suggested
  and might come outside legal restrictions. and I'm not responsible for how you
  will use this API as and this is totally for educational or for fun purpose.
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

    name = df.loc[i, 'name']
    # adding a used value to this sample in dataset
    df.loc[i, 'used?'] = 'yes'
    df.to_csv(self.names_dataset_path, header=True, index=False)
    return name, i

  def Do(self) -> None:
    OpenPage(url='https://mail.com')()
    time.sleep(8)

    self.selenium_client.find_element(**MailConfigs.SIGN_UP).click()
    time.sleep(4)
    name, index = self._generate_mail_id()
    self.selenium_client.find_element(**MailConfigs.EMAIL_FIELD).send_keys(name)


CreateMainAccounts(number=1)()
