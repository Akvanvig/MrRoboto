from .json_h import *

_config_cache = None

# Set force_read to True to read from disk
def get(*, force_read = False):
    global _config_cache

    if force_read or _config_cache == None:
        try:
            # Read and merge
            bot_json = getJson("./config/bot.json")
            secrets_json = getJson("./config/secrets.json")

            _config_cache = {**bot_json, **secrets_json}
        except IOError as e:
            if e.errno == 2: print("Config files are missing")
            quit()

    return _config_cache