# flake8: noqa
from selenium.webdriver.common.by import By

class Login():
  EMAIL_KEY = "naveenkumar@mail.com"
  USERNAME_KEY = "naveen kumar"
  PASSWORD_KEY = "naveenkumar3@123"

  EMAIL_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'}
  LOGIN_BUTTON = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div'}
  PASSWORD_FIELD = {'by': By.XPATH, 'value': '//*[@id="react-root"]/div/div/div/main/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[3]/div/label/div/div[2]/div[1]/input'}
  USERNAME_FIELD = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input'}
  NEXT_BUTTON = {'by': By.XPATH, 'value': '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/span/span'}
