import random
import statistics

import pytest


def test_examples(load):
    m = load("ex05_streaming_median")
    assert m.solve([5, 15, 1, 3]) == [5, 10.0, 5, 4.0]
    assert m.solve([2, 2]) == [2, 2.0]


@pytest.mark.parametrize("cls_name", ["MedianFinder", "MedianSort", "MedianInsort"])
def test_empty_raises(load, cls_name):
    m = load("ex05_streaming_median")
    with pytest.raises(ValueError):
        getattr(m, cls_name)().median()


@pytest.mark.parametrize("stream", [[7], [10, 1], [-1, -2, -3, -4], [3, 3, 3], [1, 100, 2, 99]])
def test_edge_cases(load, stream):
    m = load("ex05_streaming_median")
    expected = [statistics.median(stream[: i + 1]) for i in range(len(stream))]
    for cls in (m.MedianFinder, m.MedianSort, m.MedianInsort):
        assert m.solve(stream, cls) == expected


def test_random_vs_statistics(load):
    m = load("ex05_streaming_median")
    rng = random.Random(6)
    for _ in range(200):
        stream = [rng.randint(-5, 5) for _ in range(rng.randint(1, 30))]
        expected = [statistics.median(stream[: i + 1]) for i in range(len(stream))]
        assert m.solve(stream) == expected
        assert m.solve(stream, m.MedianInsort) == expected


def test_heap_invariant(load):
    m = load("ex05_streaming_median")
    mf, rng = m.MedianFinder(), random.Random(7)
    for _ in range(200):
        mf.add(rng.randint(-50, 50))
        assert 0 <= len(mf.low) - len(mf.high) <= 1
        if mf.high:
            assert -mf.low[0] <= mf.high[0]
