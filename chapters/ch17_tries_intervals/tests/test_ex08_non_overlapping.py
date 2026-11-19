import random

import pytest


def test_examples(load):
    m = load("ex08_non_overlapping")
    iv = [[1, 2], [2, 3], [3, 4], [1, 3]]
    assert m.solve(iv) == (1, [3])
    assert m.solve(iv, closed=True) == (2, [1, 3])
    assert m.solve([[1, 2], [1, 2], [1, 2]]) == (2, [1, 2])
    assert m.solve([]) == (0, [])


@pytest.mark.parametrize("intervals", [[[1, 10], [2, 3], [4, 5], [6, 7]], [[1, 5], [4, 7], [6, 10]]])
def test_tempting_rules_lose(load, intervals):
    m = load("ex08_non_overlapping")
    assert m.solve(intervals)[0] == m.brute_force(intervals) == 1
    if intervals[0] == [1, 10]:
        assert m.wrong_by_start(intervals) == 3


def _kept_is_valid(m, ivs, removed, closed):
    gone = set(removed)
    kept = [iv for i, iv in enumerate(ivs) if i not in gone]
    return all(m._compatible(a, b, closed) for i, a in enumerate(kept) for b in kept[i + 1:])


def test_random_against_brute(load):
    m = load("ex08_non_overlapping")
    rng = random.Random(8)
    for _ in range(250):
        ivs = []
        for _ in range(rng.randint(0, 8)):
            s = rng.randint(0, 8)
            ivs.append([s, s + rng.randint(1, 3)])
        for closed in (False, True):
            count, removed = m.solve(ivs, closed)
            assert count == m.brute_force(ivs, closed) == m.dp(ivs, closed), (ivs, closed)
            assert len(removed) == count and _kept_is_valid(m, ivs, removed, closed)
