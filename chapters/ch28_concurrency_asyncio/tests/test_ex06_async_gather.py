import pytest


def test_examples(load):
    m = load("ex06_async_gather")
    jobs = [("a", 0.2), ("b", 0.1)]
    assert m.run_virtual(m.run_sequential(jobs)) == (["a:0.2", "b:0.1"], 0.3)
    assert m.run_virtual(m.run_gather(jobs)) == (["a:0.2", "b:0.1"], 0.2)
    assert m.run_virtual(m.run_as_completed(jobs)) == (["b", "a"], 0.2)


def test_gather_is_concurrent_and_ordered(load):
    m = load("ex06_async_gather")
    jobs = [(f"j{i}", d) for i, d in enumerate([0.5, 0.1, 0.4, 0.2, 0.3])]
    res, secs = m.run_virtual(m.run_gather(jobs))
    assert res == [f"j{i}:{d}" for i, d in enumerate([0.5, 0.1, 0.4, 0.2, 0.3])]
    assert secs == 0.5                              # max, not sum (1.5)
    assert m.run_virtual(m.run_sequential(jobs))[1] == 1.5


def test_as_completed_order(load):
    m = load("ex06_async_gather")
    jobs = [("slow", 0.9), ("fast", 0.1), ("mid", 0.5)]
    assert m.run_virtual(m.run_as_completed(jobs)) == (["fast", "mid", "slow"], 0.9)


def test_gather_safe_keeps_slots(load):
    m = load("ex06_async_gather")
    jobs = [("bad-1", 0.1), ("ok", 0.2), ("bad-2", 0.3)]
    assert m.run_virtual(m.run_gather_safe(jobs)) == (
        ["error: ConnectionError", "ok:0.2", "error: ConnectionError"], 0.3)


def test_plain_gather_propagates(load):
    m = load("ex06_async_gather")
    with pytest.raises(ConnectionError):
        m.run_virtual(m.run_gather([("ok", 0.2), ("bad", 0.1)]))


@pytest.mark.parametrize("fn", ["run_sequential", "run_gather", "run_as_completed",
                                "run_gather_safe"])
def test_empty(load, fn):
    m = load("ex06_async_gather")
    assert m.run_virtual(getattr(m, fn)([])) == ([], 0.0)
