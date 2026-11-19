import io

import pytest


def test_examples(load):
    m = load("ex04_fast_output")
    assert m.format_row([1, 2, 3]) == "1 2 3"
    assert m.format_cases(["YES", 7]) == "Case #1: YES\nCase #2: 7"
    assert m.format_float(2 / 3, 3) == "0.667"
    assert m.format_float(-0.0001, 2) == "0.00"
    assert m.format_bool(False) == "NO"


@pytest.mark.parametrize("x, places, expected", [
    (0.0, 2, "0.00"),
    (-0.0, 3, "0.000"),
    (-1e-12, 6, "0.000000"),
    (-0.5, 1, "-0.5"),
    (0.1 + 0.2, 2, "0.30"),
    (2.675, 2, "2.67"),            # 2.675 is stored as 2.67499...
    (1234.5, 0, "1234"),           # .0f rounds half to even
    (7, 3, "7.000"),
])
def test_format_float(load, x, places, expected):
    assert load("ex04_fast_output").format_float(x, places) == expected


def test_row_and_cases_edge_cases(load):
    m = load("ex04_fast_output")
    assert m.format_row([]) == ""
    assert m.format_row(["a", 1, None]) == "a 1 None"
    assert m.format_row(x * x for x in range(3)) == "0 1 4"     # any iterable
    assert m.format_cases([]) == ""
    assert m.format_bool(True) == "YES"


def test_write_lines_single_write_and_matches_print(load):
    m = load("ex04_fast_output")

    class Recorder(io.StringIO):
        calls = 0

        def write(self, s):
            Recorder.calls += 1
            return super().write(s)

    lines = [str(i) for i in range(500)]
    out = Recorder()
    m.write_lines(lines, out)
    assert Recorder.calls == 1
    ref = io.StringIO()
    m.print_loop(lines, ref)
    assert out.getvalue() == ref.getvalue() == "\n".join(lines) + "\n"


def test_write_lines_empty_writes_nothing(load):
    out = io.StringIO()
    load("ex04_fast_output").write_lines([], out)
    assert out.getvalue() == ""
