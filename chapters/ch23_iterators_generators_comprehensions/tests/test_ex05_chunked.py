from itertools import count, islice

import pytest


@pytest.mark.parametrize("data, n, expected", [
    (range(7), 3, [[0, 1, 2], [3, 4, 5], [6]]),
    ([], 3, []),
    ("abcd", 2, [["a", "b"], ["c", "d"]]),
    ([1], 5, [[1]]),
    (range(3), 1, [[0], [1], [2]]),
])
def test_chunked(load, data, n, expected):
    m = load("ex05_chunked")
    assert list(m.chunked(data, n)) == expected
    assert list(m.chunked_manual(data, n)) == expected
    assert m.chunked_slicing(list(data), n) == expected


def test_works_on_generators_and_infinite(load):
    m = load("ex05_chunked")
    assert list(m.chunked((x for x in range(5)), 2)) == [[0, 1], [2, 3], [4]]
    assert list(islice(m.chunked(count(), 3), 2)) == [[0, 1, 2], [3, 4, 5]]


def test_bad_n(load):
    m = load("ex05_chunked")
    for fn in (m.chunked, m.chunked_manual):
        with pytest.raises(ValueError):
            list(fn([1, 2], 0))
    with pytest.raises(ValueError):
        m.chunked_slicing([1], 0)


def test_padded(load):
    m = load("ex05_chunked")
    assert m.chunked_padded("abcde", 2, ".") == [("a", "b"), ("c", "d"), ("e", ".")]
