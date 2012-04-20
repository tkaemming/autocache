#!/usr/bin/env python
"""
Self-versioning and argument-hashing cache decorator for deterministic functions.
Designed to be extensible and API-compliant with Django and Flask cache backends.

For examples and caveats, see the bottom of the file.

Ted Kaemming: https://github.com/tkaemming
Mike Tigas: https://github.com/mtigas
"""
import functools
import hashlib


def generate_function_key(fn):
    """
    Generates a key for this callable by hashing the bytecode. This appears
    to be deterministic on CPython for trivial implementations, but likely
    is implementation-specific.
    """
    return hashlib.md5(fn.func_code.co_code).hexdigest()


def generate_unique_key(*args, **kwargs):
    """
    Generates a unique key based on the hashed values of all of the passed
    arguments. This makes a pretty bold assumption that the hash() function
    is deterministic, which is (probably) implementation specific.
    """
    hashed_args = ['%s' % hash(arg) for arg in args]
    hashed_kwargs = ['%s ' % hash((key, value)) for (key, value) in kwargs.items()]
    # this is md5 hashed again to avoid the key growing too large for memcached
    return hashlib.md5(':'.join(hashed_args + hashed_kwargs)).hexdigest()


def cached(backend, **kwargs):
    """
    Automagical caching for deterministic functions.

    Supported keyword arguments:
    * key: use a user-defined cache key (not versioned) instead of hashing the
        function's bytecode
    * key_generator: use a user-defined cache key generator instead of using
        `__hash__` on the args/kwargs passed to the callable
    * set_kwargs: keyword arguments passed to the cache backend's `set` method,
        so you can pass timeouts, etc. when setting cached values
    """
    def decorator(fn, key=None, key_generator=None, set_kwargs=None):
        if key is None:
            key = generate_function_key(fn)

        if key_generator is None:
            key_generator = generate_unique_key

        if set_kwargs is None:
            set_kwargs = {}

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            unique_key = '%s:%s' % (key, key_generator(*args, **kwargs))

            # If the value is `None` from the cache, then generate the real
            # value and store it.
            value = backend.get(unique_key)
            if value is None:
                value = fn(*args, **kwargs)
                backend.set(unique_key, value, **set_kwargs)

            return value
        return inner

    return functools.partial(decorator, **kwargs)
