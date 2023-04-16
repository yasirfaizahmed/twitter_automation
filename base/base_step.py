from log_handling.log_handling import InitilizeLogger
import logging

logger = InitilizeLogger(handler=logging.FileHandler, level=10)()


class response():
  def __init__(self):
    self.ok = False
    self.data = None


class BaseStep(object):

  def main(self):
    self.response = response()
    self.logger = logger

    self.Do()
    self.response.ok = self.CheckCondition()
    verdict = "PASSED" if self.response.ok is True else "FAILED"
    self.logger.info("{} {}".format(self.__class__, verdict))

  def __call__(self):
    self.main()
    return self.response

  def Do(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseStep.Do()")

  def CheckCondition(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseStep.CheckCondition()")
