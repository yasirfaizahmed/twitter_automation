# flake8: noqa
import json
import os
from json import JSONDecodeError
from attributedict.collections import AttributeDict
from pathlib import Path as pp

from selenium.webdriver.common.by import By
from patterns.patterns import Singleton


class BotMetadata(metaclass=Singleton):
  def __init__(self):
    try:
      here = pp(__file__)
      __default_metadata_path = str(pp(here.parent.parent, "bot_metadata.json"))
      __file_path = os.getenv('METADATA', __default_metadata_path)
      __file = open(__file_path)
      self.__data = json.load(__file)
    except JSONDecodeError:
      print("ERROR- Either the bot_metadata.json file is empty or the data-format is inconsistant")

  # TODO: need to obsfcate the data
  @property
  def data(self) -> AttributeDict:
    return AttributeDict(self.__data)


class SeleniumConfigs():

  EMAIL_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'}
  LOGIN_BUTTON1 = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div'}
  LOGIN_BUTTON2 = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div/span/span'}
  PASSWORD_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'}
  USERNAME_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input'}
  NEXT_BUTTON = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/span/span'}

  LIKE_ICON = {'by': By.XPATH, 'value': '//div[@data-testid="like"]'}
  RETWEET_ICON1 = {'by': By.CSS_SELECTOR, 'value': '.css-18t94o4[data-testid ="retweet"]'}
  RETWEET_ICON2 = {'by': By.XPATH, 'value': "//*[contains(text(), 'Retweet')]"}

  TWEET_FIELD = {'by': By.XPATH, 'value': '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div'}


class ReportingIconWorkflow():
  workflow = ['profile_burger_h', 'report_flag', 'start_report_button', 'someone_else_option', 'next_button',
              'attacked_coz_of_identity_option', 'next_button', 'wishing_harm_coz_of_identity_option', 'next_button',
              'religion_option', 'next_button', 'tweets_option', 'next_button', 'yes_continue_button', 'submit_button', 
              'done_button']


class MailConfigs():
  SIGN_UP = {'by': By.CSS_SELECTOR, 'value': "#signup-button > span"}
  EMAIL_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"check-email-availability-email-input\"]"}
  GENDER_OPT = {'by': By.CSS_SELECTOR, 'value': ".ng-touched:nth-child(2) .pos-input-radio__checker"}
  FIRSTNAME_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"first-name-input\"]"}
  lASTNAME_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"last-name-input\"]"}
  COUNTRY_DROPDOWN = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"country-input\"]"}