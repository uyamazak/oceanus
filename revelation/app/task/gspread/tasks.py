from task.celery_app import app, logger
from .gspread import GoogleSpreadSheetsTasks


gs_tasks = GoogleSpreadSheetsTasks()


@app.task(bind=True, rate_limit='1/s', retry_kwargs={'max_retries': 3})
def send2ws(self, data, **kwargs):
    logger.debug("send2ws")
    try:
        result = gs_tasks.send2ws(data, **kwargs)
    except Exception as e:
        logger.error("gspread task error:{}".format(e))
        raise self.retry(exc=e, countdown=30)
    return result
