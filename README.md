oceanus
========

Open Source Data collecter. Fast and low cost.

Oceanus get HTTP Request and save to Google BigQuery and
y ou can judge important data in real time and can notify and aggregate

Run it on Docker and Google Container Engine.

## Description
![oceanus構成図](https://cdn-ak.f.st-hatena.com/images/fotolife/u/uyamazak/20170419/20170419163411.png "oceanus構成図")

oceanusは低予算のビッグデータ収集＆活用基盤です。

bizocean( https://www.bizocean.jp/ )の各種データを集め、月3万円以下（2017年4月現在）でビッグデータを活用してます。

例えば、会員属性や行動ログのデータを元に、メールマガジン広告のクリックを機械学習して予測してます。

ビッグデータの保存と分析には初期費用不要でディスクもスキャンも安いBigQuery、サーバーにはDockerとGoogle Container Engineを使っています。

機械学習にはGoogle Cloud Datalabを使ってPythonで書いてます。

まだ絶賛開発中のため、bizoceanの環境に依存するものがいろいろ混じってたり、詳細やインストール手順等は書けていないので、興味がある方はご連絡ください。

### arms/
web server
Get parameters and save to Redis list and PubSub.

- python3
- falcon https://falconframework.org/
- Cerberus http://docs.python-cerberus.org/en/stable/

### r2bq/
Remove the data from Redis list and save to BigQuery.

- python3
- Redis
- BigQuery

### redis-pd/
https://redis.io/
Docker image of most official of Redis With Persistent Disc on GCP.


### table-manager/
To see if there is a table required on the BigQuery, creating one if there is none

- python3
- BigQuery

### revelation/
Using the PubPub of Redis, perform a streaming process.
It can be write to the slack and Google spread sheets depending on the conditions.

- python3
- Redis
- RabbitMQ
- Celery http://www.celeryproject.org/
- BigQuery
- SendGrid https://sendgrid.kke.co.jp/
- Google SpreadSheet

### gopub/
A High-speed high-speed relay server written in Go language which receives data by socket TCP/IP and sends it to Google Cloud Pub/Sub asynchronously.

- Golang
- Google Cloud Pub/Sub

### rabbitmq/
https://www.rabbitmq.com/

### management/
management tools. docker build, push etc.

- shell scripts

## Demo
http://www.bizocean.jp

Google Chromeなどで開発者ツール（F12）を開きながら、bizocean上のページを読み込みます。「Network」の検索窓で「oceanus」を入力すると下記のようなURLに送信しているデータが確認できます。

https://oceanus.bizocean.co.jp/swallow/bizocean?

## VS.

## Requirement

Docker

Kubernetes OR Google Container Engine

Google Cloud Account

## Usage


## Install


## Contribution


## Licence

[MIT]

## Author

[uyamazak](http://uyamazak.hatenablog.com/)

