import pytest

BOARD = ["ABCE", "SFCS", "ADEE"]


@pytest.mark.parametrize("word, expected", [("ABCCED", True), ("SEE", True), ("ABCB", False),
                                            ("A", True), ("Z", False), ("ESCCBA", True),
                                            ("ABCESEEDAS", True), ("SFCSECB", False)])
def test_examples(load, word, expected):
    m = load("ex10_word_search")
    board = [list(r) for r in BOARD]
    assert m.solve(board, word) is expected
    assert board == [list(r) for r in BOARD]          # board restored
    assert m.brute_force([list(r) for r in BOARD], word) is expected


def test_cell_reuse_not_allowed(load):
    m = load("ex10_word_search")
    assert m.solve([["A", "B"]], "ABA") is False
