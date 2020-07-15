FROM python:latest

RUN apt update && \
    apt install libffi-dev && \
    apt install libnacl-dev && \
    apt install libpq-dev && \
    apt install python3-dev && \
    apt install ffmpeg

RUN pip install pipenv

COPY bot . 
WORKDIR /bot

RUN pipenv install
RUN pipenv run bot