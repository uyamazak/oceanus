#!/usr/bin/env python
import sys
import redis
import gc
from os import environ
from time import sleep
from multiprocessing import Process
from google.cloud import pubsub
from signal import signal, SIGINT, SIGTERM
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST,
                             REDIS_PORT,
                             OCEANUS_SITES)
from hook.hook import apply_hook
from subscriber import (list_subscriptions,
                        create_subscription)

logger = oceanus_logging()

SPREAD_SHEET_KEY = environ.get('SPREAD_SHEET_KEY')
GOPUB_COMBINED_TOPIC_NAME = environ.get("GOPUB_COMBINED_TOPIC_NAME")
GOPUB_COMBINED_SUBSCRIPTION_NAME = environ.get("GOPUB_COMBINED_SUBSCRIPTION_NAME")
PUBSUB_PULL_INTERVAL = int(environ.get("PUBSUB_PULL_INTERVAL", 1))
PROCESS_RESTART_MESSAGE_COUNT = int(environ.get("PROCESS_RESTART_MESSAGE_COUNT", 10000))
ONCE_PULL_COUNT = int(environ.get("ONCE_PULL_COUNT", 200))


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
        self.keep_processing = True
        self.connect_redis()
        self.pubsub_client = pubsub.Client()
        self.topic = self.pubsub_client.topic(GOPUB_COMBINED_TOPIC_NAME)

        if GOPUB_COMBINED_SUBSCRIPTION_NAME not in list_subscriptions(GOPUB_COMBINED_TOPIC_NAME):
            create_subscription(GOPUB_COMBINED_TOPIC_NAME,
                                GOPUB_COMBINED_SUBSCRIPTION_NAME)
            logger.debug("create_subscription. "
                         "topic:{} "
                         "sub:{}".format(GOPUB_COMBINED_TOPIC_NAME,
                                         GOPUB_COMBINED_SUBSCRIPTION_NAME))

    def signal_exit_func(self, num, frame):
        if self.keep_processing:
            self.keep_processing = False
        # delete_subscription(GOPUB_COMBINED_TOPIC_NAME,
        #                    GOPUB_COMBINED_SUBSCRIPTION_NAME)

    def separete_channnel_data(self, raw_message):
        channel = raw_message.split()[0]
        data = raw_message[len(channel):].strip()
        return {"channel": channel, "data": data}

    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        logger.info("REDIS_HOST:{}, "
                    "REDIS_PORT:{}, "
                    "REDIS_LIST:{}, "
                    "GOPUB_COMBINED_TOPIC_NAME:{}, "
                    "GOPUB_COMBINED_SUBSCRIPTION_NAME:{}, "
                    "".format(REDIS_HOST,
                              REDIS_PORT,
                              self.site_name_list,
                              GOPUB_COMBINED_TOPIC_NAME,
                              GOPUB_COMBINED_SUBSCRIPTION_NAME))

        subscription = self.topic.subscription(GOPUB_COMBINED_SUBSCRIPTION_NAME)
        message_count = 0
        while self.keep_processing:
            results = subscription.pull(return_immediately=True,
                                        max_messages=ONCE_PULL_COUNT)
            # logger.debug('Received {} messages.'.format(len(results)))
            for ack_id, message in results:
                separeted_message = self.separete_channnel_data(message.data)
                if not separeted_message["data"]:
                    logger.debug('not data')
                    continue
                count = apply_hook(separeted_message, self.redis)
                if count > 0:
                    logger.debug("apply_hook count:{}"
                                 "separeted_message:{}".format(count, separeted_message))
            # Acknowledge received messages. If you do not acknowledge,
            # Pub/Sub will redeliver the message.
            if results:
                subscription.acknowledge([ack_id for ack_id, message in results])
            message_count += len(results)
            sleep(PUBSUB_PULL_INTERVAL)

            if message_count > PROCESS_RESTART_MESSAGE_COUNT:
                logger.info('over message_count break')
                break
        sys.exit("end while exit")


if __name__ == '__main__':
    logger.info("starting make revelation and send to RabbitMQ...")

    def main():
        reve = Revelation([site["site_name"] for site in OCEANUS_SITES])
        reve.main()

    while True:
        p = Process(target=main)
        p.start()
        p.join()
        gc.collect()
