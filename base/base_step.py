class base_step(object):
  def __call__(self):
    self.do()
    result = self.check_condition()
    print("API PASSED") if result else print("API FAILED")



  def do(self):
    pass

  def check_condition(self):
    pass