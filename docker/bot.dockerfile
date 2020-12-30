ARG ARCH=
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto


RUN apt-get update -y \
&& apt-get upgrade -y \
&& apt-get install libffi-dev libnacl-dev libpq-dev -y \
&& apt-get install ffmpeg -y \
&& apt-get install python3-pip -y

WORKDIR /MrRoboto
COPY /bot ./bot/

RUN python3 -m pip install -r /MrRoboto/requirements.txt

CMD python3 /Discord-bot-py/client.py

# docker build --no-cache -t ghcr.io/akvanvig/mrroboto_no-audio:arm64v8 -t ghcr.io/akvanvig/mrroboto_no-audio:latest -f ./docker/bot_no-audio.dockerfile . --build-arg ARCH=arm64v8
