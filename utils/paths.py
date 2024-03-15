from pathlib import Path as pp


__here = pp(__file__)

TA = __here.parent.parent

APIS = pp(TA, "APIs")
BASE = pp(TA, "base")
CONFIG = pp(TA, "config")
DATA_HANDLER = pp(TA, "data_handler")
PATTERNS = pp(TA, "patterns")
TEMPLATE_IMAGES = pp(TA, "template_images")
OTHERS = pp(TA, "others")
UTILS = pp(TA, "utils")
LOGS = pp(TA, "_LOGs")
USER_DATA = pp(TA, "_USER_DATA")
