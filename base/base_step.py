class BaseStep(object):

  def __call__(self):
    self.do()
    result = self.check_condition()
    print("API PASSED") if result else print("API FAILED")

  def Do(self):
    pass

  def CheckCondition(self):
    pass
