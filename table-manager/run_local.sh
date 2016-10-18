#!/bin/zsh
sudo docker run -it -d \
	-v /home/BIZOCEAN/yu_yamazaki/project-oceanus/table-manager/www:/var/www  \
    -e DATA_SET=oceanus_test \
    -e LOG_LEVEL=DEBUG \
    asia.gcr.io/oceanus-dev/table-manager:latest
