ARG ARCH=
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto



WORKDIR /MrRoboto
COPY /bot/cogs ./cogs
COPY /bot/common ./common
COPY /bot/client.py ./client.py
COPY /bot/requirements.txt ./requirements.txt

RUN python3 -m pip install -r /MrRoboto/requirements.txt

CMD python3 /MrRoboto/client.py

# docker build --no-cache -t mrroboto:arm64v8 -f .\bot_no-audio.Dockerfile . --build-arg ARCH=arm64v8
