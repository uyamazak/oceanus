#!/bin/zsh
sudo docker run -dit\
        -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/revelation/app:/oceanus/app \
        -e DATA_SET=oceanus_test \
        -e REDISMASTER_SERVICE_HOST=192.168.2.70 \
        -e REDISLIST=oceanus_test \
        -e LOG_LEVEL=DEBUG \
        -e SPREAD_SHEET_KEY=1n6Yq9JbKFs5PmVi90ebrxaq6tRUQOo2f1BXGWjMoYdY \
        asia.gcr.io/oceanus-dev/revelation:latest
