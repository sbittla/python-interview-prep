import random

import pytest


def test_examples(load):
    m = load("ex04_merge_feeds")
    assert m.merge_feeds([[(1, "a"), (5, "e")], [(2, "b")], []]) == [(1, "a"), (2, "b"), (5, "e")]
    assert m.running_kth_largest([5, 1, 7, 3, 9], 2) == [None, 1, 5, 5, 7]


@pytest.mark.parametrize("feeds, expected", [
    ([], []),
    ([[], []], []),
    ([[(1, "x")]], [(1, "x")]),
    ([[(2, "b")], [(2, "a")]], [(2, "a"), (2, "b")]),
])
def test_merge_edges(load, feeds, expected):
    assert load("ex04_merge_feeds").merge_feeds(feeds) == expected


def test_merge_random(load):
    m = load("ex04_merge_feeds")
    rng = random.Random(4)
    for _ in range(100):
        feeds = [sorted((rng.randint(0, 20), rng.choice("abc")) for _ in range(rng.randint(0, 6)))
                 for _ in range(rng.randint(0, 5))]
        assert m.merge_feeds(feeds) == m.brute_force_merge(feeds) == m.merge_with_stdlib(feeds)


def test_kth_largest(load):
    m = load("ex04_merge_feeds")
    assert m.running_kth_largest([], 3) == []
    assert m.running_kth_largest([4, 4, 4], 2) == [None, 4, 4]
    assert m.running_kth_largest([-1, -5], 1) == [-1, -1]
    rng = random.Random(44)
    for _ in range(100):
        s = [rng.randint(-9, 9) for _ in range(rng.randint(0, 12))]
        k = rng.randint(1, 4)
        assert m.running_kth_largest(s, k) == m.brute_force_kth(s, k)
