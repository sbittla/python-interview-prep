import random
from collections import Counter

import pytest

M = "ex03_top_k_tie_breaking"


def reference(text, k):
    counts = Counter(text.lower().split())
    return sorted(counts.items(), key=lambda wc: (-wc[1], wc[0]))[:max(k, 0)]


def test_oracle_matches_reference(load):
    m = load(M)
    rng = random.Random(5)
    for _ in range(300):
        text = m.random_text(rng)
        k = rng.randint(-1, 6)
        assert m.oracle(text, k) == reference(text, k)


def test_random_text_is_messy_enough(load):
    m = load(M)
    rng = random.Random(11)
    texts = [m.random_text(rng) for _ in range(300)]
    assert "" in texts
    assert any("  " in t for t in texts)
    assert any("\n" in t or "\t" in t for t in texts)
    assert any(t != t.lower() for t in texts)
    counts = [Counter(t.lower().split()) for t in texts]
    assert any(len(set(c.values())) < len(c) for c in counts)          # ties occur


def test_finds_all_three_generated_bugs(load):
    m = load(M)
    found = m.find_counterexamples(m.generated_top_k_words)
    assert set(found) == {"empty-token", "tie-order", "other"}
    for text, k in found.values():
        assert m.generated_top_k_words(text, k) != reference(text, k)
    assert found["empty-token"][0].strip() == ""                       # shortest: blank text


def test_harness_is_not_vacuous(load):
    m = load(M)
    assert m.find_counterexamples(reference) == {}
    assert m.find_counterexamples(lambda t, k: reference(t, k)[::-1]) != {}


def test_fix_has_no_counterexamples(load):
    m = load(M)
    assert m.find_counterexamples(m.top_k_words) == {}
    assert m.find_counterexamples(m.top_k_words, trials=1500, seed=42) == {}


@pytest.mark.parametrize("text, k, expected", [
    ("", 3, []),
    ("   \n\t ", 2, []),
    ("b a b a c", 2, [("a", 2), ("b", 2)]),
    ("A a  b", 5, [("a", 2), ("b", 1)]),
    ("x y", 0, []),
    ("x y", -2, []),
    ("cat\ncat\tdog", 1, [("cat", 2)]),
    ("z y x", 2, [("x", 1), ("y", 1)]),
])
def test_fix_values(load, text, k, expected):
    assert load(M).top_k_words(text, k) == expected


def test_complexity_stated(load):
    t = load(M).COMPLEXITY["time"].replace(" ", "").lower()
    assert t in {"o(l+dlogk)", "o(l+d*logk)", "o(l+d·logk)"}
