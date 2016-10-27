#!/usr/bin/env python
from datetime import datetime, timezone, timedelta
import os
import json
import sys
import io
import redis
import time
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
SPREAD_SHEET_KEY = os.environ['SPREAD_SHEET_KEY']


class Revelation:

    def connect_redis(self):
        self.r = redis.StrictRedis(host=REDIS_HOST,
                                   port=REDIS_PORT,
                                   db=0,
                                   socket_connect_timeout=3)

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

    def __init__(self, site_name_list):
        """
        arg site is defined in settings.py
        """
        self.site_name_list = site_name_list
        self.keep_processing = True
        self.connect_redis()
        self.pubsub = self.r.pubsub()
        self.open_gspread_sheet()

    def create_ws_title(self, prefix="", suffix="", date_format="%Y-%m"):
        d = datetime.now()
        return "{}{}{}".format(prefix,
                               d.strftime(date_format),
                               suffix)

    def get_ws(self, ws_title=None):
        if not ws_title:
            ws_title = self.create_ws_title()
        sheet_title_list = [ws.title for ws in self.gsheet.worksheets()]
        logger.debug("worksheets{}".format(sheet_title_list))
        if ws_title not in sheet_title_list:
            self.gsheet.add_worksheet(ws_title, 1, 20)
            logger.info("create worksheet:{}".format(ws_title))
        self.worksheet = self.gsheet.worksheet(ws_title)
        return self.worksheet

    def format_ws_row(self, args):
        row = []
        for a in args:
            logger.debug("a: {}".format(a))
            if isinstance(a, tuple):
                row.append(":".join(str(i) for i in a))
            elif isinstance(a, str):
                row.append(a)
            elif a is None:
                row.append("")
            else:
                try:
                    row.append(str(a))
                except Exception as e:
                    logger.error("row format error {} "
                                 "type:{}".format(e, a))
        return row

    def send2ws(self, ws_title, message):
        logger.debug("messsage:{}".format(message))
        row = self.format_ws_row(message)
        logger.debug("row:{}".format(row))
        ws = self.get_ws(ws_title)
        result = False
        try:
            result = ws.append_row(row)
        except Exception as e:
            # retry
            logger.error("gsheet.append_row error:{}".format(e))
            self.open_gspread_sheet()
            ws = self.get_ws(ws_title)
            time.sleep(10)
            try:
                result = ws.append_row(row)
            except Exception as e:
                logger.error("retry gsheet.append_row error:{}".format(e))

        logger.debug("result:{}".format(result))
        return result

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

    def send2ranking(self, ranking_name, value):
        logger.debug("send2ranking "
                     "name:{} value:{}".format(ranking_name, value))
        try:
            result = self.r.zincrby(ranking_name, value, amount=int(1))
        except Exception as e:
            logger.error("Problem adding ranking."
                         "name:{} value:{} e:{}".format(ranking_name,
                                                        value, e))
        sort = self.r.zrevrange(ranking_name, 0, 100)
        logger.debug("result:{}\n sort:{}".format(result, sort))

    def make_revelation(self, item):
        ex_item = self.prepare_item(item)
        data = ex_item.get("data")
        channel = ex_item.get("channel")
        dt = ex_item.get("dt")
        jsn = ex_item.get("jsn")
        jsn_text = ex_item.get("jsn_text")
        revelation_count = 0
        # 動画広告フォーム
        if channel == "movieform":
            ws_title = self.create_ws_title(prefix="movie_")
            self.send2ws(ws_title,
                         (dt,
                          data.get("cname"),
                          data.get("uid"),
                          data.get("url"),
                          ))
            revelation_count = revelation_count + 1
        # bizocean内
        if channel == "bizocean":
            # 検索見つからない
            if data["evt"] == "search_not_found":
                ws_title = self.create_ws_title(prefix="not_found_")
                if not jsn:
                    logger.error("jsn is None. {}".format(data))
                else:
                    self.send2ws(ws_title,
                                 (dt,
                                  jsn.get("kwd", ""),
                                  jsn.get("cat", ""),
                                  data.get("uid", ""),
                                  data.get("sid", ""),
                                  data.get("url", ""),
                                  ))
                    self.send2ranking("search_not_found", jsn_text)
                revelation_count = revelation_count + 1

            # 有料書式DL完了
            if data["evt"] == "paid":
                ws_title = self.create_ws_title(prefix="paid_")
                self.send2ws(ws_title,
                             (dt,
                              "有料書式売れた!",
                              jsn.get("price"),
                              ("title", jsn.get("title")),
                              data.get("url"),
                              ("id", jsn.get("id")),
                              ("uid", data.get("uid")),
                              ))
                revelation_count = revelation_count + 1
            # エラー
            if "error" in data["evt"]:
                ws_title = self.create_ws_title(prefix="error_")
                self.send2ws(ws_title,
                             (dt,
                              data.get("evt", ""),
                              data.get("url", ""),
                              data.get("ref", ""),
                              ("sid", data.get("sid")),
                              ("uid", data.get("uid")),
                              data.get("ua"),
                              data.get("rad"),
                              ))
                revelation_count = revelation_count + 1

        return revelation_count

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
        :q    #                                        username=SLACK_BOT_NAME)
            # logger.debug("slack_result:{}".format(slack_result))
            logger.debug("revelation_count:{}".format(revelation_count))
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
