import random

import pytest


def test_examples(load):
    m = load("ex03_burst_detection")
    assert m.max_in_window([0, 10, 59, 60, 61], 60) == 4
    assert m.per_minute([61, 0, 59, 125]) == [(0, 2), (60, 1), (120, 1)]
    assert m.flag_bursts([("a", 0), ("a", 5), ("b", 0)], 60, 1) == [("a", 2)]


@pytest.mark.parametrize("times, w, expected", [
    ([], 60, 0),
    ([5], 60, 1),
    ([7, 7, 7], 1, 3),
    ([0, 60], 60, 1),          # half-open: exactly w apart never share a window
    ([0, 59], 60, 2),
    ([60, 0, 59, 30], 60, 3),  # unsorted input
])
def test_edges(load, times, w, expected):
    assert load("ex03_burst_detection").max_in_window(times, w) == expected


def test_straddling_burst_beats_buckets(load):
    m = load("ex03_burst_detection")
    burst = list(range(50, 70, 2))
    assert max(c for _, c in m.per_minute(burst)) == 5
    assert m.max_in_window(burst, 60) == 10


def test_limit_is_strict_and_sorted(load):
    m = load("ex03_burst_detection")
    hits = [("b", t) for t in (0, 1, 2)] + [("a", t) for t in (9, 3, 5)]
    assert m.flag_bursts(hits, 60, 3) == []
    assert m.flag_bursts(hits, 60, 2) == [("a", 3), ("b", 3)]
    assert m.flag_bursts([], 60, 0) == []


def test_random_vs_brute(load):
    m = load("ex03_burst_detection")
    rng = random.Random(3)
    for _ in range(200):
        ts = [rng.randint(0, 300) for _ in range(rng.randint(0, 25))]
        w = rng.randint(1, 90)
        assert m.max_in_window(ts, w) == m.brute_max_in_window(ts, w)


def test_data_file(load):
    m = load("ex03_burst_detection")
    assert m.flag_bursts(m.load_ip_times(), 60, 5) == [("198.51.100.7", 9)]
