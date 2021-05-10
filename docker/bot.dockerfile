# Base image
ARG ARCH=arm64v8
FROM ${ARCH}/python:3.9-slim-buster as base


#Fetching package files
FROM busybox as builder
WORKDIR /MrRoboto/
COPY bot/cogs ./bot/cogs
COPY bot/common ./bot/common
COPY bot/client.py ./bot/client.py
COPY bot/db.py ./bot/db.py
COPY bot/requirements.txt ./bot/requirements.txt
COPY docker/install-packages.sh ./bot/install-packages.sh

# Building pip packages
FROM base as pip-builder
ENV LIBSODIUM_MAKE_ARGS=-j
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /MrRoboto/
COPY bot/requirements.txt ./requirements.txt
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip libpq-dev
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r ./requirements.txt --no-cache-dir --target="/MrRoboto/dependencies"

# Main image
FROM base
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto
ENV PYTHONPATH=/MrRoboto/dependencies

WORKDIR /MrRoboto/bot
COPY --from=builder /MrRoboto/bot /MrRoboto/bot
RUN /bin/bash ./install-packages.sh
COPY --from=pip-builder /MrRoboto/dependencies /MrRoboto/dependencies

CMD python3 /MrRoboto/bot/client.py

# run from repo root folder
# docker build --no-cache -t ghcr.io/akvanvig/mrroboto_no-audio:arm64v8 -t ghcr.io/akvanvig/mrroboto_no-audio:latest -f .\docker\bot.dockerfile . --build-arg ARCH=arm64v8
