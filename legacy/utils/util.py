import warnings
import random as ran

from config.scripts_config import BotMetadata


def GetBotMetadata(botname: str = "bot1", random: bool = False):
	warnings.warn(
		"This method is legacy, and is Depricated, new version is in data_handler.data_handler.BotMetadata",
		DeprecationWarning,
		stacklevel=2,
	)
	__bmd = BotMetadata()
	if random is False:
		# if re.search(r'\d+$', botname).group().isdigit():  # validating the botname
		if botname in __bmd.data.keys():
			return __bmd.data.get(
				botname, __bmd.data.get("default_bot", None)
			)  # if botname is not found, return bot1 metadata
		else:
			return __bmd.data.get("default_bot")
	else:
		return ran.choice(list(__bmd.data.values()))


def GetBotsCount():
	warnings.warn(
		"This method is legacy, and is Depricated, new version is in data_handler.data_handler.BotMetadata",
		DeprecationWarning,
		stacklevel=2,
	)
	__bmd = BotMetadata()
	return len(__bmd.data)
