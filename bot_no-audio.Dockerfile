ARG ARCH=
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/discord-bot-py_no-audio


RUN apt update -y \
&& apt upgrade -y \
&& apt install libffi-dev libnacl-dev libpq-dev -y \
&& apt install ffmpeg -y \
&& apt install python3-pip -y

WORKDIR /Discord-bot-py
COPY /bot/cogs ./cogs
COPY /bot/common ./common
COPY /bot/client.py ./client.py
COPY /bot/requirements.txt ./requirements.txt

RUN python3 -m pip install -r /Discord-bot-py/requirements.txt

CMD python3 /Discord-bot-py/client.py

# docker build --no-cache -t test-discord:arm64v8 -f .\bot_no-audio.Dockerfile . --build-arg ARCH=arm64v8
