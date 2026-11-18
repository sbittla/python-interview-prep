import pytest


@pytest.mark.parametrize("data, n, expected", [
    ([1, 2, 3, 4], 2, [(1, 2), (2, 3), (3, 4)]),
    ([1, 2], 3, []),
    ([], 1, []),
    ("abc", 3, [("a", "b", "c")]),
])
def test_windowed(load, data, n, expected):
    m = load("ex06_sliding_window")
    assert list(m.windowed(data, n)) == expected
    assert m.windowed_slicing(list(data), n) == expected


def test_windowed_generator_input(load):
    m = load("ex06_sliding_window")
    assert list(m.windowed((x for x in range(4)), 3)) == [(0, 1, 2), (1, 2, 3)]


def test_moving_average(load):
    m = load("ex06_sliding_window")
    assert list(m.moving_average([1, 2, 3, 4, 5], 3)) == [2.0, 3.0, 4.0]
    data = [5, 1, 7, 3, 9, 2, 8]
    for n in range(1, 8):
        assert list(m.moving_average(iter(data), n)) == m.moving_average_naive(data, n)
    assert list(m.moving_average([1, 2], 3)) == []


def test_bad_n(load):
    m = load("ex06_sliding_window")
    with pytest.raises(ValueError):
        list(m.windowed([1], 0))
    with pytest.raises(ValueError):
        list(m.moving_average([1], 0))
