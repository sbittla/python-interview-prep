import random

import pytest

M = "ex11_tsp_bitmask"
D4 = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]


def _tour_cost(dist, tour):
    return sum(dist[a][b] for a, b in zip(tour, tour[1:]))


def test_examples(load):
    m = load(M)
    assert m.tsp(D4) == (80, [0, 2, 3, 1, 0])
    assert m.tsp_cost(D4) == 80


@pytest.mark.parametrize("dist, cost", [
    ([[0]], 0), ([[0, 4], [6, 0]], 10), ([[0, 1, 9], [9, 0, 1], [1, 9, 0]], 3), (D4, 80),
])
def test_edges(load, dist, cost):
    m = load(M)
    total, tour = m.tsp(dist)
    assert total == cost == m.tsp_memo(dist) == m.tsp_brute(dist)
    assert tour[0] == tour[-1] == 0
    assert sorted(tour[1:]) == list(range(len(dist)))
    assert _tour_cost(dist, tour) == cost


def test_asymmetric_direction_matters(load):
    m = load(M)
    one_way = [[0, 1, 9], [9, 0, 1], [1, 9, 0]]
    assert m.tsp(one_way) == (3, [0, 1, 2, 0])


def test_random_against_brute(load):
    m = load(M)
    rng = random.Random(41)
    for _ in range(60):
        n = rng.randint(1, 7)
        dist = [[0 if i == j else rng.randint(1, 20) for j in range(n)] for i in range(n)]
        total, tour = m.tsp(dist)
        assert total == m.tsp_brute(dist) == m.tsp_memo(dist)
        assert _tour_cost(dist, tour) == total
        assert sorted(tour[1:]) == list(range(n))
