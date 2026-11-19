import pytest

NAMES = [f"s{i:02d}" for i in range(1, 11)]


@pytest.mark.parametrize("name", NAMES)
def test_answer_matches_measurement(load, name):
    m = load("ex03_classify_snippets")
    assert m.ANSWERS[name] == m.measured(name)


def test_exact_counts(load):
    m = load("ex03_classify_snippets")
    n = 16
    assert m.s01(n) == 16 and m.s02(n) == 32 and m.s03(n) == 256
    assert m.s04(n) == 120                 # n(n-1)/2
    assert m.s05(n) == 4 and m.s06(n) == 64
    assert m.s07(n) == 31                  # 16 + 8 + 4 + 2 + 1 < 2n
    assert m.s08(n) == 100 and m.s08(10**6) == 100
    assert m.s09(n) == 2 ** 16
    assert m.s10(n) == 120                 # every miss scans the whole list


def test_all_ten_answered(load):
    m = load("ex03_classify_snippets")
    assert sorted(m.ANSWERS) == NAMES
