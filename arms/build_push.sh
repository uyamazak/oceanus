#!/bin/zsh
sudo docker images | grep arms | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/arms:$tag \
        -t asia.gcr.io/oceanus-dev/arms:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/arms

sudo gcloud docker push asia.gcr.io/oceanus-dev/arms:$tag

echo "tag: $tag complete"
echo "please edit, to deploy"
echo "kc edit deployment oceanus"
