sudo docker run -it \
    -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/script:/data/script \
    -v /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/file:/data/file \
    -v /etc/localtime:/etc/localtime:ro \
    bizocean-tool:latest

/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/gsutil \
    rsync \
        /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/file/ \
        gs://bizocean_member_data/

/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/bq rm -f bizocean.member

/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/bq \
    load bizocean.member \
	gs://bizocean_member_data/member.csv.gz \
    /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/script/schema.json

/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/bq rm -f bizocean.member_del

/home/BIZOCEAN/yu_yamazaki/google-cloud-sdk/bin/bq load \
    bizocean.member_del \
	gs://bizocean_member_data/member_del.csv.gz \
    /home/BIZOCEAN/yu_yamazaki/project-oceanus/bizocean-tool/script/schema_del.json
