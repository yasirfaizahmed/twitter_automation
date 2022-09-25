from selenium import webdriver
from selenium.webdriver.common.by import By

def check_exists_by_xpath(driver, xpath):
  try:
    driver.find_element(By.XPATH, xpath)
  except Exception:
    return False
  return True

# Github credentials
email = "naveenkumar@mail.com"
username = "naveen kumar"
password = "naveenkumar3@123"

if __name__ == '__main__':
  # initialize the Chrome driver
  driver = webdriver.Chrome("/home/xd/Documents/Python_codes/twitter_aut/chromedriver_linux64/chromedriver")

  # twitter.com
  driver.get("https://twitter.com/i/flow/login")
  # email
  driver.find_element("name", "text").send_keys(email)
  # click login button
  driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div').click()

  # if password asked
  if check_exists_by_xpath(driver, '//*[@id="react-root"]/div/div/div/main/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[3]/div/label/div/div[2]/div[1]/input'):
    driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div/main/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[3]/div/label/div/div[2]/div[1]/input').send_keys(password)
  # if username asked
  elif check_exists_by_xpath(driver, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input'):
    driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input').send_keys(username)
  # next
  driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/span/span').click()
  print("asdf")