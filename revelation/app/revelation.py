#!/usr/bin/env python
import sys
import redis
from os import environ
from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST,
                             REDIS_PORT,
                             OCEANUS_SITES)
from hooks.hook import apply_hook

logger = oceanus_logging()

JSON_KEY_FILE = environ.get('JSON_KEY_FILE')
SPREAD_SHEET_KEY = environ.get('SPREAD_SHEET_KEY')

TASK_KEY_PREFIX = "task_revelation_"
TASK_KEY_EXPIRE = 300
TASK_KEY_LIMIT = 30


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

    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        logger.info("REDIS_HOST:{}, "
                    "REDIS_PORT:{}, "
                    "REDIS_LIST:{}".format(REDIS_HOST,
                                           REDIS_PORT,
                                           self.site_name_list))
        self.pubsub.subscribe(self.site_name_list)
        for message in self.pubsub.listen():
            logger.debug("for message in pubsub.listen()")

            if not message:
                logger.debug('not message')
                continue

            if message["type"] == "subscribe":
                logger.debug("type subscribe")
                continue

            count = apply_hook(message, self.r)
            if count > 0:
                logger.debug("apply_hook count:{}".format(count))

            if not self.keep_processing:
                logger.debug("unsubscribe()")
                break
        else:
            logger.debug("end listen")


if __name__ == '__main__':
    logger.info("starting revelation...")
    reve = Revelation([site["site_name"] for site in OCEANUS_SITES])
    reve.main()
