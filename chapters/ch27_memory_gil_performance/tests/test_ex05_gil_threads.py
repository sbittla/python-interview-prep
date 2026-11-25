import sys
import time


def test_gil_enabled_matches_interpreter(load):
    m = load("ex05_gil_threads")
    expected = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    assert m.gil_enabled() is expected


def test_sleep_bound_threads_overlap(load):
    assert load("ex05_gil_threads").speedup(lambda: time.sleep(0.03), 4) > 2


def test_report_matches_build(load):
    m = load("ex05_gil_threads")
    report = m.report()
    assert set(report) == {"gil enabled", "threads overlap sleep-bound work",
                           "threads speed up CPU-bound work", "CPU result matches the build"}
    assert report["threads overlap sleep-bound work"] is True
    if m.gil_enabled():
        assert report["threads speed up CPU-bound work"] is False   # never 1.5x with a GIL
    assert report["CPU result matches the build"] is True
