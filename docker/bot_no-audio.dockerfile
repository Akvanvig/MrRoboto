ARG ARCH=
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto


RUN apt-get update -y \
&& apt-get upgrade -y \
&& apt-get install libffi-dev libnacl-dev libpq-dev -y \
&& apt-get install ffmpeg -y \
&& apt-get install python3-pip -y

WORKDIR /MrRoboto
COPY /bot/cogs ./bot/cogs
COPY /bot/common ./bot/common
COPY /bot/client.py ./bot/client.py
COPY /bot/requirements.txt ./requirements.txt

RUN python3 -m pip install -r /MrRoboto/requirements.txt

CMD python3 /MrRoboto/client.py

# docker build --no-cache -t mrroboto:arm64v8 -f .\bot_no-audio.Dockerfile . --build-arg ARCH=arm64v8
