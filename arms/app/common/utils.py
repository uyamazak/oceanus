# Since this file is called from several applications,
# I recommend sharing it with a hard link
# When you git clone from repository,
# please create a hard link to run the management/link_common_files.sh.
import logging
import base64
import ipaddress
from datetime import datetime, timedelta, timezone
from os import environ
from common.settings import INTERNAL_IPS_V4

loggers = {}


def oceanus_logging(name=None):
    global loggers
    if name is None:
        name = __name__

    if loggers.get(name):
        return loggers.get(name)

    LOG_LEVEL = environ['LOG_LEVEL']
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - '
                                  '%(levelname)s - '
                                  '%(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    handler.setLevel(getattr(logging, LOG_LEVEL))
    logger.addHandler(handler)
    loggers[name] = logger
    return logger


def resp_beacon_gif(resp):
    resp.append_header('Cache-Control',
                       'no-cache, no-store, must-revalidate')
    resp.append_header('expires', 'Mon, 01 Jan 1990 00:00:00 GMT')
    resp.append_header('pragma', 'no-cache')
    resp.append_header('Content-type', 'image/gif')
    resp.body = base64.b64decode('R0lGODlhAQABAID/AP///wAA'
                                 'ACwAAAAAAQABAAACAkQBADs=')
    return resp


def create_bq_table_name(site_name, delta_days=0,
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
                     key_file: str):
    bq_result = False
    for i in range(1, retry + 1):
        try:
            bq_client = get_client(json_key_file=key_file,
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


def convert2jst(dt_str):
    JST = timezone(timedelta(hours=+9), 'JST')
    try:
        obj_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        # if microseconds is not set
        obj_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    utc_ts = obj_dt.replace(tzinfo=timezone.utc).timestamp()
    dt = datetime.fromtimestamp(utc_ts, JST)
    return dt


def is_internal_ip(client_ip_str) -> bool:
    internal_ip_list = INTERNAL_IPS_V4.split(",")
    client_ip = ipaddress.ip_address(client_ip_str)
    for internal_ip in internal_ip_list:
        ip_network = ipaddress.ip_network(internal_ip)
        if client_ip in ip_network:
            return True

    return False
