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
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC

from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST, REDIS_PORT,
                             OCEANUS_SITES)
logger = oceanus_logging()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
SLACK_BOT_NAME = os.environ["SLACK_BOT_NAME"]

JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
SPREAD_SHEET_TITLE = os.environ['SPREAD_SHEET_TITLE']
SPREAD_SHEET_KEY = os.environ['SPREAD_SHEET_KEY']


class revelation:

    def connect_redis(self):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0,
                                   socket_connect_timeout=3)

    def create_ws_title(self):
        d = datetime.now()
        return d.strftime("%Y-%U")

    def open_gspread_sheet(self):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SAC.from_json_keyfile_name(JSON_KEY_FILE, scope)
        try:
            gc = gspread.authorize(credentials)
        except Exception as e:
            logger.error("open_gspread_sheet {}".format(e))
        ws_title = self.create_ws_title()
        logger.debug("ws_title:{}".format(ws_title))
        self.gsheet = gc.open_by_key(SPREAD_SHEET_KEY)

    def get_gworksheet(self):
        self.open_gspread_sheet()
        ws_title = self.create_ws_title()
        sheet_title_list = [ws.title for ws in self.gsheet.worksheets()]
        logger.debug("worksheets{}".format(sheet_title_list))
        if ws_title not in sheet_title_list:
            self.gsheet.add_worksheet(ws_title, 1, 20)
            logger.info("create worksheet:{}".format(ws_title))
        self.worksheet = self.gsheet.worksheet(ws_title)

    def __init__(self, site_name_list):
        """
        arg site is defined in settings.py
        """
        self.site_name_list = site_name_list
        self.keep_processing = True
        self.get_gworksheet()
        self.connect_redis()
        self.pubsub = self.r.pubsub()
        self.messages = []

    def append_gs_row(self, message_list):
        logger.debug("message_list len():{}".format(len(message_list)))
        self.get_gworksheet()
        for mess in message_list:
            logger.debug("mess:{}".format(mess))
            try:
                result = self.worksheet.append_row(mess)
            except Exception as e:
                logger.error("gsheet.append_row error:{}".format(e))
                result = self.worksheet.append_row(mess)

            logger.debug("result:{}".format(result))
        else:
            return True

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

    def add_mess(self, dt, *args, **kwargs):
        line = ["{}".format(dt)]
        for a in args:
            if not a:
                continue
            line.append("{}".format(a))
        for k, v in kwargs.items():
            if not v:
                continue
            line.append("{}:{}".format(k, v))
        self.messages.append(line)
        return self.messages

    def create_messages(self, item):
        ex_item = self.prepare_item(item)
        data = ex_item.get("data")
        channel = ex_item.get("channel")
        dt = ex_item.get("dt")
        jsn = ex_item.get("jsn")
        jsn_text = ex_item.get("jsn_text")

        if channel == "movieform":
            self.add_mess(dt,
                          "動画MAのコンバージョン",
                          "cname",
                          data["cname"],
                          "uid",
                          data.get("uid"),
                          )

        if channel == "bizocean":
            if data["evt"] == "search_not_found":
                if not jsn:
                    logger.error("jsn is None. {}".format(data))
                else:
                    self.add_mess(dt,
                                  "書式見つからない",
                                  "kwd",
                                  jsn.get("kwd"),
                                  )
                    self.add_ranking("search_not_found", jsn_text)

            if data["evt"] == "paid":
                self.add_mess(dt,
                              "有料書式売れた!",
                              "price",
                              jsn.get("price"),
                              "title",
                              jsn.get("title"),
                              "id",
                              jsn.get("id"),
                              "uid",
                              data.get("uid"),
                              )

            if data["tit"] == "bizocean/500":
                self.add_mess(dt,
                              "bizoceanで500エラー！",
                              "url",
                              data["url"],
                              )

        message_list = self.messages
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
                self.append_gs_row(message_list)

                logger.debug("message:{}".format(message_list))

                # slack.api_token = SLACK_API_TOKEN
                # slack_result = slack.chat.post_message(SLACK_CHANNEL,
                #                                        message,
                #                                        username=SLACK_BOT_NAME)
                # logger.debug("slack_result:{}".format(slack_result))
            self.messages = []
            time.sleep(0.05)

            if not self.keep_processing:
                logger.debug("unsubscribe()")
                break
        else:
            logger.debug("end listen")

if __name__ == '__main__':
    logger.info("starting revelation...")
    reve = revelation([site["site_name"] for site in OCEANUS_SITES])
    reve.main()
