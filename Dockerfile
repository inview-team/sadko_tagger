FROM python:3.10-slim-buster

RUN pip3 install --upgrade pip
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 git -y

WORKDIR /app/src
COPY . /app

RUN pip3 install -r /app/requirements.txt

CMD python3 main.py
