#!/usr/bin/env python
import functools
import hashlib
import inspect


def generate_function_key(fn):
    """
    Generates a key for this callable by hashing the bytecode. This appears
    to be deterministic on CPython for trivial implementations, but likely
    is implementation-specific.
    """
    return hashlib.md5(fn.func_code.co_code).hexdigest()


def convert_dict_to_tuple(d):
    """
    Converts an unhashable dict to a hashable tuple, sorted by key.
    """
    return tuple(sorted(d.items(), key=lambda item: item[0]))


def generate_unique_key(fn, *args, **kwargs):
    """
    Generates a unique key based on the hashed values of all of the passed
    arguments. This makes a pretty bold assumption that the hash() function
    is deterministic, which is (probably) implementation specific.
    """
    arguments = inspect.getcallargs(fn, *args, **kwargs)
    if 'kwargs' in arguments:
        arguments['kwargs'] = convert_dict_to_tuple(arguments['kwargs'])
    arguments = convert_dict_to_tuple(arguments)
    # This is passed back through MD5 to ensure that the key does not grow too
    # long for caching backends with a limited key size (read: memcached.)
    return hashlib.md5(':'.join(map(str, map(hash, arguments)))).hexdigest()


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
            unique_key = '%s:%s' % (key, key_generator(fn, *args, **kwargs))

            # If the value is `None` from the cache, then generate the real
            # value and store it.
            value = backend.get(unique_key)
            if value is None:
                value = fn(*args, **kwargs)
                backend.set(unique_key, value, **set_kwargs)

            return value
        return inner

    return functools.partial(decorator, **kwargs)
