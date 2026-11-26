import json

import pytest

BANK = [
    {"id": "py01", "section": "44.1", "xref": "§7.1", "keywords": ["once", "None"]},
    {"id": "py02", "section": "44.1", "xref": "§7.6", "keywords": ["identity"]},
    {"id": "py03", "section": "44.1", "xref": "§7.3", "keywords": ["same list"]},
    {"id": "al01", "section": "44.3", "xref": "§10.5", "keywords": ["contiguous"]},
    {"id": "ml01", "section": "44.6", "xref": "§35.7", "keywords": ["flagged", "found"]},
    {"id": "ai01", "section": "44.7", "xref": "§39.1", "keywords": ["variance"]},
]


@pytest.fixture
def m(load):
    return load("ex03_quiz_runner")


def test_normalise(m):
    assert m.normalise("O(log n), `heapify`!") == "o log n heapify"
    assert m.normalise("  Min-Heap  ") == "min heap"


@pytest.mark.parametrize("kws, resp, expected", [
    (["min-heap", "negated"], "heapq is a MIN HEAP; push negated keys", (2, 2, True)),
    (["rank"], "ranking", (0, 1, False)),
    (["same list"], "the same, list-wise", (1, 1, True)),
    (["once", "None"], "evaluated once", (1, 2, True)),
    (["once", "None"], "", (0, 2, False)),
    ([], "anything", (0, 0, False)),
])
def test_grade(m, kws, resp, expected):
    assert m.grade({"keywords": kws}, resp) == expected


def test_grade_threshold(m):
    e = {"keywords": ["a", "b", "c"]}
    assert m.grade(e, "a b", threshold=0.7) == (2, 3, False)
    assert m.grade(e, "a b", threshold=0.6) == (2, 3, True)


def test_pick_round_robin_across_sections(m):
    ids = m.pick(BANK, 4, seed=0)
    assert [i[:2] for i in ids] == ["py", "al", "ml", "ai"]
    more = m.pick(BANK, 6, seed=0)
    assert sorted(more) == sorted(e["id"] for e in BANK)
    assert more[:4] == ids
    assert m.pick(BANK, 6, seed=0) == more


def test_pick_sorts_sections_whatever_the_bank_order(m):
    shuffled = [BANK[5], BANK[3], BANK[4], BANK[0], BANK[1], BANK[2]]   # 44.7 first
    assert [i[:2] for i in m.pick(shuffled, 4, seed=0)] == ["py", "al", "ml", "ai"]
    assert m.pick(shuffled, 4, seed=0) == m.pick(BANK, 4, seed=0)


def test_pick_uses_one_shared_random(m):
    import random
    a = [{"id": f"a{k}", "section": "44.1"} for k in range(6)]
    b = [{"id": f"b{k}", "section": "44.2"} for k in range(6)]
    for seed in range(5):
        rng = random.Random(seed)
        qa, qb = [e["id"] for e in a], [e["id"] for e in b]
        rng.shuffle(qa)
        rng.shuffle(qb)                                    # same rng, continued state
        expected = [x for pair in zip(qa, qb) for x in pair]
        assert m.pick(b + a, 12, seed=seed) == expected
    # identical groups would be shuffled identically by a fresh Random(seed) per group
    patterns = [[i[1] for i in m.pick(a + b, 12, seed=s)] for s in range(5)]
    assert any(p[0::2] != p[1::2] for p in patterns)


def test_pick_seed_and_section_filter(m):
    orders = {tuple(m.pick(BANK, 3, seed=s, sections=["44.1"])) for s in range(10)}
    assert len(orders) > 1
    assert all(sorted(o) == ["py01", "py02", "py03"] for o in orders)
    with pytest.raises(ValueError):
        m.pick(BANK, 4, seed=0, sections=["44.1"])


def test_run_quiz_report(m):
    ids = ["ai01", "py01", "al01", "ml01"]
    resp = {"py01": "evaluated once, use None", "al01": "it must be contiguous",
            "ml01": "no idea"}
    r = m.run_quiz(BANK, ids, resp)
    assert r["score"] == (2, 4)
    assert [row[0] for row in r["rows"]] == ids
    assert r["by_section"] == {"44.1": [1, 1], "44.3": [1, 1], "44.6": [0, 1], "44.7": [0, 1]}
    assert r["review"] == ["§35.7", "§39.1"]


def test_review_sorted_numerically_and_unique(m):
    bank = [dict(BANK[0], id="a", xref="§16.10"), dict(BANK[0], id="b", xref="§16.9"),
            dict(BANK[0], id="c", xref="§7.1"), dict(BANK[0], id="d", xref="§7.1")]
    r = m.run_quiz(bank, ["a", "b", "c", "d"], {})
    assert r["review"] == ["§7.1", "§16.9", "§16.10"]


def test_unknown_id(m):
    with pytest.raises(KeyError):
        m.run_quiz(BANK, ["nope"], {})


def test_real_bank_model_answers_pass(m):
    bank = json.loads(m.BANK_PATH.read_text(encoding="utf-8"))
    for e in bank:                   # the model answer must grade as a pass
        assert m.grade(e, e["answer"]) == (len(e["keywords"]),) * 2 + (True,), e["id"]
    ids = m.pick(bank, 7, seed=44)
    assert len({i[:2] for i in ids}) == 7
