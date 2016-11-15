#!/bin/zsh
sudo docker run -it  \
	-v /home/BIZOCEAN/yu_yamazaki/project-oceanus/table-manager/app:/oceanus/app  \
    -e DATA_SET=oceanus_test \
    -e LOG_LEVEL=DEBUG \
    asia.gcr.io/oceanus-dev/table-manager:latest
