#!/usr/bin/python3

import os
import sys
import platform
import json
import subprocess

# TODO(Fredrico): Add error messages to ReqError and CompatError exceptions

#
# CONSTANTS
#

FILE_DIR = os.path.dirname(__file__)

APT_PACKAGES = [
    'libffi-dev', 
    'libnacl-dev', 
    'libpq-dev', 
    'python3-pip', 
    'ffmpeg'
]

EXAMPLE_SECRETS = {
    'discordToken': 'fdjkakjdfefehsabh93,.3mejnfe',
    'ownerIds': [],
    'postgresql': {
        'user': 'test',
        'database': 'testdb',
        'host': 'localhost',
        'password': 'password'
    }
}

EXAMPLE_CONFIG = {
    'commandPrefix': '?', 
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
    while True:
        answer = input(string + " [y/n]:    ").lower()
        if answer in ('y', 'yes'): return True
        elif answer in ('n', 'no'): return False
        else: print("Error, enter a valid input")

def install_requirements_pip():
    try:
        print("...Attempting to install pip requirements")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(FILE_DIR, "bot/requirements.txt")])
        print("...Success, installed pip requirements")
    except subprocess.CalledProcessError:
        raise ReqError()

def install_requirements_windows():
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    from http.client import IncompleteRead
    from io import BytesIO
    from zipfile import ZipFile

    url_file = None

    # Download and install ffmpeg

    try:
        print("...Attempting to download ffmpeg")
        with urlopen(Request(
            url = "https://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-latest-win32-static.zip", 
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
        ) as urlObj:
            url_file = BytesIO(urlObj.read())
        print("...Success, downloaded ffmpeg")
    except (URLError, IncompleteRead):
        raise ReqError()

    with ZipFile(url_file, mode = 'r') as zipObj:
        print("...Extracting ffmpeg from archive")
        for zip_info in zipObj.infolist():
            if zip_info.filename[-1] == '/': continue
            
            basename = os.path.basename(zip_info.filename)

            if not basename == 'ffmpeg.exe': continue
            
            zip_info.filename = os.path.join("bot", basename)
            zipObj.extract(zip_info)
            break
        print("...Success, extracted ffmpeg.exe from archive")
    
def install_requirements_linux():
    # For now let's assume the distro is debian
    # or else we have to install another pip package to detect the distro

    # Download and install apt packages
    try:
        print("...Attempting to download dev dependencies")
        subprocess.check_call(['sudo', 'apt', 'install'] + APT_PACKAGES + ['-y'], stdout=sys.stdout, stderr=sys.stderr)
        print("...Success, dev dependencies downloaded")
    except subprocess.CalledProcessError:
        raise ReqError()

def install_requirements(*, local : bool):  
    print("\n[INSTALLING REQUIREMENTS]")

    # Local
    if local:
        system_name = platform.system()

        try:
            # System specific install requirements
            if system_name == 'Windows': install_requirements_windows()
            elif system_name == 'Linux': install_requirements_linux()
            else: raise CompatError()

            # Download and install pip requirements
            install_requirements_pip()
        except CompatError:
            print("...Error, you are not on a supported system")
        except ReqError:
            print("...Error, failed to download a requirement")
    # Kubernetes
    else:
        pass

    print("[FINISHED INSTALLATION]")

def generate_configs_at(path : str):    
    if not os.path.exists(path):
        os.makedirs(path)

    print("...Attempting to generate secrets.json file in {}.".format(path))
    file = open(os.path.join(path, "secrets.json"), 'w')
    json.dump(EXAMPLE_SECRETS, file, indent=4)
    file.close()
    print("...Success, file generated")
    
    print("...Attempting to generate bot.json file in {}.".format(path))
    file = open(os.path.join(path, "bot.json"), 'w')
    json.dump(EXAMPLE_CONFIG, file, indent=4)
    file.close()
    print("...Success, file generated")

def generate_configs(*, local : bool):
    print("\n[GENERATING CONFIGS]")
    
    # Local
    if local:
        generate_configs_at(os.path.join(FILE_DIR, "bot/config/"))
    # Kubernetes
    else:
        generate_configs_at(os.path.join(FILE_DIR,"config/"))

    print("[FINISHED GENERATING CONFIGS]")

#
# MAIN
#

def main():
    print("Welcome to discord-bot quickstart\n")

    # Ask for type
    # Ask if user wants to install requirements
    # Ask if user wants to generate example configs
    use_local = input_yn("Input: \n (Y)es if you are using the bot locally\n (N)o if you are using kubernetes\n")
    print('')

    if input_yn("Is this your first time running quickstart on this machine?"):
        install_reqs = gen_configs = True
    else:
        install_reqs = input_yn("Do you want to install all the requirements?")
        gen_configs = input_yn("Do you want to generate example config files?")

    if install_reqs: install_requirements(local = use_local)
    if gen_configs: generate_configs(local = use_local)

    print("\nQuickstart finished running")

if __name__ == '__main__':
    main()
else:
    print("Error, can only run quickstart as main")