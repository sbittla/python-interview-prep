import random

import pytest


def test_examples(load):
    q = load("ex11_circular_queue").CircularQueue(2)
    assert (q.enqueue(1), q.enqueue(2), q.enqueue(3)) == (True, True, False)
    assert (q.dequeue(), q.enqueue(3), q.front(), q.rear()) == (1, True, 2, 3)


@pytest.mark.parametrize("cls", ["CircularQueue", "NaiveBoundedQueue"])
def test_empty_and_capacity_one(load, cls):
    q = getattr(load("ex11_circular_queue"), cls)(1)
    assert q.is_empty() and not q.is_full()
    for name in ("dequeue", "front", "rear"):
        with pytest.raises(IndexError):
            getattr(q, name)()
    assert q.enqueue("a") and not q.enqueue("b")
    assert q.is_full() and q.front() == q.rear() == "a"
    assert q.dequeue() == "a" and q.is_empty()


@pytest.mark.parametrize("cap", [0, -2])
def test_bad_capacity(load, cap):
    with pytest.raises(ValueError):
        load("ex11_circular_queue").CircularQueue(cap)


def test_wraps_around(load):
    q = load("ex11_circular_queue").CircularQueue(3)
    out = []
    for i in range(10):
        assert q.enqueue(i)
        if i >= 2:
            out.append(q.dequeue())
    assert out == list(range(8)) and (q.front(), q.rear(), len(q)) == (8, 9, 2)


def test_random_against_naive(load):
    m = load("ex11_circular_queue")
    rng = random.Random(37)
    for cap in (1, 2, 3, 5):
        q, ref = m.CircularQueue(cap), m.NaiveBoundedQueue(cap)
        for _ in range(500):
            if rng.random() < 0.5:
                x = rng.randint(0, 9)
                assert q.enqueue(x) == ref.enqueue(x)
            elif not ref.is_empty():
                assert q.front() == ref.front() and q.rear() == ref.rear()
                assert q.dequeue() == ref.dequeue()
            assert (len(q), q.is_full(), q.is_empty()) == (len(ref), ref.is_full(), ref.is_empty())
