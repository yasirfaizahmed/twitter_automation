import os


class SeleniumClientConf():
  DRIVER_PATH = os.getenv('DRIVER_PATH', '/home/xd/Documents/drivers/chromedriver')
