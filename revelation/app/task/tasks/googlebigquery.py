#!/usr/bin/env python
import os
import json
from common.utils import oceanus_logging, convert2jst
from bigquery import get_client
from datetime import date, timedelta
from task import celery_app
from jinja2 import Environment, FileSystemLoader

PATH = os.path.dirname(os.path.abspath(__file__))
jinja2_env = Environment(
    loader=FileSystemLoader(os.path.join(PATH, 'templates'),
                            encoding='utf8')
)

logger = oceanus_logging()
LOG_LEVEL = os.environ['LOG_LEVEL']

JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
DATA_SET = os.environ['DATA_SET']
PROJECT_ID = os.environ['PROJECT_ID']
TABLE_PREFIX = os.environ['BQ_TABLE_PREFIX']

HISTORY_LIMIT = os.environ.get("HISTORY_LIMIT", 150)


class GoogleBigQueryTasks:

    def __init__(self):
        pass

    def get_history_by_sid(self, site_name, sid="", delta_days=1):
        table_prefix = "[{}:{}.{}{}_]".format(PROJECT_ID,
                                              DATA_SET,
                                              TABLE_PREFIX,
                                              site_name)
        jst_today = date.today() + timedelta(hours=9)
        delta_day = jst_today - timedelta(days=delta_days)
        from_date = delta_day.strftime('%Y-%m-%d')
        to_date = jst_today.strftime('%Y-%m-%d')
        sql = """
        SELECT
            dt,
            STRFTIME_UTC_USEC(
                DATE_ADD(TIMESTAMP(dt), +9, "HOUR"),
                "%Y-%m-%d %H:%M:%S"
            ) as dt_jp,
            sid,
            uid,
            evt,
            tit,
            url,
            dev,
            rad
        FROM
            TABLE_DATE_RANGE(
              {table_prefix},
              TIMESTAMP("{from_date}"),
              TIMESTAMP("{to_date}")
            )
        WHERE
            sid="{sid}"
        ORDER BY dt DESC
        LIMIT {HISTORY_LIMIT}
        """.format(table_prefix=table_prefix,
                   from_date=from_date,
                   to_date=to_date,
                   sid=sid,
                   HISTORY_LIMIT=HISTORY_LIMIT,
                   )
        logger.debug(sql)
        bq_client = get_client(json_key_file=JSON_KEY_FILE)
        job_id, _results = bq_client.query(sql, timeout=30)
        complete, row_count = bq_client.check_job(job_id)
        if complete:
            results = bq_client.get_query_rows(job_id)
            del bq_client
            return results
        else:
            print("not complete")

    def prepare_data(self, data):
        if data.get("dt"):
            data["dt_jp"] = convert2jst(data.get("dt"))
        if data.get("jsn"):
            data["jsn_loads"] = json.loads(data.get("jsn"))
        return data

    def create_mail_body(self, sid, data, history, desc):
        tpl = jinja2_env.get_template('history.html')
        content = {
            "title": "sid: {} の履歴".format(sid),
            "data": self.prepare_data(data),
            "desc": desc,
            "history": history,
            "error": "",
        }

        if not len(history):
            content["error"] = "<p>履歴が見つかりませんでした</p>"
        html = tpl.render(content)
        return html

    def send_user_history(self, site_name, sid, data, **kwargs):
        delta_days = kwargs.get("delta_days", 1)
        desc = kwargs.get("desc", "")
        mail_subject = kwargs.get("subject", "[oceanus]お知らせメール")

        history = self.get_history_by_sid(site_name,
                                          sid,
                                          delta_days=delta_days)
        mail_body = self.create_mail_body(sid=sid,
                                          data=data,
                                          history=history,
                                          desc=desc)
        celery_app.send2email.delay(subject=mail_subject, body=mail_body)
        logger.debug("mail_subject:{}".format(mail_subject))
