#!/usr/bin/env python
from datetime import datetime, timezone, timedelta
import os
import json
import sys
import io
import redis
import time
import slack
import slack.chat
from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST, REDIS_PORT,
                             OCEANUS_SITES)
logger = oceanus_logging()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
SLACK_BOT_NAME = os.environ["SLACK_BOT_NAME"]


class revelation:

    def __init__(self, site_name_list):
        """
        arg site is defined in settings.py
        """
        self.site_name_list = site_name_list
        self.keep_processing = True
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.pubsub = self.r.pubsub()

    def signal_exit_func(self, num, frame):
        if self.keep_processing:
            self.keep_processing = False
        self.pubsub.unsubscribe()
        sys.exit("unsubscribe and sys.exit()")

    def prepare_messages(self, messages):
        if not messages:
            return None
        return [mess.replace("\u3000", " ") for mess in messages]

    def dict2text(self, dic):
        text = ""
        for k, v in sorted(dic.items()):
            logger.debug("k:{}, v:{}".format(type(k), type(v)))
            text = "{} {}: {}".format(text, k, v)
        return text

    def convert2jst(self, dt_str):
        JST = timezone(timedelta(hours=+9), 'JST')
        obj_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
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

    def add_ranking(self, ranking_name, value):
        logger.debug("add_ranking"
                     "name:{} value:{}".format(ranking_name, value))
        try:
            result = self.r.zincrby(ranking_name, value, amount=int(1))
        except Exception as e:
            logger.error("Problem adding ranking."
                         "name:{} value:{} e:{}".format(ranking_name,
                                                        value, e))
        sort = self.r.zrevrange(ranking_name, 0, 100)
        logger.debug("result:{}\n sort:{}".format(result, sort))

    def create_messages(self, item):
        ex_item = self.prepare_item(item)
        data = ex_item["data"]
        channel = ex_item["channel"]
        dt = ex_item["dt"]
        jsn = ex_item["jsn"]
        jsn_text = ex_item["jsn_text"]
        messages = []
        if channel == "movieform":
            messages.append("動画MAのコンバージョン "
                            "cname: {} "
                            "uid: {}".format(data["cname"],
                                             data["uid"]))

        if channel == "bizocean":
            if data["evt"] == "search_not_found":
                if not jsn:
                    logger.error("jsn is None. {}".format(data))
                else:
                    messages.append("書式見つからない "
                                    "{} ".format(jsn_text))
                    self.add_ranking("search_not_found", jsn_text)

            if data["evt"] == "paid":
                messages.append("有料書式売れた!"
                                "{}円 "
                                "title:{} "
                                "id:{} "
                                "uid:{}".format(jsn["price"],
                                                jsn["title"],
                                                jsn["id"],
                                                data["uid"]))

            if data["tit"] == "bizocean/500":
                messages.append("{}\n"
                                "bizoceanで500エラー！\n"
                                "url:{}".format(dt, data["url"]))

        message_list = self.prepare_messages(messages)
        return message_list

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

            message_list = self.create_messages(item)
            if message_list:
                message = "\n".join(message_list).replace("\u3000", " ")

                logger.debug("message:{}".format(message))
                slack.api_token = SLACK_API_TOKEN
                slack_result = slack.chat.post_message(SLACK_CHANNEL,
                                                       message,
                                                       username=SLACK_BOT_NAME)
                logger.debug("slack_result:{}".format(slack_result))
            time.sleep(0.05)

            if not self.keep_processing:
                logger.debug("unsubscribe()")
                break

if __name__ == '__main__':
    logger.info("starting revelation...")
    reve = revelation([site["site_name"] for site in OCEANUS_SITES])
    reve.main()
