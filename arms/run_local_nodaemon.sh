#!/bin/zsh
sudo docker run -it \
        -p 8080:80 \
        -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/arms/app:/oceanus/app \
        -e OCEANUS_ARMS_HOST=http://192.168.2.70:8080 \
        -e REDIS_PD_SERVICE_HOST=192.168.2.70 \
        -e GOPUB_SERVICE_HOST=192.168.2.70 \
        -e GOPUB_TOPIC_NAME=ml30gen9testtopic \
        -e GOPUB_SUBSCRIPTION_NAME=ml30gen9testsub \
        -e LOG_LEVEL=ERROR \
        asia.gcr.io/oceanus-dev/arms:latest \
        gunicorn -c gunicorn_conf_debug.py arms:app
