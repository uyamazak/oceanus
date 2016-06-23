FROM ubuntu:16.04
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y \
python3.5 \
python3-pip\
&& apt-get clean

RUN pip3 install --upgrade -q \
cython \
bigquery-python \
google-api-python-client \
redis \
python-daemon

ENV PROJECT_ID oceanus-dev
ENV GOOGLE_APPLICATION_CREDENTIALS /var/www/Oceanus-dev-784c5c9ec4b7.json
ENV PUBSUB_TOPIC projects/oceanus-dev/topics/oceanus-test

ENV DATA_SET oceanus_prod
ENV JSON_KEY_FILE Oceanus-dev-784c5c9ec4b7.json
ENV SESSION_KEY oceanus_sid
ENV TABLE_PREFIX oceanus_v1

ENV REDISMASTER_SERVICE_HOST localhost
ENV REDISMASTER_SERVICE_PORT 6379
ENV REDISLIST oceanus_prod
ENV CHUNK_NUM 50
ENV LOG_LEVEL DEBUG

RUN mkdir /var/www

WORKDIR /var/www

COPY www /var/www

CMD python3.5 redis2bq.py
