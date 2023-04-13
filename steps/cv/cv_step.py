import cv2
import invoke
import tempfile
from datetime import datetime
from os.path import join
import traceback

from log_handling.log_handling import InitilizeLogger
import logging


class CV_Step():
  def __init__(self):
    self.logger = InitilizeLogger(handler=logging.FileHandler, level=10)()
    self.temp_dir = tempfile.mkdtemp()
    self.template_source_dir = 'template_images'

  def take_screen_shot(self):
    # taking screenshot
    try:
      self.logger.info("cv testing 1")
      screenshot_file = datetime.now().strftime('%Y-%m-%d_%H:%M:%S.png')
      result = invoke.run('scrot {} -e \'mv $f {}\''.format(screenshot_file, self.temp_dir))
      if result.ok:
        return join(self.temp_dir, screenshot_file)
    except Exception:
      # TODO
      self.logger.error("Exception occured")
      self.logger.error(traceback.format_exc())

from base.base_step import BaseStep
class t(BaseStep):
  def Do(self):
    self.logger.info("bs testing 1")
  def CheckCondition(self):
    pass

CV_Step().take_screen_shot()

# def get_icon_coordinates(template_path: str):
#   try:
#     invoke.run('scrot test.png')

#   template = cv2.imread('start_tweet.png')

#   test = cv2.imread('test.png')

#   res = cv2.matchTemplate(test, template, cv2.TM_CCOEFF_NORMED)

#   min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#   top_left = max_loc
#   bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

#   cv2.rectangle(test, top_left, bottom_right, (0, 0, 255), 2)
#   cv2.imwrite('res.png',test)