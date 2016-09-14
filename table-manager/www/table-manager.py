#!/usr/bin/env python
import datetime
import os
import time
from bigquery import get_client
from common.utils import oceanus_logging
from common.settings import OCEANUS_SITES
logger = oceanus_logging()

"""Google Parameters"""
PROJECT_ID = os.environ['PROJECT_ID']
DATA_SET = os.environ['DATA_SET']
JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
TABLE_PREFIX = os.environ['TABLE_PREFIX']
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

    def create_table_name(self, delta_days=0):
        """return table name"""
        if delta_days != 0:
            date_delta = datetime.datetime.now() + \
                         datetime.timedelta(days=delta_days)

            return TABLE_PREFIX + self.site_name + \
                date_delta.strftime('_%Y%m%d')

        else:
            return TABLE_PREFIX + self.site_name + \
                    datetime.datetime.now().strftime('_%Y%m%d')

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
        table_name_tomorrow = self.create_table_name(delta_days=1)
        table_name_today = self.create_table_name()
        created_tommorow = self.create_table(table_name_tomorrow)
        created_today = self.create_table(table_name_today)
        return created_tommorow or created_today


if __name__ == '__main__':
    plist = []
    logger.info("start managing BigQuery tables...")
    logger.info("PROJECT_ID:{} "
                "DATA_SET:{} "
                "TABLE_PREFIX:{}".format(PROJECT_ID,
                                         DATA_SET,
                                         TABLE_PREFIX))

    while True:
        for site in OCEANUS_SITES:
            logger.debug("check:{}".format(site["site_name"]))
            tm = TableManager(site)
            tm.prepare_table()
        time.sleep(INTERVAL_SECOND)
