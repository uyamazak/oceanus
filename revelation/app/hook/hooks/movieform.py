from hook.base import BaseHook
from task.celery_app import send2ws


class MovieformHook(BaseHook):

    def main(self) -> int:
        channel = self.item.get("channel")

        if channel != "movieform":
            return 0

        data = self.item.get("data")
        dt = self.item.get("dt")
        count = 1

        values = (dt,
                  data.get("cname"),
                  data.get("uid"),
                  data.get("url"),
                  )
        send2ws.delay(data=values,
                      title_prefix="movie_")

        return count
