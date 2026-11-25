import random

import pytest

CASES = [[], [7], [3, -1, 3, 0], [5, 4, 3, 2, 1], [2, 2, 2]]


@pytest.mark.parametrize("xs", CASES)
def test_fast_matches_slow(load, xs):
    m = load("ex08_builtin_speedups")
    assert m.fast_total(xs) == m.slow_total(xs) == sum(xs)
    assert m.fast_largest(xs) == m.slow_largest(xs)
    assert m.fast_sorted(xs) == m.slow_sorted(xs) == sorted(xs)


def test_largest_empty_is_none(load):
    assert load("ex08_builtin_speedups").fast_largest([]) is None


def test_common(load):
    m = load("ex08_builtin_speedups")
    assert m.fast_common([3, 1, 3, 2], [2, 3, 5]) == [2, 3]
    assert m.fast_common([], [1]) == []
    rng = random.Random(1)
    a = [rng.randrange(50) for _ in range(200)]
    b = [rng.randrange(50) for _ in range(200)]
    assert m.fast_common(a, b) == m.slow_common(a, b)


def test_fast_sorted_does_not_mutate(load):
    m = load("ex08_builtin_speedups")
    xs = [3, 1, 2]
    assert m.fast_sorted(xs) == [1, 2, 3]
    assert xs == [3, 1, 2]


def test_race_big_gaps(load):
    result = load("ex08_builtin_speedups").race(2_000)
    assert set(result) == {"total", "largest", "sorted", "common"}
    assert result["sorted"] is True and result["common"] is True     # better big-O: huge margin
