FROM busybox as builder
WORKDIR /MrRoboto
COPY bot/cogs ./cogs
COPY bot/common ./common
COPY bot/client.py ./client.py
COPY bot/requirements.txt ./requirements.txt
COPY docker/install-packages.sh ./install-packages.sh


ARG ARCH=arm64v8
FROM ${ARCH}/python:3.8-slim-buster
# LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto

WORKDIR /MrRoboto/bot
COPY --from=builder /MrRoboto/bot /MrRoboto/bot
RUN ./install-packages.sh


CMD python3 MrRobotoclient.py

# docker build --no-cache -t ghcr.io/akvanvig/mrroboto_test:latest -f ./docker/test.dockerfile . --build-arg ARCH=arm64v8
