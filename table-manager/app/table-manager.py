#!/usr/bin/env python
import gc
from sys import exit
from datetime import datetime
from os import environ
from time import sleep
from bigquery import get_client
from common.utils import (oceanus_logging,
                          create_bq_table_name)
from common.settings import OCEANUS_SITES
logger = oceanus_logging(__name__)

"""Google Parameters"""
PROJECT_ID = environ['PROJECT_ID']
DATA_SET = environ['DATA_SET']
JSON_KEY_FILE = environ['JSON_KEY_FILE']
BQ_TABLE_PREFIX = environ['BQ_TABLE_PREFIX']
INTERVAL_SECOND = int(environ.get('INTERVAL_SECOND', 30))
BQ_CONNECTION_RETRY = int(environ.get('BQ_CONNECT_RETRY', 3))


class TableManager:

    def __init__(self, site, bq_client):
        """
        arg site is defined in settings.py
        TableManager"""
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.bq_client = bq_client

    def table_exsits(self, table_name):
        return self.bq_client.check_table(DATA_SET,
                                          table_name)

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

    def clean_up_memory(self):
        self.bq_client = None
        self.site_name = None
        self.table_schema = None
        del self.bq_client
        del self.site_name
        del self.table_schema
        gc.collect()

    def main(self):
        self.prepare_table()
        self.clean_up_memory()
        return

if __name__ == '__main__':
    logger.info("start managing BigQuery tables...\n"
                "PROJECT_ID:{} "
                "DATA_SET:{} "
                "BQ_TABLE_PREFIX:{}".format(PROJECT_ID,
                                            DATA_SET,
                                            BQ_TABLE_PREFIX))

    def create_bq_client():
        bq_result = False
        for i in range(1, BQ_CONNECTION_RETRY+1):
            try:
                bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                       readonly=False)
            except Exception as e:
                logger.error("connecting BigQuery failed."
                             "count:{}/{}"
                             "\n{}".format(i, BQ_CONNECTION_RETRY, e))
                bq_result = False
                sleep(i*15)
            else:
                return bq_client

        if bq_result is False:
            logger.critical("connnecting BigQuery retry failed."
                            "count:{}/{}".format(i, BQ_CONNECTION_RETRY))
            return bq_result

    bq_client = create_bq_client()
    if bq_client is False:
        exit("create_bq_client() failed")

    while True:
        for site in OCEANUS_SITES:
            # logger.debug("check:{}".format(site["site_name"]))
            tm = TableManager(site, bq_client)
            try:
                tm.main()
            except BrokenPipeError:
                logger.error("BrokenPipeError at tm.main()\n"
                             "retry create_bq_client()")
                bq_client = create_bq_client()
                if bq_client is False:
                    exit("retry create_bq_client() failed. exit()")
                break
            except Exception as e:
                logger.critical("{} at tm.main()\n".format(e))
                exit()
            else:
                tm = None
                site = None
                del tm
                del site
                gc.collect()
        sleep(INTERVAL_SECOND)
