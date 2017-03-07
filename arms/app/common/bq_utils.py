# Since this file is called from several applications,
# I recommend sharing it with a hard link
# When you git clone from repository,
# please create a hard link to run the management/link_common_files.sh.
from datetime import datetime, timedelta
from os import environ
from time import sleep
from bigquery import get_client
from .utils import oceanus_logging
logger = oceanus_logging(__name__)


def create_bq_table_name(site_name: str, delta_days=0,
                         time_partitioning_type=""):
    """return BigQuery table name"""
    TABLE_PREFIX = environ['BQ_TABLE_PREFIX']
    prefix = TABLE_PREFIX + site_name

    """
    Using auto table partitioning
    https://cloud.google.com/bigquery/docs/creating-partitioned-tables
    """
    if time_partitioning_type == "DAY":
        return prefix

    """
    Regacy manual table patition by surfix _YYYYMMDD
    """
    date_part = ""
    if delta_days != 0:
        date_delta = datetime.now() + timedelta(days=delta_days)
        date_part = date_delta.strftime('_%Y%m%d')
    else:
        date_part = datetime.now().strftime('_%Y%m%d')

    return prefix + date_part


def create_bq_client(retry: int, retry_internal_base: int,
                     json_key_file: str):
    bq_result = False
    for i in range(1, retry + 1):
        try:
            bq_client = get_client(json_key_file=json_key_file,
                                   readonly=False)
        except Exception as e:
            logger.error("connecting BigQuery failed."
                         "count:{}/{}"
                         "\n{}".format(i, retry, e))
            bq_result = False
            sleep(i * retry_internal_base)
        else:
            return bq_client

    if bq_result is False:
        logger.critical("connnecting BigQuery retry failed."
                        "count:{}/{}".format(i, retry))
        return False
