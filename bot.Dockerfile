ARG ARCH=
FROM ${ARCH}/python:3.8-buster

RUN apt update -y \
&& apt upgrade -y \
&& apt install libffi-dev libnacl-dev libpq-dev -y \
&& apt install ffmpeg -y \
&& apt install python3-pip -y

RUN python3 -m pip install discord.py[voice] youtube-dl aiopg sqlalchemy psycopg2

WORKDIR /Discord-bot-py
COPY /bot .

#RUN pipenv install
#RUN pipenv run bot
CMD python3 /Discord-bot-py/client.py

# docker build --no-cache -t test-discord:arm64v8 -f .\dockerfile . --build-arg ARCH=arm64v8
