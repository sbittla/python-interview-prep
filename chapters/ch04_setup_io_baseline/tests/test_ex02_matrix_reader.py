import io

import pytest


def rl(text):
    return io.StringIO(text).readline


def test_examples(load):
    m = load("ex02_matrix_reader")
    assert m.read_matrix(rl("2 3\n1 2 3\n4 5 6\n")) == [[1, 2, 3], [4, 5, 6]]
    assert m.read_grid(rl("2 3\r\n.#.\r\n##.")) == [".#.", "##."]
    assert m.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_reads_consecutive_blocks_from_one_stream(load):
    m = load("ex02_matrix_reader")
    readline = rl("1 2\n-1 7\n2 2\n#.\n.#\n")
    assert m.read_matrix(readline) == [[-1, 7]]
    assert m.read_grid(readline) == ["#.", ".#"]


@pytest.mark.parametrize("text, expected", [
    ("0 5\n", []),
    ("1 1\n42", [[42]]),                       # last line without newline
    ("2 2\r\n1 2\r\n3 4\r\n", [[1, 2], [3, 4]]),
    ("1 3\n  1   2\t3  \n", [[1, 2, 3]]),
])
def test_matrix_edge_cases(load, text, expected):
    assert load("ex02_matrix_reader").read_matrix(rl(text)) == expected


@pytest.mark.parametrize("text", ["2 2\n1 2\n3\n", "1 2\n1 2 3\n"])
def test_matrix_wrong_width_raises(load, text):
    with pytest.raises(ValueError):
        load("ex02_matrix_reader").read_matrix(rl(text))


def test_grid_wrong_width_raises(load):
    with pytest.raises(ValueError):
        load("ex02_matrix_reader").read_grid(rl("2 3\n...\n..\n"))


def test_naive_reader_shows_the_bug(load):
    m = load("ex02_matrix_reader")
    assert m.read_grid_naive(rl("2 3\r\n.#.\r\n##.")) == [".#.\r", "##"]


def test_transpose_edge_cases(load):
    m = load("ex02_matrix_reader")
    assert m.transpose([]) == []
    assert m.transpose([[1], [2]]) == [[1, 2]]
    t = m.transpose([[1, 2]])
    t[0].append(9)                             # rows are real lists, not tuples
    assert t == [[1, 9], [2]]
