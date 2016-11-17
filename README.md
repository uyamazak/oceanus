oceanus
========

Open Source Data collecter. Fast and low cost.

Oceanus get HTTP Request and save to Google BigQuery.

You can run it on Docker and Google Container Engine.

## Description
アクセスログ、クリックログ、フォームデータ、リンククリックなどのデータを簡単にBigQueryに保存することができます。

### 高速
WEBリクエストから直接BigQueryに保存するのではなく、Redisを挟むことで、非常に高速にレスポンスできます。
言語にはPython3、フレームワークにはfalconを使っています。

### 高いリアルタイム性
頻度の多いアクセスログは50件に一回、フォームデータは1件に1回などBigQueryへ書き込むタイミングをパフォーマンスと合わせて調整できます。

そのため、ほぼリアルタイムにBigQueryからデータを確認することができます。

### 低コスト
bizoceanでは月間1000万PV、1日200MBを超えるデータを送り続けていますが、GCPのコストは1万円/月程度で収まっています。

またGoogle Cloud Platformに合わせたクラウドネイティブな設計のため、サーバーの構築や死活監視などを簡単に行えるためメンテナンスコストも削減できます。

BigQueryも使った分だけの課金なので初期費用もありません。

### 障害への強さ
BigQueryへ書き込みを失敗した時や、障害時はRedisにデータが保存されるため、データを失うことがありません。

RedisにはGCEの永続ディスクを接続することで、再起動時のデータ消失も防げます。

コンテナの更新時なども、終了シグナルを受けとりメモリ内のデータをBigQuery、もしくはRedisに保存してから安全に終了します。

また、GKEとGoogle HTTP Load Balancerを組み合わせることで、マルチリージョンでの展開も容易に可能です。

### 拡張性
arms/swallowは単純な1pxGIFビーコンとしてレスポンスするので、JavaScript等でクエリを組み立てれば自由にデータを送ることができます。

例えば、bizoceanでは、クッキーに保存したセッションキーと、会員の場合はユーザー識別子を渡すことで、特定のユーザーが何時何分にどんなページを見たかなどをほぼリアルタイムに確認できるためユーザーサポートに役立っています。

BigQueryはJSON形式にも対応しており、新しいデータを追加するときも、特にソースコードを変更することなくそのまま保存できます。

単純なHTTPリクエストを、バリデーション、変換などを行った後に、Redisサーバーに保存します。

また、BigQueryのテーブルスキーマ、バリデーションルールなどの設定を追加すれば、新しいデータ形式の追加も簡単に行なえます。
## Description
Data such as access logs, click logs, form data, link clicks, etc. can be easily stored in BigQuery.

### high speed
Instead of saving it directly from the web request to BigQuery, you can respond very quickly by sandwiching Redis.
I use Python 3 as the language and falcon as the framework.

### High real time
You can adjust the timing of writing to BigQuery, such as frequent access logs once per 50 cases, form data once per case, along with performance.

Therefore, you can check data from BigQuery in near real time.

### low cost
Bizocean continues to send data over 10 million PV per month, over 200 MB per day, but the cost of GCP is about 10,000 yen per month.

Moreover, because it is a cloud native design tailored to Google Cloud Platform, maintenance costs can be reduced because it is easy to build a server and check for life and death.

Since BigQuery also charges as much as you used it, there is no initial cost.

### Strength to failure
When writing to BigQuery fails or failure occurs, data is saved in Redis, so there is no loss of data.

By connecting GCE permanent disk to Redis, it is also possible to prevent data loss at restart.

Upon updating the container, etc., it will safely terminate after receiving the end signal and saving the data in memory to BigQuery or Redis.

Also, by combining GKE and Google HTTP Load Balancer, deployment in multiple regions is easily possible.

### Scalability
Since arms / swallow responds as a simple 1px GIF beacon, you can send data freely by assembling the query with JavaScript etc.

For example, in bizocean, by passing the session key stored in the cookie and the user identifier in the case of the member, it is useful for user support because it is possible to check in real time what time and what kind of page a specific user has seen. I will.

BigQuery also supports the JSON format, so when adding new data, you can save it without changing the source code, in particular.

Simple HTTP requests are saved on the Redis server after validation, conversion, etc.

You can also easily add new data formats by adding BigQuery table schema, validation rules and other settings.

### arms
web server
Get parameters and save to Redis list and PubSub.

### r2bq
Remove the data from Redis list and save to BigQuery.

### redis-pd
Docker image of most official of Redis With Persistent Disc on GCP.

### table-manager
To see if there is a table required on the BigQuery, creating one if there is none

### revelation
Using the PubPub of Redis, perform a streaming process.
It can be write to the slack and Google spread sheets depending on the conditions.

### management
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

