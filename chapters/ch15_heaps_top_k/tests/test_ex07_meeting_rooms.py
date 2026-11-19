import random

import pytest


def test_examples(load):
    m = load("ex07_meeting_rooms")
    assert m.solve([(0, 30), (5, 10), (15, 20)]) == 2
    assert m.solve([(1, 5), (5, 8)]) == 1
    assert m.assign_rooms([(0, 30), (5, 10), (15, 20)]) == [0, 1, 1]


@pytest.mark.parametrize("ms, expected", [
    ([], 0), ([(1, 2)], 1), ([(1, 3), (1, 3), (1, 3)], 3),
    ([(1, 2), (2, 3), (3, 4)], 1), ([(7, 10), (2, 4)], 1),
])
def test_edge_cases(load, ms, expected):
    m = load("ex07_meeting_rooms")
    assert m.solve(ms) == m.brute_force(ms) == m.by_sweep(ms) == expected
    assert len(set(m.assign_rooms(ms))) == expected


def _valid(ms, rooms):
    for r in set(rooms):
        mine = sorted(x for x, rr in zip(ms, rooms) if rr == r)
        if any(a[1] > b[0] for a, b in zip(mine, mine[1:])):
            return False
    return True


def test_random_vs_brute(load):
    m = load("ex07_meeting_rooms")
    rng = random.Random(9)
    for _ in range(400):
        ms = []
        for _ in range(rng.randint(0, 12)):
            s = rng.randint(0, 15)
            ms.append((s, s + rng.randint(1, 5)))
        n = m.solve(ms)
        assert n == m.brute_force(ms) == m.by_sweep(ms)
        rooms = m.assign_rooms(ms)
        assert len(rooms) == len(ms) and _valid(ms, rooms)
        assert sorted(set(rooms)) == list(range(n))
