from .json_h import get_json
from os.path import dirname, join

#
# PRIVATE INTERFACE
#

_FILE_DIR = dirname(__file__)

_config_cache = None

#
# PUBLIC INTERFACE
#

# TODO(Fredrico): Separate into different functions

# Set force_read to True to read from disk
def get(*, force_read = False):
    global _config_cache

    if force_read or _config_cache == None:
        try:
            # Read and merge
            bot_json = get_json(join(_FILE_DIR, "../config/bot.json"))
            secrets_json = get_json(join(_FILE_DIR, "../config/secrets.json"))

            _config_cache = {**bot_json, **secrets_json}
        except IOError as e:
            if e.errno == 2: print("Config files are missing")
            quit()

    return _config_cache