import math
import random

import pytest

M = "ex03_grid_paths"


def test_examples(load):
    m = load(M)
    assert m.unique_paths([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
    assert m.min_path([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == (7, "RRDD")


@pytest.mark.parametrize("grid, expected", [
    ([[0]], 1), ([[1]], 0), ([[0, 1], [0, 0]], 1), ([[1, 0], [0, 0]], 0),
    ([[0, 0], [0, 1]], 0), ([[0, 0], [1, 1], [0, 0]], 0), ([[0, 0, 0, 0]], 1),
    ([[0], [0], [0]], 1), ([[0, 1, 0, 0]], 0),
])
def test_unique_paths_edges(load, grid, expected):
    m = load(M)
    assert m.unique_paths(grid) == expected
    assert m.unique_paths_table(grid) == m.unique_paths_memo(grid) == expected


@pytest.mark.parametrize("rows, cols", [(1, 1), (3, 7), (10, 10), (18, 4)])
def test_unique_paths_no_rocks_is_binomial(load, rows, cols):
    m = load(M)
    grid = [[0] * cols for _ in range(rows)]
    assert m.unique_paths(grid) == math.comb(rows + cols - 2, rows - 1)


def _replay(grid, moves):
    r = c = 0
    total = grid[0][0]
    for mv in moves:
        r, c = (r + 1, c) if mv == "D" else (r, c + 1)
        total += grid[r][c]
    assert (r, c) == (len(grid) - 1, len(grid[0]) - 1)
    return total


def test_random_grids_against_brute(load):
    m = load(M)
    rng = random.Random(5)
    for _ in range(150):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        rocks = [[int(rng.random() < 0.25) for _ in range(cols)] for _ in range(rows)]
        assert m.unique_paths(rocks) == m.unique_paths_brute(rocks)
        costs = [[rng.randint(0, 9) for _ in range(cols)] for _ in range(rows)]
        best = m.min_path_sum_brute(costs)
        assert m.min_path_sum(costs) == m.min_path_sum_table(costs) == m.min_path_sum_memo(costs) == best
        total, moves = m.min_path(costs)
        assert total == best == _replay(costs, moves)
        assert len(moves) == rows + cols - 2


def test_single_cell_and_lines(load):
    m = load(M)
    assert m.min_path([[5]]) == (5, "")
    assert m.min_path([[1, 2, 3]]) == (6, "RR")
    assert m.min_path([[1], [2], [3]]) == (6, "DD")
