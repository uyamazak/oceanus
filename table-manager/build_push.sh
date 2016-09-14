#!/bin/zsh
sudo docker images | grep oceanus-table-manager | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-table-manager:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-table-manager:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/table-manager

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-table-manager:$tag


echo "tag: $tag complete"
echo "please edit, to deploy"
echo "sudo kubectl edit deployment oceanus-table-manager"
