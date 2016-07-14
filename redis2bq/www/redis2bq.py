#!/usr/bin/env python
import datetime
import json
import os
import sys
import redis
import time
import logging
from settings import OCEANUS_SITES
from signal import signal, SIGINT, SIGTERM
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


class redis2bq:

    def __init__(self, site):
        self.site = site[0]
        self.table_schema = site[1]
        self.keep_processing = True
        self.lines = []
        self.bq_client = None
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    def connect_bigquery(self):
        self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                    readonly=False)

    def create_table_name(self, delta_days=0):
        if delta_days != 0:
            date_delta = datetime.datetime.now() \
                         + datetime.timedelta(days=delta_days)
            return TABLE_PREFIX + self.site + date_delta.strftime('_%Y%m%d')
        else:
            return TABLE_PREFIX + self.site + \
                   datetime.datetime.now().strftime('_%Y%m%d')

    def create_table(self, table_name):
        """ create today's table in BigQuery"""
        exists = self.bq_client.check_table(DATA_SET, table_name)
        created = False
        if not exists:
            created = self.bq_client.create_table(DATA_SET,
                                                  table_name,
                                                  self.table_schema)
        return created

    def prepare_table(self):
        table_name_tomorrow = self.create_table_name(delta_days=1)
        table_name = self.create_table_name()
        self.create_table(table_name_tomorrow)
        created = self.create_table(table_name)
        if created:
            time.sleep(30)
        return created

    def write_to_redis(self, line):
        try:
            result = self.r.lpush(self.site, line)
        except Exception as e:
            logger.critical('Problem adding data to Redis. {}'.format(e))

        return result

    def restore_to_redis(self, lines):
        if not len(lines):
            return None
        count = 0
        try:
            # release blocking
            self.r.lpush(self.site, "")
            for l in lines:
                line = json.dumps(l)
                result = self.write_to_redis(line)
                if result:
                    count = count + 1
                logger.debug("result:{}, count:{}".format(result, count))
        except Exception as e:
            logger.error('Problem restore to redis. {}'.format(e))
            return False

        return count

    def write_to_bq(self, lines):
        if not len(lines):
            return None

        try:
            table_name = self.create_table_name()
            inserted = self.bq_client.push_rows(DATA_SET,
                                                table_name,
                                                self.lines,
                                                'dt')
        except Exception as e:
            logger.error('Problem writing data BigQuery. {}'.format(e))
            return False

        return inserted

    def clean_up(self):
        if not len(self.lines):
            sys.exit('[{}] cleaned up:no lines'.format(self.site))
            return

        bq_inserted = self.write_to_bq(self.lines)
        if bq_inserted:
            logger.info("[{}] cleaned up "
                        "bigquery inserted:{} lines".format(self.site,
                                                            len(self.lines)))
            self.lines = []
            sys.exit('[{}] exit'.format(self.site))
            return

        redis_pushed = self.restore_to_redis(self.lines)
        if redis_pushed:
            logger.info("[{}] cleaned up "
                        "redis restore:{} lines".format(self.site,
                                                        len(self.lines)))
            self.lines = []
            sys.exit('[{}] exit'.format(self.site))
            return

        sys.exit('[{}] cleaned up failed: '
                 '{} lines exit'.format(self.site,
                                        len(self.lines)))

    def signal_exit_func(self, num, frame):
        if self.keep_processing:
            self.keep_processing = False
            self.clean_up()

    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        """Write the data to BigQuery in small chunks."""
        line = None
        redis_errors = 0
        allowed_redis_errors = 10
        self.connect_bigquery()
        table_name = self.create_table_name()
        table_created = self.create_table(table_name)
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
                                                self.site))

            while len(self.lines) < CHUNK_NUM:
                res = None
                try:
                    res = self.r.brpop(self.site, 0)
                    logger.info("[{}]-CHUNK:{}/{}".format(self.site,
                                                          len(self.lines) + 1,
                                                          CHUNK_NUM))
                    logger.debug("res:{}".format(res[1]))
                except Exception as e:
                    logger.error('[{}] Problem getting data from Redis.'
                                 '{}'.format(self.site, e))
                    redis_errors += 1
                    time.sleep(3)
                    if redis_errors > allowed_redis_errors:
                        logger.critical("Too many redis errors"
                                        " {}:".format(redis_errors, e))
                        time.sleep(10)
                    continue
                try:
                    line = json.loads(res[1].decode('utf-8'),
                                      encoding="utf-8")
                except Exception as e:
                    logger.error('json loads error {}'.format(e))
                    continue

                self.lines.append(line)

            redis_errors = 0
            self.prepare_table()
            # insert the self.lines into bigquery
            inserted = self.write_to_bq(self.lines)
            if inserted:
                logger.info('[{}] bigquery inserted:{}'.format(self.site,
                                                               inserted))
            else:
                """retry"""
                logger.info('bigquery not inserted retry...')
                time.sleep(6)
                self.connect_bigquery()
                inserted = self.write_to_bq(self.lines)

            if not inserted:
                logger.info('bigquery not inserted. restore redis')
                self.restore_to_redis(self.lines)

            self.lines = []

if __name__ == '__main__':
    logger.info("starting write to BigQuery....!")

    def multi(site):
        r2bq = redis2bq(site)
        r2bq.main()

    """
    multiprocess number of OCEANUS_SITES
    """
    plist = []
    for site in OCEANUS_SITES:
        plist.append(Process(target=multi, args=(site,)))

    for p in plist:
        p.start()

    def graceful_exit(num, frame):
        for p in plist:
            logger.info('graceful_exit')
            p.terminate()
            p.join()

    for s in (SIGINT, SIGTERM):
        signal(s, graceful_exit)
