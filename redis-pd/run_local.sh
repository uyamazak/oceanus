#!/bin/zsh
sudo docker run -d \
    -p 6379:6379 \
    asia.gcr.io/oceanus-dev/redis-pd:latest
