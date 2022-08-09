FROM python:3.7.13-slim-buster
WORKDIR /api
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get -y install libpq-dev gcc
RUN pip3 install -r requirements.txt
COPY ./api/. .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
