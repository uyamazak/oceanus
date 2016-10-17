#!/bin/zsh
sudo docker images | grep swallow | head -5
sudo docker images | grep redis2bq | head -5
sudo docker images | grep sub2revelation | head -5
echo "enter tag"

read tag

echo "tag:  $tag start"

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-web:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-web:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/oceanus

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-redis2bq:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-redis2bq:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/redis2bq

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-sub2revelation:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-sub2revelation:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/sub2revelation

sudo docker build \
        -t asia.gcr.io/oceanus-dev/oceanus-table-manager:$tag \
        -t asia.gcr.io/oceanus-dev/oceanus-table-manager:latest \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/table-manager

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-web:$tag
sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-redis2bq:$tag
sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-sub2revelation:$tag
sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-table-manager:$tag

echo "tag: $tag complete"
echo "please edit, to deploy"
echo "kc edit deployment oceanus"
echo "kc edit deployment oceanus-redis2bq"
echo "kc edit deployment oceanus-sub2revelation"
echo "kc edit deployment oceanus-table-manager"
