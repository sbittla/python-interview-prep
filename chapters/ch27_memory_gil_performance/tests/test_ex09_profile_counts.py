import pytest


def fib_calls(n):
    return 1 if n < 2 else 1 + fib_calls(n - 1) + fib_calls(n - 2)


@pytest.mark.parametrize("n", [0, 1, 2, 10, 15])
def test_naive_fib_counts(load, n):
    m = load("ex09_profile_counts")
    assert m.call_counts(m.fib, n) == {"fib": fib_calls(n)}


@pytest.mark.parametrize("n", [0, 1, 10, 20])
def test_memo_fib_counts(load, n):
    m = load("ex09_profile_counts")
    assert m.call_counts(m.fib_memo_fresh, n) == {"fib_memo": 1 if n < 2 else n + 1}


def test_pipeline_counts(load):
    m = load("ex09_profile_counts")
    assert m.call_counts(m.build_report, 100) == {"build_report": 1, "load": 1, "pad_rows": 1}


def test_top_allocation_line(load):
    m = load("ex09_profile_counts")
    assert m.top_allocation_line(m.build_report, 20_000) == 'return [f"{v:>40}" for v in values]'
    assert m.top_allocation_line(m.load, 20_000) == "return list(range(n))"
