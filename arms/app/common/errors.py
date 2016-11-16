class RedisConnectionError(Exception):
    pass


class RedisWritingError(Exception):
    pass


class RedisReadingError(Exception):
    pass


class BigQueryConnectionError(Exception):
    pass


class BigQueryWritingError(Exception):
    pass


class BigQueryTableNotExistsError(Exception):
    pass
