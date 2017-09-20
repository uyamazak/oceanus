#!/usr/bin/env python
import redis
import gc
from time import sleep
from os import environ
from google.cloud import pubsub
from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST,
                             REDIS_PORT,
                             OCEANUS_SITES)
from hook.hook import apply_hooks

logger = oceanus_logging()

PROJECT_ID = environ["PROJECT_ID"]
GOPUB_COMBINED_TOPIC_NAME = environ["GOPUB_COMBINED_TOPIC_NAME"]
GOPUB_COMBINED_SUBSCRIPTION_NAME = environ["GOPUB_COMBINED_SUBSCRIPTION_NAME"]
PUBSUB_PULL_INTERVAL = int(environ.get("PUBSUB_PULL_INTERVAL", 5))


class Revelation:
    """
    Revelation can check the contents of channels and data
    by filtering the data acquired from Google Cloud Pub/Sub
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
        self.site_name_list = site_name_list
        self.connect_redis()
        self.client = pubsub.SubscriberClient()
        self.sub_path = self.client.subscription_path(PROJECT_ID, GOPUB_COMBINED_SUBSCRIPTION_NAME)
        self.topic_path = self.client.topic_path(PROJECT_ID, GOPUB_COMBINED_TOPIC_NAME)
        self.project_path = self.client.project_path(PROJECT_ID)
        logger.debug("\nsub_path:{} \ntopic_path:{} \nproject_path:{}".format(self.sub_path,
                                                                              self.topic_path,
                                                                              self.project_path))

        if self.sub_path not in [s.name for s in self.client.list_subscriptions(self.project_path)]:
            self.subscriber = self.client.create_subscription(self.sub_path, self.topic_path)
        else:
            self.subscriber = self.client.get_subscription(self.sub_path)

        logger.info("REDIS_HOST:{}, "
                    "REDIS_PORT:{}, "
                    "REDIS_LIST:{}, "
                    "".format(REDIS_HOST,
                              REDIS_PORT,
                              self.site_name_list))

        logger.debug("create_subscription. \n"
                     "topic_path:{} \n"
                     "sub_path:{} \n"
                     "self.subscriber:{}".format(self.topic_path,
                                                 self.sub_path,
                                                 self.subscriber))

    def separete_channnel_data(self, raw_message):
        channel = raw_message.split()[0]
        data = raw_message[len(channel):].strip()
        return {"channel": channel, "data": data}

    def main(self):
        def subscribe_callback(message):
            separeted_message = self.separete_channnel_data(message.data)
            if not separeted_message["data"]:
                logger.debug('empty data')
                return

            count = apply_hooks(separeted_message, self.redis)
            if count > 0:
                logger.debug("separeted_message:{}".format(separeted_message))

            message.ack()

        subscription = self.client.subscribe(self.sub_path)
        subscription.open(subscribe_callback)
        logger.debug("end subscription.open()")


if __name__ == '__main__':
    logger.info("starting make revelation and send to RabbitMQ...")

    keep_processing = True

    def signal_exit_func(num, frame):
        global keep_processing
        logger.error("signal_exit_func")
        keep_processing = False

    for s in (SIGINT, SIGTERM):
        signal(s, signal_exit_func)

    while keep_processing:
        reve = Revelation([site["site_name"] for site in OCEANUS_SITES])
        reve.main()
        gc.collect()
        sleep(PUBSUB_PULL_INTERVAL)
