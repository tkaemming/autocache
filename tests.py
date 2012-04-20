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


def test_backend():
    """
    Test basic cache backend interface compatibility.
    """
    cache = SimpleCacheBackend()

    @autocache.cached(backend=cache)
    def foo(x):
        foo.counter += 1
        return x ** x

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

    @autocache.cached(backend=cache)
    def bar(x):
        bar.counter += 1
        return x ** (x + 1)

    bar.counter = 0

    bar(1)
    assert len(cache.values) == 3
    assert bar.counter == 1

    bar(2)
    assert len(cache.values) == 4
    assert bar.counter == 2


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
