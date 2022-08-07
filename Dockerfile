# syntax=docker/dockerfile:1
FROM python:3.7.13-slim-buster
WORKDIR /bot
COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN pip3 install -r requirements.txt
COPY ./bot/. .
CMD ["python3", "-u", "bot.py"]
