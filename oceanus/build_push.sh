#!/bin/zsh
sudo docker images | grep oceanus-web | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-web:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-web:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/oceanus

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-web:$tag

echo "tag: $tag complete"
echo "please edit, to deploy"
echo "kc edit deployment oceanus"
