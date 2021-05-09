#!/bin/bash
# Tell apt-get we're never going to be able to give manual feedback:
export DEBIAN_FRONTEND=noninteractive

#Speeds up building of PyNaCl wheel (halves container build time)
export LIBSODIUM_MAKE_ARGS=-j

#Installing required packages
apt-get update
apt-get -y upgrade
apt-get -y install libffi-dev libnacl-dev libpq-dev ffmpeg tesseract-ocr python3-pip #--no-install-recommends

# installing pip packages
python3 -m pip install --upgrade pip
python3 -m pip install -r ./requirements.txt --no-cache-dir

# Delete cached files we don't need anymore:
apt-get clean
rm -rf /var/lib/apt/lists/*


#python3 -m pip install -r ./requirements.txt --no-cache-dir --prefix ~/pip/
