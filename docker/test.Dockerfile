FROM busybox as builder
WORKDIR MrRoboto
COPY /bot/cogs ./cogs
COPY /bot/common ./common
COPY /bot/client.py ./client.py
COPY /bot/requirements.txt ./requirements.txt


ARG ARCH=arm64v8
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto

WORKDIR /MrRoboto
COPY --from=builder /MrRoboto /MrRoboto


CMD python3 MrRobotoclient.py

# docker build --no-cache -t mrroboto:arm64v8 -f .\bot_no-audio.Dockerfile . --build-arg ARCH=arm64v8
