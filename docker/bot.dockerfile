ARG ARCH=
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto


RUN apt-get update -y \
&& apt-get upgrade -y \
&& apt-get install libffi-dev libnacl-dev libpq-dev -y \
&& apt-get install ffmpeg -y \
&& apt-get install python3-pip -y

WORKDIR /MrRoboto
COPY /bot .

RUN python3 -m pip install -r /MrRoboto/requirements.txt

CMD python3 /Discord-bot-py/client.py

# docker build --no-cache -t test-discord:arm64v8 -f .\bot.Dockerfile . --build-arg ARCH=arm64v8
