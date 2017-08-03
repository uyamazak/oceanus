from .googlebigquery import GoogleBigQueryTasks
from task.celery_app import app, logger

bq_tasks = GoogleBigQueryTasks()


@app.task(bind=True, rate_limit='15/m')
def send_user_history(self, site_name, sid, data, **kwargs):
    try:
        result = bq_tasks.send_user_history(site_name=site_name,
                                            sid=sid,
                                            data=data,
                                            **kwargs)
    except Exception as e:
        logger.error("googlebigquery task error:{}".format(e))
        raise self.retry(exc=e, countdown=30)

    return result
