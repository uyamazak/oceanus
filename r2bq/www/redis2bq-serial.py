#!/usr/bin/env python
import os
import json
import sys
import redis
import time
from signal import signal, SIGINT, SIGTERM
from bigquery import get_client
from common.utils import oceanus_logging, create_bq_table_name
from common.settings import (REDIS_HOST, REDIS_PORT,
                             OCEANUS_SITES)
logger = oceanus_logging()

"""Google Parameters"""
PROJECT_ID = os.environ['PROJECT_ID']
DATA_SET = os.environ['DATA_SET']
JSON_KEY_FILE = os.environ['JSON_KEY_FILE']

"""serial Parameters"""
BRPOP_TIMEOUT = os.environ.get('BRPOP_TIMEOUT', 1)
SERIAL_INTERVAL_SECOND = os.environ.get('SERIAL_INTERVAL_SECOND', 0.5)


class redis2bqSerial:

    def connect_redis(self):
        """return True in success, else False"""
        try:
            self.r = redis.StrictRedis(host=REDIS_HOST,
                                       port=REDIS_PORT,
                                       db=0,
                                       socket_connect_timeout=3)
        except Exception as e:
            logger.critical("connnecting Redis faild.\n"
                            "{}".format(e))
            return False

        return True

    def __init__(self, site, llen):
        """
        arg site is defined in settings.py
        """
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.chunk_num = site["chunk_num"]
        self.llen = llen
        self.keep_processing = True
        self.lines = []
        self.bq_client = None
        self.connect_redis()

    def connect_bigquery(self):
        """return None """
        self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                    readonly=False)

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
        """when app received kill signal or
           when filed writing to the BigQuery
           return the data to redis
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

        table_name = create_bq_table_name(self.site_name)
        try:
            inserted = self.bq_client.push_rows(DATA_SET,
                                                table_name,
                                                lines,
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

        logger.critical('[{}] cleaned up failed: '
                        'lost {} lines and exit'.format(self.site_name,
                                                        len(self.lines)))
        sys.exit("exit with losting data")

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
        table_name = create_bq_table_name(self.site_name)

        logger.debug("PROJECT_ID:{}, "
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

        MAX_CHUNK_NUM = 100
        if self.llen > MAX_CHUNK_NUM:
            self.llen = MAX_CHUNK_NUM
        while len(self.lines) < self.llen:
            res = None
            logger.debug("len(self.lines):{}".format(len(self.lines)))
            try:
                res = self.r.brpop(self.site_name, BRPOP_TIMEOUT)
                """
                res[0] list's key
                res[1] content
                """
                logger.debug("[{}]-CHUNK:{}/{}".format(self.site_name,
                                                       len(self.lines) + 1,
                                                       self.chunk_num))
                logger.debug("res:{}".format(res))
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

            if not res:
                logger.debug("not res break")
                break

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

        if len(self.lines) == 0:
            logger.debug("len(self.lines) == 0 return")
            return

        redis_errors = 0
        # insert the self.lines into BigQuery
        inserted = self.write_to_bq(self.lines)
        if inserted:
            logger.debug('[{}] BigQuery inserted:{}'.format(self.site_name,
                                                            inserted))
            self.lines = []
            return
        else:
            """retry"""
            logger.warning('[{}] '
                           'BigQuery not inserted. '
                           'retry...'.format(self.site_name))
            time.sleep(5)
            self.connect_bigquery()
            inserted = self.write_to_bq(self.lines)

        if inserted:
            logger.info('[{}] '
                        'BigQuery retry success'.format(self.site_name))
        else:
            logger.warning('[{}] '
                           'retry failed, BigQuery not inserted. '
                           'restore Redis...'.format(self.site_name))
            self.restore_to_redis(self.lines)
            self.lines = []

if __name__ == '__main__':
    r = redis.StrictRedis(host=REDIS_HOST,
                          port=REDIS_PORT,
                          db=0,
                          socket_connect_timeout=3)
    keep_processing = True

    def graceful_exit(num=None, frame=None):
        global keep_processing
        logger.info("graceful_exit")
        time.sleep(1)
        keep_processing = False

    for s in (SIGINT, SIGTERM):
        signal(s, graceful_exit)

    while keep_processing:
        for site in OCEANUS_SITES:
            llen = r.llen(site["site_name"])
            logger.debug("{}:{}".format(site["site_name"], llen))
            if llen >= site["chunk_num"]:
                logger.debug("over chunk_num:{}\n"
                             "llen:{}".format(site["site_name"], llen))
                r2bq = redis2bqSerial(site, llen)
                r2bq.main()
        time.sleep(SERIAL_INTERVAL_SECOND)
