"""
Setup config
"""

import logging

from common.jsonhelper import getJson, saveJson

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
            _config_cache = getJson("./config/config.json")
        except IOError as e:
            if e.errno == 2:
                logging.warning("The config.json file is missing, creating a new one")

                exampleConf = {'discordToken':'fdjkakjdfefehsabh93,.3mejnfe', 'commandPrefix':'?', 'ownerIds':[] , 'ytdlFormatOptions': {'format': 'bestaudio/best','outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s', 'restrictfilenames': True, 'noplaylist': True, 'nocheckcertificate': True, 'ignoreerrors': False, 'logtostderr': False, 'quiet': True, 'no_warnings': True, 'default_search': 'auto', 'source_address': '0.0.0.0',"HighWaterMark":3145728}, "ffmpeg_options":"-vn","ffmpeg_before_options":"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"}
                saveJson(exampleConf, "./config/config.json")

                logging.critical("Fill the required fields in the config.json file and run the script again")
            
            quit()

    return _config_cache