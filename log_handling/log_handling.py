import logging
from logging import Handler
from logging import handlers
import time
from datetime import date

from patterns.patterns import Singleton

levels = [50, 40, 30, 20, 10, 0]
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0

handlers_ = [logging.StreamHandler,
             logging.FileHandler,
             handlers.SocketHandler]


class InitilizeLogger(Singleton):

  def __call__(self):
    return self.logger

  def __init__(self, handler: Handler, level: int = logging.DEBUG):
    super().__init__()
    # basic setup
    self.logger = logging.getLogger(name="TA")
    level = level if level in levels else logging.DEBUG
    self.logger.setLevel(level=level)

    _current_time = time.strftime("%H-%M-%S", time.localtime())
    _current_date = date.today().strftime("%B-%d-%Y")

    # file_handler setup
    self.file_handler = handler('_LOGs/{}_{}.log'.format(_current_date, _current_time))
    self.file_handler.setLevel(level=level)
    self.file_handler.setFormatter(self._formatter())

    # stdout_handler setup
    self.std_handler = logging.StreamHandler()
    self.std_handler.setLevel(level=level)
    self.std_handler.setFormatter(self._formatter())

    # add handler to logger
    self.logger.addHandler(self.file_handler)
    self.logger.addHandler(self.std_handler)

  def _formatter(self):
    return logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == "__main__":
  logger = InitilizeLogger(handler=logging.FileHandler, level=10)()
  logger.warning("this is a test warning")