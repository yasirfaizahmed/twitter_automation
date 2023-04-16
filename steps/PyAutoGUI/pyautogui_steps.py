from steps.PyAutoGUI.pyautogui_step import PyAutoGUI_Step
import pyautogui as P
import time


class Click(PyAutoGUI_Step):
  def __init__(self, x, y, **kwargs):
    super().__init__(**kwargs)
    self.coordinates = (x, y)

  def Do(self):
    P.moveTo(*self.coordinates)
    P.click()
    self.logger.info("Clicked  ({}, {})".format(*self.coordinates))

    P.moveTo(*self.initial_coordinates)
    self.response.ok = True

    time.sleep(3)

  def CheckCondition(self):
    return self.response.ok


class Write(PyAutoGUI_Step):
  def __init__(self, string: str, **kwargs):
    super().__init__(**kwargs)
    self.string = string

  def Do(self):
    P.write(self.string)
    self.response.ok = True
    self.logger.info("Wrote string {}".format(self.string))

    time.sleep(2)

  def CheckCondition(self):
    return self.response.ok
