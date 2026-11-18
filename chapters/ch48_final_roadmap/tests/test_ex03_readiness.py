import pytest


def _all(m, r):
    return {a: r for a in m.AREAS}


def test_bounds(load):
    m = load("ex03_readiness")
    for t in "SML":
        assert m.self_score(_all(m, 4), t) == pytest.approx(100.0)
        assert m.self_score(_all(m, 0), t) == pytest.approx(0.0)


def test_readiness_mixes_mocks(load):
    m = load("ex03_readiness")
    r = _all(m, 3)  # self score 75
    assert m.readiness(r, "S", [60, 90, 70]) == pytest.approx(0.7 * 75 + 0.3 * 80)
    assert m.readiness(_all(m, 4), "S", []) == 70.0  # capped without mock evidence


@pytest.mark.parametrize("score, gated, expected", [
    (80, False, "READY"), (79.9, False, "ALMOST"), (65, False, "ALMOST"),
    (64.9, False, "NOT YET"), (95, True, "ALMOST"), (50, True, "NOT YET"),
])
def test_verdict(load, score, gated, expected):
    assert load("ex03_readiness").verdict(score, gated) == expected


def test_gate_and_weak_areas(load):
    m = load("ex03_readiness")
    r = _all(m, 4)
    r["techniques"] = 1
    r["concurrency"] = 0  # weight 2 for track S: does not gate
    assert m.gated(r, "S") == ["techniques"]
    weak = m.weak_areas(r, "S")
    assert weak[0] == ("techniques", 9, [18, 19, 20, 21])
    assert weak[1][0] == "concurrency"
    assert len(weak) == 2


@pytest.mark.parametrize("bad", ["too_high", "missing", "unknown"])
def test_validation(load, bad):
    m = load("ex03_readiness")
    ratings = _all(m, 2)
    if bad == "too_high":
        ratings["python_fluency"] = 5
    elif bad == "missing":
        ratings.pop("genai")
    else:
        ratings["nonsense"] = 1
    with pytest.raises(ValueError):
        m.self_score(ratings, "L")
