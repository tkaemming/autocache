#!/usr/bin/env python
from distutils.core import setup

setup(name='autocache',
    version='0.1-dev',
    description="simple function caching/memoization with argument value " \
        "and bytecode hashing for cache key generation and versioning",
    author='ted kaemming',
    author_email='ted@kaemming.com',
    url='https://github.com/tkaemming/autocache',
    py_modules=['autocache'],
)
