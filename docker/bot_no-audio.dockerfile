ARG ARCH=
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto


RUN apt-get update -y \
&& apt-get upgrade -y \
&& apt-get install -y libffi-dev libnacl-dev libpq-dev \
&& apt-get install -y ffmpeg \
&& apt-get install -y python3-pip

WORKDIR /MrRoboto/bot
COPY /bot/cogs ./cogs
COPY /bot/common ./common
COPY /bot/client.py ./client.py
COPY /bot/requirements.txt ./requirements.txt

RUN python3 -m pip install -r /MrRoboto/bot/requirements.txt

CMD python3 /MrRoboto/bot/client.py

# docker build --no-cache -t mrroboto:arm64v8 -f .\bot_no-audio.Dockerfile . --build-arg ARCH=arm64v8
