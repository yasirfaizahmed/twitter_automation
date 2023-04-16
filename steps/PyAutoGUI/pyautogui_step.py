from base.base_step import BaseStep
import pyautogui as P


class PyAutoGUI_Step(BaseStep):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.initial_coordinates = P.position()
