FROM python:3.5-alpine
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN apk add --force --update build-base

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
ENV SWALLOW_DEFAULT_SITE_NAME bizocean

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
