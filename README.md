oceanus
========

Open Source Data collecter. Fast and low cost.

Oceanus get HTTP Request and save to Google BigQuery.

You can run it on Docker and Google Container Engine.

## Description
アクセスログ、クリックログ、フォームデータ、リンククリックなどのデータを高速かつ低コストでBigQueryに保存することができます。
開発はローカルのDocker、本番はGoogle Cloud Platform（GCP）のGoogle Container Engine（GKE）で運用することができます。

自社サービスのデータをBigQueryで一元管理したい。でも予算は限られている、というbizoceanのために作られました。

### bizocean上での実績
oceanusは、登録会員190万人（2016年11月現在）を超えるビジネス書式ダウンロードサイト「bizocean」(http://www.bizocean.jp)で、
あらゆるデータをBigQuery上に保存することで、データの有効活用、ユーザーサポートの充実、サイトの改善をするために開発され続けています。


### 柔軟性
bizoceanでは既存のアクセス解析サービスを使っていましたが、メール、会員属性など他の自社データと組み合わせることが簡単にはできませんでした。

oceanusを使いデータをすべてBigQueryに流し込むことで、自在にデータを組み合わせて集計、解析を行うことができるようになりました。

欲しいデータができたら、少しjsを書くだけで、独自のデータをoceanusに送ることができます。

BigQueryではJSON型のカラムも利用できるため、データ構造はそのままで新しいデータを集めて集計することができます。

### 高速
WEBリクエストから直接BigQueryに保存するのではなく、Redisを挟むことで、非常に高速にレスポンスできます。

アプリケーション部分のフレームワークにはPythonでもっとも高速と言われるfalconを使っています。

### リアルタイム
BigQueryへ書き込むタイミングを頻度の多いアクセスログは50件に一回、フォームデータは1件に1回などパフォーマンスと合わせて調整できます。

たとえばbizoceanでは約5秒ごとにBigQueryへ書き込みが行われています。

そのためほぼリアルタイムにBigQueryからデータを確認することができます。


### 低コスト
bizoceanでは月間1000万PV、1日70万レコード計250MBを超えるデータを送り続けていますが、GCPのコストは1万円/月程度（2016年10月時点）で収まっています。

そのうちサーバー代（GKE）は5000円程度のため、国レベルで冗長化するマルチリージョン構成にしても、+5000円程度で可能なことを意味します。

またGCPに合わせたクラウドネイティブな設計のため、サーバーの追加や死活監視などをWEBの管理画面から簡単に行えて、メンテナンスコストも削減できます。

自前でビッグデータのためのインフラを準備しようと思ったらよくて数十万、データ量によっては数千万レベルも珍しくはありません。またそれを維持するための人件費も莫大です。BigQueryは使った分だけの課金なので初期費用もなく、bizoceanの規模であれば今のところ月1000円もかかっていません。

### データを失わない耐障害設計
BigQueryのストリーミングインサートは便利ですが、ときおりエラーとなり書き込めないことがあります。また過去には3時間以上に渡る完全なダウンも発生しました。

そのため、oceanusではリトライを行うのはもちろん、それでもBigQueryへ書き込みができない場合Redisにデータが戻されるため、データを失うことがありません。

RedisにはGCEの永続ディスクを接続することで、Redisの再起動時のデータ消失も防げます。

アップデート時も終了シグナルを受けとりメモリ内のデータをBigQuery、もしくはRedisに保存してから安全に終了します。

また、GKEがダウンした時に備えるには、GKEとGoogle HTTP Load Balancerを組み合わせることで、マルチリージョンでの展開も容易に可能です。

### カスタマイズ性
arms/swallowは単純な1pxGIFビーコンとしてレスポンスするので、JavaScript等でクエリを組み立てれば自由にデータを送ることができます。

例えば、bizoceanでは、クッキーに保存したセッションキーと、会員の場合はユーザー識別子を渡すことで、特定のユーザーが何時何分にどんなページを見たかなどをほぼリアルタイムに確認できるためユーザーサポートに役立っています。

BigQueryはJSON形式にも対応しており（SELECTのJSON_EXTRACT等）、oceanusももちろん対応しています。新しいデータを追加するときも、特にソースコードを変更することなくJSON形式そのままで保存できます。

単純なHTTPリクエストを、バリデーション、変換などを行った後に、Redisサーバーに保存します。

また、BigQueryのテーブルスキーマ、バリデーションルールなどの設定を追加すれば、新しいデータ形式の追加も簡単に行なえます。

### データ解析も低コストで可能
一般的に販売されているBIツールは月額何十万円と小さい企業には手が出せません。

GCPには、Google内部で使われているGoogle Cloud Datalab（ベータ）が無料で公開されており、これを使えばBigQueryの料金だけで、データの分析、可視化、機械学習などが可能です。

### arms/
web server
Get parameters and save to Redis list and PubSub.

### r2bq/
Remove the data from Redis list and save to BigQuery.

### redis-pd/
Docker image of most official of Redis With Persistent Disc on GCP.

### table-manager/
To see if there is a table required on the BigQuery, creating one if there is none

### revelation/
Using the PubPub of Redis, perform a streaming process.
It can be write to the slack and Google spread sheets depending on the conditions.

### management/
management tools. docker build, push etc.

## Demo
http://www.bizocean.jp

## VS.

## Requirement

Docker

Kubernetes OR Google Container Engine

BigQuery Account

## Usage


## Install


## Contribution


## Licence

[MIT]

## Author

[uyamazak](http://uyamazak.hatenablog.com/)

