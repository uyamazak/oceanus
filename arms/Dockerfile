FROM python:3.6-alpine
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

# set by kubernetes
# ENV REDIS_PD_SERVICE_HOST localhost
# ENV REDIS_PD_SERVICE_PORT 6379
# ENV GOPUB_SERVICE_HOST localhost
# ENV GOPUB_SERVICE_PORT 8765

RUN mkdir /oceanus/
COPY app /oceanus/app/
WORKDIR /oceanus/app/

EXPOSE 80
EXPOSE 443

CMD ["gunicorn", "-c", "gunicorn_conf.py", "arms:app"]
