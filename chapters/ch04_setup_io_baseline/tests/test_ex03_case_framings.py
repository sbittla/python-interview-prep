import io

import pytest


def test_examples(load):
    m = load("ex03_case_framings")
    assert m.read_until_sentinel(["3 4\n", "10 2\n", "0 0\n", "9 9\n"]) == [(3, 4), (10, 2)]
    assert m.read_until_eof(["1 2 3\n", "\n", "4\n"]) == [[1, 2, 3], [4]]
    assert m.read_blocks(["1 2\n", "3\n", "\n", "\n", "4\n"]) == [[[1, 2], [3]], [[4]]]


@pytest.mark.parametrize("lines, expected", [
    ([], []),
    (["0 0\n"], []),
    (["5 6"], [(5, 6)]),                        # sentinel missing: stop at EOF
    (["0 1\n", "1 0\n", "0 0\n"], [(0, 1), (1, 0)]),  # only (0, 0) is the sentinel
    (["\n", "2 3\r\n", "0 0\r\n"], [(2, 3)]),
])
def test_sentinel_edge_cases(load, lines, expected):
    assert load("ex03_case_framings").read_until_sentinel(lines) == expected


def test_until_eof_with_stringio(load):
    m = load("ex03_case_framings")
    assert m.read_until_eof(io.StringIO("7\n  \n-1 -2\r\n\n3 4 5")) == [[7], [-1, -2], [3, 4, 5]]
    assert m.read_until_eof(io.StringIO("")) == []


@pytest.mark.parametrize("text, expected", [
    ("", []),
    ("\n\n\n", []),
    ("1\n", [[[1]]]),                           # final flush with no trailing blank line
    ("\n\n1 2\n\n\n3\n\n", [[[1, 2]], [[3]]]),
    ("1\r\n \t \r\n2\r\n", [[[1]], [[2]]]),      # whitespace-only line counts as blank
])
def test_blocks_edge_cases(load, text, expected):
    assert load("ex03_case_framings").read_blocks(io.StringIO(text)) == expected


def test_naive_split_breaks_on_crlf(load):
    m = load("ex03_case_framings")
    crlf = "1 2\r\n3\r\n\r\n4\r\n"
    assert m.read_blocks_naive(crlf) != m.read_blocks(io.StringIO(crlf, newline=""))
    assert m.read_blocks(io.StringIO(crlf, newline="")) == [[[1, 2], [3]], [[4]]]
