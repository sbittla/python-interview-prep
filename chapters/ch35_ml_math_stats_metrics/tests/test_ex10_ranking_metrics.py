import random
from math import log2

import pytest


def test_examples(load):
    m = load("ex10_ranking_metrics")
    r, rel = ["a", "b", "c", "d"], {"a", "c", "x"}
    assert m.precision_at_k(r, rel, 3) == pytest.approx(2 / 3)
    assert m.recall_at_k(r, rel, 3) == pytest.approx(2 / 3)
    assert m.reciprocal_rank(["b", "a"], {"a"}) == 0.5


def test_ap_by_hand(load):
    m = load("ex10_ranking_metrics")
    ranked, rel = ["d3", "d1", "d7", "d2", "d9"], {"d1", "d2", "d4"}
    assert m.ap_at_k(ranked, rel, 5) == pytest.approx((1 / 2 + 2 / 4) / 3)
    assert m.ap_at_k(ranked, rel, 3) == pytest.approx((1 / 2) / 3)
    assert m.ap_at_k(["a", "b"], {"a", "b"}, 1) == 1.0          # divisor min(|rel|, k) = 1


def test_ap_fast_equals_brute(load):
    m = load("ex10_ranking_metrics")
    rng = random.Random(10)
    for _ in range(300):
        docs = list(range(20))
        rng.shuffle(docs)
        ranked = docs[: rng.randint(1, 15)]
        rel = set(rng.sample(range(20), rng.randint(0, 6)))
        k = rng.randint(1, 20)
        assert m.ap_at_k(ranked, rel, k) == pytest.approx(m.ap_at_k_brute(ranked, rel, k))


def test_mrr_and_map(load):
    m = load("ex10_ranking_metrics")
    runs = [(["x", "a"], {"a"}), (["a"], {"a"}), (["x", "y"], {"z"})]
    assert m.mrr(runs) == pytest.approx((0.5 + 1 + 0) / 3)
    assert m.map_at_k(runs, 2) == pytest.approx((0.5 + 1 + 0) / 3)


def test_ndcg_by_hand(load):
    m = load("ex10_ranking_metrics")
    gains = {"d1": 3, "d2": 2, "d3": 0, "d4": 1, "d7": 1}
    dcg = 0 + 7 / log2(3) + 1 / 2
    idcg = 7 + 3 / log2(3) + 1 / 2
    assert m.ndcg_at_k(["d3", "d1", "d7", "d2"], gains, 3) == pytest.approx(dcg / idcg)
    lin = (3 / log2(3) + 1 / 2) / (3 + 2 / log2(3) + 1 / 2)
    assert m.ndcg_at_k(["d3", "d1", "d7"], gains, 3, exp_gain=False) == pytest.approx(lin)


def test_ndcg_bounds_and_ideal(load):
    m = load("ex10_ranking_metrics")
    rng = random.Random(11)
    for _ in range(100):
        gains = {i: rng.randint(0, 3) for i in range(6)}
        ranked = list(range(6))
        rng.shuffle(ranked)
        k = rng.randint(1, 6)
        v = m.ndcg_at_k(ranked, gains, k)
        assert 0.0 <= v <= 1.0 + 1e-12
        ideal = sorted(gains, key=lambda d: -gains[d])
        if any(gains.values()):
            assert m.ndcg_at_k(ideal, gains, k) == pytest.approx(1.0)
            assert m._dcg(sorted(gains.values(), reverse=True)[:k], True) == pytest.approx(m.idcg_brute(gains, k))


def test_edge_cases(load):
    m = load("ex10_ranking_metrics")
    assert m.precision_at_k(["a"], {"a"}, 5) == 0.2               # missing slots are misses
    assert m.reciprocal_rank(["x"], {"a"}) == 0.0
    assert m.ap_at_k(["a"], set(), 3) == 0.0
    assert m.ndcg_at_k(["a", "b"], {"a": 0}, 2) == 0.0
    with pytest.raises(ValueError):
        m.recall_at_k(["a"], set(), 1)
