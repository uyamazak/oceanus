from requests.exceptions import ConnectionError

class RedisConnectionError(ConnectionError):
    pass


class BigQueryConnectionError(ConnectionError):
    pass
