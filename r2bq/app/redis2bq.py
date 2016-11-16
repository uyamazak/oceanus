#!/usr/bin/env python
import json
import redis
from timeout_decorator import timeout, TimeoutError
from sys import exit
from os import environ
from time import sleep
from signal import signal, SIGINT, SIGTERM
from bigquery import get_client
from common.utils import (oceanus_logging,
                          create_bq_table_name)
from common.settings import (REDIS_HOST, REDIS_PORT,
                             OCEANUS_SITES)
from common.errors import (RedisConnectionError,
                           RedisWritingError,
                           BigQueryConnectionError,
                           BigQueryWritingError,
                           BigQueryTableNotExistsError)
logger = oceanus_logging(__name__)

"""Google Parameters"""
PROJECT_ID = environ['PROJECT_ID']
DATA_SET = environ['DATA_SET']
JSON_KEY_FILE = environ['JSON_KEY_FILE']

"""Serial Parameters"""
BRPOP_TIMEOUT = int(environ.get('BRPOP_TIMEOUT', 1))
SERIAL_INTERVAL_SECOND = float(environ.get('SERIAL_INTERVAL_SECOND', 1.0))
MAX_CHUNK_NUM = int(environ.get('MAX_CHUNK_NUM', 100))
CONNECTION_RETRY = int(environ.get('CONNECTION_RETRY', 3))
WRITING_RETRY = int(environ.get('WRITING_RETRY', 3))
MAIN_PROCESS_TIMEOUT = int(environ.get('MAIN_PROCESS_TIMEOUT', 30))


