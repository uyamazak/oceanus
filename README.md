oceanus
========
oceanusはbizocean(https://www.bizocean.jp)のデータ収集＆活用プロジェクトです。

集めたデータをユーザーサポートや、サイト改善に活かします。

インフラにはDockerとKubernetes(Google Container Engine)を活用してコスト削減にも挑戦しています。

## Description
![oceanus構成図](https://cdn-ak.f.st-hatena.com/images/fotolife/u/uyamazak/20170120/20170120102719.png "oceanus構成図")

HTTP経由で送られた様々なデータをリアルタイムにBigQueryに保存し、簡単に素早くデータを活用できるようにします。

アクセスログ、クリックログ、フォームデータ、リンククリックなどのデータを高速かつ低コストでBigQueryに保存し、簡単に素早くデータを活用できるようにします。

開発環境はローカルのDocker、本番はGoogle Container Engine（GKE）で運用することができます。

自社サービスのデータをBigQueryで一元管理したい。でも予算は限られている、というbizoceanのために作られています。

プログラミング言語にはPython、インフラにはDockerとGoogle Container Engineを利用しています。

導入や運用の支援、自社でのデータ分析のサポートも行いますので、興味のある方はご連絡ください。

### 柔軟性
bizoceanでは既存のアクセス解析サービスを使っていましたが、メール、会員属性など他の自社データと組み合わせることが簡単にはできませんでした。

oceanusを使いデータをすべてBigQueryに流し込むことで、異なるイベントデータをユーザーID（bizoceanの会員ID、もしくはクッキーに保存するセッションキー）を組み合わせて集計、解析を行うことができるようになりました。

欲しいデータができたら、必要なページに少しjsを書くだけで、独自のデータをoceanusに送ることができます。

BigQueryではJSON型のカラムも利用できるため、データ構造はそのままで新しいデータを集めて集計することができます。

### 高速
WEBリクエストから直接BigQueryに保存するのではなく、ローカルネットワーク内で稼働しているRedisを挟むことで、高速にレスポンスできます。

WEBアプリケーションのフレームワークにはPythonでもっとも高速と言われるfalconを使っています。



### リアルタイム性
oceanusでは、BigQueryへのストリーミングインサートを使用しています。

大量に送られてくるデータを一つずつBigQueryに書き込むのは処理時間がかかってしまうため、ある程度貯めてから、まとめて書き込む形を取っています。

タイミングは頻度の多いアクセスログは50件に一回、フォームデータは1件に1回など用途や、リクエスト数に合わせて調整できます。

たとえばbizoceanでは約5秒ごとにBigQueryへ書き込みが行われています。そのためほぼリアルタイムにBigQueryからデータを確認することができます。

ストリーミングインサートは費用が別途かかるため敬遠されている人もいますが、bizoceanでストリーミングインサートにかかる費用は月に18821.9 Mebibytesで、111円程度です。情報のリアルタイム性と一度ストレージに保存してから書き込む処理を省けることを考えると非常に安いと感じています。


### ストリーミング処理
データを中継しているRedisには、リストへの保存だけでなく、1対多のデータ配信を行うPubSubにも送っています。そのため、BigQueryに保存する処理とは別に、リアルタイムにデータを取得し、処理することが可能です。bizoceanでは、エラーと思われるデータをスプレッドシートに書き込んだり、コンバージョンのようなイベントをメールで通知する用途で使用しています。


### 低コスト
bizoceanでは月間1000万PV、1日70万レコード計200MBを超えるデータを送り続けていますが、GCPのコストは1万円/月程度（2016年10月時点）で収まっています。

そのうちサーバー代（GKE）は5000円程度のため、国レベルで冗長化するマルチリージョン構成も、同じものをもう一つ+5000円程度で可能です。

またGCPに合わせたクラウドネイティブな設計のため、サーバーの追加や死活監視などをWEBの管理画面から簡単に行えて、メンテナンスコストも削減できます。

自前でビッグデータのためのインフラを準備しようと思ったらよくて数十万、データ量によっては数千万レベルも珍しくはありません。またそれを維持するための人件費も莫大です。BigQueryは使った分だけの課金なので初期費用もなく、bizoceanの規模であれば今のところ月1000円もかかっていません。

### データを失わない耐障害設計
BigQueryのストリーミングインサートは便利ですが、ときおりエラーとなり書き込めないことがあります。また過去には3時間以上に渡る完全なダウンも発生しました。

そのため、oceanusではリトライを行うのはもちろん、それでもBigQueryへ書き込みができない場合Redisにデータが戻されるため、データを失うことがありません。

RedisにはGCEの永続ディスクを接続することで、Redisの再起動時のデータ消失も防げます。

ソフトウェアの変更によるアップデート時も終了シグナルを受けとりメモリ内のデータをBigQuery、もしくはRedisに保存してから安全に終了します。

また、GKEがリージョン、ゾーン単位でダウンした時の対策としては、GKEとGoogle HTTP Load Balancerを組み合わせることで、マルチリージョンでの展開が可能で、非常に簡単に設定することができます。

### カスタマイズ性
arms/swallowは単純な1pxGIFビーコンとしてレスポンスするので、imgタグや、JavaScript等でクエリを組み立てれば自由にデータを送ることができます。

例えば、bizoceanでは、クッキーに保存したセッションキーと、会員の場合はユーザー識別子を渡すことで、特定のユーザーが何時何分にどんなページを見たかなどをほぼリアルタイムに確認できるためユーザーサポートに役立っています。

BigQueryはJSON形式にも対応しており（SELECTのJSON_EXTRACT等）、oceanusももちろん対応しています。新しいデータを追加したいときも、特にソースコードを変更することなくJSON形式そのままで保存できます。

また、BigQueryのテーブルスキーマ、バリデーションルールなどの設定を追加すれば、独自のデータ形式の追加も簡単に行なえます。

### bizocean上での実績
oceanusは、登録会員約200万人（2017年2月現在）を超えるビジネス書式ダウンロードサイト「bizocean」( http://www.bizocean.jp )で、あらゆるデータをBigQuery上に保存することで、データの有効活用、ユーザーサポートの充実、サイトの改善をするために開発され続けています。

### メッセージキューイングによる非同期処理
revelationでは、RabiitMQとCeleryを使い、メールの送信、スプレッドシートの書き込み、BigQueryのスキャンなどの重い処理を一旦タスク化し、別コンテナで処理しています。

このことで、数分以上かかるような重い処理も少ないサーバーリソースでパンクさせることなく適切に処理することが可能です。

また、Celeryの機能であるイベントから数分後に処理を走らせるなども簡単にできます。たとえば、お問い合わせから10分後に、そのユーザーの履歴をスキャンしてお問い合わせ内容と一緒に送る、等です。

### データ解析も低コストで可能
一般的に販売されているBIツールは月額何十万円と小さい企業には手が出せません。

GCPには、Google内部で使われているGoogle Cloud Datalab（ベータ）が無料で公開されており、これを使えばBigQueryの料金だけで、データの分析、可視化、機械学習などが可能です。

市販の有料ツールは、非常にとっつきやすいですが、高度なカスタマイズや、高速化等が必要になると結局、PythonのPandas等を直接触る必要が出てくることが多いと言われています。

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

- Python3
- BigQuery

### revelation/
Using the PubPub of Redis, perform a streaming process.
It can be write to the slack and Google spread sheets depending on the conditions.

- Python3
- Redis
- RabbitMQ
- Celery http://www.celeryproject.org/
- BigQuery
- SendGrid https://sendgrid.kke.co.jp/
- Google SpreadSheet

### rabbitmq
https://www.rabbitmq.com/

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


## Contribution


## Licence

[MIT]

## Author

[uyamazak](http://uyamazak.hatenablog.com/)

