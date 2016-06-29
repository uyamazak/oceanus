#!/usr/bin/env python
import datetime
import json
import os
import redis
import time
import logging
import settings
from multiprocessing import Process
from bigquery import get_client
from logging import getLogger

LOG_LEVEL = os.environ['LOG_LEVEL']
logger = getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(handler)

# BigQuery settings
PROJECT_ID = os.environ['PROJECT_ID']

DATA_SET = os.environ['DATA_SET']
JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
SESSION_KEY = os.environ['SESSION_KEY']
TABLE_PREFIX = os.environ['TABLE_PREFIX']

# redis settings
REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']
CHUNK_NUM = int(os.environ['CHUNK_NUM'])
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

OCEANUS_SITES = settings.OCEANUS_SITES


class redis2bq():

    def connect_bigquery(self):
        json_key = JSON_KEY_FILE
        client = get_client(json_key_file=json_key, readonly=False)
        return client

    def create_table_name(self, site_name, delta_days=0):
        if delta_days != 0:
            date_delta = datetime.datetime.now() \
                         + datetime.timedelta(days=delta_days)
            return TABLE_PREFIX + site_name + date_delta.strftime('_%Y%m%d')
        else:
            return TABLE_PREFIX + site_name + \
                    datetime.datetime.now().strftime('_%Y%m%d')

    def prepare_table(self, client, table_name):
        """ create today's table in BigQuery"""
        exists = client.check_table(DATA_SET, table_name)
        created = False
        if not exists:
            schema = [
                {'name': 'dt',  'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'oid', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'sid', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'uid', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'rad', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'evt', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'tit', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'url', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'ref', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'jsn', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'ua',  'type': 'STRING', 'mode': 'nullable'},
                {'name': 'enc', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'scr', 'type': 'STRING', 'mode': 'nullable'},
                {'name': 'vie', 'type': 'STRING', 'mode': 'nullable'},
            ]
            created = client.create_table(DATA_SET, table_name, schema)
        return created

    def write_to_bq(self, site_name):
        """Write the data to BigQuery in small chunks."""
        lines = []
        line = None
        redis_errors = 0
        allowed_redis_errors = 5
        client = self.connect_bigquery()
        table_name = self.create_table_name(site_name=site_name)
        table_created = self.prepare_table(client, table_name)
        if table_created:
            logger.info('table: {0} created:{1}'.format(table_name,
                                                        table_created))
            time.sleep(5)

        while True:
            logger.info("LOG_LEVEL:{0}".format(LOG_LEVEL))
            logger.info("PROJECT_ID:{0}, "
                        "DATA_SET:{1}, "
                        "table_name:{2}".format(PROJECT_ID,
                                                DATA_SET,
                                                table_name))
            logger.info("REDIS_HOST:{0}, "
                        "REDIS_PORT:{1}, "
                        "REDIS_LIST:{2}".format(REDIS_HOST,
                                                REDIS_PORT,
                                                site_name))

            while len(lines) < CHUNK_NUM:
                # We'll use a blocking list pop -- it returns when there is
                # new data.
                res = None
                try:
                    res = r.brpop(site_name)
                    logger.info("{0} - CHUNK:{1}/{2}".format(
                        site_name,
                        len(lines) + 1,
                        CHUNK_NUM))
                    logger.debug("{0}".format(res))
                except Exception as e:
                    logger.error('Problem getting data from Redis.'
                                 '{0}'.format(e))
                    redis_errors += 1
                    time.sleep(6)
                    if redis_errors > allowed_redis_errors:
                        logger.critical("Too many redis errors {0}:"
                                        "exiting.{1}".format(redis_errors, e))
                        time.sleep(30)
                    continue
                try:
                    line = json.loads(res[1].decode('utf-8'),
                                      encoding="utf-8")
                except Exception as e:
                    logger.error('json loads error {0}'.format(e))
                    continue

                lines.append(line)

            table_name = self.create_table_name(site_name)
            table_name_tomorrow = self.create_table_name(site_name,
                                                         delta_days=1)
            self.prepare_table(client, table_name)
            self.prepare_table(client, table_name_tomorrow)
            # insert the lines into bigquery
            inserted = client.push_rows(DATA_SET, table_name, lines, 'dt')
            if not inserted:
                client = self.connect_bigquery()
                table_name = self.create_table_name(site_name)
                self.prepare_table(client, table_name)
                time.sleep(5)
                inserted = client.push_rows(DATA_SET, table_name, lines, 'dt')
            logger.info('bigquery inserted:{0}'.format(inserted))
            lines = []


if __name__ == '__main__':
    logger.info("starting write to BigQuery....!")

    def multi(site_name):
        r2bq = redis2bq()
        r2bq.write_to_bq(site_name)

    """
    multiprocess OCEANUS_SITES num
    """
    for site_name in OCEANUS_SITES:
        Process(target=multi, args=(site_name,)).start()
