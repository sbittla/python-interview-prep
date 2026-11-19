import math
import random
from collections import Counter

import pytest


def test_example(load):
    counts = load("ex10_reservoir_shuffle").exact_counts("fisher_yates", 3)
    assert len(counts) == 6 and set(counts.values()) == {1}


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_fisher_yates_and_pick_pop_exactly_uniform(load, n):
    m = load("ex10_reservoir_shuffle")
    for algo in ("fisher_yates", "pick_pop"):
        counts = m.exact_counts(algo, n)
        assert len(counts) == math.factorial(n) and set(counts.values()) == {1}


@pytest.mark.parametrize("n", [3, 4])
def test_naive_shuffle_is_biased(load, n):
    counts = load("ex10_reservoir_shuffle").exact_counts("naive", n)
    assert sum(counts.values()) == n ** n
    assert len(set(counts.values())) > 1


@pytest.mark.parametrize("n, k", [(5, 2), (6, 3), (4, 4), (3, 1), (6, 0)])
def test_reservoir_exactly_uniform(load, n, k):
    counts = load("ex10_reservoir_shuffle").exact_counts("reservoir", n, k)
    assert len(counts) == math.comb(n, k) and len(set(counts.values())) == 1


def test_short_stream_and_bad_k(load):
    m = load("ex10_reservoir_shuffle")
    rng = random.Random(0)
    assert m.reservoir_sample(range(2), 5, rng.randrange) == [0, 1]
    assert m.reservoir_sample([], 3, rng.randrange) == []
    assert sorted(m.sample_brute(range(2), 5, rng)) == [0, 1]
    with pytest.raises(ValueError):
        m.reservoir_sample(range(5), -1, rng.randrange)
    with pytest.raises(ValueError):
        m.sample_brute(range(5), -1, rng)


def test_seeded_empirical(load):
    m = load("ex10_reservoir_shuffle")
    rng = random.Random(99)
    trials, n, k = 20_000, 5, 2
    hits = Counter(x for _ in range(trials) for x in m.reservoir_sample(iter(range(n)), k, rng.randrange))
    for x in range(n):
        assert abs(hits[x] - trials * k / n) < 0.04 * trials * k / n
    assert sorted(m.fisher_yates(list(range(10)), rng.randrange)) == list(range(10))
    assert sorted(m.shuffle_pick_pop(list("abc"), rng.randrange)) == list("abc")
