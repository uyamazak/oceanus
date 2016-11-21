#!/usr/bin/env python
from datetime import datetime
from os import environ
from time import sleep
from bigquery import get_client
from common.utils import (oceanus_logging,
                          create_bq_table_name)
from common.settings import OCEANUS_SITES
from common.errors import BigQueryConnectionError
logger = oceanus_logging(__name__)

"""Google Parameters"""
PROJECT_ID = environ['PROJECT_ID']
DATA_SET = environ['DATA_SET']
JSON_KEY_FILE = environ['JSON_KEY_FILE']
BQ_TABLE_PREFIX = environ['BQ_TABLE_PREFIX']
INTERVAL_SECOND = int(environ.get('INTERVAL_SECOND', 5))
BQ_CONNECTION_RETRY = int(environ.get('BQ_CONNECT_RETRY', 3))


class TableManager:

    def __init__(self, site):
        """
        arg site is defined in settings.py
        TableManager"""
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.bq_client = None

    def connect_bigquery(self):
        for i in range(1, BQ_CONNECTION_RETRY+1):
            try:
                self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                            readonly=False)
            except Exception as e:
                logger.error("connecting BigQuery failed."
                             "count:{}/{}"
                             "\n{}".format(i, BQ_CONNECTION_RETRY, e))
                sleep(3)
            else:
                return True

        logger.critical("connnecting BigQuery retry failed."
                        "count:{}/{}".format(i, BQ_CONNECTION_RETRY))
        raise BigQueryConnectionError

    def table_exsits(self, table_name):
        return self.bq_client.check_table(DATA_SET, table_name)

    def create_table(self, table_name):
        """ create table in BigQuery"""
        if self.table_exsits(table_name):
            logger.debug("table {} already exists."
                         "".format(table_name))
            return False

        logger.info("table not exists."
                    "table_name:{}".format(table_name))
        created = self.bq_client.create_table(DATA_SET,
                                              table_name,
                                              self.table_schema)
        if created:
            logger.info("table:{} created".format(table_name))
        else:
            logger.critical("create table fail."
                            "table_name:{}".format(table_name))
        return created

    def prepare_table(self):
        """ create today and tommow tables
        return create result
        """
        now = datetime.now()
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
            return
        self.prepare_table()

if __name__ == '__main__':
    logger.info("start managing BigQuery tables...\n"
                "PROJECT_ID:{} "
                "DATA_SET:{} "
                "BQ_TABLE_PREFIX:{}".format(PROJECT_ID,
                                            DATA_SET,
                                            BQ_TABLE_PREFIX))

    import gc
    while True:
        for site in OCEANUS_SITES:
            logger.debug("check:{}".format(site["site_name"]))
            tm = TableManager(site)
            tm.main()
            del tm
            del site
            gc.collect()
        sleep(INTERVAL_SECOND)
