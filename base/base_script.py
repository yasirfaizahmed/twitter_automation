from log_handling.log_handling import InitilizeLogger
import logging

logger = InitilizeLogger(handler=logging.FileHandler, level=10)


class BaseScript():

  def __call__(self):
    self.Setup()
    self.Run()
    self.Teardown()

  def Setup(self):
    self.logger = logger
    self.logger.warning("If you are seeing this then you have not overwritten BaseScript.Setup()")

  def Run(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseScript.Run()")

  def Teardown(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseScript.Teardown()")
