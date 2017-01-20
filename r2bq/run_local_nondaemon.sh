#!/bin/zsh
sudo docker run -it \
        -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/r2bq/app:/oceanus/app \
        -e DATA_SET=oceanus_test \
        -e REDIS_PD_SERVICE_HOST=192.168.2.70 \
        -e REDISLIST=oceanus_test \
        -e LOG_LEVEL=DEBUG \
        asia.gcr.io/oceanus-dev/r2bq:latest
