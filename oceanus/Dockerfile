FROM ubuntu:16.04
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y \
zsh \
python3.5 \
python3-pip\
&& apt-get clean

RUN pip3 install --upgrade -q \
cython \
falcon \
gunicorn \
bigquery-python \
google-api-python-client \
Benchmarker \
cerberus \
redis

ENV REDISMASTER_SERVICE_HOST localhost
ENV REDISMASTER_SERVICE_PORT 6379
ENV REDISLIST oceanus_prod

ENV OCEANUS_SWALLOW_HOST https://oceanus.bizocean.co.jp
ENV LOG_LEVEL DEBUG

RUN mkdir /var/www

WORKDIR /var/www

COPY www /var/www

CMD gunicorn -c gunicorn_conf.py oceanus:app

EXPOSE 80
EXPOSE 443
