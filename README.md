oceanus
========
oceanusはbizocean( https://www.bizocean.jp )の低予算データ収集＆活用プロジェクトです。

データの蓄積と分析にはGoogle BigQuery、ストリーミング処理にはCloud Pub/Subを利用しています。

インフラにはDockerとKubernetes(Google Container Engine)を活用して、メンテナンスコストを削減しています。

## Description
![oceanus構成図](https://cdn-ak.f.st-hatena.com/images/fotolife/u/uyamazak/20170419/20170419163411.png "oceanus構成図")

<<<<<<< HEAD
HTTP経由で送られたアクセスログ、クリックログ、フォームデータ、リンククリックなどのデータをBigQueryに保存し、簡単に素早くデータを活用できるようにします。

開発環境はローカルのDocker、本番はGoogle Container Engine（GKE）で運用しています。

自社サービスのデータをBigQueryで一元管理したい、でも予算は限られているbizoceanのために作ってます。

プログラミング言語には主にPythonとGo言語、インフラにはDockerとGoogle Container Engineを利用しています。


bizoceanでの実績
================
会員数200万人、月間約1000万PVのbizocean( https://www.bizocean.jp/ )の各種データを集め、月3万円以下（2017年4月現在）のインフラコストでビッグデータを活用してます。
=======
HTTP経由で送られたアクセスログ、クリックログ、フォームデータ、リンククリックなどのデータを高速かつ低コストでBigQueryに保存し、簡単に素早くデータを活用できるようにします。

開発環境はローカルのDocker、本番はGoogle Container Engine（GKE）で運用しています。

自社サービスのデータをBigQueryで一元管理したい。でも予算は限られている、というbizoceanのために作ってます。


プログラミング言語にはPython、インフラにはDockerとGoogle Container Engineを利用しています。
=======
bizocean( https://www.bizocean.jp/ )の各種データを集め、月3万円以下（2017年4月現在）でビッグデータを活用してます。
>>>>>>> 241a2afbaab9b2c0921d5e1a3495506bd978b8fa

例えば、会員属性や行動ログのデータを元に、メールマガジン広告のクリックを機械学習して予測してます。

機械学習にはGoogle Cloud Datalabを使ってPythonで書いてます。


### arms/
web server
Get parameters and save to Redis list and PubSub.

- Python3
- falcon https://falconframework.org/
- Cerberus http://docs.python-cerberus.org/en/stable/

### r2bq/
Pull the data from Redis list and save to BigQuery.

- Python3
- Redis
- BigQuery

### redis-pd/
Redis with Persistent Disc.

https://redis.io/
Docker image of most official of Redis With Persistent Disc on GCP.


### table-manager/
To see if there is a table required on the BigQuery, creating one if there is none

- Python3
- BigQuery

### revelation/
Using the Google Cloud Pub/Sub, perform a streaming process.
ex. Sending Email, Writing SpreadSheet.

Tasks are processed asynchronously via RabbitMQ and Celery.

- Python3
- Redis
- RabbitMQ
- Celery http://www.celeryproject.org/
- BigQuery
- Cloud Pub/Sub
- SendGrid https://sendgrid.kke.co.jp/
- Google SpreadSheet


### rabbitmq/
https://www.rabbitmq.com/

### gopub/
A High-speed relay server written in Go language which receives data by socket TCP/IP and sends it to Google Cloud Pub/Sub asynchronously.

- Golang
- Google Cloud Pub/Sub


### management/
management tools. docker build, push etc.

- shell scripts

## Demo
https://www.bizocean.jp

Google Chromeなどで開発者ツール（F12）を開きながら、bizocean上のページを読み込みます。「Network」の検索窓で「oceanus」を入力すると下記のようなURLに送信しているデータが確認できます。

https://oceanus.bizocean.co.jp/swallow/bizocean?

## VS.

## Requirement

Docker

Kubernetes OR Google Container Engine

Google Cloud Account

## Usage


## Install
まだ開発中のため、bizocean特有のコードや設定を多く含んでいます。ご興味のある方はお問い合わせください。

必要に応じて無料のハンズオンセミナー等も開催を予定しています。


## Contribution


## Licence

[MIT]

## Author

[uyamazak](http://uyamazak.hatenablog.com/)

