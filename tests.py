from nose import with_setup

import autocache


class CacheBackend(object):
    def get(self, key, fallback=None):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError


class SimpleCacheBackend(CacheBackend):
    def __init__(self):
        self.values = {}

    def get(self, key, fallback=None):
        return self.values.get(key, fallback)

    def set(self, key, value):
        self.values[key] = value

    def clear(self):
        del self.values
        self.values = {}


cache = SimpleCacheBackend()


@with_setup(cache.clear)
def test_backend():
    """
    Test basic cache backend interface compatibility.
    """
    def original_foo(x):
        foo.counter += 1
        return x ** x

    foo = autocache.cached(backend=cache)(original_foo)
    foo.counter = 0

    # The cache should be empty.
    assert len(cache.values) == 0

    result = foo(1)
    assert result == 1

    assert len(cache.values) == 1
    assert foo.counter == 1

    foo(1)
    assert foo.counter == 1

    foo(2)
    assert len(cache.values) == 2
    assert foo.counter == 2

    foo(x=1)
    assert len(cache.values) == 2
    assert foo.counter == 2

    foo(**{'x': 1})
    assert len(cache.values) == 2
    assert foo.counter == 2

    def original_bar(x):
        bar.counter += 1
        return x ** (x + 1)

    bar = autocache.cached(backend=cache)(original_bar)
    bar.counter = 0

    bar(1)
    assert len(cache.values) == 3
    assert bar.counter == 1

    bar(2)
    assert len(cache.values) == 4
    assert bar.counter == 2

    # Now, define a function that will compile to the same bytecode as `foo`...

    def original_baz(x):
        baz.counter += 1
        return x ** x

    baz = autocache.cached(backend=cache)(original_baz)
    baz.counter = 0

    assert original_baz.func_code.co_code == original_foo.func_code.co_code
    assert original_baz.func_code.co_code != original_bar.func_code.co_code

    # The cache will not grow, since the method signature and the bytecode are
    # identical, and it will actually use the cached value from `foo`!

    # This also demonstrates that the function really should have no side
    # effects if you're going to be caching the result value, and that the
    # function should also not be dependent on external state to calculate it's
    # result.

    baz(1)
    assert baz.counter == 0
    assert len(cache.values) == 4


@with_setup(cache.clear)
def test_bytecode_versioning():
    """
    Tests bytecode versioning to ensure functions with the same name but
    different implementations are not cached with the same hashes.
    """
    assert len(cache.values) == 0  # sanity check

    @autocache.cached(backend=cache)
    def foo(x):
        return x

    result = foo(1)
    assert result == 1
    assert len(cache.values) == 1

    @autocache.cached(backend=cache)
    def foo(x):
        return x + 1

    result = foo(1)
    assert result == 2
    assert len(cache.values) == 2


def test_argument_variations():
    """
    Test to ensure that permutations of argument order and/or argument naming
    all reduce to the identical unique hash for the same invocation.
    """
    def foo(bar, baz, *args, **kwargs):
        pass

    def check(*keys):
        assert len(set(keys)) == 1

    check(
        autocache.generate_unique_key(foo, 1, 2, 3, 4, a=1, b=2, c=3),
        autocache.generate_unique_key(foo, 1, 2, 3, 4, b=2, a=1, c=3),
        autocache.generate_unique_key(foo, 1, 2, 3, 4, b=2, c=3, a=1),
    )

    check(
        autocache.generate_unique_key(foo, 1, 2),
        autocache.generate_unique_key(foo, bar=1, baz=2),
        autocache.generate_unique_key(foo, baz=2, bar=1),
        autocache.generate_unique_key(foo, 1, baz=2)
    )
