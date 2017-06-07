FROM python:3.6-alpine
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN pip3 install --upgrade -q \
bigquery-python \
google-api-python-client \
timeout-decorator \
redis

# set by kubernetes
# ENV REDIS_PD_SERVICE_HOST localhost
# ENV REDIS_PD_SERVICE_PORT 6379

RUN mkdir /oceanus/
COPY app /oceanus/app
WORKDIR /oceanus/app/

CMD ["python3","redis2bq.py"]
