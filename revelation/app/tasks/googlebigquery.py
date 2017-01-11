#!/usr/bin/env python
import os
from common.utils import oceanus_logging
from bigquery import get_client
from datetime import date, timedelta
from . import app
from jinja2 import Environment, FileSystemLoader

PATH = os.path.dirname(os.path.abspath(__file__))
jinja2_env = Environment(
    loader=FileSystemLoader(os.path.join(PATH, 'templates'),
                            encoding='utf8')
)


logger = oceanus_logging()

JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
DATA_SET = os.environ['DATA_SET']
PROJECT_ID = os.environ['PROJECT_ID']
TABLE_PREFIX = os.environ['BQ_TABLE_PREFIX']

HISTORY_LIMIT = os.environ.get("HISTORY_LIMIT", 1000)


class GoogleBigQueryTasks:
    def __init__(self):
        self.bq_client = get_client(json_key_file=JSON_KEY_FILE)

    def get_history_by_sid(self, site_name, sid="", delta_days=1):
        table_prefix = "[{}:{}.{}{}_]".format(PROJECT_ID,
                                              DATA_SET,
                                              TABLE_PREFIX,
                                              site_name)
        JST_TODAY = date.today() + timedelta(hours=9)
        from_date = (JST_TODAY - timedelta(days=delta_days)).strftime('%Y-%m-%d')
        to_date = JST_TODAY.strftime('%Y-%m-%d')
        sql = """
        SELECT
            dt,
            STRFTIME_UTC_USEC(DATE_ADD(TIMESTAMP(dt), +9, "HOUR"), "%Y-%m-%d %H:%M:%S") as dt_jp,
            sid,
            uid,
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
        ORDER BY dt ASC
        LIMIT {HISTORY_LIMIT}
        """.format(table_prefix=table_prefix,
                   from_date=from_date,
                   to_date=to_date,
                   sid=sid,
                   HISTORY_LIMIT=HISTORY_LIMIT,
                  )
        logger.debug(sql)
        job_id, _results = self.bq_client.query(sql, timeout=20)
        complete, row_count = self.bq_client.check_job(job_id)
        if complete:
            results = self.bq_client.get_query_rows(job_id)
            return results
        else:
            print("not complete")

    def create_mail_body(self, sid, data, history, description):
        tpl = jinja2_env.get_template('history.html')
        content = {
            "title": "sid: {} の履歴".format(sid),
            "data": data,
            "description":  description,
            "history" : history,
            "error": "",
        }

        if not len(history):
            content["error"] = "<p>履歴が見つかりませんでした</p>"
        html = tpl.render(content)
        return html

    def main(self, site_name, sid, data, delta_days=1, description=""):
        history = self.get_history_by_sid(site_name, sid, delta_days=1)
        mail_body = self.create_mail_body(sid, data, history, description)
        mail_subject = "[oceanus]お知らせメール"
        app.send2email.delay(subject=mail_subject, body=mail_body)
        logger.debug("mail_subject:{}".format(mail_subject))
        logger.debug("mail_body:{}".format(mail_body))
        #app.send2email(subject=mail_subject, body=mail_body)
