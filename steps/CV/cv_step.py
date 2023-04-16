import invoke
import tempfile
from datetime import datetime
from os.path import join
import traceback
import logging

from log_handling.log_handling import InitilizeLogger
from base.base_step import BaseStep
from steps.CV.cv_config import CVConfig


class CV_Step(BaseStep, CVConfig):
  def __init__(self, debug_mode: bool = False, **kwargs):
    super().__init__(**kwargs)
    self.logger = InitilizeLogger(handler=logging.FileHandler, level=10)()
    self.temp_dir = tempfile.mkdtemp()
    self.template_source_dir = 'template_images'
    self.debug_mode = debug_mode

  def take_screen_shot(self):
    # taking screenshot
    try:
      screenshot_file = datetime.now().strftime('%Y-%m-%d_%H:%M:%S.png')
      result = invoke.run('scrot {} -e \'mv $f {}\''.format(screenshot_file, self.temp_dir))
      if result.ok:
        self.logger.info("Taking screenshot, saving at {}".format(join(self.temp_dir, screenshot_file)))
        return join(self.temp_dir, screenshot_file)
    except Exception:
      # TODO
      self.logger.error("Exception occured while taking screenshot")
      self.logger.error(traceback.format_exc())
