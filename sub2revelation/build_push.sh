#!/bin/zsh
sudo docker images | grep sub2revelation | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-sub2revelation:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-sub2revelation:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/sub2revelation

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-sub2revelation:$tag


echo "tag: $tag complete"
echo "please edit, to deploy"
echo "kc edit deployment oceanus-sub2revelation"
