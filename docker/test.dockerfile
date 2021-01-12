ARG ARCH=arm64v8

FROM busybox as builder
#FROM ${ARCH}/python:3.8-slim-buster as builder
WORKDIR /MrRoboto/
COPY bot/cogs ./bot/cogs
COPY bot/common ./bot/common
COPY bot/client.py ./bot/client.py
COPY bot/requirements.txt ./bot/requirements.txt
COPY docker/install-packages.sh ./bot/install-packages.sh

#RUN python3 -m pip install --upgrade pip \
#&& python3 -m pip install -r bot/requirements.txt \
#&& mv /root/.local .local


ARG ARCH=arm64v8
FROM ${ARCH}/python:3.8-slim-buster
LABEL org.opencontainers.image.source https://github.com/Akvanvig/MrRoboto

WORKDIR /MrRoboto/bot
COPY --from=builder /MrRoboto/bot /MrRoboto/bot
RUN /bin/bash ./install-packages.sh

#ENV PATH=/MrRoboto/bot/.local/bin:$PATH
CMD python3 /MrRoboto/bot/client.py

# docker build --no-cache -t ghcr.io/akvanvig/mrroboto_test:latest -f ./docker/test.dockerfile . --build-arg ARCH=arm64v8
