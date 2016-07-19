#!/bin/zsh
sudo docker images | grep swallow | head -5
sudo docker images | grep redis2bq | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build -t asia.gcr.io/oceanus-dev/oceanus-swallow:$tag /home/BIZOCEAN/yu_yamazaki/project-oceanus/oceanus
sudo docker build -t asia.gcr.io/oceanus-dev/oceanus-redis2bq:$tag /home/BIZOCEAN/yu_yamazaki/project-oceanus/redis2bq

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-swallow:$tag
sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-redis2bq:$tag

echo "tag: $tag complete"
