import random

import pytest

DOCS = {1: "Red fox.", 2: "red hen", 3: "Blue fox!", 4: "'Quoted' words, here; Fox?"}


def test_examples(load):
    m = load("ex02_inverted_index")
    idx = m.build_index({1: "Red fox.", 2: "red hen", 3: "Blue fox!"})
    assert m.search_all(idx, "red fox") == [1]
    assert m.search_any(idx, "hen blue") == [2, 3]


@pytest.mark.parametrize("query, all_ids, any_ids", [
    ("", [], []),
    ("FOX", [1, 3, 4], [1, 3, 4]),
    ("fox zebra", [], [1, 3, 4]),
    ("quoted", [4], [4]),
    ("red red", [1, 2], [1, 2]),
])
def test_edge_cases(load, query, all_ids, any_ids):
    m = load("ex02_inverted_index")
    idx = m.build_index(DOCS)
    assert m.search_all(idx, query) == all_ids
    assert m.search_any(idx, query) == any_ids


def test_queries_do_not_add_keys(load):
    m = load("ex02_inverted_index")
    idx = m.build_index(DOCS)
    before = set(idx)
    m.search_all(idx, "nothing here")
    m.search_any(idx, "absent words")
    assert set(idx) == before


def test_random_against_brute(load):
    m = load("ex02_inverted_index")
    rng = random.Random(2)
    vocab = ["a", "b", "c", "d", "e"]
    for _ in range(100):
        docs = {i: " ".join(rng.choice(vocab) for _ in range(rng.randint(0, 5)))
                for i in range(rng.randint(1, 6))}
        idx = m.build_index(docs)
        q = " ".join(rng.choice(vocab) for _ in range(rng.randint(1, 3)))
        assert m.search_all(idx, q) == m.brute_force_all(docs, q)
