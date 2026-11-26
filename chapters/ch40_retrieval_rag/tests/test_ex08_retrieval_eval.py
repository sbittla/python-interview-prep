import random

import pytest


def test_examples(load):
    m = load("ex08_retrieval_eval")
    assert m.recall_at_k(["d3", "d1", "d1", "d2"], {"d1", "d2"}, 3) == 1.0
    assert m.reciprocal_rank(["d3", "d1"], {"d1"}) == 0.5


@pytest.mark.parametrize("ranked, relevant, k, expected", [
    ([], {"a"}, 5, 0.0),
    (["a", "a", "a"], {"a", "b"}, 3, 0.5),        # duplicates do not earn extra credit
    (["x", "a", "b"], {"a", "b"}, 2, 0.5),
    (["x", "a", "b"], {"a", "b"}, 0, 0.0),
    (["a", "b"], {"a", "b", "c", "d"}, 10, 0.5),
])
def test_recall_cases(load, ranked, relevant, k, expected):
    assert load("ex08_retrieval_eval").recall_at_k(ranked, relevant, k) == expected


def test_recall_empty_relevant_raises(load):
    with pytest.raises(ValueError):
        load("ex08_retrieval_eval").recall_at_k(["a"], set(), 1)


@pytest.mark.parametrize("ranked, relevant, k, expected", [
    (["a"], {"a"}, None, 1.0), ([], {"a"}, None, 0.0), (["x", "y"], {"a"}, None, 0.0),
    (["x", "x", "a"], {"a"}, None, 0.5),           # rank computed after dedupe
    (["x", "y", "a"], {"a"}, 2, 0.0), (["x", "y", "a"], {"a"}, 3, 1 / 3),
])
def test_reciprocal_rank_cases(load, ranked, relevant, k, expected):
    assert load("ex08_retrieval_eval").reciprocal_rank(ranked, relevant, k) == pytest.approx(expected)


def test_to_docs(load):
    m = load("ex08_retrieval_eval")
    assert m.to_docs(["d06#1", "d06#0", "d15#0", "d06#2"]) == ["d06", "d15"]
    assert m.to_docs([]) == [] and m.to_docs(["plain"]) == ["plain"]


def test_evaluate_aggregates_and_skips(load):
    m = load("ex08_retrieval_eval")
    queries = [{"qid": "a", "query": "x", "relevant": ["1"]},
               {"qid": "b", "query": "y", "relevant": ["2", "3"]},
               {"qid": "c", "query": "z", "relevant": []}]
    runs = {"x": ["9", "1"], "y": ["3", "8", "2"], "z": ["1"]}
    res = m.evaluate(runs.__getitem__, queries, ks=(1, 2))
    assert res["n"] == 2 and res["skipped"] == ["c"]
    assert res["recall@1"] == 0.25 and res["recall@2"] == 0.75 and res["mrr"] == 0.75
    assert [r["qid"] for r in res["per_query"]] == ["a", "b"]
    empty = m.evaluate(runs.__getitem__, [queries[2]])
    assert empty["n"] == 0 and empty["mrr"] == 0.0


def test_evaluate_random_against_definition(load):
    m = load("ex08_retrieval_eval")
    rng = random.Random(408)
    qs, runs = [], {}
    for i in range(50):
        rel = rng.sample("abcdefgh", rng.randint(1, 3))
        qs.append({"qid": f"q{i}", "query": f"q{i}", "relevant": rel})
        runs[f"q{i}"] = rng.sample("abcdefgh", rng.randint(0, 8))
    res = m.evaluate(runs.__getitem__, qs, ks=(3,))
    r3 = sum(len(set(runs[q["qid"]][:3]) & set(q["relevant"])) / len(q["relevant"]) for q in qs) / 50
    rr = sum(next((1 / i for i, d in enumerate(runs[q["qid"]], 1) if d in q["relevant"]), 0.0)
             for q in qs) / 50
    assert res["recall@3"] == round(r3, 4) and res["mrr"] == round(rr, 4)


def test_regressions(load):
    m = load("ex08_retrieval_eval")
    base = {"mrr": 0.9, "recall@1": 0.8, "recall@3": 1.0, "n": 12, "skipped": []}
    cand = {"mrr": 0.89, "recall@1": 0.7, "recall@3": 1.0, "n": 12, "skipped": []}
    assert m.regressions(base, cand) == [("recall@1", 0.8, 0.7)]          # mrr within tolerance
    assert m.regressions(base, cand, tolerance=0.0) == [("mrr", 0.9, 0.89), ("recall@1", 0.8, 0.7)]
    assert m.regressions(base, base) == []


def test_corpus_numbers(load):
    m = load("ex08_retrieval_eval")
    from ragkit import dense_ranking, load_corpus, load_queries
    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    res = m.evaluate(lambda q: [d for d, _ in dense_ranking(q, docs)], load_queries())
    assert (res["recall@1"], res["recall@3"], res["mrr"]) == (0.75, 1.0, 0.9167)
