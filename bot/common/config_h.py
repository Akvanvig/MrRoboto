from .json_h import get_json
from os.path import dirname, abspath, join

#
# PRIVATE INTERFACE
#

def _read_from_disk():
    try:
        dir_ = abspath(join(__file__ , "../../.."))
        
        print("Reading config from: "+dir_)

        # Read
        bot_config = get_json(join(dir_, "config/bot_config.json"))
        bot_secrets = get_json(join(dir_, "config/bot_secrets.json"))

        # Merge
        return {**bot_config, **bot_secrets}
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