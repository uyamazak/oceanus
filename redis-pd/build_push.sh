#!/bin/zsh
sudo docker images | grep redis-pd | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/redis-pd:$tag \
        -t asia.gcr.io/oceanus-dev/redis-pd:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/redis-pd

sudo gcloud docker push asia.gcr.io/oceanus-dev/redis-pd:$tag

echo "tag: $tag complete"
echo "please edit, to deploy"
echo "kc edit deployment oceanus"
