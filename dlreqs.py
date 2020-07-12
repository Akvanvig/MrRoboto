#!/usr/bin/python3
"""
Retrieves the latest ffmpeg package.
"""

import platform
import os

from urllib.request import urlopen, Request
from urllib.error import URLError
from http.client import IncompleteRead
from io import BytesIO

class CompatError(Exception):
    """
    Raise if system is incompatible
    """
    pass

def download(url, headers):
    with urlopen(Request(url = url, headers = headers)) as urlObj:
        try:
            return BytesIO(urlObj.read())
        except IncompleteRead:
            raise URLError()
try:
    # Need this to check which file extraction method we should use
    system_name = platform.system()
    system_machine = platform.machine().lower()

    # Pretend we are a user
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36', 'Connection': 'Keep-Alive'}

    print("Attempting to download newest version of ffmpeg. This can take some time")

    if system_name == 'Windows':
        from zipfile import ZipFile

        if not system_machine == 'amd64': raise CompatError()

        content = download("https://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-latest-win32-static.zip", headers)
        
        print("Succeeded, now unzipping the zip archive")

        with ZipFile(content, mode = 'r') as zipObj:
            for zip_info in zipObj.infolist():
                if zip_info.filename[-1] == '/': continue
                
                basename = os.path.basename(zip_info.filename)

                if not basename == 'ffmpeg.exe': continue
                
                zip_info.filename = basename
                zipObj.extract(zip_info)
                break

    elif system_name == 'Linux':
        import tarfile

        content = None
        
        if system_machine == 'x86_64': content = download("https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz", headers)
        elif system_machine == 'aarch64': content = download("https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-arm64-static.tar.xz", headers)
        else: raise CompatError()

        print("Succeeded, now unzipping the tar archive")

        with tarfile.open(fileobj = content, mode='r:xz' ) as tarObj:
            for tar_info in tarObj.getmembers():
                if tar_info.name[-1] == '/': continue
                
                basename = os.path.basename(tar_info.name)

                if not basename == 'ffmpeg': continue
                
                tar_info.name = basename
                tarObj.extract(tar_info)
                break

    else: raise CompatError()

except CompatError as e:
    print("Error, you are not on a supported system")
except URLError:
    print("Error, couldn't successfully download ffmpeg")
else:
    print("Succeeded, ffmpeg extracted")
