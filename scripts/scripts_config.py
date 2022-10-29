# flake8: noqa
from selenium.webdriver.common.by import By

class Configs():
  EMAIL_KEY = "stephenhawking@post.com"
  USERNAME_KEY = "stephen35763420"
  PASSWORD_KEY = "stephenhawking@123"

  EMAIL_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'}
  LOGIN_BUTTON1 = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div'}
  LOGIN_BUTTON2 = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div/span/span'}
  PASSWORD_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'}
  USERNAME_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input'}
  NEXT_BUTTON = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/span/span'}

  LIKE_ICON = {'by': By.XPATH, 'value': '//div[@data-testid="like"]'}
  RETWEET_ICON1 = {'by': By.CSS_SELECTOR, 'value': '.css-18t94o4[data-testid ="retweet"]'}
  RETWEET_ICON2 = {'by': By.XPATH, 'value': "//*[contains(text(), 'Retweet')]"}
  