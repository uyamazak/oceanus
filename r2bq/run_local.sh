#!/bin/zsh
sudo docker run -d -it \
        -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/r2bq/www:/var/www \
        -e DATA_SET=oceanus_test \
        -e REDISMASTER_SERVICE_HOST=ml30gen9 \
        -e REDISLIST=oceanus_test \
        -e LOG_LEVEL=DEBUG \
        asia.gcr.io/oceanus-dev/r2bq:latest
