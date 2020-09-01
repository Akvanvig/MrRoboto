from .json_h import get_json
from os.path import dirname, join

#
# PRIVATE INTERFACE
#

def _read_from_disk():
    try:
        _dir = dirname(__file__)
           
        # Read
        bot_json = get_json(join(_dir, "../config/bot.json"))
        secrets_json = get_json(join(_dir, "../config/secrets.json"))

        # Merge
        return {**bot_json, **secrets_json}
    except IOError as e:
        if e.errno == 2: 
            print("Config files are missing")
        quit()

_config_cache = _read_from_disk()

#
# PUBLIC INTERFACE
#

def get(*, from_disk = False):
    global _config_cache

    if from_disk:
        _config_cache = _read_from_disk()
        
    return _config_cache 