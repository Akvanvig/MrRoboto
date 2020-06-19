"""
Retrieves the latest ffmpeg package.
"""

import platform
import os

from urllib.request import urlopen, Request
from urllib.error import URLError
from io import BytesIO

try:
    # Need this to check which file extraction method we should use
    system_name = platform.system()

    # Pretend we are a user
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

    print("Attempting to download newest version of ffmpeg. This can take some time")

    if system_name == "Windows":
        from zipfile import ZipFile

        url = "https://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-latest-win32-static.zip"
        content = urlopen(Request(url = url, headers = headers)).read()
        print("Succeeded, now unzipping the zip archive")

        with ZipFile(BytesIO(content), mode = 'r') as zipObj:
            for zip_info in zipObj.infolist():
                if zip_info.filename[-1] == '/':
                    continue
                
                basename = os.path.basename(zip_info.filename)

                if not basename == "ffmpeg.exe":
                    continue
                
                zip_info.filename = basename
                zipObj.extract(zip_info)
                break

    elif system_name == "Linux":
        import tarfile

        url = "https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz"
        content = urlopen(Request(url = url, headers = headers)).read()
        print("Succeeded, now unzipping the tar archive")

        with tarfile.open(fileobj = BytesIO(content), mode='r:xz' ) as tarObj:
            for tar_info in tarObj.getmembers():
                if tar_info.name[-1] == '/':
                    continue
                
                basename = os.path.basename(tar_info.name)

                if not basename == "ffmpeg":
                    continue
                
                tar_info.name = basename
                tarObj.extract(tar_info)
                break

    else:
        print("Error, you are not on a supported system")
        
except URLError:
    print("Error, couldn't successfully download ffmpeg")
else:
    print("Succeeded, ffmpeg extracted")