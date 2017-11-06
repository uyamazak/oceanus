oeanus
========
oceanusはbizocean( https://www.bizocean.jp )のデータ収集＆活用プロジェクトです。

データの蓄積と分析にはGoogle BigQuery、ストリーミング処理にはCloud Pub/Subを利用しています。

インフラにはDockerとKubernetes(Google Container Engine)を利用して運用コストを削減しています。

## Description
![oceanus構成図](https://cdn-ak.f.st-hatena.com/images/fotolife/u/uyamazak/20170816/20170816160317.png "oceanus構成図")


HTTP経由で送られたアクセスログ、クリックログ、フォームデータ、リンククリックなどのデータをBigQueryに保存とPub/Subに送信し、簡単にデータを活用できます。

開発環境はローカルのDocker、本番はGoogle Container Engine（GKE）で運用しています。

自社サービスのデータをBigQueryで一元管理したい、でも予算は限られているbizoceanのために作ってます。

プログラミング言語には主にPythonとGo言語、インフラにはDockerとGoogle Container Engineを利用しています。


bizoceanでの実績
================
会員数200万人、月間約1000万PVのbizocean( https://www.bizocean.jp/ )の各種データを集め、月3万円以下（2017年4月現在）のインフラコストでビッグデータを活用してます。

自社サービスのデータをBigQueryで一元管理したい。でも予算は限られているというbizoceanのために開発しています。

サーバーはGoogle Container Engine（GKE）を主ににすべてGCP上で運用しています。

bizocean( https://www.bizocean.jp/ )の会員属性や行動ログのデータを元に、メールマガジン広告のクリックを機械学習して予測し、クリック率の高いユーザーを抽出する等を行っています。

データからのレポート作成にはData Studio( https://datastudio.google.com/ )、データ探索や機械学習にはCloud Datalabを使用しています。

### arms/
Get parameters and save to Redis list and Cloud Pub/Sub through gopub.

- Python3
- gunicorn http://gunicorn.org/
- falcon https://falconframework.org/
- Cerberus http://docs.python-cerberus.org/en/stable/
- Cloud Pub/Sub

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
It monitors for the existence of the necessary table for BigQuery and creates it if it does not exist.

- Python3
- BigQuery

### revelation/
Using the Google Cloud Pub/Sub, perform a realtime streaming process.

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


### shortener/

URL shortening service for oceanus.

By accessing the URL you made you can send the data to the beacon (oceanus/arms) before redirecting.

It operates with Google App Engine, so it can withstand sudden mass access.

Only users registered with Django can make shortend URL and they will not be issued to anonymous user.

- GAE Standard environment
- Cloud SQL (MySQL)
- Python2.7
- Django


## Demo
https://www.bizocean.jp

On almost all the pages of bizocean, we are doing data from the beacon of javascript for the following URL.

https://oceanus.bizocean.co.jp/swallow/bizocean?

## VS.

## Requirement

Docker

Google Container Engine

Google Cloud Account

## Usage
## Install
## Contribution

個人、会社を問わず使えるように開発を進めていますが、まだ一部にbizocean特有のコードや設定を含んでいます。サンプルとしてご利用ください。

自社での利用にご興味のある方はお問い合わせください。

必要に応じてハンズオンセミナー等も開催も可能です。


## Licence

[MIT]

## Author

[uyamazak](http://uyamazak.hatenablog.com/)
