import sys

import pytest


def test_examples(load):
    m = load("ex05_version_features")
    assert m.supports("match statement (PEP 634)", (3, 9)) is False
    assert m.supports("ExceptionGroup / except* (PEP 654)", (3, 11)) is True
    assert m.check_baseline((3, 12)) == "ok"
    assert list(m.batched("abcde", 2)) == [("a", "b"), ("c", "d"), ("e",)]


@pytest.mark.parametrize("feature, version, expected", [
    ("match statement (PEP 634)", (3, 10), True),
    ("X | Y unions at runtime (PEP 604)", (3, 9), False),
    ("tomllib module (PEP 680)", (3, 10), False),
    ("type-parameter syntax (PEP 695)", (3, 11), False),
    ("type-parameter syntax (PEP 695)", (3, 12), True),
    ("itertools.batched", (3, 12), True),
    ("template strings t'' (PEP 750)", (3, 13), False),
    ("template strings t'' (PEP 750)", (3, 14), True),
    ("match statement (PEP 634)", (3, 10, 4, "final", 0), True),  # full version_info shape
    ("match statement (PEP 634)", (4, 0), True),
])
def test_supports(load, feature, version, expected):
    assert load("ex05_version_features").supports(feature, version) is expected


def test_unknown_feature_raises(load):
    with pytest.raises(KeyError):
        load("ex05_version_features").supports("goto statement", (3, 12))


def test_tuple_not_string_comparison(load):
    m = load("ex05_version_features")
    assert "3.9" > "3.10"                                   # the string trap
    assert m.supports("match statement (PEP 634)", (3, 9)) is False


def test_report_and_baseline(load):
    m = load("ex05_version_features")
    report = m.feature_report((3, 11))
    assert set(report) == set(m.FEATURES)
    assert [k for k, v in report.items() if not v] == [
        "type-parameter syntax (PEP 695)", "itertools.batched", "template strings t'' (PEP 750)"]
    msg = m.check_baseline((3, 9))
    assert msg.startswith("below 3.10: avoid ")
    assert "match statement (PEP 634)" in msg and "tomllib" not in msg
    assert m.check_baseline((3, 10)) == "ok"
    assert m.check_baseline((3, 11), minimum=(3, 12)).count("(PEP") == 1


def test_runtime_probe_agrees_with_table(load):
    m = load("ex05_version_features")
    assert m.probe_runtime() == m.feature_report(sys.version_info[:2])


@pytest.mark.parametrize("data, n", [("", 3), ("abc", 1), ("abcdefg", 3), (range(10), 10), (range(5), 7)])
def test_batched_fallback_matches(load, data, n):
    m = load("ex05_version_features")
    expected = [tuple(list(data)[i:i + n]) for i in range(0, len(list(data)), n)]
    assert list(m._batched_fallback(data, n)) == expected
    assert list(m.batched(data, n)) == expected


def test_batched_rejects_zero(load):
    m = load("ex05_version_features")
    with pytest.raises(ValueError):
        list(m._batched_fallback("abc", 0))
