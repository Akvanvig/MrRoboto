#!/usr/bin/python3

import os
import sys
import platform
import json
import subprocess

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

EXAMPLE_BOT_CONFIG = {
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
        'agelimit': 20,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        "HighWaterMark":3145728
    },
    "ffmpeg_options": "-vn",
    "ffmpeg_before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

EXAMPLE_BOT_SECRETS = {
    'discordToken': 'fdjkakjdfefehsabh93,.3mejnfe',
    'ownerIds': [],
    'postgresql': {
        'user': 'postgres',
        'database': 'postgres',
        'host': 'localhost',
        'password': 'password'
    },
    "hereApiToken": "<A Rest API Key from developer.here.com>",
    "apiUserAgentIdentification": "roboto/v0.1 <contact email>"
}

KUBE_BOT_CONFIG = {
    'apiVersion': 'v1',
    'kind': 'ConfigMap',
    'metadata': {
        'name': 'robotobot-config',
        'namespace': 'roboto'
    },
    'data': {
        'bot_config.json' : json.dumps(EXAMPLE_BOT_CONFIG)
    }
}

KUBE_BOT_SECRETS = {
    'apiVersion': 'v1',
    'kind': 'Secret',
    'type': 'Opaque',
    'metadata': {
        'name': 'robotobot-secrets',
        'namespace': 'roboto'
    },
    'data': {
        'bot_secrets.json': json.dumps(EXAMPLE_BOT_SECRETS)
    }
}

KUBE_DB_SECRETS = {
    'apiVersion': 'v1',
    'kind': 'Secret',
    'type': 'Opaque',
    'metadata': {
        'name': 'robotodb-secrets',
        'namespace': 'roboto',
        'labels': {
            'app': 'roboto-postgres'
        }
    },
    'data': {
        'POSTGRES_PASSWORD': 'password'
    }
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
        raise ReqError("...Error, failed to download/install pip requirements")

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
        raise ReqError("...Error, failed to download ffmpeg")

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
        raise ReqError("...Error, failed to download dev dependencies")

def install_requirements(*, local : bool):
    print("\n[INSTALLING REQUIREMENTS]")

    try:
        # Local
        if local:
            system_name = platform.system()

            # System specific install requirements
            if system_name == 'Windows': install_requirements_windows()
            elif system_name == 'Linux': install_requirements_linux()
            else: raise CompatError("...Error, you are not on a supported system")

            # Download and install pip requirements
            install_requirements_pip()

        # Kubernetes
        else:
            pass

    except (CompatError, ReqError) as e:
        print(str(e))

    print("[FINISHED INSTALLING REQUIREMENTS]")

def create_file_at(file_obj, path : str, filename : str):
    print("...Attempting to generate {} file in {}.".format(filename, path))
    file = open(os.path.join(path, filename), 'w')
    json.dump(file_obj, file, indent=4)
    file.close()
    print("...Success, file generated")

def generate_configs(*, local : bool):
    print("\n[GENERATING CONFIGS]")

    try:
        path = os.path.join(FILE_DIR, "config/")

        if not os.path.exists(path): os.makedirs(path)

        if local:
            create_file_at(EXAMPLE_BOT_CONFIG, path, "bot_config.json")
            create_file_at(EXAMPLE_BOT_SECRETS, path, "bot_secrets.json")
        else:
            create_file_at(KUBE_BOT_CONFIG, path, "bot_config.json")
            create_file_at(KUBE_BOT_SECRETS, path, "bot_secrets.json")
            create_file_at(KUBE_DB_SECRETS, path, "db_secrets.json")

    except IOError as e:
        print("...Error, failed to generate configs")

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
