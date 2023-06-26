# flake8: noqa
import json
import os
from attributedict.collections import AttributeDict

from selenium.webdriver.common.by import By
from patterns.patterns import Singleton


class BotMetadata(metaclass=Singleton):
  def __init__(self):
    __file_path = os.environ['METADATA']
    __file = open(__file_path)
    self.__data = json.load(__file)

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
  EMAIL_DOMAIN = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"check-email-availability-email-domain-input\"]"}
  GENDER_OPT = {'by': By.XPATH, 'value': "/html/body/onereg-app/div/onereg-form/div/div/form/section/section[3]/onereg-progress-meter/onereg-personal-info/fieldset/div/div/onereg-radio-wrapper[2]/pos-input-radio/label/i"}
  FIRSTNAME_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"first-name-input\"]"}
  lASTNAME_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"last-name-input\"]"}
  COUNTRY_DROPDOWN = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"country-input\"]"}
  MONTH_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"month\"]"}
  DAY_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"day\"]"}
  YEAR_FIELD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"year\"]"}
  CHOOSE_PASSWORD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"choose-password-input\"]"}
  CONFIRM_PASSWORD = {'by': By.CSS_SELECTOR, 'value': "*[data-test=\"choose-password-confirm-input\"]"}


  # css=*[data-test="check-email-availability-email-domain-input"]
  # <i class="pos-input-radio__border"><span class="pos-input-radio__checker"></span></i>

