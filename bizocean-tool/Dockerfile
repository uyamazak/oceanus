FROM ubuntu:16.04
MAINTAINER yu_yamazaki@bizocean.co.jp

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y \
python3.5 \
python3-pip \
zsh \
vim \
&& apt-get autoclean \
&& apt-get autoremove


RUN pip3 install --upgrade -q \
pip \
cython \
bigquery-python \
google-api-python-client \
redis \
unicodecsv \
py-postgresql


RUN mkdir /data
RUN mkdir /data/script
RUN mkdir /data/file

WORKDIR data/script

ENV FILE_DIR /data/file

COPY script script

VOLUME file

CMD ["zsh"]
#CMD ["python3.5", "staging_db.py"]
