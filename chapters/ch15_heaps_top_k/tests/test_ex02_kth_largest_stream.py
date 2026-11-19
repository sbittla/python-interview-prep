import random

import pytest


def test_examples(load):
    m = load("ex02_kth_largest_stream")
    assert m.solve(3, [4, 5, 8, 2], [3, 5, 10, 9, 4]) == [4, 5, 5, 8, 8]
    assert m.solve(2, [], [7, 7, 1]) == [None, 7, 7]


@pytest.mark.parametrize("k, init, stream, expected", [
    (1, [], [5], [5]),
    (3, [1], [2], [None]),
    (2, [9, 9, 9], [9], [9]),
    (1, [-3], [-5, -1], [-3, -1]),
])
def test_edge_cases(load, k, init, stream, expected):
    m = load("ex02_kth_largest_stream")
    for cls in (m.KthLargest, m.KthLargestSort, m.KthLargestInsort):
        assert m.solve(k, init, stream, cls) == expected


def test_random_vs_sort(load):
    m = load("ex02_kth_largest_stream")
    rng = random.Random(3)
    for _ in range(300):
        init = [rng.randint(-3, 3) for _ in range(rng.randint(0, 6))]
        stream = [rng.randint(-3, 3) for _ in range(rng.randint(1, 10))]
        k = rng.randint(1, 6)
        seen, expected = list(init), []
        for x in stream:
            seen.append(x)
            expected.append(sorted(seen)[-k] if len(seen) >= k else None)
        for cls in (m.KthLargest, m.KthLargestSort, m.KthLargestInsort):
            assert m.solve(k, init, stream, cls) == expected


def test_heap_stays_size_k(load):
    m = load("ex02_kth_largest_stream")
    t = m.KthLargest(4, list(range(100)))
    for x in range(50):
        t.add(x)
    assert len(t.heap) == 4
