from functools import lru_cache

import pytest


def test_fib_counts(load):
    m = load("ex07_memoize")
    fib = m.make_fib(m.memoize)
    assert fib(30) == 832040
    assert (fib.misses, fib.hits) == (31, 28)
    assert fib(30) == 832040 and fib.hits == 29


def test_matches_lru_cache(load):
    m = load("ex07_memoize")
    ours, std = m.make_fib(m.memoize), m.make_fib(lru_cache(maxsize=None))
    for n in (0, 1, 10, 40):
        assert ours(n) == std(n)
    info = std.cache_info()
    assert (ours.hits, ours.misses) == (info.hits, info.misses)


def test_plain_call_count(load):
    m = load("ex07_memoize")
    assert [m.count_plain_calls(n) for n in (0, 1, 2, 10, 25)] == [1, 1, 3, 177, 242785]


def test_falsy_results_cached(load):
    m = load("ex07_memoize")
    calls = []

    @m.memoize
    def f(x):
        calls.append(x)
        return None if x else 0

    for _ in range(3):
        f(0)
        f(1)
    assert calls == [0, 1] and f.misses == 2 and f.hits == 4


def test_buggy_recomputes_falsy(load):
    m = load("ex07_memoize")
    buggy = m.memoize_buggy(lambda x: 0)
    buggy(5)
    buggy(5)
    assert buggy.misses == 2


def test_kwargs_order_and_distinct_keys(load):
    m = load("ex07_memoize")
    calls = []

    @m.memoize
    def area(w, h=1):
        calls.append((w, h))
        return w * h

    assert area(w=2, h=3) == area(h=3, w=2) == 6
    assert len(calls) == 1
    assert area(2, 3) == 6 and area(2) == 2       # positional forms are separate keys
    assert len(area.cache) == 3


def test_unhashable_and_clear(load):
    m = load("ex07_memoize")
    f = m.memoize(len)
    with pytest.raises(TypeError):
        f([1, 2])
    f("ab")
    f.cache_clear()
    assert (len(f.cache), f.hits, f.misses) == (0, 0, 0)
    assert f.__name__ == "len"
