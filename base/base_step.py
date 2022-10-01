import logging


class BaseStep(object):

  def __call__(self):
    self.response = False
    self.Do()
    result = self.CheckCondition()
    print("API PASSED") if result else print("API FAILED")

  def Do(self):
    logging.warning("If you are seeing this then you have not overwritten BaseStep.Do()")

  def CheckCondition(self):
    logging.warning("If you are seeing this then you have not overwritten BaseStep.CheckCondition()")
