import pytest


def test_examples(load):
    m = load("ex03_union_find_costs")
    assert m.adversarial_hops(5, compress=False, by_rank=False) == 10
    assert m.adversarial_hops(5, compress=True, by_rank=True) == 6
    assert m.binomial_find_hops(8, compress=False, by_rank=True, rounds=1) == 12


@pytest.mark.parametrize("n", [1, 2, 10, 500])
def test_naive_is_quadratic(load, n):
    m = load("ex03_union_find_costs")
    assert m.adversarial_hops(n, False, False) == n * (n - 1) // 2


@pytest.mark.parametrize("compress, by_rank", [(True, False), (False, True), (True, True)])
def test_optimised_is_linear_on_chain(load, compress, by_rank):
    m = load("ex03_union_find_costs")
    assert m.adversarial_hops(2000, compress, by_rank) <= 2 * 2000


def test_rank_bounds_height(load):
    m = load("ex03_union_find_costs")
    assert m.chain_height(1000, by_rank=False) == 999
    assert m.chain_height(1000, by_rank=True) == 1
    uf = m.UnionFind(1024, compress=False, by_rank=True)
    size = 1
    while size < 1024:
        for i in range(0, 1024, 2 * size):
            uf.union(i, i + size)
        size *= 2
    assert uf.height() == 10                       # log2 n: the rank bound is tight


def test_compression_helps_binomial(load):
    m = load("ex03_union_find_costs")
    rank_only = m.binomial_find_hops(1024, compress=False, by_rank=True, rounds=3)
    both = m.binomial_find_hops(1024, compress=True, by_rank=True, rounds=3)
    assert rank_only == 3 * 1024 * 5               # average depth log2(n) / 2
    assert both < rank_only / 3


def test_connectivity(load):
    m = load("ex03_union_find_costs")
    for compress in (False, True):
        for by_rank in (False, True):
            uf = m.UnionFind(6, compress, by_rank)
            assert uf.union(0, 1) and uf.union(2, 3) and uf.union(1, 3)
            assert not uf.union(0, 2)
            assert uf.find(0) == uf.find(3) and uf.find(4) != uf.find(0)
            assert uf.find(5) == 5


def test_find_is_iterative(load):
    m = load("ex03_union_find_costs")
    uf = m.UnionFind(20_000, compress=False, by_rank=False)
    for i in range(19_999):
        uf.union(i, i + 1)
    assert uf.find(0) == 19_999                    # no RecursionError
