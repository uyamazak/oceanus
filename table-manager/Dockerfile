FROM python:3.5-alpine
#FROM ubuntu:16.04
MAINTAINER yu_yamazaki@bizocean.co.jp

#RUN apk add --force --update build-base
#RUN apt-get update && apt-get -y upgrade
#RUN apt-get install -y \
#lsof \
#python3.5 \
#python3-pip \
#&& apt-get autoclean \
#&& apt-get autoremove

RUN pip3 install --upgrade -q \
#cython \
bigquery-python \
google-api-python-client

ENV PROJECT_ID oceanus-dev
ENV GOOGLE_APPLICATION_CREDENTIALS /var/www/Oceanus-dev-784c5c9ec4b7.json
ENV PUBSUB_TOPIC projects/oceanus-dev/topics/oceanus-test

ENV DATA_SET oceanus_prod
ENV JSON_KEY_FILE Oceanus-dev-784c5c9ec4b7.json
ENV BQ_TABLE_PREFIX oceanus_v3_


RUN mkdir /var/www

COPY www /var/www

WORKDIR /var/www

CMD ["python3.5","table-manager.py"]
