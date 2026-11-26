import pytest

SRCS = {1: "Plain HTTP requests are rejected with error E403.",
        2: "Rotate access keys every 90 days."}


def test_examples(load):
    m = load("ex09_groundedness")
    assert m.split_claims("Keys rotate every 90 days [2]. Use two keys [1][2].") == [
        ("Keys rotate every 90 days.", [2]), ("Use two keys.", [1, 2])]


def test_split_claims_edges(load):
    m = load("ex09_groundedness")
    assert m.split_claims("") == []
    assert m.split_claims("No cites here.") == [("No cites here.", [])]
    assert m.split_claims("A [2] and B [1][2][2].") == [("A and B.", [2, 1])]
    assert m.split_claims("Done [10].") == [("Done.", [10])]


@pytest.mark.parametrize("claim, texts, expected", [
    ("rotate keys", ["Rotate access keys"], 1.0),
    ("rotate keys daily", ["Rotate access keys"], 2 / 3),
    ("rotate keys", [], 0.0),
    ("the of and", ["anything"], 1.0),                      # no content terms
    ("e403 keys", ["error E403", "keys"], 1.0),              # union of several sources
])
def test_support(load, claim, texts, expected):
    assert load("ex09_groundedness").support(claim, texts) == pytest.approx(expected)


@pytest.mark.parametrize("answer, status", [
    ("Rotate access keys every 90 days [2].", "supported"),
    ("Rotate access keys every 90 days [1].", "unsupported"),   # true, but not in the cited source
    ("Rotate access keys every 90 days.", "uncited"),
    ("Rotate access keys every 90 days [3].", "bad-citation"),
    ("Rotate access keys every 90 days [2][3].", "bad-citation"),
    ("Plain HTTP requests are not rejected [1].", "supported"),  # documented lexical blind spot
])
def test_statuses(load, answer, status):
    (claim,) = load("ex09_groundedness").check_answer(answer, SRCS)["claims"]
    assert claim[2] == status


def test_rates_and_threshold(load):
    m = load("ex09_groundedness")
    ans = "Rotate access keys every 90 days [2]. Egress is free [1]. Keys are blue [7]. Hello."
    res = m.check_answer(ans, SRCS)
    assert [c[2] for c in res["claims"]] == ["supported", "unsupported", "bad-citation", "uncited"]
    assert res["grounded"] == 0.25 and res["citations_valid"] == 0.5 and not res["abstained"]
    half = "Rotate keys daily weekly [2]."                       # support 2/4
    assert m.check_answer(half, SRCS, threshold=0.5)["claims"][0][2] == "supported"
    assert m.check_answer(half, SRCS, threshold=0.6)["claims"][0][2] == "unsupported"


def test_abstain_and_empty(load):
    m = load("ex09_groundedness")
    from ragkit import ABSTAIN
    res = m.check_answer(ABSTAIN, SRCS)
    assert res["abstained"] and res["claims"] == [] and res["grounded"] == 1.0
    assert m.check_answer("", SRCS)["grounded"] == 0.0


def test_mock_modes_are_caught(load):
    m = load("ex09_groundedness")
    from ragkit import MockLLM, format_prompt
    srcs = [("d06#1", "Rotate access keys every 90 days. Holding two keys allows rotation."),
            ("d05#1", "All API endpoints require TLS 1.2 or newer.")]
    prompt = format_prompt("how often rotate access keys", srcs)
    numbered = {1: srcs[0][1], 2: srcs[1][1]}
    good = m.check_answer(MockLLM().complete(prompt), numbered)
    assert good["grounded"] == 1.0 and good["citations_valid"] == 1.0
    bad = m.check_answer(MockLLM("hallucinate").complete(prompt), numbered)
    assert bad["claims"][-1][2] == "unsupported" and bad["grounded"] < 1.0
    shifted = m.check_answer(MockLLM("miscite").complete(prompt), numbered)
    assert shifted["grounded"] < 1.0
