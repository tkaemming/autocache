from autocache.hashing import argument_hash, bytecode_hash, source_hash
from autocache.utils import convert_dict_to_tuple


def test_callable_hashing():
    """
    Test callable hashing implementations.
    """
    def foo(x):
        return x

    def bar(x):
        return x

    # assert runtime determinism
    assert bytecode_hash(foo) == bytecode_hash(foo)
    assert source_hash(foo) == source_hash(foo)

    # different functions with the same implementation will have the same hash
    assert bytecode_hash(foo) == bytecode_hash(bar)

    # but not for source hashing -- the names are different
    assert source_hash(foo) != source_hash(bar)


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
        argument_hash(foo, 1, 2, 3, 4, a=1, b=2, c=3),
        argument_hash(foo, 1, 2, 3, 4, b=2, a=1, c=3),
        argument_hash(foo, 1, 2, 3, 4, b=2, c=3, a=1),
        argument_hash(foo, a=1, b=2, c=3, *(1, 2, 3, 4)),
        argument_hash(foo, 1, 2, *(3, 4), **{'a': 1, 'b': 2, 'c': 3}),
    )

    check(
        argument_hash(foo, 1, 2),
        argument_hash(foo, bar=1, baz=2),
        argument_hash(foo, baz=2, bar=1),
        argument_hash(foo, 1, baz=2)
    )


def test_dictionary_conversion():
    """
    Test converting dictionaries to tuples and ensuring proper key order.
    """
    assert convert_dict_to_tuple({}) == ()

    expected = (('a', 1), ('b', 2))
    assert convert_dict_to_tuple({'a': 1, 'b': 2}) == expected
    assert convert_dict_to_tuple({'b': 2, 'a': 1}) == expected
