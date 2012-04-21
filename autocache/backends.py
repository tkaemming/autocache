# The fallback value for a cache miss.
CACHE_MISS = None


class CacheBackend(object):
    """
    An abstract CacheBackend class that defines the caching API.
    """
    def get(self, key):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError


class LoggingMixin(object):
    """
    Mixin for CacheBackend-like objects that adds logging instrumentation to
    `get` and `set` operations.
    """
    def __init__(self, logger=None, level=None, *args, **kwargs):
        self.logger = logger

        if self.logger:
            import logging
            if level is not None:
                self.level = level
            else:
                self.level = logging.DEBUG

        super(LoggingMixin, self).__init__(*args, **kwargs)

    def get(self, key):
        value = super(LoggingMixin, self).get(key)
        self.log('GET %s: %s', key, value)
        return value

    def set(self, key, value, **kwargs):
        super(LoggingMixin, self).set(key, value, **kwargs)
        self.log('SET %s: %s', key, value)

    def log(self, *args, **kwargs):
        if self.logger:
            self.logger.log(self.level, *args, **kwargs)


class DummyCacheBackend(LoggingMixin, CacheBackend):
    """
    A dummy cache backend for development that doesn't actually cache anything.
    """
    def get(self, key):
        return CACHE_MISS

    def set(self, key, value, **kwargs):
        pass


class SimpleCacheBackend(CacheBackend):
    """
    A simple cache backend that uses a dictionary for storage. Not thread-safe.
    Suitable for simple in-process memoization.
    """
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key, CACHE_MISS)

    def set(self, key, value):
        self.values[key] = value

    def clear(self):
        del self.values
        self.values = {}
