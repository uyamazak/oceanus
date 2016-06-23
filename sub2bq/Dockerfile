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
Benchmarker

ENV PROJECT_ID oceanus-dev
ENV GOOGLE_APPLICATION_CREDENTIALS /var/www/Oceanus-dev-784c5c9ec4b7.json
ENV PUBSUB_TOPIC projects/oceanus-dev/topics/oceanus-test

RUN mkdir /var/www

WORKDIR /var/www

COPY www /var/www

#CMD gunicorn -b :80 --reload --log-level debug oceanus:app
#CMD gunicorn -c gunicorn_conf.py oceanus:app
CMD python3.5 sub2bq.py

