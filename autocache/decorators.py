import functools

from autocache.backends import CACHE_MISS
from autocache.hashing import argument_hash, bytecode_hash, source_hash


def cached(backend, prefix_generator=bytecode_hash, **kwargs):
    def decorator(function, set_kwargs=None):
        prefix = prefix_generator(function)

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


bytecode_cached = functools.partial(cached, prefix_generator=bytecode_hash)
source_cached = functools.partial(cached, prefix_generator=source_hash)
