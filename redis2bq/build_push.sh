#!/bin/zsh
sudo docker images | grep redis2bq | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-redis2bq:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-redis2bq:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/redis2bq

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-redis2bq:$tag


echo "tag: $tag complete"
echo "please edit, to deploy"
sudo kubectl edit deployment oceanus-redis2bq
