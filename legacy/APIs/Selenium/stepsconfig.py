import os
from pathlib import Path as pp


class SeleniumClientConf:
	DRIVER_PATH = os.getenv(
		"DRIVER_PATH",
		str(pp(pp(__file__).parent.parent.parent, "chrome-driver/chromedriver")),
	)
