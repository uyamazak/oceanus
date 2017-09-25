#!/usr/bin/env python
import redis
from os import environ
from sys import exit
from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST, REDIS_PORT, OCEANUS_SITES)
from hook.hook import apply_hooks

logger = oceanus_logging()

PROJECT_ID = environ["PROJECT_ID"]


class Revelation:
    """
    Revelation can check the contents of channels and data
    by filtering the data acquired from Redis PubSub
    and pass it to tasks.
    Writing to Google spreadsheets, sending mail, etc. are
    handled on the task side through the task queue
    """

    def connect_redis(self):
        self.redis = redis.StrictRedis(host=REDIS_HOST,
                                       port=REDIS_PORT,
                                       db=0,
                                       socket_connect_timeout=3)

    def __init__(self, site_name_list):
        """
        arg site is defined in settings.py
        """
        self.connect_redis()
        self.pubsub = self.redis.pubsub()
        self.site_name_list = site_name_list

        self.keep_processing = True

        logger.info("REDIS_HOST:{}, "
                    "REDIS_PORT:{}, "
                    "".format(REDIS_HOST,
                              REDIS_PORT))

    def signal_exit_func(self, num, frame):
        """called in signal()"""
        logger.debug("signal_exit_func(), num:{} frame:{}".format(num, frame))
        if self.keep_processing:
            self.keep_processing = False
        self.pubsub.unsubscribe()
        exit("unsubscribe and exit()")

    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        self.pubsub.subscribe(self.site_name_list)
        for message in self.pubsub.listen():
            # logger.debug("for message in pubsub.listen()")

            if not message:
                logger.debug('not message')
                continue

            if message["type"] == "subscribe":
                logger.debug("type subscribe")
                continue

            count = apply_hooks(message, self.redis)
            if count > 0:
                logger.debug("apply_hook count:{}".format(count))

            if not self.keep_processing:
                logger.info("unsubscribe()")
                break
        else:
            logger.info("end listen")


if __name__ == '__main__':
    logger.info("starting make revelation and send to RabbitMQ...")
    reve = Revelation([site["site_name"] for site in OCEANUS_SITES])
    reve.main()
