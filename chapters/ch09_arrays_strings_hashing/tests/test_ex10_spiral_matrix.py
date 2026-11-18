import random

import pytest


def test_examples(load):
    m = load("ex10_spiral_matrix")
    assert m.solve([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert m.diagonals([[1, 2], [3, 4]]) == [[1], [2, 3], [4]]


@pytest.mark.parametrize("grid, expected", [
    ([], []), ([[]], []), ([[1, 2, 3]], [1, 2, 3]), ([[1], [2], [3]], [1, 2, 3]),
    ([[1, 2], [3, 4], [5, 6]], [1, 2, 4, 6, 5, 3]),
])
def test_edge_cases(load, grid, expected):
    assert load("ex10_spiral_matrix").solve(grid) == expected


def test_random_against_simulation(load):
    m = load("ex10_spiral_matrix")
    rng = random.Random(10)
    for _ in range(100):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[r * cols + c for c in range(cols)] for r in range(rows)]
        out = m.solve(grid)
        assert out == m.brute_force(grid)
        assert sorted(out) == list(range(rows * cols))
