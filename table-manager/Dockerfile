FROM python:3.6-alpine
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN pip3 install -q \
bigquery-python \
objgraph \
google-api-python-client

RUN mkdir /oceanus/
COPY app /oceanus/app

WORKDIR /oceanus/app/

CMD ["python3","table-manager.py"]
