#!/bin/zsh
sudo docker images | grep revelation | head -6
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-revelation:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-revelation:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/revelation

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-revelation:$tag


echo "tag: $tag complete"
echo "please edit, to deploy"
echo "kc edit deployment oceanus-revelation"

#sudo kubectl edit deployment oceanus-revelation
