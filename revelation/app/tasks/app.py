from celery import Celery
from common.settings import (RABBITMQ_HOST,
                             RABBITMQ_PORT,
                             RABBITMQ_USER,
                             RABBITMQ_PASSWORD)
from .sendgrid import SendGridTasks
from .gspread import GoogleSpreadSheetsTasks
from .googlebigquery import GoogleBigQueryTasks

celery_broker = ('pyamqp://{RABBITMQ_USER}:'
                 '{RABBITMQ_PASSWORD}'
                 '@{RABBITMQ_HOST}'
                 ':{RABBITMQ_PORT}'
                 '//'.format(RABBITMQ_USER=RABBITMQ_USER,
                             RABBITMQ_PASSWORD=RABBITMQ_PASSWORD,
                             RABBITMQ_HOST=RABBITMQ_HOST,
                             RABBITMQ_PORT=RABBITMQ_PORT))
celery_backend = 'rpc://'
app = Celery('tasks', broker=celery_broker, backend=celery_backend)

gs_tasks = GoogleSpreadSheetsTasks()
sg_tasks = SendGridTasks()
bq_tasks = GoogleBigQueryTasks()


@app.task
def add(x, y):
    return x + y


@app.task
def send2ws(data,
            title_prefix="",
            title_suffix="",
            date_format=None):
    return gs_tasks.main(data,
                         title_prefix=title_prefix,
                         title_suffix=title_suffix,
                         date_format=date_format)


@app.task
def send2email(**kwargs):
    return sg_tasks.main(kwargs)


@app.task
def send_user_history(site_name, sid="", data=None, desc=""):
    bq_tasks.main(site_name=site_name,
                  sid=sid,
                  data=data,
                  desc=desc)
    return
