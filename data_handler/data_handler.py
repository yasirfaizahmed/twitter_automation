import json
import os
from json import JSONDecodeError
from attributedict.collections import AttributeDict
from pathlib import Path as pp
import random as ran
from datetime import date
import time

from patterns.patterns import Singleton
from log_handling.log_handling import logger
from utils import paths


class BotMetadata(metaclass=Singleton):
  def __init__(self):
    try:
      here = pp(__file__)
      __default_metadata_path = str(pp(here.parent.parent, "bot_metadata.json"))
      __file_path = os.getenv('METADATA', __default_metadata_path)
      __file = open(__file_path)
      self.__data = json.load(__file)
    except JSONDecodeError:
      logger.error("ERROR- Either the bot_metadata.json file is empty or the data-format is inconsistant")
      exit(-1)

  # TODO: need to obsfcate the data
  @property
  def data(self) -> AttributeDict:
    return AttributeDict(self.__data)

  def GetBotMetadata(self, botname: str = 'bot1', random: bool = False) -> dict:
    if random is False:
      # if re.search(r'\d+$', botname).group().isdigit():  # validating the botname
      if botname in self.data.keys():
        return self.data.get(botname, self.data.get('default_bot', None))  # if botname is not found, return bot1 metadata
      else:
        return self.data.get('default_bot')
    else:
      return ran.choice(list(self.data.values()))

  def GetBotsCount(self) -> int:
    return len(self.data)


def create_data_file(format='json') -> pp:
  if paths.USER_DATA.exists() is False:
    logger.info("_USER_DATA dir was not found in workspace, creating it..")
    paths.USER_DATA.mkdir()
  _current_time = time.strftime("%H-%M-%S", time.localtime())
  _current_date = date.today().strftime("%B-%d-%Y")
  data_file = "{}/{}_{}.{}".format(paths.USER_DATA, _current_date, _current_time, format)
  return pp(data_file)
