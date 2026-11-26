import random

import pytest


def _ck(i, text, score):
    return {"id": i, "text": text, "score": score}


def test_examples(load):
    m = load("ex07_prompt_assembly")
    assert m.edge_order(["r1", "r2", "r3", "r4", "r5"]) == ["r1", "r3", "r5", "r4", "r2"]


@pytest.mark.parametrize("items, expected", [
    ([], []), (["a"], ["a"]), (["a", "b"], ["a", "b"]), (["a", "b", "c", "d"], ["a", "c", "d", "b"]),
])
def test_edge_order_small(load, items, expected):
    assert load("ex07_prompt_assembly").edge_order(items) == expected


def test_budget_dedupe_and_skip(load):
    m = load("ex07_prompt_assembly")
    from ragkit import count_tokens, format_prompt
    base = count_tokens(format_prompt("q x", []))
    chunks = [_ck("a", "one two three", 0.9), _ck("b", "ONE   two three", 0.9),
              _ck("c", " ".join(["w"] * 30), 0.8), _ck("d", "short one", 0.1)]
    # a costs 5 tokens ([1] (a) one two three); budget leaves room for a + d but not c
    res = m.assemble("q x", chunks, budget=base + 10 + 12, reserve=10)
    assert res["sources"] == {1: "a", 2: "d"}
    assert res["dropped"] == [("b", "duplicate"), ("c", "budget")]
    assert res["tokens"] == count_tokens(res["prompt"]) and res["tokens"] + 10 <= base + 22
    assert "[1] (a) one two three" in res["prompt"] and "[2] (d) short one" in res["prompt"]


def test_duplicate_keeps_higher_score_then_smaller_id(load):
    m = load("ex07_prompt_assembly")
    res = m.assemble("q", [_ck("z", "Same text", 0.5), _ck("y", "same  TEXT", 0.7)], 500, 0)
    assert res["sources"] == {1: "y"} and res["dropped"] == [("z", "duplicate")]
    res = m.assemble("q", [_ck("z", "Same text", 0.7), _ck("y", "same text", 0.7)], 500, 0)
    assert res["sources"] == {1: "y"}


def test_too_small_budget_and_bad_order(load):
    m = load("ex07_prompt_assembly")
    from ragkit import count_tokens, format_prompt
    need = count_tokens(format_prompt("q", [])) + 5
    assert m.assemble("q", [], need, 5)["sources"] == {}
    with pytest.raises(ValueError):
        m.assemble("q", [], need - 1, 5)
    with pytest.raises(ValueError):
        m.assemble("q", [], 500, order="random")


def test_no_sources_makes_mock_abstain(load):
    m = load("ex07_prompt_assembly")
    from ragkit import ABSTAIN, MockLLM, count_tokens, format_prompt
    tight = count_tokens(format_prompt("rotate keys", [])) + 1
    res = m.assemble("rotate keys", [_ck("a", "Rotate keys every 90 days.", 1.0)], tight, 1)
    assert res["sources"] == {} and res["dropped"] == [("a", "budget")]
    assert MockLLM().complete(res["prompt"]) == ABSTAIN


def test_random_never_exceeds_budget(load):
    m = load("ex07_prompt_assembly")
    rng = random.Random(407)
    for _ in range(200):
        chunks = [_ck(f"c{i}", " ".join(rng.choice("ab") for _ in range(rng.randint(1, 12))),
                      rng.choice([0.1, 0.5, 0.9])) for i in range(rng.randint(0, 10))]
        budget, reserve = rng.randint(40, 120), rng.randint(0, 20)
        try:
            res = m.assemble("a question", chunks, budget, reserve, rng.choice(["score", "edges"]))
        except ValueError:
            continue
        assert res["tokens"] + reserve <= budget
        kept = set(res["sources"].values())
        assert kept | {i for i, _ in res["dropped"]} == {c["id"] for c in chunks}
        assert not kept & {i for i, _ in res["dropped"]}
        assert list(res["sources"]) == list(range(1, len(kept) + 1))


def test_edges_order_on_prompt(load):
    m = load("ex07_prompt_assembly")
    chunks = [_ck(c, c, s) for c, s in [("a", 0.9), ("b", 0.8), ("c", 0.7), ("d", 0.6)]]
    assert list(m.assemble("q", chunks, 500, 0, "edges")["sources"].values()) == ["a", "c", "d", "b"]
    assert list(m.assemble("q", chunks, 500, 0)["sources"].values()) == ["a", "b", "c", "d"]


def test_naive_truncate_loses_question(load):
    m = load("ex07_prompt_assembly")
    chunks = [_ck("a", " ".join(["w"] * 200), 1.0)]
    assert "Question:" not in m.naive_truncate("q", chunks, 100)
