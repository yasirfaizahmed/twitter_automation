import cv2
from pathlib import Path
from steps.CV.cv_step import CV_Step
import os


class GetIconCoordinates(CV_Step):
  def __init__(self, icon_name: str, threshold: float = 0.8, **kwargs):
    super().__init__(**kwargs)
    if Path(self.__getattribute__(icon_name)).exists():
      self.template_path = self.__getattribute__(icon_name)
    self.threshold = threshold

  def _get_icon_center(self, rect: tuple):
    return (rect[0][0] + (rect[1][0] - rect[0][0]) // 2, rect[0][1] + (rect[1][1] - rect[0][1]) // 2)

  def Do(self):
    template = cv2.imread(self.template_path)

    current_screen = self.take_screen_shot()
    if current_screen:
      test = cv2.imread(current_screen)
    else:
      self.logger.error("Error occured while taking screenshot")
      self.response.ok = False
      return self.response.ok

    # template matching
    res = cv2.matchTemplate(test, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= self.threshold:
      # gettting top-left, bottom-right corners
      top_left = max_loc
      bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

      self.response.data = {
          'rectangle': (top_left, bottom_right),
          'center': self._get_icon_center((top_left, bottom_right))}
      self.response.ok = True

      if self.debug_mode:
        cv2.rectangle(test, pt1=top_left, pt2=bottom_right, color=(255, 0, 0), thickness=4)
        cv2.imwrite(os.path.join(self.temp_dir, 'result.png'), test)
        self.logger.debug("Result image saved at {}".format(os.path.join(self.temp_dir, 'result.png')))

    else:
      self.logger.error("Could not find the template icon on the current screen")

  def CheckCondition(self):
    return True if self.response.ok else False
