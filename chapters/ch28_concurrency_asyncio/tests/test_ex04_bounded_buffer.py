import threading

import pytest


def bounded(fn, *args, timeout=10):
    """Run fn in a daemon thread; fail (instead of hanging pytest) if it does not finish."""
    box = {}

    def target():
        try:
            box["value"] = fn(*args)
        except BaseException as exc:          # re-raised in the test thread below
            box["error"] = exc

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    assert not t.is_alive(), f"{getattr(fn, '__name__', fn)} hung (deadlock?)"
    if "error" in box:
        raise box["error"]
    return box["value"]


def test_examples(load):
    m = load("ex04_bounded_buffer")
    b = m.BoundedBuffer(2)
    b.put("a")
    b.put("b")
    assert (b.get(), b.get()) == ("a", "b")
    with pytest.raises(TimeoutError):
        m.BoundedBuffer(1).get(timeout=0.01)


def test_put_times_out_when_full(load):
    b = load("ex04_bounded_buffer").BoundedBuffer(1)
    b.put(1)
    with pytest.raises(TimeoutError):
        b.put(2, timeout=0.01)
    assert b.get() == 1 and b.max_seen == 1


def test_put_blocks_until_get(load):
    b = load("ex04_bounded_buffer").BoundedBuffer(1)
    b.put("x")
    done = threading.Event()

    def producer():
        b.put("y")                 # must block: buffer is full
        done.set()

    t = threading.Thread(target=producer, daemon=True)
    t.start()
    assert not done.wait(0.05)     # still blocked
    assert b.get() == "x"
    assert done.wait(5)            # unblocked by the get
    t.join(5)
    assert not t.is_alive()
    assert b.get() == "y"


def test_fifo_single_thread(load):
    b = load("ex04_bounded_buffer").BoundedBuffer(5)
    for i in range(5):
        b.put(i)
    assert [b.get() for _ in range(5)] == list(range(5))


@pytest.mark.parametrize("p, per, c, cap", [(3, 200, 2, 4), (1, 100, 4, 1), (5, 50, 5, 2),
                                            (2, 0, 3, 3)])
def test_pipeline_exactly_once_and_bounded(load, p, per, c, cap):
    items, peak = bounded(load("ex04_bounded_buffer").run_pipeline, p, per, c, cap)
    assert items == sorted((i, s) for i in range(p) for s in range(per))
    assert peak <= cap