class redis2bqSerial:

    def __init__(self, site):
        """
        arg site is defined in common.settings
        """
        self.site_name = site["site_name"]
        self.table_schema = site["table_schema"]
        self.table_name = create_bq_table_name(self.site_name)
        self.chunk_num = site["chunk_num"]
        self.keep_processing = True
        self.lines = []
        self.bq_client = None
        self.llen = None

    def connect_redis(self):
        for i in range(1, CONNECTION_RETRY + 1):
            """return True in success, else raise error"""
            try:
                self.r = redis.StrictRedis(host=REDIS_HOST,
                                           port=REDIS_PORT,
                                           db=0,
                                           socket_connect_timeout=3)
                self.llen = self.r.llen(self.site_name)
            except Exception as e:
                logger.error("connnecting Redis failed. "
                             "retry:{}/{}"
                             "\n{}".format(i, CONNECTION_RETRY, e))
                sleep(5)
            else:
                return True

        logger.critical("connnecting Redis retry failed."
                        "{}/{}".format(i, CONNECTION_RETRY))
        raise RedisConnectionError

    def connect_bigquery(self):
        """return True in success, else raise error"""
        for i in range(1, CONNECTION_RETRY + 1):
            try:
                self.bq_client = get_client(json_key_file=JSON_KEY_FILE,
                                            readonly=False)
            except Exception as e:
                logger.error('[{}] '
                             'connecting BigQuery.failed.'
                             "retry:{}/{}"
                             '\n{}'.format(self.site_name,
                                           i, CONNECTION_RETRY,
                                           e))
                sleep(5)
            else:
                return True

        logger.critical('[{}] '
                        'connecting BigQuery retry failed.'
                        '{}'.format(self.site_name, e))
        raise BigQueryConnectionError

    def ensure_table_exists(self):
        exists = self.bq_client.check_table(DATA_SET, self.table_name)
        if exists:
            logger.debug("table [{}] exists".format(self.table_name))
            return True
        else:
            logger.critical("table [{}] not exists".format(self.table_name))
            raise BigQueryTableNotExistsError
            return False

    def write_to_redis(self, line):
        """ return writing Redis result
        exsiting list num
        """
        for i in range(1, WRITING_RETRY + 1):
            try:
                result = self.r.lpush(self.site_name, line)
            except Exception as e:
                logger.error("[{}] "
                             "Problem Writing to Redis. "
                             "retry:{}/{}"
                             "\n{}".format(self.site_name,
                                           i, WRITING_RETRY,
                                           e))
                sleep(5)
            else:
                return result

        logger.critical('[{}] '
                        'Problem adding data to Redis. '
                        '{}'.format(self.site_name, e))
        raise RedisWritingError

    def restore_to_redis(self, lines):
        """when app received kill signal or
           filed writing to the BigQuery
           return the data to redis
        """
        if not len(lines):
            return None
        count = 0
        try:
            """release blocking with
            pushing empty data"""
            self.r.lpush(self.site_name, "")
            for l in lines:
                line = json.dumps(l)
                result = self.write_to_redis(line)
                if result:
                    count += 1
                logger.debug("result:{}, count:{}".format(result, count))
        except Exception as e:
            logger.critical('[{}] Problem restore to Redis. '
                            '{}'.format(self.site_name, e))
            return False

        return count

    def write_to_bq(self, lines):
        if not len(lines):
            return None

        inserted = False
        for i in range(1, WRITING_RETRY + 1):
            """self.bq_client.push_rows never raise errors,
               but show error logs.
               so use 'inserted' to distinguish between success and not
            """
            try:
                inserted = self.bq_client.push_rows(DATA_SET,
                                                    self.table_name,
                                                    lines,
                                                    'dt')
            except Exception as e:
                logger.error('[{}] '
                             'Problem writing data BigQuery.'
                             'retry:{}/{}'
                             '\n{}'.format(self.site_name,
                                           i, WRITING_RETRY,
                                           e))
                sleep(5)
                continue

            logger.debug("inserted:{}".format(inserted))
            if inserted:
                break

        if inserted:
            if i > 1:
                logger.info("[{}] "
                            "BigQuery retry "
                            "success".format(self.site_name))

            return True
        else:
            logger.critical("[{}] "
                            "BigQuery {} retrys "
                            "failed.".format(self.site_name, i))
            raise BigQueryWritingError
            return False

    def clean_up(self):
        """When the process is killed ,
        return the data to redis or BigQuery
        so that data is not lost.
        """

        if not len(self.lines):
            exit('[{}] cleaned up:no lines'.format(self.site_name))
            return
        # save to BigQuery
        try:
            inserted = self.write_to_bq(self.lines)
        except BigQueryWritingError:
            logger.error("BigQueryWritingError")

        if inserted:
            logger.info("[{}] cleaned up "
                        "BigQuery inserted:{} lines".format(self.site_name,
                                                            len(self.lines)))
            self.lines = []
            exit('[{}] BigQuery inserted and exit'.format(self.site_name))
            return

        # save to Redis if BigQuery failed
        try:
            self.restore_to_redis(self.lines)
        except RedisWritingError:
            logger.error("RedisWritingError")
        else:
            logger.info("[{}] cleaned up "
                        "Redis restore:{} lines".format(self.site_name,
                                                        len(self.lines)))
            self.lines = []
            exit('[{}] Redis pushed and exit'.format(self.site_name))
            return

        # Both failed
        logger.critical('[{}] cleaned up failed: '
                        'lost {} lines and exit'.format(self.site_name,
                                                        len(self.lines)))
        exit("exit with losting data")

    def signal_exit_func(self, num, frame):
        """called in signal()"""
        if self.keep_processing:
            self.keep_processing = False
            self.clean_up()

    def needs_writing_bq(self):
        logger.debug("site_name:{} "
                     "chunk_num:{} "
                     "llen:{}".format(self.site_name,
                                      self.chunk_num,
                                      self.llen))
        if self.llen >= self.chunk_num:
            return True
        else:
            return False

    def ensure_dependencies(self):
        try:
            self.connect_redis()
        except RedisConnectionError:
            return False

        if not self.needs_writing_bq():
            logger.debug("[{}] there is no need "
                         "writing to BigQuery".format(self.site_name))
            return False

        try:
            self.connect_bigquery()
        except BigQueryConnectionError:
            logger.info("[{}]"
                        "llen:{} pendding".format(self.site_name, self.llen))
            return False

        try:
            self.ensure_table_exists()
        except BigQueryTableNotExistsError:
            logger.info("[{}]"
                        "llen:{} pendding".format(self.site_name, self.llen))
            return False

        return True

    @timeout(MAIN_PROCESS_TIMEOUT)
    def main(self):
        for s in (SIGINT, SIGTERM):
            signal(s, self.signal_exit_func)

        if not self.ensure_dependencies():
            return

        """Write the data to BigQuery in small chunks."""
        CHUNK_NUM = min(self.llen, MAX_CHUNK_NUM)
        logger.debug("PROJECT_ID:{}, "
                     "DATA_SET:{}, "
                     "table_name:{} "
                     "llen:{} "
                     "CHUNK_NUM:{} "
                     "REDIS_HOST:{}, "
                     "REDIS_PORT:{}, "
                     "REDIS_LIST:{}".format(PROJECT_ID,
                                            DATA_SET,
                                            self.table_name,
                                            self.llen,
                                            CHUNK_NUM,
                                            REDIS_HOST,
                                            REDIS_PORT,
                                            self.site_name))
        redis_writing_errors = 0

        while len(self.lines) < CHUNK_NUM:
            res = None
            logger.debug("len(self.lines):{}".format(len(self.lines)))
            try:
                # getting data from redis with blocking
                res = self.r.brpop(self.site_name, BRPOP_TIMEOUT)
                """
                res[0] list's key (same as self.site_name)
                res[1] content text
                """
                logger.debug("[{}]-CHUNK:{}/{}".format(self.site_name,
                                                       len(self.lines) + 1,
                                                       self.chunk_num))
                logger.debug("res:{}".format(res))

            except Exception as e:
                logger.error('[{}] Problem getting data from Redis. '
                             '{}'.format(self.site_name, e))

                redis_writing_errors += 1
                if redis_writing_errors > WRITING_RETRY:
                    logger.critical("Too many writing redis errors.")
                    break

                continue

            if res is None:
                """
                It happens if you're running multiple r2bq processes.
                When another process has taken the data first,
                this res is None."""
                logger.debug("res is None. break")
                break

            if not res[1]:
                "if body is empty, proceed to the next"
                logger.debug("res[1] is empty. break")
                continue

            try:
                line = json.loads(res[1].decode('utf-8'), encoding="utf-8")
            except Exception as e:
                logger.error('json.loads error {} '
                             '{}'.format(e, decoded_res))
                continue
            else:
                self.lines.append(line)

        if len(self.lines) == 0:
            logger.debug("len(self.lines) == 0 return")
            return

        # insert the self.lines into BigQuery
        bq_inserted = False
        try:
            bq_inserted = self.write_to_bq(self.lines)
        except BigQueryWritingError:
            logger.warning('[{}] '
                           'retry failed, BigQuery not inserted. '
                           'restore Redis...'.format(self.site_name))
            self.restore_to_redis(self.lines)
            return

        logger.info("[{}] BigQuery "
                    "inserted {} "
                    "{} lines".format(self.site_name,
                                      bq_inserted,
                                      len(self.lines)))


if __name__ == '__main__':
    keep_processing = True

    def graceful_exit(num=None, frame=None):
        global keep_processing
        logger.info("graceful_exit")
        keep_processing = False

    for s in (SIGINT, SIGTERM):
        signal(s, graceful_exit)
    logger.info("site_name start:" +
                ",".join([site["site_name"] for site in OCEANUS_SITES]))
    while keep_processing:
        for site in OCEANUS_SITES:
            r2bq = redis2bqSerial(site)
            try:
                r2bq.main()
            except TimeoutError:
                logger.critical("timeout error exit")
                r2bq.clean_up()

        sleep(SERIAL_INTERVAL_SECOND)
