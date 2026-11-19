import pytest

STRONG = {"core": 8, "gotchas": 7, "complexity": 11, "coding": 8}
SAMPLE = {"core": 7, "gotchas": 4, "complexity": 9, "coding": 6}
WEAK = {"core": 3, "gotchas": 2, "complexity": 4, "coding": 0}


def test_examples(load):
    m = load("ex02_placement")
    assert m.place(STRONG)["path"] == "fast"
    assert m.choose_plan("full", 5) == ("crash-4", True)


@pytest.mark.parametrize("scores, path, weak", [
    (STRONG, "fast", []),
    (SAMPLE, "full", ["gotchas"]),
    (WEAK, "foundations", ["coding", "gotchas", "complexity", "core"]),
    ({"core": 6, "gotchas": 6, "complexity": 9, "coding": 6}, "fast", []),   # exactly 75 %
    ({"core": 6, "gotchas": 5, "complexity": 9, "coding": 6}, "full", ["gotchas"]),
    ({"core": 8, "gotchas": 8, "complexity": 12, "coding": 0}, "full", ["coding"]),
    ({"core": 4, "gotchas": 4, "complexity": 5, "coding": 2}, "full",        # 15/36 = 42 %
     ["coding", "complexity", "core", "gotchas"]),
    ({"core": 4, "gotchas": 4, "complexity": 4, "coding": 2}, "foundations",  # 14/36 = 39 %
     ["coding", "complexity", "core", "gotchas"]),
])
def test_place(load, scores, path, weak):
    got = load("ex02_placement").place(scores)
    assert got["path"] == path
    assert got["weak"] == weak


@pytest.mark.parametrize("path, weeks, expected", [
    ("fast", 4, ("crash-4", False)), ("fast", 8, ("standard-8", False)),
    ("full", 7, ("crash-4", True)), ("full", 8, ("standard-8", False)),
    ("foundations", 12, ("foundations-12", False)), ("foundations", 11, ("standard-8", True)),
])
def test_choose_plan(load, path, weeks, expected):
    assert load("ex02_placement").choose_plan(path, weeks) == expected


def test_weekly_plan_tracks_and_repair(load):
    m = load("ex02_placement")
    weeks = dict(m.weekly_plan(SAMPLE, "L", 8)["weeks"])
    assert len(weeks) == 8 and weeks[6] == "Track part 1: Ch. 38-40"
    assert "Repair: gotchas" in weeks[1] and weeks[1].endswith("diagnostic retake")
    fast = dict(m.weekly_plan(STRONG, "S", 10)["weeks"])
    assert fast[1].startswith("Skim Part I") and "Repair" not in fast[1]
    assert "track S highlights" in dict(m.weekly_plan(STRONG, "S", 4)["weeks"])[3]
    found = m.weekly_plan(WEAK, "M", 12)
    assert len(found["weeks"]) == 12 and found["weeks"][3][1].endswith("diagnostic retake")
    assert dict(found["weeks"])[10] == "Track part 1: Ch. 33-35"


def test_tables_not_mutated(load):
    m = load("ex02_placement")
    before = (list(m.STANDARD), list(m.CRASH), list(m.FOUNDATIONS))
    for track in "SML":
        for scores in (STRONG, SAMPLE, WEAK):
            for weeks in (4, 8, 12):
                m.weekly_plan(scores, track, weeks)
    assert (m.STANDARD, m.CRASH, m.FOUNDATIONS) == before


@pytest.mark.parametrize("call", [
    lambda m: m.place({"core": 9}),
    lambda m: m.place({"coding": -1}),
    lambda m: m.weekly_plan(STRONG, "X", 8),
    lambda m: m.choose_plan("fast", 0),
    lambda m: m.choose_plan("slow", 8),
])
def test_errors(load, call):
    with pytest.raises(ValueError):
        call(load("ex02_placement"))
