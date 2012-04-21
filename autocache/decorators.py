import functools

from autocache.backends import CACHE_MISS
from autocache.hashing import bytecode_hash, argument_hash


def cached(backend, **kwargs):
    def decorator(function, set_kwargs=None):
        # TODO: Make the prefix generator pluggable.
        prefix = bytecode_hash(function)

        if set_kwargs is None:
            set_kwargs = {}

        @functools.wraps(function)
        def inner(*args, **kwargs):
            # TODO: Make the argument hash function pluggable.
            key = '%s:%s' % (prefix, argument_hash(function, *args, **kwargs))

            # Try to get the value from the cache. If it doesn't exist, invoke
            # the function and set the cache value to the returned value.
            value = backend.get(key)
            if value is CACHE_MISS:
                value = function(*args, **kwargs)
                backend.set(key, value)

            return value

        return inner

    return functools.partial(decorator, **kwargs)
