from os import environ
from hooks.base import BaseHook
from tasks.celery_app import send_user_history
from common.utils import oceanus_logging
logger = oceanus_logging()

DOQREQ_DELAY_SECONDS = int(environ.get("DOQREQ_DELAY_SECONDS", 90))


class DocreqHook(BaseHook):

    def main(self)-> int:
        channel = self.item.get("channel")

        count = 0
        if channel != "docreq":
            return 0

        data = self.item.get("data")

        # 書式リクエスト
        delay_seconds = DOQREQ_DELAY_SECONDS
        desc = ("書式リクエスト送信から {} 秒後に"
                "行動履歴をスキャンしています".format(delay_seconds))

        task_key = "bq_docreq_" + data.get("sid")
        if self.is_registerable_task(task_key) is False:
            logger.debug("重複タスクのためキャンセル")
            return 0

        ip = data.get("rad")
        if self.is_allowed_by_ip(ip) is False:
            logger.debug("IP制限のためキャンセル")
            return 0

        # 履歴メール
        send_user_history.apply_async(
            kwargs={
                "site_name": "bizocean",
                "sid": data.get("sid"),
                "data": data,
                "desc": desc,
                "subject": "[oceanus]書式リクエスト {}".format(task_key),
            },
            countdown=delay_seconds)

        count += 1
        return count
