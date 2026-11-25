import threading

import pytest


def test_examples(load):
    m = load("ex02_queue_worker_pool")
    assert m.process_all([1, 2, 3], lambda x: x * 10, n_workers=2, maxsize=1)[0] == [10, 20, 30]
    assert m.process_all([1, 0], lambda x: 1 // x, n_workers=2, maxsize=4)[0] == [
        1, "error: ZeroDivisionError: integer division or modulo by zero"]


@pytest.mark.parametrize("n_workers, maxsize", [(1, 1), (3, 2), (8, 50)])
def test_matches_sequential_in_input_order(load, n_workers, maxsize):
    m = load("ex02_queue_worker_pool")
    items = list(range(40))
    res, peak = m.process_all(items, m.slow_square, n_workers, maxsize)
    assert res == m.sequential(items, m.slow_square)
    assert 1 <= peak <= maxsize


def test_empty_and_more_workers_than_items(load):
    m = load("ex02_queue_worker_pool")
    assert m.process_all([], m.slow_square, 4, 1) == ([], 0)
    assert m.process_all([2], m.slow_square, 5, 1)[0] == [4]


def test_all_threads_finish(load):
    m = load("ex02_queue_worker_pool")
    before = threading.active_count()
    m.process_all(list(range(10)), m.slow_square, 6, 2)
    assert threading.active_count() == before


def test_uses_multiple_workers(load):
    # A Barrier(3) only opens if three workers run func at the same time.
    m = load("ex02_queue_worker_pool")
    barrier = threading.Barrier(3)
    res, _ = m.process_all([1, 2, 3], lambda x: barrier.wait(timeout=5) * 0 + x, 3, 3)
    assert res == [1, 2, 3]
