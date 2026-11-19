import heapq
import random
from itertools import count, islice

import pytest


def test_examples(load):
    m = load("ex04_merge_k_iterators")
    assert list(m.solve([[1, 4, 7], [2, 5], [], [3, 6, 9]])) == [1, 2, 3, 4, 5, 6, 7, 9]
    assert list(islice(m.solve([count(0, 3), count(0, 5)]), 6)) == [0, 0, 3, 5, 6, 9]


@pytest.mark.parametrize("srcs", [[], [[]], [[], []], [[1]], [[1, 1], [1]]])
def test_edge_cases(load, srcs):
    m = load("ex04_merge_k_iterators")
    expected = sorted(x for s in srcs for x in s)
    assert list(m.solve(srcs)) == m.brute_force(srcs) == m.one_by_one(srcs) == expected


def test_is_lazy(load):
    m = load("ex04_merge_k_iterators")
    pulled = []

    def gen(tag, vals):
        for v in vals:
            pulled.append(tag)
            yield v

    g = m.solve([gen("a", [1, 2, 3]), gen("b", [10, 11])])
    assert next(g) == 1
    assert len(pulled) == 2                           # one head per source, nothing more


def test_payloads_and_stability(load):
    m = load("ex04_merge_k_iterators")
    srcs = [[{"t": 1, "s": 0}, {"t": 2, "s": 0}], [{"t": 1, "s": 1}], [{"t": 1, "s": 2}]]
    out = list(m.solve(srcs, key=lambda d: d["t"]))
    assert [(d["t"], d["s"]) for d in out] == [(1, 0), (1, 1), (1, 2), (2, 0)]


def test_random_vs_sorted(load):
    m = load("ex04_merge_k_iterators")
    rng = random.Random(5)

    def key(p):
        return p[0]                                   # ties on key; p[1] shows the source

    for _ in range(300):
        srcs = [sorted((rng.randint(0, 5), i) for _ in range(rng.randint(0, 6)))
                for i in range(rng.randint(0, 5))]
        expected = sorted((p for s in srcs for p in s), key=key)
        assert m.brute_force(srcs, key=key) == expected
        assert list(m.solve(srcs, key=key)) == expected
        assert m.one_by_one(srcs, key=key) == expected
        assert list(heapq.merge(*srcs, key=key)) == expected
