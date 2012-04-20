import autocache


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
