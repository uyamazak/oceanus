#!/bin/zsh
sudo docker run -d \
    -p 6379:6379 \
    -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/redis-pd/data:/data \
    asia.gcr.io/oceanus-dev/redis-pd:latest
