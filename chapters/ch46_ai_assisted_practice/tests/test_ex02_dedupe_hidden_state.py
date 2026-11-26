import pytest

M = "ex02_dedupe_hidden_state"


def test_leaks_state_detects_the_mutable_default(load):
    m = load(M)
    assert m.leaks_state(m.generated_dedupe) is True
    assert m.leaks_state(m.dedupe) is False
    assert m.leaks_state(lambda xs: list(dict.fromkeys(xs))) is False


def test_leaks_state_does_not_depend_on_earlier_calls(load):
    m = load(M)
    m.generated_dedupe([1, 2, 3])
    assert m.leaks_state(m.generated_dedupe) is True
    assert m.leaks_state(m.generated_dedupe) is True                 # still, on a second check


def test_leaks_state_flags_a_wrong_answer_too(load):
    m = load(M)
    assert m.leaks_state(lambda xs: list(xs)) is True                 # never dedupes


def test_eq_calls_exposes_quadratic_lookup(load):
    m = load(M)

    def fresh(xs):
        return m.generated_dedupe(xs, [])

    for n in (50, 100, 200):
        assert m.eq_calls(fresh, n) == n * (n - 1) // 2
    assert m.eq_calls(m.generated_dedupe, 100) >= 100 * 99 // 2


def test_eq_calls_is_zero_for_hash_lookup(load):
    m = load(M)
    assert m.eq_calls(m.dedupe, 500) == 0
    assert m.eq_calls(lambda xs: list(dict.fromkeys(xs)), 500) == 0


@pytest.mark.parametrize("items, expected", [
    ([], []),
    ([1], [1]),
    ([3, 1, 3, 2, 1], [3, 1, 2]),
    (["b", "a", "b"], ["b", "a"]),
    ([1, True, 1.0], [1]),                                            # 1 == True == 1.0
    ((x % 3 for x in range(10)), [0, 1, 2]),                          # any iterable
])
def test_fix_values(load, items, expected):
    assert load(M).dedupe(items) == expected


def test_fix_repeated_calls_are_independent(load):
    m = load(M)
    assert m.dedupe([3, 1]) == [3, 1]
    assert m.dedupe([3, 4]) == [3, 4]


def test_complexity_stated(load):
    c = load(M).COMPLEXITY
    assert {k: v.replace(" ", "").lower() for k, v in c.items()} == {"time": "o(n)",
                                                                      "space": "o(n)"}
