import pytest

M = "ex05_eval_gate"


def item(m, qid="x", facts=("150",), source="doc5", answerable=True, slice_="numeric"):
    return m.Item(qid, slice_, "?", facts, source, answerable)


def test_normalise(load):
    m = load(M)
    assert m.normalise("Up to $1,000  per\nYEAR") == "up to $1000 per year"
    assert m.normalise("1,5 and 12,345,678") == "1,5 and 12345678"


@pytest.mark.parametrize("answer, ok", [
    ("Hotels up to $150 per night [doc5].", True),
    ("Hotels up to $1500 per night [doc5].", False),          # whole-number match only
    ("Hotels up to $150 per night.", False),                  # missing citation
    ("Hotels up to $150 per night [doc4].", False),           # wrong citation
    ("I don't know, maybe 150 [doc5].", False),               # refusal on answerable item
    (None, False),
])
def test_check_answerable(load, answer, ok):
    m = load(M)
    assert m.check(item(m), answer) is ok


def test_check_multiword_fact(load):
    m = load(M)
    it = item(m, facts=("16 weeks",), source="doc6")
    assert m.check(it, "Leave is 16 weeks [doc6].")
    assert not m.check(it, "Leave is 16 paid weeks [doc6].")


@pytest.mark.parametrize("answer, ok", [
    ("I DON'T KNOW.", True),
    ("That is not in the provided documents.", True),
    ("The bonus will be 10% [doc3].", False),
    ("", False),
])
def test_check_unanswerable(load, answer, ok):
    m = load(M)
    assert m.check(item(m, facts=(), source="", answerable=False), answer) is ok


def test_reports(load):
    m = load(M)
    base = m.evaluate(m.GOLDEN, m.BASELINE)
    assert [q for q, ok in base.items() if not ok] == ["q2", "q4", "q7"]
    assert m.report(m.GOLDEN, base) == {"ALL": (9, 12), "numeric": (3, 4), "policy": (2, 4),
                                        "unanswerable": (4, 4)}
    assert m.report(m.GOLDEN, m.evaluate(m.GOLDEN, {}))["ALL"] == (0, 12)


def test_flips_sorted_naturally(load):
    m = load(M)
    base = m.evaluate(m.GOLDEN, m.BASELINE)
    assert m.flips(base, m.evaluate(m.GOLDEN, m.CANDIDATE_A)) == (["q10"], ["q2", "q4", "q7"])
    assert m.flips(base, base) == ([], [])


def test_gate_blocks_critical_regression_despite_higher_average(load):
    m = load(M)
    base = m.evaluate(m.GOLDEN, m.BASELINE)
    cand = m.evaluate(m.GOLDEN, m.CANDIDATE_A)
    assert m.report(m.GOLDEN, cand)["ALL"] == (11, 12)
    assert m.gate(m.GOLDEN, base, cand) == ("BLOCK", ["critical regression: q10"])
    assert m.gate(m.GOLDEN, base, cand, critical=())[0] == "PASS"


def test_gate_pass_and_threshold_rules(load):
    m = load(M)
    base = m.evaluate(m.GOLDEN, m.BASELINE)
    assert m.gate(m.GOLDEN, base, m.evaluate(m.GOLDEN, m.CANDIDATE_B)) == ("PASS", [])
    assert m.gate(m.GOLDEN, base, base) == ("PASS", [])
    one_drop = m.evaluate(m.GOLDEN, {**m.BASELINE, "q1": "no [doc1]"})       # -1/12, -1/4
    assert m.gate(m.GOLDEN, base, one_drop) == ("BLOCK", ["overall drop 0.08 > 0.02"])
    assert m.gate(m.GOLDEN, base, one_drop, overall_tol=0.1) == ("PASS", [])
    two = m.evaluate(m.GOLDEN, {**m.BASELINE, "q1": "no", "q3": "no"})
    decision, reasons = m.gate(m.GOLDEN, base, two)
    assert decision == "BLOCK"
    assert reasons == ["overall drop 0.17 > 0.02", "slice policy drop 0.50 > 0.25"]


def test_gate_reason_order_critical_first(load):
    m = load(M)
    base = m.evaluate(m.GOLDEN, m.BASELINE)
    bad = m.evaluate(m.GOLDEN, {**m.BASELINE, "q9": "It is 1M [doc1].", "q12": "Yes [doc2]."})
    assert m.gate(m.GOLDEN, base, bad)[1] == ["critical regression: q9",
                                              "critical regression: q12",
                                              "overall drop 0.17 > 0.02"]
