import pytest


@pytest.mark.parametrize("attempts, expected", [
    ([("2026-11-05", "failed")], ("2026-11-06", 0)),
    ([("2026-11-05", "struggled")], ("2026-11-06", 0)),
    ([("2026-11-01", "solved")], ("2026-11-02", 1)),
    ([("2026-11-09", "solved"), ("2026-11-02", "solved")], ("2026-11-12", 2)),  # unsorted input
    ([("2026-11-01", "solved"), ("2026-11-02", "solved"), ("2026-11-05", "solved")],
     ("2026-11-12", 3)),
    ([("2026-11-01", "failed"), ("2026-11-02", "solved")], ("2026-11-03", 1)),  # streak restarts
    ([(f"2026-11-0{d}", "solved") for d in range(1, 6)], (None, 5)),  # retired
])
def test_next_review(load, attempts, expected):
    assert load("ex02_spaced_repetition").next_review(attempts) == expected


def test_next_review_empty(load):
    with pytest.raises(ValueError):
        load("ex02_spaced_repetition").next_review([])


def test_schedule_and_agenda(load):
    m = load("ex02_spaced_repetition")
    items = m.schedule(m.load_log(), "2026-11-18")
    by = {it["problem"]: it for it in items}
    assert by["top_k_frequent"]["status"] == "due today"
    assert by["course_schedule"]["status"] == "overdue"
    assert by["two_sum"]["streak"] == 4 and by["two_sum"]["status"] == "upcoming"
    plan = m.agenda(items, "2026-11-18", days=7, max_per_day=3)
    assert len(plan) == 7 and all(len(v) <= 3 for v in plan.values())
    assert plan["2026-11-18"][0] == "course_schedule"
    scheduled = [p for v in plan.values() for p in v]
    assert len(scheduled) == len(set(scheduled)) == 10  # every overdue/due item placed once


def test_bad_result(load, tmp_path):
    m = load("ex02_spaced_repetition")
    f = tmp_path / "log.csv"
    f.write_text("date,problem,pattern,result,minutes\n2026-11-01,x,y,maybe,3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 2"):
        m.load_log(f)


def test_pattern_weakness(load):
    m = load("ex02_spaced_repetition")
    table = m.pattern_weakness(m.load_log())
    assert table[0][0] == "dynamic_programming"
    assert table[0][2] == 0.0


def test_same_day_attempts_keep_log_order(load):
    m = load("ex02_spaced_repetition")
    # solved, failed, solved on one day -> last logged is "solved", streak 1 (not 2)
    log = [("2026-11-05", "solved"), ("2026-11-05", "failed"), ("2026-11-05", "solved")]
    assert m.next_review(log) == ("2026-11-06", 1)
    # failed logged last on the same day -> streak 0
    assert m.next_review([("2026-11-05", "solved"), ("2026-11-05", "failed")]) == ("2026-11-06", 0)
