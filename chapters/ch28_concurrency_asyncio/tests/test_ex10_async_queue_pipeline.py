import pytest


def test_examples(load):
    m = load("ex10_async_queue_pipeline")
    assert m.run_virtual(m.pipeline(4, 2, maxsize=1, arrival=0, work=1.0)) == (
        [(0, 0), (1, 1), (2, 4), (3, 9)], 1, 2.0)


@pytest.mark.parametrize("n, k, expected_secs", [(8, 1, 3.3), (8, 2, 1.8), (8, 4, 1.2),
                                                 (8, 8, 1.2), (1, 3, 0.5)])
def test_elapsed_and_results(load, n, k, expected_secs):
    m = load("ex10_async_queue_pipeline")
    res, peak, secs = m.run_virtual(m.pipeline(n, k, maxsize=2, arrival=0.1, work=0.4))
    assert res == [(i, i * i) for i in range(n)]
    assert 1 <= peak <= 2
    assert secs == pytest.approx(expected_secs)


def test_backpressure_bounds_queue(load):
    m = load("ex10_async_queue_pipeline")
    _, peak, _ = m.run_virtual(m.pipeline(50, 1, maxsize=3, arrival=0, work=1.0))
    assert peak == 3                       # producer outruns the worker, capped by maxsize


def test_poison_does_not_kill_worker(load):
    m = load("ex10_async_queue_pipeline")
    res, _, secs = m.run_virtual(m.pipeline(4, 1, maxsize=1, arrival=0, work=0.5,
                                            poison=frozenset({0, 2})))
    assert res == [(0, "error"), (1, 1), (2, "error"), (3, 9)]
    assert secs == 2.0


def test_empty(load):
    m = load("ex10_async_queue_pipeline")
    assert m.run_virtual(m.pipeline(0, 3, maxsize=1, arrival=0, work=1)) == ([], 0, 0.0)
