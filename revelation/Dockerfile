FROM python:3.6-alpine
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN pip install --upgrade -q \
pip \
bigquery-python \
requests \
redis \
Celery \
Jinja2 \
gspread \
sendgrid

# set by kubernetes
# ENV REDIS_PD_SERVICE_HOST localhost
# ENV REDIS_PD_SERVICE_PORT 6379
# ENV RABBITMQ_SERVICE_HOST localhost
# ENV RABBITMQ_SERVICE_PORT  5672

RUN mkdir /oceanus/
COPY app /oceanus/app
WORKDIR /oceanus/app

CMD ["python3", "revelation.py"]
