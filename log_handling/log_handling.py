import logging
from logging import Handler
from logging import handlers
import time

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


class InitilizeLogger():

  def __init__(self, handler: Handler, level: int = logging.DEBUG):
    # basic setup
    self.logger = logging.getLogger(name="TA")
    level = level if level in levels else logging.DEBUG
    self.logger.setLevel(level=level)

    _current_time = time.strftime("%H-%M-%S", time.localtime())

    # handler setup
    self.handler = handler('{}.log'.format(_current_time))
    self.handler.setLevel(level=level)
    self.handler.setFormatter(self._formatter())

    # add handler to logger
    self.logger.addHandler(self.handler)

  def _formatter(self):
    return logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  def __call__(self):
    return self.logger


if __name__ == "__main__":
  logger = InitilizeLogger(handler=logging.FileHandler, level=10)()
  logger.warning("this is a test warning")
