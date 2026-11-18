import pytest


def test_examples(load):
    m = load("ex11_n_queens")
    assert m.solve(4) == [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]
    assert m.solve(1) == [["Q"]]
    assert m.solve(2) == [] and m.solve(3) == []


@pytest.mark.parametrize("n, expected", [(1, 1), (4, 2), (5, 10), (6, 4), (8, 92), (10, 724)])
def test_count(load, n, expected):
    m = load("ex11_n_queens")
    assert m.count(n) == expected


@pytest.mark.parametrize("n", [5, 6, 7])
def test_matches_brute_force(load, n):
    m = load("ex11_n_queens")
    assert m.solve(n) == m.brute_force(n)


def test_boards_are_valid(load):
    m = load("ex11_n_queens")
    for board in m.solve(8):
        cols = [row.index("Q") for row in board]
        assert len(set(cols)) == 8
        assert len({r - c for r, c in enumerate(cols)}) == 8
        assert len({r + c for r, c in enumerate(cols)}) == 8
