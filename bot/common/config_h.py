from .json_h import get_json
from os.path import dirname, abspath, join

#
# GLOBAL
#

CONFIG_PATH = abspath(join(__file__ , "../../../config"))

#
# PRIVATE
#

def _read_from_disk():
    try:
        # Read
        bot_config = get_json(join(CONFIG_PATH, "bot_config.json"))
        bot_secrets = get_json(join(CONFIG_PATH, "bot_secrets.json"))

        # Merge
        return {**bot_config, **bot_secrets}
    except IOError as e:
        if e.errno == 2: 
            print("Config files are missing")
        quit()

_config_cache = _read_from_disk()

#
# PUBLIC
#

def get(*, from_disk = False):
    global _config_cache

    if from_disk:
        _config_cache = _read_from_disk()
        
    return _config_cache 