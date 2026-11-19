import io
import random

import pytest


def test_examples(load):
    m = load("ex01_bulk_token_reader")
    assert m.solve(b"2\n3 1 2 3\n1 -5\n") == "Case #1: 6 3\nCase #2: -5 -5"
    assert m.solve(b"1\n4 1\n2\n3 4\n") == "Case #1: 10 4"
    assert m.solve(b"1\n0\n") == "Case #1: 0 -"


@pytest.mark.parametrize("data, expected", [
    (b"", ""),                                        # no input at all
    (b"0\n", ""),                                     # zero test cases
    (b"1\r\n2 7 -9\r\n", "Case #1: -2 7"),            # CRLF bytes (raw sys.stdin.buffer)
    (b"  1 \n\n\t3   5 5 5  \n\n", "Case #1: 15 5"),  # blank lines, tabs, extra spaces
    (b"1 1 123456789012345678901234567890", "Case #1: 123456789012345678901234567890 "
     "123456789012345678901234567890"),               # no trailing newline, big int
])
def test_edge_cases(load, data, expected):
    assert load("ex01_bulk_token_reader").solve(data) == expected


def test_tokens_are_bytes(load):
    m = load("ex01_bulk_token_reader")
    assert list(m.tokens(b"a  b\r\nc")) == [b"a", b"b", b"c"]


def test_line_reader_matches_on_one_case_per_line(load):
    m = load("ex01_bulk_token_reader")
    rng = random.Random(4)
    for _ in range(100):
        cases = [[rng.randint(-50, 50) for _ in range(rng.randint(0, 6))] for _ in range(rng.randint(0, 5))]
        text = f"{len(cases)}\n" + "".join(f"{len(c)} {' '.join(map(str, c))}\n" for c in cases)
        assert m.solve_lines(io.StringIO(text).readline) == m.solve(text.encode())


def test_line_reader_rejects_wrapped_case(load):
    m = load("ex01_bulk_token_reader")
    with pytest.raises(ValueError):
        m.solve_lines(io.StringIO("1\n3 1\n2 3\n").readline)
