FROM python:3.5-alpine
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN pip3 install --upgrade -q \
google-api-python-client \
redis \
pyslack \
requests \
gspread \
oauth2client

ENV REDISMASTER_SERVICE_HOST localhost
ENV REDISMASTER_SERVICE_PORT 6379
ENV LOG_LEVEL WARNING

ENV SLACK_API_TOKEN xoxp-26111211698-36585627747-66573775025-5435c23de5
ENV SLACK_CHANNEL C1Z3FFMPS
ENV SLACK_BOT_NAME oceanus_bot

ENV JSON_KEY_FILE keys/Oceanus-dev-ce1631fa9cd6.json
ENV SPREAD_SHEET_KEY 13e1g80hoJkLSOyvLX_JNoRS8LxC1hL9GL4FptKz-Ovk

RUN mkdir /oceanus/
COPY app /oceanus/app
WORKDIR /oceanus/app/

CMD ["python3.5","revelation.py"]
