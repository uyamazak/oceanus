#!/bin/zsh
sudo docker run -d -it \
        -p 8080:80 \
        -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/arms/www:/var/www \
        -e OCEANUS_SWALLOW_HOST=http://ml30gen9:8080 \
        -e REDISMASTER_SERVICE_HOST=ml30gen9 \
        -e LOG_LEVEL=DEBUG asia.gcr.io/oceanus-dev/arms:latest
