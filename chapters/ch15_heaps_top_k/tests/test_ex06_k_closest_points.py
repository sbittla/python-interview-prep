import random

import pytest


def test_examples(load):
    m = load("ex06_k_closest_points")
    assert m.solve([(1, 3), (-2, 2), (2, -2)], 2) == [(-2, 2), (2, -2)]
    assert m.solve([(0, 5), (3, 4), (5, 0)], 1, target=(3, 3)) == [(3, 4)]


@pytest.mark.parametrize("pts, k, expected", [
    ([], 0, []),
    ([(4, 4)], 0, []),
    ([(1, 0), (0, 1), (-1, 0), (0, -1)], 3, [(-1, 0), (0, -1), (0, 1)]),
    ([(2, 2), (2, 2), (1, 1)], 2, [(1, 1), (2, 2)]),
    ([(5, 0), (3, 4)], 2, [(3, 4), (5, 0)]),            # equal distance 25 -> by x
])
def test_edge_cases(load, pts, k, expected):
    m = load("ex06_k_closest_points")
    for fn in (m.solve, m.brute_force, m.by_nsmallest, m.by_max_heap):
        assert fn(pts, k) == expected


def test_random_ties_vs_sort(load):
    m = load("ex06_k_closest_points")
    rng = random.Random(8)
    for _ in range(400):
        pts = [(rng.randint(-3, 3), rng.randint(-3, 3)) for _ in range(rng.randint(0, 25))]
        k = rng.randint(0, len(pts))
        t = (rng.randint(-2, 2), rng.randint(-2, 2))
        expected = sorted(pts, key=lambda p: ((p[0] - t[0]) ** 2 + (p[1] - t[1]) ** 2, p))[:k]
        assert m.solve(pts, k, t) == expected
        assert m.by_nsmallest(pts, k, t) == expected
