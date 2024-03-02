import json
import os
from json import JSONDecodeError
from attributedict.collections import AttributeDict
from pathlib import Path as pp
import random as ran

from patterns.patterns import Singleton
from log_handling.log_handling import logger


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
