#!/bin/zsh
sudo docker stop `sudo docker ps -f ancestor=asia.gcr.io/oceanus-dev/revelation:latest -q`
