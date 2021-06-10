#!/bin/bash
# Tell apt-get we're never going to be able to give manual feedback:
export DEBIAN_FRONTEND=noninteractive

#Installing required packages
apt-get update
apt-get -y upgrade
apt-get -y install libffi-dev libnacl-dev libpq-dev ffmpeg tesseract-ocr tesseract-ocr-nor tesseract-ocr-jpn tesseract-ocr-ara tesseract-ocr-kor # --no-install-recommends

# Delete cached files we don't need anymore:
apt-get clean
rm -rf /var/lib/apt/lists/*


#python3 -m pip install -r ./requirements.txt --no-cache-dir --prefix ~/pip/
