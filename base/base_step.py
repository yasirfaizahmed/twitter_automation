from log_handling.log_handling import InitilizeLogger
import logging

logger = InitilizeLogger(handler=logging.FileHandler, level=10)()


class BaseStep(object):

  def __call__(self):
    self.response = False
    self.logger = logger
    self.Do()
    result = self.CheckCondition()
    print("API PASSED") if result else print("API FAILED")

  def Do(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseStep.Do()")

  def CheckCondition(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseStep.CheckCondition()")
