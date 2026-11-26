import pytest

M = "ex06_design_rubric"


def by_name(lines):
    return {l.name: l for l in lines}


def test_empty_and_strong(load):
    m = load(M)
    assert m.total(m.score("")) == 0.0
    assert m.total(m.score(m.STRONG)) == 100.0
    assert m.gaps(m.score(m.STRONG)) == []


def test_weak_notes_partial_credit(load):
    m = load(M)
    lines = by_name(m.score(m.WEAK))
    assert (lines["architecture"].hits, lines["architecture"].points) == (2, 10.0)
    assert (lines["requirements"].hits, lines["requirements"].points) == (1, 5.0)
    assert m.total(m.score(m.WEAK)) == 15.0
    assert m.gaps(m.score(m.WEAK)) == ["estimates", "evaluation", "requirements"]


def test_signals_count_once_and_case_insensitive(load):
    m = load(M)
    assert by_name(m.score("cache CACHE Cache"))["architecture"].hits == 1
    assert by_name(m.score("Gateway, Rerank, Queue"))["architecture"].points == 15.0


def test_word_boundary(load):
    m = load(M)
    assert by_name(m.score("unretrieved"))["architecture"].hits == 0
    assert by_name(m.score("retrieval"))["architecture"].hits == 1


def test_estimates_need_units(load):
    m = load(M)
    assert by_name(m.score("we need 3 and 50 and 7"))["estimates"].hits == 0
    e = by_name(m.score("50 qps, 300 tokens, 26 GPUs, 2 s, 50 qps"))["estimates"]
    assert (e.hits, e.points) == (4, 15.0)
    assert by_name(m.score("16 GB"))["estimates"].points == 5.0
    assert by_name(m.score("5 seconds"))["estimates"].hits == 0       # unit must end the token


def test_gaps_ordering_and_k(load):
    m = load(M)
    lines = m.score("")
    assert m.gaps(lines, k=5) == ["requirements", "estimates", "architecture", "evaluation",
                                  "data"]
    assert m.gaps(lines, k=0) == []


def test_rubric_weights_validated(load):
    m = load(M)
    bad = (m.Criterion("x", 50, ("a",), 1),)
    with pytest.raises(ValueError):
        m.score("a", bad)
    ok = (m.Criterion("x", 100, ("alpha", "beta", "gamma"), 2),)
    assert m.total(m.score("alpha", ok)) == 50.0
