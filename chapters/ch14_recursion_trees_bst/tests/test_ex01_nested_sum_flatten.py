import random

import pytest


def random_nested(rng, depth=0):
    out = []
    for _ in range(rng.randint(0, 4)):
        if depth < 5 and rng.random() < 0.35:
            out.append(random_nested(rng, depth + 1))
        else:
            out.append(rng.randint(-9, 9))
    return out


def test_examples(load):
    m = load("ex01_nested_sum_flatten")
    assert m.depth_sum_recursive([1, [4, [6]]]) == 27
    assert m.depth_sum_iterative([[1, 1], 2, [1, 1]]) == 10
    assert m.flatten_iterative([1, [2, [3, 4]], [], 5]) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("nested, total, flat", [
    ([], 0, []), ([[[]]], 0, []), ([-3, [-2]], -7, [-3, -2]), ([[[[5]]]], 20, [5]),
    ([[1], [2], [3]], 12, [1, 2, 3]),
])
def test_edge_cases(load, nested, total, flat):
    m = load("ex01_nested_sum_flatten")
    assert m.depth_sum_recursive(nested) == m.depth_sum_iterative(nested) == total
    assert m.flatten_recursive(nested) == m.flatten_iterative(nested) == flat


def test_random_recursive_vs_iterative(load):
    m = load("ex01_nested_sum_flatten")
    rng = random.Random(1401)
    for _ in range(300):
        nested = random_nested(rng)
        assert m.depth_sum_iterative(nested) == m.depth_sum_recursive(nested)
        assert m.flatten_iterative(nested) == m.flatten_recursive(nested)


def test_deep_nesting_iterative_only(load):
    m = load("ex01_nested_sum_flatten")
    big = m.deep(20_000)
    assert m.depth_sum_iterative(big) == 20_000 * 20_001 // 2
    assert m.flatten_iterative(big) == [1] * 20_000
    with pytest.raises(RecursionError):
        m.depth_sum_recursive(big)
