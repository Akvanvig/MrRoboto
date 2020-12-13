# Tell apt-get we're never going to be able to give manual feedback:
export DEBIAN_FRONTEND=noninteractive

#Installing required packages
apt-get update -y
apt-get upgrade -y
apt-get install libffi-dev libnacl-dev libpq-dev ffmpeg python3-pip -y --no-install-recommend

# installing pip packages
python3 -m pip install -r requirements.txt
