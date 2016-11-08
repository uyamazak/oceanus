FROM ubuntu:16.04
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y \
python3.5 \
python3-pip \
zsh \
vim \
&& apt-get clean

RUN pip3 install --upgrade -q \
Django==1.9 \
bigquery-python \
google-api-python-client \

COPY .vimrc /root/
COPY .zshrc /root/

CMD ["zsh"]
