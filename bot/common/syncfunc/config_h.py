"""
Setup config
"""

import logging

from common.syncfunc.json_h import *

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s: %(levelname)s: %(message)s"
)

_config_cache = None

# Set force_read to True to read from disk
def get(*, force_read = False):
    global _config_cache

    if force_read or _config_cache == None:
        try:
            _config_cache = getJson("./config/bot.json")
        except IOError as e:
            if e.errno == 2: logging.warning("The bot.json file is missing")
            quit()

    return _config_cache