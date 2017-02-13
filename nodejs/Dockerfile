FROM node:7.5.0
RUN apt-get update; apt-get install -y vim && \
  npm update && \
  npm install redis && \
  npm install opts && \
  npm install websocket

RUN mkdir /oceanus/
COPY app /oceanus/app/
WORKDIR /oceanus/app/

ENV PORT 9998

EXPOSE 9998
