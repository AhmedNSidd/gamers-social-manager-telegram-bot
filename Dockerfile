# syntax=docker/dockerfile:1
FROM python:3.7.13-slim-buster
WORKDIR /bot
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./bot/. .
EXPOSE 80
CMD ["python3", "-u", "bot.py"]
