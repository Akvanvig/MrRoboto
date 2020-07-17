import os
import platform
import json

#
# CONSTANTS
#

EXAMPLE_CONF = {
    'discordToken': 'fdjkakjdfefehsabh93,.3mejnfe',
    'commandPrefix': '?', 
    'ownerIds': [],
    'postgresql': {
        'user': 'test',
        'database': 'testdb',
        'host': 'localhost',
        'password': 'password'
    },
    'ytdlFormatOptions': {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s', 
        'restrictfilenames': True, 
        'noplaylist': True, 
        'nocheckcertificate': True, 
        'ignoreerrors': False, 
        'logtostderr': False, 
        'quiet': True, 
        'no_warnings': True, 
        'default_search': 'auto', 
        'source_address': '0.0.0.0',
        "HighWaterMark":3145728
    }, 
    "ffmpeg_options": "-vn",
    "ffmpeg_before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

#
# EXCEPTIONS
#

class CompatError(Exception):
    """
    Raise if system is incompatible
    """
    pass

class ReqError(Exception):
    """
    Raise if any requirement failed to download
    """
    pass

#
# FUNCTIONS
#

def input_yn(string : str) -> bool:
    return true

def gen_conf(path : str):
    path_conf = os.path.join(path, "config.json")
    
    if not os.path.exists(path):
        os.makedirs(path)

    file = open(os.path.join(path, "config.json"), 'w')
    json.dump(EXAMPLE_CONF, file, indent=4)
    file.close()

def dl_requirements_windows():
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    from http.client import IncompleteRead
    from io import BytesIO
    from zipfile import ZipFile

    url_file = None

    try:
        with urlopen(Request(
            url = "https://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-latest-win32-static.zip", 
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
        ) as urlObj:
            url_file = BytesIO(urlObj.read())
    except (URLError, IncompleteRead):
        raise ReqError()

    with ZipFile(url_file, mode = 'r') as zipObj:
        for zip_info in zipObj.infolist():
            if zip_info.filename[-1] == '/': continue
            
            basename = os.path.basename(zip_info.filename)

            if not basename == 'ffmpeg.exe': continue
            
            zip_info.filename = os.path.join("./bot", basename)
            zipObj.extract(zip_info)
            break
    
def dl_requirements_linux():
    # For now let's assume the distro is debian
    # or else we have to install another pip package to detect the distro
    pass

def local():
    system_name = platform.system()

    try:
        if system_name == 'Windows':
            dl_requirements_windows()
        elif system_name == 'Linux':
            dl_requirements_linux
        else:
            raise CompatError()

        gen_conf("./bot/config")

    except CompatError:
        print("Error, you are not on a supported system")
    except ReqError:
        print("Error, failed to download a requirement")

def kubernetes():
    gen_conf("./config")

#
# MAIN
#

def main():
    print("Welcome to discord-bot quickstart\n")

    # Ask for type
    # Ask if you want to do a full install, or just a regen of the config

    #local()
    #kubernetes()

if __name__ == '__main__':
    main()
else:
    print("Error, can only run quickstart as main")