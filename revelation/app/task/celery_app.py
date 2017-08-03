from celery import Celery
from common.settings import (RABBITMQ_HOST,
                             RABBITMQ_PORT,
                             RABBITMQ_USER,
                             RABBITMQ_PASSWORD)
from common.utils import oceanus_logging
from .task_settings import INSTALLED_TASKS

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
app.autodiscover_tasks(INSTALLED_TASKS)

logger.info("INSTALLED_TASKS: {}".format(INSTALLED_TASKS))
