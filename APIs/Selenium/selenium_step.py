from APIs.Selenium.stepsconfig import SeleniumClientConf
from patterns.patterns import Singleton
from config.scripts_config import SeleniumConfigs, MailConfigs
from selenium.webdriver.chrome.service import Service


from log_handling.log_handling import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pathlib
# import os
# import tempfile

OPTIONS = Options()
OPTIONS.add_argument("--no-sandbox")
# OPTIONS.add_argument('--headless')
OPTIONS.add_argument("--disable-dev-shm-usage")
OPTIONS.add_argument("--force-device-scale-factor=1")
OPTIONS.add_argument("--disable-infobars")
OPTIONS.add_argument("--start-minimized")
# user_data_dir = os.getenv('user_data_dir', '')
# tempdir = tempfile.mkdtemp()
# if user_data_dir == '':
#   user_data_dir = tempdir
# OPTIONS.add_argument("--user-data-dir={}".format(user_data_dir))
# OPTIONS.add_argument("--profile-directory=Default")


class SeleniumClient(SeleniumClientConf, metaclass=Singleton):
	def __init__(self, driver_path: str = None, **kwargs):
		driver_path = self.DRIVER_PATH if driver_path is None else driver_path
		if pathlib.Path(self.DRIVER_PATH).exists() and self.DRIVER_PATH != "":
			service = Service(executable_path=self.DRIVER_PATH)
			self.driver = webdriver.Chrome(service=service, options=OPTIONS)
			self.driver.find_element
		else:
			logger.error(
				"env variable DRIER_PATH is not set, point it to the chrome driver executable"
			)
			exit(-1)
		self._kwargs = kwargs


class Selenium_Step:
	# All interactive related API classes must inherite from Selenium_Step
	def __init__(self, **kwargs):
		# if kwargs.get("exclude_args", None) is not None:
		# for argument in kwargs.get('exclude_args'):
		#   pass
		self.selenium_client = SeleniumClient(**kwargs).driver
		self.config = SeleniumConfigs()

	def _CheckExistsByXpath(self, element):  # custom step method
		try:
			self.selenium_client.find_element(**element)
		except Exception:
			return False
		return True


class Mail_Step:
	def __init__(self):
		self.config = MailConfigs()


if __name__ == "__main__":
	a = SeleniumClient().driver
