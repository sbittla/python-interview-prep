import pytest


def test_fake_clock(load):
    clock = load("ex06_timing_logging").FakeClock(0.5)
    assert [clock(), clock(), clock()] == [0.0, 0.5, 1.0]


def test_timed_reports_and_stores(load):
    m = load("ex06_timing_logging")
    reports = []
    f = m.timed(clock=m.FakeClock(0.25), report=reports.append)(lambda x: x * 2)
    assert f.last_elapsed is None
    assert f(4) == 8
    assert f.last_elapsed == 0.25 and reports == ["<lambda> took 0.250s"]


def test_timed_on_exception(load):
    m = load("ex06_timing_logging")
    reports = []

    @m.timed(clock=m.FakeClock(2.0), report=reports.append)
    def boom():
        raise ValueError("x")

    with pytest.raises(ValueError):
        boom()
    assert reports == ["boom took 2.000s"] and boom.last_elapsed == 2.0


def test_log_calls_success_and_failure(load):
    m = load("ex06_timing_logging")
    lines = []

    @m.log_calls(lines.append)
    def divide(a, b=1):
        return a / b

    assert divide(9, b=2) == 4.5
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
    assert lines == [
        "call divide(9, b=2)", "divide -> 4.5",
        "call divide(1, 0)", "divide raised ZeroDivisionError('division by zero')",
    ]
    assert divide.__name__ == "divide"


def test_log_calls_uses_repr(load):
    m = load("ex06_timing_logging")
    lines = []
    m.log_calls(lines.append)(lambda s: None)("a b")
    assert lines == ["call <lambda>('a b')", "<lambda> -> None"]


def test_default_clock_is_real(load):
    m = load("ex06_timing_logging")
    f = m.timed(report=lambda msg: None)(sum)
    assert f([1, 2]) == 3 and f.last_elapsed >= 0.0
