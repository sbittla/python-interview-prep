import heapq
import random

import pytest


def test_examples(load):
    m = load("ex01_min_heap")
    h = m.MinHeap([5, 3, 8, 1])
    assert (h.pop(), h.pop(), len(h)) == (1, 3, 2)
    assert m.solve([4, 1, 3, 1]) == [1, 1, 3, 4]


def test_empty_heap_raises(load):
    m = load("ex01_min_heap")
    h = m.MinHeap()
    for op in (h.pop, h.peek, lambda: h.replace(1)):
        with pytest.raises(IndexError):
            op()
    assert h.pushpop(3) == 3 and len(h) == 0      # pushpop on empty returns x
    assert m.solve([]) == []


def test_heapify_is_valid_and_linear(load):
    m = load("ex01_min_heap")
    n = 2 ** 12 - 1
    h = m.MinHeap(range(n, 0, -1))
    assert m.is_min_heap(h.as_list())
    assert h.swaps <= n                            # O(n) build: at most ~n swaps
    assert m.build_by_pushes(range(n, 0, -1)).swaps > 5 * n


def test_random_ops_match_heapq(load):
    m = load("ex01_min_heap")
    rng = random.Random(1)
    for _ in range(200):
        init = [rng.randint(-5, 5) for _ in range(rng.randint(0, 10))]
        h, ref = m.MinHeap(init), list(init)
        heapq.heapify(ref)
        for _ in range(30):
            op, x = rng.choice(["push", "pop", "pushpop", "replace"]), rng.randint(-5, 5)
            if op == "push":
                h.push(x)
                heapq.heappush(ref, x)
            elif op == "pushpop":
                assert h.pushpop(x) == heapq.heappushpop(ref, x)
            elif ref and op == "pop":
                assert h.pop() == heapq.heappop(ref)
            elif ref:
                assert h.replace(x) == heapq.heapreplace(ref, x)
            assert len(h) == len(ref) and m.is_min_heap(h.as_list())
            if ref:
                assert h.peek() == ref[0]


def test_random_sort_all_rungs(load):
    m = load("ex01_min_heap")
    rng = random.Random(2)
    for _ in range(200):
        xs = [rng.randint(-3, 3) for _ in range(rng.randint(0, 25))]
        assert m.solve(xs) == m.brute_force(xs) == sorted(xs)
