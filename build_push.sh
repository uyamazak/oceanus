#!/bin/zsh
echo "tag:  $1 start"

sudo docker build -t asia.gcr.io/oceanus-dev/oceanus-swallow:$1 /home/BIZOCEAN/yu_yamazaki/project-oceanus/oceanus
sudo docker build -t asia.gcr.io/oceanus-dev/oceanus-redis2bq:$1 /home/BIZOCEAN/yu_yamazaki/project-oceanus/redis2bq

sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-swallow:$1
sudo gcloud docker push asia.gcr.io/oceanus-dev/oceanus-redis2bq:$1

echo "tag: $1 complete"
