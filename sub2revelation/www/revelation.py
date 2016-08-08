#!/usr/bin/env python
from datetime import datetime, timezone, timedelta
import os
import json
import sys
import redis
import time
import slack
import slack.chat
from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST, REDIS_PORT,
                             OCEANUS_SITES)
logger = oceanus_logging()
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

    def signal_exit_func(self, num, frame):
        if self.keep_processing:
            self.keep_processing = False
            sys.exit("signal exit")

    def create_message(self, item):
        json_text = item["data"].decode('utf-8')
        data = json.loads(json_text, encoding="utf-8")
        dt = None
        if data["dt"]:
            JST = timezone(timedelta(hours=+9), 'JST')
            dt = data["dt"]
            obj_dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
            utc_ts = obj_dt.replace(tzinfo=timezone.utc).timestamp()
            dt = datetime.fromtimestamp(utc_ts, JST)

        channel = item['channel'].decode('utf-8')
        messages = []
        if channel == "movieform":
            messages.append("{}\n"
                            "動画MAのコンバージョンがありました\n"
                            "uid:{}".format(dt, data["uid"]))

        if channel == "bizocean":
            if data["evt"] == "serch_not_found":
                messages.append("{}\n"
                                "書式見つからないキーワード\n"
                                "kwd:{}".format(dt, data["jsn"]["kwd"]))
            if data["tit"] == "bizocean/500":
                messages.append("{}\n"
                                "500エラー\n"
                                "url:{}".format(dt, data["url"]))

        return messages

    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        logger.info("REDIS_HOST:{}, "
                    "REDIS_PORT:{}, "
                    "REDIS_LIST:{}".format(REDIS_HOST,
                                           REDIS_PORT,
                                           self.site_name_list))
        pubsub = self.r.pubsub()
        pubsub.subscribe(self.site_name_list)
        for item in pubsub.listen():
            if not self.keep_processing:
                pubsub.unsubscribe()
                break
            if not item:
                return

            if item["type"] == "subscribe":
                continue

            logger.debug("channel:{}\n"
                         "type:{}\n"
                         "pattern:{}\n"
                         "data:{}".format(item['channel'],
                                          item['type'],
                                          item['pattern'],
                                          item['data']))
            message = self.create_message(item)
            if message:
                message = "\n".join(message)
                logger.debug("message:{}".format(message))
                slack.api_token = SLACK_API_TOKEN
                slack.chat.post_message(SLACK_CHANNEL,
                                        message,
                                        username=SLACK_BOT_NAME)
            time.sleep(0.1)

if __name__ == '__main__':
    logger.info("starting revelation...")
    reve = revelation([site["site_name"] for site in OCEANUS_SITES])
    reve.main()
