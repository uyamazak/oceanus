#!/bin/zsh
sudo docker run -it \
        -p 8080:80 \
        -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/arms/app:/oceanus/app \
        -e OCEANUS_ARMS_HOST=http://192.168.2.70:8080 \
        -e REDISMASTER_SERVICE_HOST=192.168.2.70 \
        -e LOG_LEVEL=DEBUG \
        asia.gcr.io/oceanus-dev/arms:latest
