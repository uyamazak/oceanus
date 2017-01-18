sudo docker exec -it \
        `sudo docker ps -q -f ancestor=asia.gcr.io/oceanus-dev/revelation` \
        sh
