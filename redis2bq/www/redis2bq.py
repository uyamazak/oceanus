#!/usr/bin/env python
import datetime
import json
import os
import sys
import redis
import time
import logging
from settings import TABLE_SCHEMA, OCEANUS_SITES
from signal import signal, SIGINT, SIGTERM, SIGQUIT, SIGABRT
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


class redis2bq():
    lines = []
    keep_processing = True
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    client = None

    def connect_bigquery(self):
        json_key = JSON_KEY_FILE
        self.client = get_client(json_key_file=json_key, readonly=False)

    def create_table_name(self, site_name, delta_days=0):
        if delta_days != 0:
            date_delta = datetime.datetime.now() \
                         + datetime.timedelta(days=delta_days)
            return TABLE_PREFIX + site_name + date_delta.strftime('_%Y%m%d')
        else:
            return TABLE_PREFIX + site_name + \
                    datetime.datetime.now().strftime('_%Y%m%d')

    def prepare_table(self, table_name):
        """ create today's table in BigQuery"""
        exists = self.client.check_table(DATA_SET, table_name)
        created = False
        if not exists:
            created = self.client.create_table(DATA_SET,
                                               table_name,
                                               TABLE_SCHEMA)
        return created

    def write_to_redis(self, data, site_name):
        try:
            result = self.r.lpush(site_name, data)
        except Exception as e:
            logger.critical('Problem adding data to Redis. {0}'.format(e))

        return result

    def restore_to_redis(self, site_name, lines):
        if not len(lines):
            return None
        try:
            for l in lines:
                line = json.dumps(l)
                result = self.write_to_redis(line, site_name)
        except Exception as e:
            logger.error('Problem restore to redis. {e}'.format(e))
            return False

        return result

    def write_to_bq(self, site_name, lines):
        if not len(lines):
            return None
        table_name = self.create_table_name(site_name)
        table_created = self.prepare_table(table_name)

        if table_created:
            time.sleep(30)

        try:
            table_name = self.create_table_name(site_name)
            inserted = self.client.push_rows(DATA_SET,
                                             table_name,
                                             self.lines,
                                             'dt')
        except Exception as e:
            logger.error('Problem writing data BigQuery. {e}'.format(e))
            return False

        return inserted

    def clean_up(self, site_name):
        if not len(self.lines):
            sys.exit('cleaned up:no lines [{}]'.format(site_name))
            return

        bq_inserted = self.write_to_bq(site_name, self.lines)
        if bq_inserted:
            logger.info("cleaned up [{0}] "
                        "bigquery inserted:{1} lines".format(site_name,
                                                             len(self.lines)))
            self.lines = []
            sys.exit('exit:[{}]'.format(site_name))
            return

        redis_pushed = self.restore_to_redis(site_name, self.lines)
        if redis_pushed:
            logger.info("cleaned up [{0}] "
                        "redis restore:{1} lines".format(site_name,
                                                         len(self.lines)))
            self.lines = []
            sys.exit('exit:[{}]'.format(site_name))
            return

        sys.exit('cleaned up failed: '
                 '[{}] {} lines exit'.format(site_name,
                                             len(self.lines)))

    def signal_exit_func(self, num, frame):
        self.keep_processing = False
        self.clean_up(site_name)

    def main(self, site_name):
        signal(SIGINT, self.signal_exit_func)
        signal(SIGTERM, self.signal_exit_func)

        """Write the data to BigQuery in small chunks."""
        self.lines = []
        line = None
        redis_errors = 0
        allowed_redis_errors = 5
        self.connect_bigquery()
        table_name = self.create_table_name(site_name=site_name)
        table_created = self.prepare_table(table_name)
        if table_created:
            logger.info('table {0} created:{1}'.format(table_name,
                                                       table_created))
            time.sleep(6)

        while self.keep_processing:
            logger.info("LOG_LEVEL:{0}, "
                        "PROJECT_ID:{1}, "
                        "DATA_SET:{2}, "
                        "table_name:{3}, "
                        "REDIS_HOST:{4}, "
                        "REDIS_PORT:{5}, "
                        "REDIS_LIST:{6}".format(LOG_LEVEL,
                                                PROJECT_ID,
                                                DATA_SET,
                                                table_name,
                                                REDIS_HOST,
                                                REDIS_PORT,
                                                site_name))

            table_name_tomorrow = self.create_table_name(site_name,
                                                         delta_days=1)
            self.prepare_table(table_name_tomorrow)

            while len(self.lines) < CHUNK_NUM:
                # We'll use a blocking list pop -- it returns when there is
                # new data.
                res = None
                try:
                    res = self.r.brpop(site_name)
                    logger.info("{0}-CHUNK:{1}/{2}".format(site_name,
                                                           len(self.lines) + 1,
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

                self.lines.append(line)

            # insert the self.lines into bigquery
            inserted = self.write_to_bq(site_name, self.lines)
            if inserted:
                logger.info('bigquery [{0}] inserted:{1}'.format(site_name,
                                                                 inserted))
            else:
                """retry"""
                logger.info('bigquery not inserted retrying...')
                time.sleep(6)
                self.connect_bigquery()
                inserted = self.write_to_bq(site_name, self.lines)

            if not inserted:
                logger.info('bigquery not inserted. restore redis')
                self.restore_to_redis(site_name, self.lines)

            self.lines = []

if __name__ == '__main__':
    logger.info("starting write to BigQuery....!")

    def multi(site_name):
        r2bq = redis2bq()
        r2bq.main(site_name)

    """
    multiprocess number of OCEANUS_SITES
    """
    plist = []
    for site_name in OCEANUS_SITES:
        plist.append(Process(target=multi, args=(site_name,)))

    for p in plist:
        p.start()

    def graceful_exit(num, frame):
        for p in plist:
            logger.info('graceful_exit')
            p.terminate()
            p.join()

    for s in (SIGINT, SIGTERM, SIGQUIT, SIGABRT):
        signal(s, graceful_exit)
