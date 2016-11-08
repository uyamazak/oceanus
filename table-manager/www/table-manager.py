#!/usr/bin/env python
import datetime
import os
import time
from bigquery import get_client
from common.utils import oceanus_logging, create_bq_table_name
from common.settings import OCEANUS_SITES
from common.errors import BigQueryConnectionError
logger = oceanus_logging()

"""Google Parameters"""
PROJECT_ID = os.environ['PROJECT_ID']
DATA_SET = os.environ['DATA_SET']
JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
BQ_TABLE_PREFIX = os.environ['BQ_TABLE_PREFIX']
INTERVAL_SECOND = int(os.environ.get('INTERVAL_SECOND', 15))
BQ_CONNECT_RETRY = int(os.environ.get('BQ_CONNECT_RETRY', 3))


class TableManager:

    def connect_bigquery(self):
        for i in range(1, BQ_CONNECT_RETRY+1):
            try:
                self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                            readonly=False)
            except Exception as e:
                logger.error("connnecting BigQuery failed."
                             "count:{}/{} {}".format(i, BQ_CONNECT_RETRY, e))
            else:
                return True

        logger.critical("connnecting BigQuery retry failed."
                        "count:{}/{}".format(i, BQ_CONNECT_RETRY))
        raise BigQueryConnectionError

    def __init__(self, site):
        """
        arg site is defined in settings.py
        TableManager"""
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.bq_client = None

    def create_table(self, table_name):
        """ create today's table in BigQuery"""
        exists = self.bq_client.check_table(DATA_SET, table_name)
        created = False
        if not exists:
            logger.info("table not exists."
                        "table_name:{}".format(table_name))
            created = self.bq_client.create_table(DATA_SET,
                                                  table_name,
                                                  self.table_schema)
            if created:
                logger.info("table:{} created".format(table_name))
                time.sleep(5)
            else:
                logger.error("create table fail."
                             "table_name:{}".format(table_name))
        return created

    def prepare_table(self):
        """ create today and tommow tables
        return create result
        """
        now = datetime.datetime.now()
        logger.debug("now.hour:{}".format(now.hour))
        created_tommorow = None
        if now.hour >= 12:
            table_name_tomorrow = create_bq_table_name(self.site_name,
                                                       delta_days=1)
            created_tommorow = self.create_table(table_name_tomorrow)

        table_name_today = create_bq_table_name(self.site_name)
        created_today = self.create_table(table_name_today)
        return created_tommorow or created_today

    def main(self):
        try:
            self.connect_bigquery()
        except BigQueryConnectionError:
            time.sleep(5)
            return

        self.prepare_table()

if __name__ == '__main__':
    plist = []
    logger.info("start managing BigQuery tables...")
    logger.info("PROJECT_ID:{} "
                "DATA_SET:{} "
                "BQ_TABLE_PREFIX:{}".format(PROJECT_ID,
                                            DATA_SET,
                                            BQ_TABLE_PREFIX))

    while True:
        for site in OCEANUS_SITES:
            logger.debug("check:{}".format(site["site_name"]))
            tm = TableManager(site)
            tm.main()

        time.sleep(INTERVAL_SECOND)
