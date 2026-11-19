import random
from collections import deque

import pytest


def test_examples(load):
    m = load("ex10_queue_via_stacks")
    q = m.StackQueue()
    q.push(1)
    q.push(2)
    assert q.pop() == 1
    q.push(3)
    assert (q.peek(), q.pop(), q.pop(), len(q)) == (2, 2, 3, 0)


@pytest.mark.parametrize("cls, methods", [
    ("StackQueue", ("pop", "peek")), ("NaiveQueue", ("pop", "peek")),
    ("QueueStack", ("pop", "top")),
])
def test_empty_raises(load, cls, methods):
    obj = getattr(load("ex10_queue_via_stacks"), cls)()
    for name in methods:
        with pytest.raises(IndexError):
            getattr(obj, name)()


def test_random_queue_against_deque(load):
    m = load("ex10_queue_via_stacks")
    rng = random.Random(29)
    q, naive, ref, pushes = m.StackQueue(), m.NaiveQueue(), deque(), 0
    for _ in range(3000):
        if ref and rng.random() < 0.45:
            assert q.peek() == naive.peek() == ref[0]
            assert q.pop() == naive.pop() == ref.popleft()
        else:
            x = rng.randint(0, 99)
            q.push(x)
            naive.push(x)
            ref.append(x)
            pushes += 1
        assert len(q) == len(naive) == len(ref)
    assert q.moves <= pushes                    # each element moved at most once


def test_random_stack_against_list(load):
    m = load("ex10_queue_via_stacks")
    rng = random.Random(31)
    s, ref = m.QueueStack(), []
    for _ in range(1000):
        if ref and rng.random() < 0.45:
            assert s.top() == ref[-1]
            assert s.pop() == ref.pop()
        else:
            x = rng.randint(0, 99)
            s.push(x)
            ref.append(x)
        assert len(s) == len(ref)
