import itertools
import random

import numpy as np
import pytest


def test_examples(load):
    m = load("ex05_rerank_mmr")
    assert m.min_window("a x b a c".split(), {"a", "c"}) == 2
    assert m.cross_score("rotate keys", "Rotation of access keys") == 0.75


@pytest.mark.parametrize("tokens, needed, expected", [
    ([], set(), 0), (["a"], set(), 0), (["a", "b"], {"z"}, None), ([], {"a"}, None),
    (["a"], {"a"}, 1), (["a", "b", "a"], {"a", "b"}, 2), (list("adobecodebanc"), set("abc"), 4),
    (["b", "a", "a", "a", "c"], {"b", "c"}, 5),
])
def test_min_window_cases(load, tokens, needed, expected):
    assert load("ex05_rerank_mmr").min_window(tokens, needed) == expected


def test_min_window_random_against_brute(load):
    m = load("ex05_rerank_mmr")
    rng = random.Random(405)
    for _ in range(300):
        toks = [rng.choice("abcd") for _ in range(rng.randint(0, 12))]
        need = set(rng.sample("abcd", rng.randint(1, 3)))
        widths = [j - i for i, j in itertools.combinations(range(len(toks) + 1), 2)
                  if need <= set(toks[i:j])]
        assert m.min_window(toks, need) == (min(widths) if widths else None)


def test_cross_score_components(load):
    m = load("ex05_rerank_mmr")
    assert m.cross_score("rotate access keys", "Rotate access keys every 90 days") == 1.05
    assert m.cross_score("rotate access keys", "Pricing per GB") == 0.0
    assert m.cross_score("", "anything") == 0.0 and m.cross_score("x", "") == 0.0
    # adjacent beats spread-out at equal coverage
    assert m.cross_score("access keys", "access keys here") > m.cross_score("access keys", "access a b c keys")
    # a weight makes the rare term matter more than the common one
    w = {"bucket": 0.1, "e409": 3.0}.get
    assert m.cross_score("bucket e409", "e409 only", w) > m.cross_score("bucket e409", "bucket only", w)


def test_idf_weights(load):
    m = load("ex05_rerank_mmr")
    w = m.idf_weights([("a", "red apple"), ("b", "green apple"), ("c", "red car")])
    assert w("apple") == pytest.approx(np.log(1 + 1.5 / 2.5))
    assert w("unknown") == pytest.approx(np.log(1 + 3.5 / 0.5))


def test_rerank_only_touches_head(load):
    m = load("ex05_rerank_mmr")
    texts = {"a": "nothing", "b": "rotate access keys", "c": "access keys", "d": "rotate access keys"}
    order, calls = m.rerank("rotate access keys", ["a", "b", "c", "d"], texts, top_n=3)
    assert order == ["b", "c", "a", "d"] and calls == 3          # d is outside the head
    order, calls = m.rerank("rotate access keys", ["a", "d", "b"], texts, top_n=10)
    assert order == ["d", "b", "a"] and calls == 3               # tie keeps first-stage order
    assert m.rerank("q", [], {}, 5) == ([], 0)


def test_rerank_improves_corpus_mrr(load):
    m = load("ex05_rerank_mmr")
    from ragkit import dense_ranking, load_corpus, load_queries
    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    w = m.idf_weights(docs)
    before = after = 0.0
    for q in load_queries():
        first = [d for d, _ in dense_ranking(q["query"], docs)]
        new, _ = m.rerank(q["query"], first, dict(docs), 5, w)
        assert sorted(new) == sorted(first)
        before += 1 / next(i for i, d in enumerate(first, 1) if d in q["relevant"])
        after += 1 / next(i for i, d in enumerate(new, 1) if d in q["relevant"])
    assert round(before / 12, 4) == 0.9167 and round(after / 12, 4) == 0.9583


def test_mmr(load):
    m = load("ex05_rerank_mmr")
    v = np.array([[1.0, 0.0], [1.0, 0.0], [0.6, 0.8], [0.0, 1.0]])
    q = np.array([1.0, 0.0])
    ids = ["a", "b", "c", "d"]
    assert m.mmr(q, v, ids, 3, lam=1.0) == ["a", "b", "c"]      # pure relevance, tie by id
    # after a: b = .7-.3 = .4, c = .42-.18 = .24, d = 0
    assert m.mmr(q, v, ids, 3, lam=0.7) == ["a", "b", "c"]
    # after a: b = .3-.7 = -.4, c = .18-.42 = -.24, d = 0 -> d; then c = .18-.7*.8 = -.38 > b
    assert m.mmr(q, v, ids, 3, lam=0.3) == ["a", "d", "c"]      # duplicate b suppressed
    assert len(m.mmr(q, v, ids, 10)) == 4 and m.mmr(q, v, ids, 0) == []


def _mmr_reference(q, v, ids, k, lam):
    chosen = []
    while len(chosen) < min(k, len(ids)):
        best = None
        for i in range(len(ids)):
            if i in chosen:
                continue
            red = max([float(v[i] @ v[j]) for j in chosen] or [0.0])
            key = (-round(lam * float(v[i] @ q) - (1 - lam) * red, 6), ids[i])
            best = min(best, (key, i)) if best else (key, i)
        chosen.append(best[1])
    return [ids[i] for i in chosen]


def test_mmr_random_against_reference(load):
    m = load("ex05_rerank_mmr")
    rng = np.random.default_rng(4051)
    for _ in range(100):
        n = int(rng.integers(1, 9))
        v = rng.integers(-2, 3, (n, 3)).astype(float)
        v[np.all(v == 0, axis=1)] = [1.0, 0.0, 0.0]
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        q = v[int(rng.integers(0, n))]
        ids = [f"x{i}" for i in rng.permutation(n)]
        k, lam = int(rng.integers(1, n + 1)), float(rng.choice([0.0, 0.3, 0.5, 0.7, 1.0]))
        assert m.mmr(q, v, ids, k, lam) == _mmr_reference(q, v, ids, k, lam)
