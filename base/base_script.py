import logging


class BaseScript():

  def __call__(self):
    self.Setup()
    self.Run()
    self.Teardown()

  def Setup(self):
    logging.warning("If you are seeing this then you have not overwritten BaseScript.Setup()")

  def Run(self):
    logging.warning("If you are seeing this then you have not overwritten BaseScript.Run()")

  def Teardown(self):
    logging.warning("If you are seeing this then you have not overwritten BaseScript.Teardown()")
