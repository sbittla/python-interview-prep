import pytest


def test_examples(load):
    m = load("ex01_comprehensions")
    assert m.even_squares([1, 2, 3, 4]) == [4, 16]
    assert m.word_lengths(["Hi", "there"]) == {"hi": 2, "there": 5}
    assert m.invert({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
    assert m.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


@pytest.mark.parametrize("matrix, expected", [
    ([], []),
    ([[1]], [[1]]),
    ([[1, 2]], [[1], [2]]),
    ([[1], [2], [3]], [[1, 2, 3]]),
])
def test_transpose_edges(load, matrix, expected):
    assert load("ex01_comprehensions").transpose(matrix) == expected


def test_invert_versions_agree(load):
    m = load("ex01_comprehensions")
    d = {f"k{i}": i % 4 for i in range(20)}
    assert m.invert(d) == m.invert_one_pass(d)
    assert m.invert({}) == {}


def test_empty_inputs(load):
    m = load("ex01_comprehensions")
    assert m.even_squares([]) == []
    assert m.word_lengths([]) == {}
    assert m.even_squares([-2, -1, 0]) == [4, 0]
