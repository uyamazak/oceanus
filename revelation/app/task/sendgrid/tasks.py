from .sendgrid import SendGridTasks
from task.celery_app import app, logger

sg_tasks = SendGridTasks()


@app.task(bind=True, rate_limit='10/m', retry_kwargs={'max_retries': 3})
def send2email(self, **kwargs):
    try:
        result = sg_tasks.send2email(kwargs)
    except Exception as e:
        logger.error("sendgrid task error:{}".format(e))
        raise self.retry(exc=e, countdown=30)
    return result
