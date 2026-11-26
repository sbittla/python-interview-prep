import math
import random

import pytest

TOY = [("a", "red apple"), ("b", "green apple"), ("c", "red red car")]


def test_examples(load):
    m = load("ex02_bm25")
    assert m.BM25(TOY).search("red", k=2) == [("c", 0.5982), ("a", 0.4992)]


def test_hand_computed_score(load):
    m = load("ex02_bm25")
    idx = m.BM25(TOY, k1=1.2, b=0.75)
    # N=3, df(red)=2 -> idf = ln(1 + 1.5/2.5) = ln 1.6; avgdl = 7/3; doc c has tf=2, |d|=3
    idf = math.log(1.6)
    assert idx.idf("red") == pytest.approx(idf)
    norm = 1 - 0.75 + 0.75 * 3 / (7 / 3)
    assert idx.score("red", "c") == pytest.approx(idf * 2 * 2.2 / (2 + 1.2 * norm))
    assert idx.idf("zebra") == pytest.approx(math.log(1 + 3.5 / 0.5))


def test_idf_never_negative(load):
    m = load("ex02_bm25")
    idx = m.BM25([(str(i), "common word") for i in range(5)])
    assert idx.idf("common") > 0
    assert idx.search("common", 2) == [("0", round(idx.score("common", "0"), 4)),
                                       ("1", round(idx.score("common", "1"), 4))]  # ties by id


def test_b_zero_ignores_length_and_k1_zero_is_binary(load):
    m = load("ex02_bm25")
    docs = [("short", "rare x"), ("long", "rare " + " ".join(f"w{i}" for i in range(20))),
            ("many", "rare rare rare rare y")]
    s0 = dict(m.BM25(docs, b=0.0).search("rare", 3))
    assert s0["short"] == s0["long"]
    s1 = dict(m.BM25(docs, b=0.75).search("rare", 3))
    assert s1["short"] > s1["long"]                       # length normalisation on
    kz = m.BM25(docs, k1=0.0)
    assert kz.score("rare", "many") == pytest.approx(kz.idf("rare"))   # tf ignored


def test_saturation_bound(load):
    m = load("ex02_bm25")
    docs = [("d", "spam " * 200), ("e", "other text"), ("f", "more text")]
    idx = m.BM25(docs, k1=1.2, b=0.0)
    assert idx.score("spam", "d") < idx.idf("spam") * 2.2      # never exceeds idf*(k1+1)
    assert idx.score("spam", "d") > idx.idf("spam") * 2.1


def test_repeated_query_terms_count_once(load):
    m = load("ex02_bm25")
    idx = m.BM25(TOY)
    assert idx.search("red red red", 3) == idx.search("red", 3)


@pytest.mark.parametrize("docs, query", [([], "red"), (TOY, ""), (TOY, "zebra"), (TOY, "the of")])
def test_empty_results(load, docs, query):
    assert load("ex02_bm25").BM25(docs).search(query, 5) == []


def test_index_matches_scan_random(load):
    m = load("ex02_bm25")
    rng = random.Random(402)
    vocab = [f"t{i}" for i in range(12)]
    for _ in range(60):
        docs = [(f"d{i:02d}", " ".join(rng.choice(vocab) for _ in range(rng.randint(0, 15))))
                for i in range(rng.randint(1, 12))]
        q = " ".join(rng.choice(vocab) for _ in range(rng.randint(1, 4)))
        k = rng.randint(1, 6)
        assert m.BM25(docs).search(q, k) == m.bm25_scan(docs, q, k)


def test_tfidf_rewards_stuffing_more_than_bm25(load):
    m = load("ex02_bm25")
    docs = [("short", "bucket error e409"), ("spam", "e409 " * 8 + "bucket"), ("x", "other")]
    tf = dict(m.tfidf_search(docs, "e409", 3))
    bm = dict(m.BM25(docs).search("e409", 3))
    assert tf["spam"] / tf["short"] == pytest.approx(8.0)
    assert bm["spam"] / bm["short"] < 2.0


def test_corpus_query(load):
    m = load("ex02_bm25")
    from ragkit import load_corpus
    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    top = [d for d, _ in m.BM25(docs).search("why does deleting my bucket fail with E409", 2)]
    assert top == ["d08", "d14"]
