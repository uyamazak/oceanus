from hooks.base import BaseHook
from tasks.celery_app import send_user_history


class DocreqHook(BaseHook):

    def main(self)-> int:
        channel = self.item.get("channel")

        count = 0
        if channel != "docreq":
            return 0

        data = self.item.get("data")

        # 書式リクエスト
        delay_seconds = 60
        desc = ("書式リクエスト {} 秒後に"
                "BigQueryをスキャンしています".format(delay_seconds))
        task_key = "bq_docreq_" + data.get("sid")
        if self.is_registerable_task(task_key):
            count += 1
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

        return count
