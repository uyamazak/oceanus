#!/bin/zsh
sudo docker images | grep r2bq | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-r2bq:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-r2bq:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/r2bq

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-r2bq:$tag

echo "tag: $tag complete"
echo "please edit, to deploy"
echo "sudo kubectl edit deployment oceanus-r2bq"
