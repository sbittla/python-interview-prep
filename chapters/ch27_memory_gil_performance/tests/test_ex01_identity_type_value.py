import platform

import pytest

CPYTHON = platform.python_implementation() == "CPython"


@pytest.mark.parametrize("x, y, expected", [
    ([1], [1], {"same_object": False, "equal": True, "same_type": True}),
    (1, 1.0, {"same_object": False, "equal": True, "same_type": False}),
    (None, None, {"same_object": True, "equal": True, "same_type": True}),
    (True, 1, {"same_object": False, "equal": True, "same_type": False}),
    ("a", "b", {"same_object": False, "equal": False, "same_type": True}),
])
def test_describe(load, x, y, expected):
    assert load("ex01_identity_type_value").describe(x, y) == expected


def test_alias_is_same_object(load):
    m = load("ex01_identity_type_value")
    a = [1, 2]
    b = a
    assert m.describe(a, b)["same_object"] is True


def test_nan_is_itself_but_not_equal(load):
    m = load("ex01_identity_type_value")
    nan = float("nan")
    assert m.describe(nan, nan) == {"same_object": True, "equal": False, "same_type": True}


@pytest.mark.skipif(not CPYTHON, reason="small-int cache is a CPython detail")
@pytest.mark.parametrize("n, cached", [(-6, False), (-5, True), (0, True), (256, True),
                                       (257, False), (10**6, False)])
def test_small_int_cache(load, n, cached):
    assert load("ex01_identity_type_value").runtime_ints_identical(n) is cached


@pytest.mark.skipif(not CPYTHON, reason="small-int cache is a CPython detail")
def test_cached_range(load):
    m = load("ex01_identity_type_value")
    assert m.cached_int_range(-10, 300) == (-5, 256)
    assert m.cached_int_range(0, 3) == (0, 3)
    assert m.cached_int_range(300, 400) is None


@pytest.mark.skipif(not CPYTHON, reason="interning is a CPython detail")
def test_interning(load):
    m = load("ex01_identity_type_value")
    assert m.interned_equal(["hello", "_", "world"]) == (False, True)
    assert m.interned_equal(["not an ", "identifier!"]) == (False, True)
