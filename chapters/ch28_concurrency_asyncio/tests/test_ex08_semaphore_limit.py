import pytest


def test_examples(load):
    m = load("ex08_semaphore_limit")
    p = m.Probe()
    assert m.run_virtual(m.fetch_bounded(["a", "bb", "ccc"], 2, p)) == ["A", "BB", "CCC"]
    assert p.peak == 2


@pytest.mark.parametrize("fn", ["fetch_bounded", "fetch_worker_pool"])
@pytest.mark.parametrize("limit, rounds", [(1, 6), (2, 3), (4, 2), (6, 1), (10, 1)])
def test_peak_and_elapsed(load, fn, limit, rounds):
    m = load("ex08_semaphore_limit")
    urls = [f"u/{c}" for c in "abcdef"]             # 0.3 s each
    p = m.Probe()
    res, secs = m.run_virtual(m.timed(getattr(m, fn), urls, limit, p))
    assert res == [u.upper() for u in urls]
    assert p.peak == min(limit, len(urls))
    assert secs == pytest.approx(0.3 * rounds)
    assert p.now == 0


@pytest.mark.parametrize("fn", ["fetch_bounded", "fetch_worker_pool"])
def test_errors_release_slots(load, fn):
    m = load("ex08_semaphore_limit")
    urls = ["bad", "bad", "x", "bad", "yy"]
    p = m.Probe()
    out = m.run_virtual(getattr(m, fn)(urls, 2, p))
    assert out == ["error: ConnectionError"] * 2 + ["X", "error: ConnectionError", "YY"]
    assert p.peak == 2 and p.now == 0


@pytest.mark.parametrize("fn", ["fetch_bounded", "fetch_worker_pool"])
def test_empty(load, fn):
    m = load("ex08_semaphore_limit")
    assert m.run_virtual(getattr(m, fn)([], 3, m.Probe())) == []
