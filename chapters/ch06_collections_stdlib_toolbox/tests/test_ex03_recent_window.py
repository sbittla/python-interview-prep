import random

import pytest


def test_examples(load):
    m = load("ex03_recent_window")
    hc = m.HitCounter(300)
    for t in (1, 2, 300):
        hc.hit(t)
    assert (hc.count(300), hc.count(301)) == (3, 2)
    rv = m.RecentlyViewed(2)
    for x in "aba":
        rv.view(x)
    assert rv.items() == ["a", "b"]
    assert m.moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_hitcounter_boundaries(load):
    m = load("ex03_recent_window")
    hc = m.HitCounter(5)
    assert hc.count(0) == 0
    hc.hit(10)
    hc.hit(10)
    assert hc.count(14) == 2      # (9, 14] contains 10
    assert hc.count(15) == 0      # (10, 15] excludes 10


def test_hitcounter_random(load):
    m = load("ex03_recent_window")
    rng = random.Random(3)
    hc, seen, t = m.HitCounter(7), [], 0
    for _ in range(500):
        t += rng.randint(0, 3)
        if rng.random() < 0.6:
            hc.hit(t)
            seen.append(t)
        else:
            assert hc.count(t) == sum(1 for s in seen if t - 7 < s <= t)


@pytest.mark.parametrize("capacity, views, expected", [
    (1, "abc", ["c"]),
    (3, "aaa", ["a"]),
    (3, "abcab", ["b", "a", "c"]),
    (2, "", []),
])
def test_recently_viewed(load, capacity, views, expected):
    rv = load("ex03_recent_window").RecentlyViewed(capacity)
    for v in views:
        rv.view(v)
    assert rv.items() == expected


def test_moving_average_edges(load):
    m = load("ex03_recent_window")
    assert m.moving_average([], 1) == []
    assert m.moving_average([5], 2) == []
    assert m.moving_average([4, 8], 1) == [4.0, 8.0]
    rng = random.Random(33)
    vals = [rng.randint(-50, 50) for _ in range(60)]
    for k in (1, 3, 10, 60):
        got = m.moving_average(vals, k)
        assert got == pytest.approx(m.brute_force_moving_average(vals, k))
