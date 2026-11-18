def test_example(load):
    m = load("ex12_sudoku_solver")
    sol = m.solve(m.PUZZLE)
    assert sol[0] == "534678912"
    assert m.is_valid_solution(sol)
    for given_row, row in zip(m.PUZZLE, sol):
        assert all(g == "." or g == d for g, d in zip(given_row, row))
    assert m.PUZZLE[0] == "53..7...."                   # input untouched


def test_brute_force_agrees(load):
    m = load("ex12_sudoku_solver")
    assert m.brute_force(m.PUZZLE) == m.solve(m.PUZZLE)


def test_hard_puzzle(load):
    m = load("ex12_sudoku_solver")
    sol = m.solve(m.HARD)
    assert sol is not None and m.is_valid_solution(sol)


def test_conflicting_givens(load):
    m = load("ex12_sudoku_solver")
    bad = ["55" + m.PUZZLE[0][2:]] + m.PUZZLE[1:]
    assert m.solve(bad) is None


def test_already_solved(load):
    m = load("ex12_sudoku_solver")
    sol = m.solve(m.PUZZLE)
    assert m.solve(sol) == sol
