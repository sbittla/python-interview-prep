import threading

import pytest


def test_increment_is_several_instructions(load):
    m = load("ex10_gil_not_thread_safety")
    assert m.bytecode_steps(m.bump) > 1

    def nothing():
        pass

    assert m.bytecode_steps(nothing) == 0


@pytest.mark.parametrize("schedule, final", [
    ("", 0), ("AAA", 1), ("AAABBB", 2), ("AAAB" + "BB", 2), ("ABABAB", 1), ("AABBAB", 1),
    ("ABBBAA", 1), ("AAABBBCCC", 3), ("ABCABCABC", 1), ("AAABCBCBC", 2),
])
def test_schedules(load, schedule, final):
    assert load("ex10_gil_not_thread_safety").run_schedule(schedule) == final


@pytest.mark.parametrize("bad", ["AAAA", "AAB", "A", "ABABA"])
def test_invalid_schedules(load, bad):
    with pytest.raises(ValueError):
        load("ex10_gil_not_thread_safety").run_schedule(bad)


class CountingLock:
    """Stands in for threading.Lock and counts how often it is entered."""
    made = 0
    entered = 0

    def __init__(self):
        CountingLock.made += 1
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        CountingLock.entered += 1          # counted while holding the lock: exact
        return self

    def __exit__(self, *exc):
        self._lock.release()
        return False

    def acquire(self, *args, **kwargs):
        got = self._lock.acquire(*args, **kwargs)
        if got:
            CountingLock.entered += 1
        return got

    def release(self):
        self._lock.release()


@pytest.mark.parametrize("threads, per_thread", [(1, 10), (4, 20_000), (8, 1000)])
def test_locked_total_takes_the_lock_every_time(load, monkeypatch, threads, per_thread):
    m = load("ex10_gil_not_thread_safety")
    CountingLock.made = CountingLock.entered = 0
    monkeypatch.setattr(m, "Lock", CountingLock)    # module-level name only; threading untouched
    assert m.locked_total(threads, per_thread) == threads * per_thread
    assert CountingLock.made == 1                               # exactly one shared lock is used
    assert CountingLock.entered == threads * per_thread         # every increment is guarded
