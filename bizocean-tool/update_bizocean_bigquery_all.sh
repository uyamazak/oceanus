#!/bin/zsh
sudo docker run \
    -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/script:/data/script \
    -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/file:/data/file \
    -v /etc/localtime:/etc/localtime:ro \
    bizocean-tool:latest

/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/gsutil \
    rsync \
     /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/file/ \
     gs://bizocean_member_data/

tables=("member" "member_del" "product" "product_category" "category")

for t in ${tables[@]}; do

	/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/bq rm -f bizocean.${t}

	/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/bq \
      load bizocean.${t} \
	  gs://bizocean_member_data/${t}.csv.gz \
      /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/schema/${t}.json

done
