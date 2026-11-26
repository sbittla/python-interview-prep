import random

import numpy as np
import pytest


def test_examples(load):
    m = load("ex03_dense_topk_filter")
    assert m.top_k(np.array([0.2, 0.9, 0.9, 0.1]), ["a", "b", "c", "d"], 2) == [("b", 0.9), ("c", 0.9)]


def test_boundary_ties_broken_by_id(load):
    m = load("ex03_dense_topk_filter")
    # three-way tie for 2nd place: the smallest id must win, whatever argpartition returns
    assert m.top_k(np.array([0.5, 0.7, 0.5, 0.5]), ["z", "y", "x", "w"], 2) == [("y", 0.7), ("w", 0.5)]
    # last-bit noise must not reorder a tie
    assert m.top_k(np.array([0.3 + 1e-12, 0.3]), ["b", "a"], 1) == [("a", 0.3)]


@pytest.mark.parametrize("k, expected", [(0, []), (-1, []), (5, [("b", 2.0), ("a", 1.0)])])
def test_k_edges(load, k, expected):
    assert load("ex03_dense_topk_filter").top_k(np.array([1.0, 2.0]), ["a", "b"], k) == expected


def test_top_k_matches_full_sort_random(load):
    m = load("ex03_dense_topk_filter")
    rng = np.random.default_rng(403)
    for _ in range(200):
        n = int(rng.integers(1, 30))
        scores = rng.integers(0, 5, n) / 4.0                  # many exact ties
        ids = [f"id{i:02d}" for i in rng.permutation(n)]
        k = int(rng.integers(1, n + 2))
        expected = sorted(zip(ids, scores.tolist()), key=lambda p: (-p[1], p[0]))[:k]
        assert m.top_k(scores, ids, k) == [(i, round(s, 4)) for i, s in expected]


def test_normalize_rows(load):
    m = load("ex03_dense_topk_filter")
    out = m.normalize_rows(np.array([[3.0, 4.0], [0.0, 0.0], [-2.0, 0.0]]))
    assert out.tolist() == [[0.6, 0.8], [0.0, 0.0], [-1.0, 0.0]]
    assert not np.isnan(out).any()


def test_index_matches_brute_force(load):
    m = load("ex03_dense_topk_filter")
    from ragkit import load_chunks
    chunks = load_chunks()
    idx = m.DenseIndex(chunks)
    for q in ["is my data encrypted at rest", "rotate credentials", "429 SlowDown", "zzz"]:
        assert idx.search(q, 4) == m.brute_force_search(q, [c["text"] for c in chunks], idx.ids, 4)


def test_pre_vs_post_filter(load):
    m = load("ex03_dense_topk_filter")
    from ragkit import load_chunks
    chunks = load_chunks()
    idx = m.DenseIndex(chunks)
    q = "how often should I rotate credentials"
    pre = idx.search(q, 3, {"year": 2025}, "pre")
    post = idx.search(q, 3, {"year": 2025}, "post")
    by_id = {c["id"]: c for c in chunks}
    assert len(pre) == 3 and all(by_id[i]["year"] == 2025 for i, _ in pre)
    assert len(post) < 3 and post == pre[:len(post)]
    assert idx.search(q, 3, {"area": "billing"}) == []
    assert idx.search(q, 3, {"no_such_field": 1}) == []
    with pytest.raises(ValueError):
        idx.search(q, 3, mode="sideways")


def test_where_rule_kinds(load):
    m = load("ex03_dense_topk_filter")
    meta = {"area": "security", "year": 2024}
    assert m.matches(meta, None) and m.matches(meta, {})
    assert m.matches(meta, {"area": {"security", "cost"}, "year": lambda y: y < 2025})
    assert not m.matches(meta, {"area": ["cost"]})
    assert not m.matches(meta, {"year": 2025})


def test_filter_random_against_reference(load):
    m = load("ex03_dense_topk_filter")
    from ragkit import embed, load_chunks
    chunks = load_chunks()
    idx = m.DenseIndex(chunks)
    rng = random.Random(4031)
    areas = sorted({c["area"] for c in chunks})
    full = {c["id"]: s for c, s in zip(chunks, (idx.matrix @ embed("bucket versions")).tolist())}
    for _ in range(30):
        allowed = set(rng.sample(areas, rng.randint(1, 3)))
        k = rng.randint(1, 6)
        ok = sorted(((c["id"], round(full[c["id"]], 6)) for c in chunks if c["area"] in allowed),
                    key=lambda p: (-p[1], p[0]))[:k]
        got = idx.search("bucket versions", k, {"area": allowed})
        assert [i for i, _ in got] == [i for i, _ in ok]
