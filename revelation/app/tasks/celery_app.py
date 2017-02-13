from celery import Celery
from common.settings import (RABBITMQ_HOST,
                             RABBITMQ_PORT,
                             RABBITMQ_USER,
                             RABBITMQ_PASSWORD)
from common.utils import oceanus_logging
from .plugins.sendgrid import SendGridTasks
from .plugins.gspread import GoogleSpreadSheetsTasks
from .plugins.googlebigquery import GoogleBigQueryTasks
logger = oceanus_logging()

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


@app.task(bind=True, rate_limit='1/s')
def send2ws(self, data, **kwargs):
    try:
        result = gs_tasks.send2ws(data, **kwargs)
    except Exception as e:
        logger.error("task error:{}".format(e))
        raise self.retry(exc=e, countdown=30)
    return result


@app.task(bind=True)
def reauthorize_gspread(self):
    logger.info("reauthorize_gspread")
    gs_tasks.open_gspread_sheet()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     """http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html"""
#     sender.add_periodic_task(60 * 15, reauthorize_gspread.s(), expires=30)


sg_tasks = SendGridTasks()


@app.task(bind=True, rate_limit='10/m')
def send2email(self, **kwargs):
    try:
        result = sg_tasks.send2email(kwargs)
    except Exception as e:
        logger.error("task error:{}".format(e))
        raise self.retry(exc=e, countdown=30)
    return result


bq_tasks = GoogleBigQueryTasks()


@app.task(bind=True, rate_limit='15/m')
def send_user_history(self, site_name, sid, data, **kwargs):
    try:
        result = bq_tasks.send_user_history(site_name=site_name,
                                            sid=sid,
                                            data=data,
                                            **kwargs)
    except Exception as e:
        logger.error("task error:{}".format(e))
        raise self.retry(exc=e, countdown=30)

    return result
