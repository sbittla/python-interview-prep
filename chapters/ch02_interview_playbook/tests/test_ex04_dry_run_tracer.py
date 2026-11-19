import sys

import pytest


def test_example(load):
    m = load("ex04_dry_run_tracer")
    rows, result = m.trace(m.count_pairs, [2, 2], 4)
    assert rows[0] == (0, {"nums": "[2, 2]", "target": "4"})
    assert result == 1


def test_rows_follow_lines(load):
    m = load("ex04_dry_run_tracer")
    rows, result = m.trace(m.count_pairs, [1, 3], 4)
    assert result == 1
    assert [line for line, _ in rows] == [0, 1, 2, 3, 4, 5, 3, 4, 5, 3, 6]
    assert rows[7] == (4, {"pairs": "1"})
    assert rows[8] == (5, {"seen": "{1: 1, 3: 1}"})


def test_detects_mutation(load):
    m = load("ex04_dry_run_tracer")

    def grow(a):
        a.append(1)
        return len(a)

    rows, result = m.trace(grow, [])
    assert result == 1
    assert rows[1] == (1, {"a": "[1]"})


def test_empty_input(load):
    m = load("ex04_dry_run_tracer")
    rows, result = m.trace(m.count_pairs, [], 0)
    assert result == 0
    assert [line for line, _ in rows] == [0, 1, 2, 3, 6]


def test_infinite_loop_guard_and_restore(load):
    m = load("ex04_dry_run_tracer")
    before = sys.gettrace()
    with pytest.raises(RuntimeError):
        m.trace(m.spin, 3, max_steps=50)
    assert sys.gettrace() is before
    _, result = m.trace(m.spin, 4)
    assert result == 0


def test_render(load):
    m = load("ex04_dry_run_tracer")
    rows, _ = m.trace(m.count_pairs, [1, 3], 4)
    out = m.render(m.count_pairs, rows)
    assert len(out) == len(rows)
    assert "(call)" in out[0] and "nums=[1, 3]" in out[0]
    assert "return pairs" in out[-1]
    assert out[4].rstrip().endswith("-")      # the first L4 changes nothing


def _helper(v):
    w = v * 2
    return w + 1


def test_called_helper_is_not_traced(load):
    m = load("ex04_dry_run_tracer")

    def outer(a):
        b = _helper(a)
        return b

    rows, result = m.trace(outer, 3)
    assert result == 7
    assert [line for line, _ in rows] == [0, 1, 2]
    assert all("w" not in changes and "v" not in changes for _, changes in rows)
