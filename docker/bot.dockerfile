ARG ARCH=arm64v8

FROM busybox as builder
#FROM ${ARCH}/python:3.8-slim-buster as builder
WORKDIR /MrRoboto/
COPY bot/cogs ./bot/cogs
COPY bot/common ./bot/common
COPY bot/client.py ./bot/client.py
COPY bot/requirements.txt ./bot/requirements.txt
COPY docker/install-packages.sh ./bot/install-packages.sh

ARG ARCH=arm64v8
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto

WORKDIR /MrRoboto/bot
COPY --from=builder /MrRoboto/bot /MrRoboto/bot
RUN /bin/bash ./install-packages.sh

CMD python3 /MrRoboto/bot/client.py

# run from repo root folder
# docker build --no-cache -t ghcr.io/akvanvig/mrroboto_no-audio:arm64v8 -t ghcr.io/akvanvig/mrroboto_no-audio:latest -f .\docker\bot.dockerfile . --build-arg ARCH=arm64v8
