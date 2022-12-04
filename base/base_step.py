from log_handling.log_handling import InitilizeLogger
import logging

logger = InitilizeLogger(handler=logging.FileHandler, level=10)()


class BaseStep(object):

  def main(self):
    self.response = False
    self.logger = logger

    self.Do()
    self.response = self.CheckCondition()
    verdict = "PASSED" if self.response is True else "FAILED"
    self.logger.info("{} {}".format(self.__class__, verdict))

  def __call__(self):
    self.main()

  def Do(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseStep.Do()")

  def CheckCondition(self):
    self.logger.warning("If you are seeing this then you have not overwritten BaseStep.CheckCondition()")
