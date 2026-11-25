import pytest


def test_examples(load):
    m = load("ex06_profile_hotspot")
    assert m.hottest(m.pipeline, 3000) == "dedupe_slow"
    assert m.pipeline(3000) == m.pipeline_fixed(3000)


@pytest.mark.parametrize("n", [0, 1, 2, 7, 100])
def test_fixed_matches_slow(load, n):
    m = load("ex06_profile_hotspot")
    records = m.parse(n)
    assert m.dedupe_fast(records) == m.dedupe_slow(records)


def test_dedupe_keeps_first_occurrence(load):
    m = load("ex06_profile_hotspot")
    recs = [("b", 1), ("a", 2), ("b", 3), ("c", 4), ("a", 5)]
    assert m.dedupe_fast(recs) == [("b", 1), ("a", 2), ("c", 4)]


def test_hottest_finds_planted_function(load):
    m = load("ex06_profile_hotspot")

    def cheap():
        return sum(range(10))

    def heavy():
        total = 0
        for i in range(200_000):
            total += i
        return total

    def outer():
        cheap()
        return heavy()

    assert m.hottest(outer) == "heavy"
    times = m.own_times(outer)
    assert {"outer", "cheap", "heavy"} <= set(times)
    assert not any(name.startswith("<") for name in times)     # no <genexpr>/<lambda>


def test_fix_removes_hotspot(load):
    m = load("ex06_profile_hotspot")
    fast = m.own_times(m.pipeline_fixed, 3000)
    assert "dedupe_slow" not in fast and "dedupe_fast" in fast
    slow_tt = m.best_own_time(m.pipeline, 12_000, "dedupe_slow")
    fast_tt = m.best_own_time(m.pipeline_fixed, 12_000, "dedupe_fast")
    assert fast_tt < 0.25 * slow_tt


def test_is_faster(load):
    m = load("ex06_profile_hotspot")
    records = m.parse(3000)
    assert m.is_faster(lambda: m.dedupe_fast(records), lambda: m.dedupe_slow(records))
    assert not m.is_faster(lambda: m.dedupe_slow(records), lambda: m.dedupe_fast(records))
