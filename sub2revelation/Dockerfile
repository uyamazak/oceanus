FROM ubuntu:16.04
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y \
python3.5 \
python3-pip\
&& apt-get clean

RUN pip3 install --upgrade -q \
cython \
google-api-python-client \
redis \
python-daemon \
pyslack \
requests

ENV REDISMASTER_SERVICE_HOST localhost
ENV REDISMASTER_SERVICE_PORT 6379
ENV LOG_LEVEL DEBUG

ENV SLACK_API_TOKEN xoxp-26111211698-36585627747-66573775025-5435c23de5
ENV SLACK_CHANNEL #oceanus-bot
ENV SLACK_BOT_NAME oceanus_bot

RUN mkdir /var/www

WORKDIR /var/www

COPY www /var/www

CMD ["python3.5","revelation.py"]
