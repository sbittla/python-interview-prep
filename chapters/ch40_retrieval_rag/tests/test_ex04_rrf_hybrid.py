import random

import pytest


def test_examples(load):
    m = load("ex04_rrf_hybrid")
    assert m.rrf([["a", "b", "c"], ["b", "c", "a"]], k=60) == [
        ("b", 0.032522), ("a", 0.032266), ("c", 0.032002)]


def test_formula_one_based_ranks(load):
    m = load("ex04_rrf_hybrid")
    (doc, score), = m.rrf([["x"]], k=60)
    assert doc == "x" and score == round(1 / 61, 6)           # rank 1 -> 1/(60+1), not 1/60
    assert dict(m.rrf([["x", "y"], ["y"]], k=10))["y"] == round(1 / 12 + 1 / 11, 6)


def test_missing_and_duplicates(load):
    m = load("ex04_rrf_hybrid")
    assert m.rrf([["a", "a", "b"], ["c"]]) == [("a", 0.016393), ("c", 0.016393), ("b", 0.015873)]
    assert m.rrf([]) == [] and m.rrf([[], []]) == []


def test_k_changes_the_winner(load):
    m = load("ex04_rrf_hybrid")
    lists = [["a", "b", "c", "d"], ["c", "b", "d", "a"]]
    assert [d for d, _ in m.rrf(lists, k=1)] == ["c", "a", "b", "d"]
    assert [d for d, _ in m.rrf(lists, k=60)] == ["c", "b", "a", "d"]   # consistency rewarded


def test_fusion_can_rank_below_every_list(load):
    m = load("ex04_rrf_hybrid")
    assert m.rrf([["a", "r", "b"], ["b", "r", "a"]]) == [
        ("a", 0.032266), ("b", 0.032266), ("r", 0.032258)]      # r: 2nd in both, 3rd fused


def test_top_n_and_bad_k(load):
    m = load("ex04_rrf_hybrid")
    assert len(m.rrf([["a", "b", "c"]], top_n=2)) == 2
    with pytest.raises(ValueError):
        m.rrf([["a"]], k=0)


def test_rrf_random_against_definition(load):
    m = load("ex04_rrf_hybrid")
    rng = random.Random(404)
    for _ in range(200):
        lists = [rng.sample("abcdefgh", rng.randint(0, 8)) for _ in range(rng.randint(1, 4))]
        k = rng.randint(1, 80)
        exp = {}
        for lst in lists:
            for r, d in enumerate(lst, 1):
                exp[d] = exp.get(d, 0.0) + 1 / (k + r)
        want = sorted(((d, round(s, 6)) for d, s in exp.items()), key=lambda p: (-p[1], p[0]))
        assert m.rrf(lists, k) == want


def test_score_fusions(load):
    m = load("ex04_rrf_hybrid")
    overlap = [("d1", 4.0), ("d2", 3.0), ("d3", 1.0)]
    cosine = [("d3", 0.41), ("d2", 0.39), ("d1", 0.05)]
    assert [d for d, _ in m.naive_sum([overlap, cosine])] == ["d1", "d2", "d3"]   # counts dominate
    assert m.minmax_fusion([overlap, cosine]) == [("d2", 1.6111), ("d1", 1.0), ("d3", 1.0)]
    assert m.minmax_fusion([[("a", 2.0), ("b", 2.0)]]) == [("a", 1.0), ("b", 1.0)]   # flat list
    assert m.minmax_fusion([overlap, cosine], [0.0, 1.0])[0] == ("d3", 1.0)
    assert m.minmax_fusion([[], cosine])[0][0] == "d3"


def test_hybrid_on_corpus(load):
    m = load("ex04_rrf_hybrid")
    from ragkit import dense_ranking, keyword_ranking, load_corpus, load_queries
    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    for q in load_queries():
        kw = keyword_ranking(q["query"], docs)
        de = [d for d, _ in dense_ranking(q["query"], docs)]
        hy = m.hybrid(q["query"], docs)
        assert sorted(hy) == sorted(set(kw) | set(de))
        assert hy == [d for d, _ in m.rrf([kw, de])]
    assert m.hybrid("make objects undeletable for regulators", docs)[0] == "d04"
