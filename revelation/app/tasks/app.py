from celery import Celery
from common.settings import (RABBITMQ_HOST,
                             RABBITMQ_PORT,
                             RABBITMQ_USER,
                             RABBITMQ_PASSWORD)
from common.utils import oceanus_logging
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

logger = oceanus_logging()

gs_tasks = GoogleSpreadSheetsTasks()
sg_tasks = SendGridTasks()
bq_tasks = GoogleBigQueryTasks()


@app.task(bind=True)
def send2ws(self, data, **kwargs):
    try:
        result = gs_tasks.main(data, **kwargs)
    except Exception as e:
        logger.error("task error:{}".format(e))
        raise self.retry(exc=e)
    return result


@app.task
def send2email(**kwargs):
    return sg_tasks.main(kwargs)


@app.task(bind=True)
def send_user_history(self, site_name, sid, data, **kwargs):
    try:
        result = bq_tasks.main(site_name=site_name,
                               sid=sid,
                               data=data,
                               **kwargs)
    except Exception as e:
        logger.error("task error:{}".format(e))
        raise self.retry(exc=e)

    return result
