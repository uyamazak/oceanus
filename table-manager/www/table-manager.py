#!/usr/bin/env python
import datetime
import os
import time
from bigquery import get_client
from common.utils import oceanus_logging, create_bq_table_name
from common.settings import OCEANUS_SITES
logger = oceanus_logging()

"""Google Parameters"""
PROJECT_ID = os.environ['PROJECT_ID']
DATA_SET = os.environ['DATA_SET']
JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
BQ_TABLE_PREFIX = os.environ['BQ_TABLE_PREFIX']
INTERVAL_SECOND = int(os.environ['INTERVAL_SECOND'])


class TableManager:

    def connect_bigquery(self):
        """return None """
        self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                    readonly=False)

    def __init__(self, site):
        """
        arg site is defined in settings.py
        TableManager"""
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.chunk_num = site["chunk_num"]
        self.keep_processing = True
        self.lines = []
        self.bq_client = None
        self.connect_bigquery()

    def create_table(self, table_name):
        """ create today's table in BigQuery"""
        exists = self.bq_client.check_table(DATA_SET, table_name)
        created = False
        if not exists:
            logger.info("table not exists."
                        "table_name:{}".format(table_name))
            self.connect_bigquery()
            created = self.bq_client.create_table(DATA_SET,
                                                  table_name,
                                                  self.table_schema)
            if created:
                logger.info("table:{} created".format(table_name))
                time.sleep(5)
            else:
                logger.error("create table fail."
                             "table_name:{}".format(table_name))
                self.connect_bigquery()
        return created

    def prepare_table(self):
        """ create today and tommow tables
        return create result
        """
        created_tommorow = False
        now = datetime.datetime.now()
        logger.debug("now.hour:{}".format(now.hour))
        if now.hour >= 12:
            table_name_tomorrow = create_bq_table_name(self.site_name,
                                                       delta_days=1)
            created_tommorow = self.create_table(table_name_tomorrow)

        table_name_today = create_bq_table_name(self.site_name)
        created_today = self.create_table(table_name_today)
        return created_tommorow or created_today


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
            tm.prepare_table()
        time.sleep(INTERVAL_SECOND)
