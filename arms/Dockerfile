#FROM ubuntu:16.04
FROM python:3.5-alpine
MAINTAINER yu_yamazaki@bizocean.co.jp

#RUN apk add --force --update python python-dev gfortran py-pip build-base
RUN apk add --force --update build-base

#RUN apt-get update && apt-get -y upgrade
#RUN apt-get install -y \
#python3.5 \
#python3-pip\
#&& apt-get clean

RUN pip3 install --upgrade -q \
cython \
falcon \
gunicorn \
bigquery-python \
google-api-python-client \
cerberus \
redis \
user-agents

ENV REDISMASTER_SERVICE_HOST localhost
ENV REDISMASTER_SERVICE_PORT 6379

ENV OCEANUS_ARMS_HOST https://o.bizocean.jp
ENV LOG_LEVEL WARNING

ENV WEB_CONCURRENCY 2

ENV REDIS_DELAY_LIMIT_RATE 2

RUN mkdir /oceanus/
COPY app /oceanus/app/
WORKDIR /oceanus/app/

EXPOSE 80
EXPOSE 443

CMD ["gunicorn", "-c", "gunicorn_conf.py", "arms:app"]
