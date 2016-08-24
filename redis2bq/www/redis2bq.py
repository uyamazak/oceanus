#!/usr/bin/env python
import datetime
import os
import json
import sys
import redis
import time
from signal import signal, SIGINT, SIGTERM
from multiprocessing import Process
from bigquery import get_client
from common.utils import oceanus_logging
from common.settings import (REDIS_HOST, REDIS_PORT,
                             OCEANUS_SITES)
logger = oceanus_logging()

"""Google Parameters"""
PROJECT_ID = os.environ['PROJECT_ID']
DATA_SET = os.environ['DATA_SET']
JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
TABLE_PREFIX = os.environ['TABLE_PREFIX']


class redis2bq:

    def connect_redis(self):
        """return True in success, else None"""
        try:
            self.r = redis.StrictRedis(host=REDIS_HOST,
                                       port=REDIS_PORT,
                                       db=0,
                                       socket_connect_timeout=3)
        except Exception as e:
            logger.critical("connnecting Redis faild.\n"
                            "{}".format(e))
            return None

        return True

    def __init__(self, site):
        """
        arg site is defined in settings.py
        """
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.chunk_num = site["chunk_num"]
        self.keep_processing = True
        self.lines = []
        self.bq_client = None
        self.connect_redis()

    def connect_bigquery(self):
        """return None """
        self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                    readonly=False)

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
            logger.error("table not exists."
                         "table_name:{}".format(table_name))
            self.connect_bigquery()
            created = self.bq_client.create_table(DATA_SET,
                                                  table_name,
                                                  self.table_schema)
            if created:
                time.sleep(30)
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

    def write_to_redis(self, line):
        """ return writing Redis result
        exsiting list num
        """
        self.connect_redis()
        try:
            result = self.r.lpush(self.site_name, line)
        except Exception as e:
            logger.critical('[{}] '
                            'Problem adding data to Redis. '
                            '{}'.format(self.site_name, e))

        return result

    def restore_to_redis(self, lines):
        """when app killed or when writing to the BigQuery
        it has failed to return the data to redis
        """
        if not len(lines):
            return None
        count = 0
        try:
            # release blocking
            self.r.lpush(self.site_name, "")
            for l in lines:
                line = json.dumps(l)
                result = self.write_to_redis(line)
                if result:
                    count = count + 1
                logger.debug("result:{}, count:{}".format(result, count))
        except Exception as e:
            logger.error('[{}] Problem restore to Redis. '
                         '{}'.format(self.site_name, e))
            return False

        return count

    def write_to_bq(self, lines):
        if not len(lines):
            return None

        table_name = self.create_table_name()
        try:
            inserted = self.bq_client.push_rows(DATA_SET,
                                                table_name,
                                                self.lines,
                                                'dt')
        except Exception as e:
            logger.error('[{}] '
                         'Problem writing data '
                         'BigQuery.'.format(self.site_name))
            logger.debug('[{}] {}'.format(self.site_name, e))
            return False

        return inserted

    def clean_up(self):
        """When the process is finished ,
        return the data to redis or BigQuery
        so that data is not lost.
        After that sys.exit()"""

        if not len(self.lines):
            sys.exit('[{}] cleaned up:no lines'.format(self.site_name))
            return

        bq_inserted = self.write_to_bq(self.lines)
        if bq_inserted:
            logger.info("[{}] cleaned up "
                        "BigQuery inserted:{} lines".format(self.site_name,
                                                            len(self.lines)))
            self.lines = []
            sys.exit('[{}] BigQuery inserted and exit'.format(self.site_name))
            return

        redis_pushed = self.restore_to_redis(self.lines)
        if redis_pushed:
            logger.info("[{}] cleaned up "
                        "Redis restore:{} lines".format(self.site_name,
                                                        len(self.lines)))
            self.lines = []
            sys.exit('[{}] Redis pushed and exit'.format(self.site_name))
            return

        sys.exit('[{}] cleaned up failed: '
                 'lost {} lines and exit'.format(self.site_name,
                                                 len(self.lines)))

    def signal_exit_func(self, num, frame):
        """called in signal()"""
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

        while self.keep_processing:
            logger.info("PROJECT_ID:{}, "
                        "DATA_SET:{}, "
                        "table_name:{}, "
                        "REDIS_HOST:{}, "
                        "REDIS_PORT:{}, "
                        "REDIS_LIST:{}".format(PROJECT_ID,
                                               DATA_SET,
                                               table_name,
                                               REDIS_HOST,
                                               REDIS_PORT,
                                               self.site_name))

            while len(self.lines) < self.chunk_num:
                res = None
                try:
                    res = self.r.brpop(self.site_name, 0)
                    """
                    res[0] list key
                    res[1] content
                    """
                    logger.debug("[{}]-CHUNK:{}/{}".format(self.site_name,
                                                           len(self.lines) + 1,
                                                           self.chunk_num))
                    logger.debug("res:{}".format(res[1]))
                except Exception as e:
                    logger.error('[{}] Problem getting data from Redis. '
                                 '{}'.format(self.site_name, e))
                    redis_errors += 1
                    time.sleep(3)
                    self.connect_redis()
                    if redis_errors > allowed_redis_errors:
                        logger.critical("Too many Redis errors "
                                        "{}:".format(redis_errors, e))
                        time.sleep(10)
                    continue

                if not res[1]:
                    continue

                try:
                    decoded_res = res[1].decode('utf-8')
                    line = json.loads(decoded_res, encoding="utf-8")
                except Exception as e:
                    logger.error('json.loads error {} '
                                 '{}'.format(e, decoded_res))
                    continue

                self.lines.append(line)

            redis_errors = 0
            self.prepare_table()
            # insert the self.lines into BigQuery
            inserted = self.write_to_bq(self.lines)
            if inserted:
                logger.info('[{}] BigQuery inserted:{}'.format(self.site_name,
                                                               inserted))
                self.lines = []
                continue
            else:
                """retry"""
                logger.warning('[{}] '
                               'BigQuery not inserted. '
                               'retry...'.format(self.site_name))
                time.sleep(6)
                self.connect_bigquery()
                inserted = self.write_to_bq(self.lines)

            if inserted:
                logger.warning('[{}] '
                               'BigQuery retry success'.format(self.site_name))
            else:
                logger.warning('[{}] '
                               'retry failed, BigQuery not inserted. '
                               'restore Redis...'.format(self.site_name))
                self.restore_to_redis(self.lines)

            self.lines = []

if __name__ == '__main__':
    logger.info("starting write to BigQuery....!")

    def multi(site):
        r2bq = redis2bq(site)
        r2bq.main()

    """
    create multiprocess number of OCEANUS_SITES
    """
    plist = []
    for site in OCEANUS_SITES:
        plist.append(Process(target=multi, args=(site,)))

    for p in plist:
        p.start()
        logger.info("[{}] process start "
                    "name:{}".format(site["site_name"], p.name))

    def graceful_exit(num=None, frame=None):
        for p in plist:
            logger.info('graceful_exit:'.format(p.name))
            p.terminate()
            p.join()

    for s in (SIGINT, SIGTERM):
        signal(s, graceful_exit)

    keep_main_process = True
    while keep_main_process:
        for p in plist:
            if not p.is_alive():
                logger.error("not is_alive:{}".format(p.name))
                graceful_exit()
                keep_main_process = False
                break
            else:
                time.sleep(3)
