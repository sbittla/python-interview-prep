from fractions import Fraction

import pytest

FULL = "clarifying={};approach=4;correctness=4;code_quality=4;complexity=4;testing=4;communication=4"
CSV = (
    "date,mock,rubric,ratings\n"
    "2026-01-03,S2,coding," + FULL.format(4) + "\n"
    "2026-01-01,S1,coding,clarifying=2;approach=2;correctness=2;code_quality=2;"
    "complexity=2;testing=2;communication=2\n"
    "2026-01-02,L3,ai,decomposition=1;prompting=4;verifying=1;integration=4;ownership=4\n"
)


def _csv(tmp_path, text):
    p = tmp_path / "scores.csv"
    p.write_text(text, encoding="utf-8")
    return p


def test_trend(load):
    m = load("ex04_progress_tracker")
    assert m.trend([50, 60, 70]) == 10
    assert m.trend([70]) == 0 and m.trend([]) == 0
    assert m.trend([50, 70, 60, 80]) == 8         # least squares, not (last - first) / 3 = 10
    assert m.trend([1, 2, 4]) == Fraction(3, 2)
    assert m.trend([80, 70]) == -10


def test_repo_data(load):
    m = load("ex04_progress_tracker")
    e = m.load_scores()
    h = m.history(e, "coding")
    assert [float(t) for _, _, t, _ in h] == [51.25, 62.5, 63.75, 75.0, 78.75, 91.25]
    assert h[-1][3] == "ready"
    assert m.weakest(e, "coding") == [("correctness", Fraction(25, 6)),
                                      ("testing", Fraction(25, 6))]
    assert m.weakest(e, "ai", n=1) == [("verifying", 15)]
    plan = m.study_plan(e, "coding")
    assert plan[0].startswith("correctness") and plan[0].endswith("retake S4")
    assert "§2.1" in plan[0] and "§2.6" in plan[1]


def test_sorted_by_date_and_window(load, tmp_path):
    m = load("ex04_progress_tracker")
    e = m.load_scores(_csv(tmp_path, CSV))
    assert [d for d, *_ in m.history(e, "coding")] == ["2026-01-01", "2026-01-03"]
    assert m.trend([t for _, _, t, _ in m.history(e, "coding")]) == 50
    # window=1: only the perfect latest mock; nothing lost, ties in rubric order
    assert m.weakest(e, "coding", n=2, window=1) == [("clarifying", 0), ("approach", 0)]
    # window=2 averages both: correctness (25) lost most
    assert m.weakest(e, "coding", n=1, window=2) == [("correctness", Fraction(25, 4))]
    # points, not ratings: verifying (30) beats decomposition (20) at the same rating
    assert m.weakest(e, "ai", n=2) == [("verifying", Fraction(45, 2)), ("decomposition", 15)]


def test_retake_tie_goes_to_most_recent(load, tmp_path):
    m = load("ex04_progress_tracker")
    text = ("date,mock,rubric,ratings\n"
            f"2026-01-01,S1,coding,{FULL.format(1)}\n"
            f"2026-01-02,S3,coding,{FULL.format(1)}\n"
            f"2026-01-03,S4,coding,{FULL.format(3)}\n")
    plan = m.study_plan(m.load_scores(_csv(tmp_path, text)), "coding", n=1)
    assert plan[0].startswith("clarifying") and plan[0].endswith("retake S3")


@pytest.mark.parametrize("ratings", [
    "clarifying=4",
    "clarifying=x;approach=1",
    FULL.format(9),
    FULL.format(4) + ";clarifying=4",
])
def test_bad_rows(load, tmp_path, ratings):
    m = load("ex04_progress_tracker")
    p = _csv(tmp_path, f"date,mock,rubric,ratings\n2026-01-01,S1,coding,{ratings}\n")
    with pytest.raises(ValueError):
        m.load_scores(p)


def test_unknown_rubric_and_empty(load, tmp_path):
    m = load("ex04_progress_tracker")
    with pytest.raises(ValueError):
        m.load_scores(_csv(tmp_path, "date,mock,rubric,ratings\n2026-01-01,S1,essay,a=1\n"))
    with pytest.raises(ValueError):
        m.history([], "coding")
