import random

import pytest


def test_examples(load):
    m = load("ex09_cpu_scheduler")
    assert m.solve([(1, 2), (2, 4), (3, 2), (4, 1)]) == [0, 2, 3, 1]
    assert m.solve([(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)]) == [4, 3, 2, 0, 1]


@pytest.mark.parametrize("jobs, expected", [
    ([], []), ([(5, 1)], [0]),
    ([(0, 3), (0, 3), (0, 3)], [0, 1, 2]),              # full tie -> index order
    ([(0, 5), (100, 1), (1, 3), (1, 3)], [0, 2, 3, 1]),  # idle gap before job 1
    ([(0, 10**9), (1, 1), (2 * 10**9, 3)], [0, 1, 2]),
])
def test_edge_cases(load, jobs, expected):
    m = load("ex09_cpu_scheduler")
    assert m.solve(jobs) == m.brute_force(jobs) == expected


def test_random_vs_brute(load):
    m = load("ex09_cpu_scheduler")
    rng = random.Random(11)
    for _ in range(400):
        jobs = [(rng.randint(0, 12), rng.randint(1, 3)) for _ in range(rng.randint(0, 12))]
        order = m.solve(jobs)
        assert sorted(order) == list(range(len(jobs)))
        assert order == m.brute_force(jobs)
