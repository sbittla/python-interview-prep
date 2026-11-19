import random
from collections import Counter

import pytest


def _methods(m):
    return (m.solve, m.by_sort, m.by_nsmallest, m.by_size_k_heap, m.by_bucket)


def test_examples(load):
    m = load("ex03_top_k_frequent_words")
    assert m.solve(["b", "a", "c", "a", "b", "d"], 2) == ["a", "b"]
    assert m.solve(["to", "be", "or", "not", "to", "be"], 3) == ["be", "to", "not"]


@pytest.mark.parametrize("words, k, expected", [
    (["cat"], 1, ["cat"]),
    (["z", "y", "x"], 2, ["x", "y"]),                  # all tie -> alphabetical
    (["b", "b", "a", "a", "c"], 1, ["a"]),              # the naive heap keeps "b"
    (["aa", "a", "a", "aa", "b"], 3, ["a", "aa", "b"]),
])
def test_edge_cases(load, words, k, expected):
    m = load("ex03_top_k_frequent_words")
    for fn in _methods(m):
        assert fn(words, k) == expected


def test_random_ties_vs_sort(load):
    m = load("ex03_top_k_frequent_words")
    rng = random.Random(4)
    for _ in range(400):
        words = [rng.choice(["ab", "a", "b", "ba", "c", "ca"]) for _ in range(rng.randint(1, 20))]
        k = rng.randint(1, len(set(words)))
        c = Counter(words)
        expected = sorted(c, key=lambda w: (-c[w], w))[:k]
        for fn in _methods(m):
            assert fn(words, k) == expected
