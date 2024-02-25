import random as ran

from config.scripts_config import BotMetadata


def GetBotMetadata(botname: str = 'bot1', random: bool = False):
  __bmd = BotMetadata()
  if random is False:
    # if re.search(r'\d+$', botname).group().isdigit():  # validating the botname
    if botname in __bmd.data.keys():
      return __bmd.data.get(botname, __bmd.data.get('bot1', None))  # if botname is not found, return bot1 metadata
    else:
      return __bmd.data.get('bot1')
  else:
    return ran.choice(list(__bmd.data.values()))


def GetBotsCount():
  __bmd = BotMetadata()
  return len(__bmd.data)
