from hook.base import BaseHook
from task.celery_app import send2ws


class BizoceanHook(BaseHook):

    def main(self) -> int:
        channel = self.item.get("channel")

        if channel != "bizocean":
            return 0

        data = self.item.get("data")
        dt = self.item.get("dt")
        jsn = self.item.get("jsn")
        count = 0

        # 検索見つからない
        if data["evt"] == "search_not_found":
            if jsn:
                count += 1
                values = (dt,
                          jsn.get("kwd", ""),
                          jsn.get("cat", ""),
                          data.get("uid", ""),
                          data.get("sid", ""),
                          data.get("url", ""),
                          )
                send2ws.delay(data=values,
                              title_prefix="not_found_")

        # 有料書式DL完了
        if data["evt"] == "paid":
            count += 1
            values = (dt,
                      "有料書式売れた!",
                      jsn.get("price"),
                      ("title", jsn.get("title")),
                      data.get("url"),
                      ("id", jsn.get("id")),
                      ("uid", data.get("uid")),
                      )
            send2ws.delay(data=values,
                          title_prefix="paid_")

        # エラー
        if "error" in data["evt"]:
            count += 1
            values = (dt,
                      data.get("evt", ""),
                      data.get("url", ""),
                      data.get("ref", ""),
                      ("sid", data.get("sid")),
                      ("uid", data.get("uid")),
                      data.get("ua"),
                      data.get("rad"),
                      )
            send2ws.delay(data=values,
                          title_prefix="error_")

        return count
