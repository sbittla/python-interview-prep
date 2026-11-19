import random

import pytest

CLASSES = ["NaiveMinStack", "TwoStackMinStack", "MinStack"]


def test_examples(load):
    m = load("ex03_min_stack")
    s = m.MinStack()
    for x in (5, 2, 7):
        s.push(x)
    assert s.get_min() == 2
    assert s.pop() == 7 and s.pop() == 2
    assert s.get_min() == 5 and s.top() == 5


@pytest.mark.parametrize("cls", CLASSES)
def test_duplicate_minimum(load, cls):
    s = getattr(load("ex03_min_stack"), cls)()
    for x in (3, 1, 1):
        s.push(x)
    s.pop()
    assert s.get_min() == 1
    s.pop()
    assert s.get_min() == 3


@pytest.mark.parametrize("cls", CLASSES)
def test_empty_raises(load, cls):
    s = getattr(load("ex03_min_stack"), cls)()
    for method in ("pop", "top", "get_min"):
        with pytest.raises(IndexError):
            getattr(s, method)()


def test_random_ops_against_naive(load):
    m = load("ex03_min_stack")
    rng = random.Random(5)
    for _ in range(50):
        stacks = [getattr(m, c)() for c in CLASSES]
        size = 0
        for _ in range(200):
            if size and rng.random() < 0.4:
                assert len({s.pop() for s in stacks}) == 1
                size -= 1
            else:
                x = rng.randint(-5, 5)
                for s in stacks:
                    s.push(x)
                size += 1
            if size:
                assert len({s.get_min() for s in stacks}) == 1
                assert len({s.top() for s in stacks}) == 1
