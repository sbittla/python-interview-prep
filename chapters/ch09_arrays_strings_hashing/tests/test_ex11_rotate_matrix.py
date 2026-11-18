import pytest


def test_examples(load):
    m = load("ex11_rotate_matrix")
    assert m.solve([[1, 2], [3, 4]]) == [[3, 1], [4, 2]]
    assert m.solve([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]


def test_in_place(load):
    m = load("ex11_rotate_matrix")
    grid = [[1, 2], [3, 4]]
    assert m.solve(grid) is grid


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 5, 6])
def test_methods_agree(load, n):
    m = load("ex11_rotate_matrix")
    grid = [[r * n + c for c in range(n)] for r in range(n)]
    expected = [list(row) for row in zip(*grid[::-1])]
    assert m.solve([r[:] for r in grid]) == expected
    assert m.brute_force([r[:] for r in grid]) == expected
    assert m.rotate_layers([r[:] for r in grid]) == expected
    four = [r[:] for r in grid]
    for _ in range(4):
        m.solve(four)
    assert four == grid


def test_ccw(load):
    m = load("ex11_rotate_matrix")
    assert m.rotate_ccw([[1, 2], [3, 4]]) == [[2, 4], [1, 3]]
