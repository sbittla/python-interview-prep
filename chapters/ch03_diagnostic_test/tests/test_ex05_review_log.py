import pytest


def rows_of(m, attempts):
    rows = []
    for day, result in attempts:
        m.record(rows, day, "p", "core", result, 5)
    return rows


def test_examples(load):
    m = load("ex05_review_log")
    assert m.next_due("2026-11-18", 0) == "2026-11-19"
    assert m.projected_dates("2026-11-18", "failed") == [
        "2026-11-19", "2026-11-20", "2026-11-23", "2026-11-30", "2026-12-21"]


@pytest.mark.parametrize("streak, expected", [
    (0, "2026-11-02"), (1, "2026-11-02"), (2, "2026-11-04"), (3, "2026-11-08"),
    (4, "2026-11-22"), (5, None), (9, None),
])
def test_ladder(load, streak, expected):
    assert load("ex05_review_log").next_due("2026-11-01", streak) == expected


def test_projected_solved_and_year_boundary(load):
    m = load("ex05_review_log")
    assert m.projected_dates("2026-12-30", "solved") == [
        "2026-12-31", "2027-01-03", "2027-01-10", "2027-01-31"]


def test_failure_restarts_ladder(load):
    m = load("ex05_review_log")
    rows = rows_of(m, [("2026-11-01", "solved"), ("2026-11-02", "solved"),
                       ("2026-11-05", "struggled")])
    assert m.due(rows, "2026-11-06") == [("2026-11-06", "p")]
    assert m.due(rows, "2026-11-05") == []


def test_unsorted_log_and_retirement(load):
    m = load("ex05_review_log")
    attempts = [("2026-11-12", "solved"), ("2026-11-01", "failed"), ("2026-11-02", "solved"),
                ("2026-11-03", "solved"), ("2026-11-06", "solved")]
    rows = rows_of(m, attempts)
    assert m.due(rows, "2099-01-01") == [("2026-12-03", "p")]   # streak 4 -> +21
    m.record(rows, "2026-12-03", "p", "core", "solved", 5)
    assert m.due(rows, "2099-01-01") == []                      # streak 5 -> retired


def test_seed_and_overdue_items_stay_due(load):
    m = load("ex05_review_log")
    log = m.seed_from_diagnostic([30, 2], "2026-11-18")
    assert [r["problem"] for r in log] == ["diag-Q02", "diag-Q30"]
    assert [r["minutes"] for r in log] == [1, 15]
    assert m.due(log, "2026-11-25") == [("2026-11-19", "diag-Q02"), ("2026-11-19", "diag-Q30")]
    assert m.seed_from_diagnostic([], "2026-11-18") == []


def test_csv_round_trip(load, tmp_path):
    m = load("ex05_review_log")
    log = m.seed_from_diagnostic([9, 17, 29], "2026-11-18")
    path = tmp_path / "log.csv"
    m.write_log(log, path)
    assert path.read_text(encoding="utf-8").splitlines()[0] == "date,problem,pattern,result,minutes"
    assert m.read_log(path) == log


@pytest.mark.parametrize("call", [
    lambda m: m.seed_from_diagnostic([31], "2026-11-18"),
    lambda m: m.record([], "2026-11-18", "p", "core", "meh", 1),
    lambda m: m.record([], "18/11/2026", "p", "core", "solved", 1),
    lambda m: m.projected_dates("2026-11-18", "ok"),
    lambda m: m.next_due("2026-11-18", -1),
    lambda m: m.due([{"date": "2026-11-18", "problem": "p", "pattern": "x",
                      "result": "??", "minutes": 1}]),
])
def test_errors(load, call):
    with pytest.raises(ValueError):
        call(load("ex05_review_log"))


def test_same_day_attempts_keep_file_order(load):
    m = load("ex05_review_log")
    failed_last = rows_of(m, [("2026-11-10", "solved"), ("2026-11-10", "failed")])
    assert m.due(failed_last, "2099-01-01") == [("2026-11-11", "p")]   # last row = failed
    solved_last = rows_of(m, [("2026-11-10", "failed"), ("2026-11-10", "solved")])
    assert m.due(solved_last, "2099-01-01") == [("2026-11-11", "p")]   # streak 1 -> +1
    two = rows_of(m, [("2026-11-09", "solved"), ("2026-11-10", "failed"), ("2026-11-10", "solved")])
    assert m.due(two, "2099-01-01") == [("2026-11-11", "p")]
    ok = rows_of(m, [("2026-11-10", "solved"), ("2026-11-10", "solved")])
    assert m.due(ok, "2099-01-01") == [("2026-11-13", "p")]            # streak 2 -> +3
