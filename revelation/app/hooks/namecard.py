from .base import BaseHook
from tasks.app import send_user_history


class namecardHook(BaseHook):

    def main(self)-> int:
        channel = self.item.get("channel")

        count = 0
        if channel != "namecard":
            return 0

        data = self.item.get("data")

        # 名刺情報
        delay_seconds = 30
        desc = ("名刺情報入力後 {} 秒後に"
                "BigQueryをスキャンしています".format(delay_seconds))
        if self.is_registerable_task("bq_" + data.get("sid")):
            count += 1
            # 履歴メール
            send_user_history.apply_async(
                kwargs={
                    "site_name": "bizocean",
                    "sid": data.get("sid"),
                    "data": data,
                    "desc": desc
                },
                countdown=delay_seconds)

        return count
