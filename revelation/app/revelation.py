#!/usr/bin/env python
from datetime import datetime, timezone, timedelta
import os
import json
import sys
import redis
import time

from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST,
                             REDIS_PORT,
                             OCEANUS_SITES)
from tasks.app import send2ws, send_user_history

logger = oceanus_logging()
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
SLACK_BOT_NAME = os.environ["SLACK_BOT_NAME"]

JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
SPREAD_SHEET_KEY = os.environ['SPREAD_SHEET_KEY']


class Revelation:
    """
    Revelation can check the contents of channels and data
    by classifying the data acquired from Redis' PubSub and
    pass it to tasks.
    Writing to Google spreadsheets, sending mail, etc. are
    handled on the task side through the task queue
    """
    def connect_redis(self):
        self.r = redis.StrictRedis(host=REDIS_HOST,
                                   port=REDIS_PORT,
                                   db=0,
                                   socket_connect_timeout=3)

    def __init__(self, site_name_list):
        """
        arg site is defined in settings.py
        """
        self.site_name_list = site_name_list
        self.keep_processing = True
        self.connect_redis()
        self.pubsub = self.r.pubsub()

    def signal_exit_func(self, num, frame):
        if self.keep_processing:
            self.keep_processing = False
        self.pubsub.unsubscribe()
        sys.exit("unsubscribe and sys.exit()")

    def prepare_messages(self, messages):
        if not messages:
            return None
        return [mess for mess in messages]

    def dict2text(self, dic):
        text = ""
        for k, v in sorted(dic.items()):
            # logger.debug("k:{}, v:{}".format(type(k), type(v)))
            text = "{} {}: {}".format(text, k, v)
        return text

    def convert2jst(self, dt_str):
        JST = timezone(timedelta(hours=+9), 'JST')
        try:
            obj_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # if microseconds is not set
            obj_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        utc_ts = obj_dt.replace(tzinfo=timezone.utc).timestamp()
        dt = datetime.fromtimestamp(utc_ts, JST)
        return dt

    def prepare_item(self, item):
        channel = item['channel'].decode('utf-8')
        data = json.loads(item["data"].decode('utf-8'), encoding="utf-8")
        dt = None
        if data["dt"]:
            dt = self.convert2jst(data["dt"])
        jsn = None
        jsn_text = ""
        if data["jsn"]:
            jsn = json.loads(data["jsn"])
            jsn_text = self.dict2text(jsn)
        exteded_item = {"data":    data,
                        "channel": channel,
                        "dt":      dt,
                        "jsn":     jsn,
                        "jsn_text": jsn_text
                        }
        return exteded_item

    def make_revelation(self, item):
        ex_item = self.prepare_item(item)
        data = ex_item.get("data")
        channel = ex_item.get("channel")
        dt = ex_item.get("dt")
        jsn = ex_item.get("jsn")
        # 動画広告フォーム
        if channel == "movieform":
            send2ws.delay((
                     dt,
                     data.get("cname"),
                     data.get("uid"),
                     data.get("url"),
                    ),
                    title_prefix="movie_")
        # 名刺情報
        if channel == "namecard":
            # 履歴メール
            # logger.debug("in url:{}".format(data["url"]))
            send_user_history.apply_async(kwargs={"site_name": "bizocean",
                                                  "sid": data.get("sid"),
                                                  "data": data,
                                                  "description": "名刺情報入力ユーザーの履歴",
                                                  },
                                          countdown=60)
        # bizocean内
        if channel == "bizocean":
            # 検索見つからない
            if data["evt"] == "search_not_found":
                if not jsn:
                    logger.error("jsn is None. {}".format(data))
                else:
                    values = (dt,
                              jsn.get("kwd", ""),
                              jsn.get("cat", ""),
                              data.get("uid", ""),
                              data.get("sid", ""),
                              data.get("url", ""),
                              )
                    send2ws.delay(data=values,
                                  title_prefix="not_found_")

            # 有料書式DL完了
            if data["evt"] == "paid":
                values = (dt,
                          "有料書式売れた!",
                          jsn.get("price"),
                          ("title", jsn.get("title")),
                          data.get("url"),
                          ("id", jsn.get("id")),
                          ("uid", data.get("uid")),
                          )
                send2ws.delay(data=values,
                              title_prefix="paid_")
            # エラー
            if "error" in data["evt"]:
                values = (dt,
                          data.get("evt", ""),
                          data.get("url", ""),
                          data.get("ref", ""),
                          ("sid", data.get("sid")),
                          ("uid", data.get("uid")),
                          data.get("ua"),
                          data.get("rad"),
                          )
                send2ws.delay(data=values,
                              title_prefix="error_")

        return

    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        logger.info("REDIS_HOST:{}, "
                    "REDIS_PORT:{}, "
                    "REDIS_LIST:{}".format(REDIS_HOST,
                                           REDIS_PORT,
                                           self.site_name_list))
        self.pubsub.subscribe(self.site_name_list)
        for item in self.pubsub.listen():
            logger.debug("for item in pubsub.listen()")

            if not item:
                logger.debug('not item')
                continue

            if item["type"] == "subscribe":
                logger.debug("type subscribe")
                continue

            revelation_count = self.make_revelation(item)
            # slack.api_token = SLACK_API_TOKEN
            # slack_result = slack.chat.post_message(SLACK_CHANNEL,
            #                                        message,
            #                                        username=SLACK_BOT_NAME)
            # logger.debug("slack_result:{}".format(slack_result))
            # logger.debug("revelation_count:{}".format(revelation_count))
            time.sleep(0.1)


            if not self.keep_processing:
                logger.debug("unsubscribe()")
                break
        else:
            logger.debug("end listen")

if __name__ == '__main__':
    logger.info("starting revelation...")
    reve = Revelation([site["site_name"] for site in OCEANUS_SITES])
    reve.main()
