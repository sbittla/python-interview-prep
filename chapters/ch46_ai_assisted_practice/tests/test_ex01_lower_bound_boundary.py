import bisect
import random

import pytest

M = "ex01_lower_bound_boundary"


def test_oracle_is_a_correct_lower_bound(load):
    m = load(M)
    rng = random.Random(7)
    for _ in range(300):
        a = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 8)))
        x = rng.randint(-2, 11)
        assert m.oracle(a, x) == bisect.bisect_left(a, x)


def test_random_case_has_the_right_shape(load):
    m = load(M)
    rng = random.Random(3)
    cases = [m.random_case(rng) for _ in range(300)]
    assert all(a == sorted(a) and len(a) <= 6 for a, _ in cases)
    assert any(len(a) == 0 for a, _ in cases)
    assert any(len(a) != len(set(a)) for a, _ in cases)            # duplicates occur
    assert any(a and x > a[-1] for a, x in cases)                   # x above all
    assert any(a and x < a[0] for a, x in cases)                    # x below all


def test_harness_finds_the_generated_bug(load):
    m = load(M)
    bad = m.find_counterexample(m.generated_first_ge)
    assert bad is not None
    a, x = bad
    assert m.generated_first_ge(a, x) != bisect.bisect_left(a, x)  # a real failure
    assert len(a) <= 2                                              # shrunk: a small one


def test_harness_is_not_vacuous(load):
    m = load(M)
    assert m.find_counterexample(bisect.bisect_left) is None
    assert m.find_counterexample(lambda a, x: 0) is not None       # obviously wrong
    assert m.find_counterexample(bisect.bisect_right) is not None  # wrong on duplicates


def test_edge_cases_are_right_and_catch_the_bug(load):
    m = load(M)
    assert len(m.EDGE_CASES) >= 4
    for (a, x), want in m.EDGE_CASES:
        assert want == bisect.bisect_left(a, x)
    assert any(a == [] for (a, _), _ in m.EDGE_CASES)
    assert any(m.generated_first_ge(*c) != w for c, w in m.EDGE_CASES)


def test_fix_passes_everything(load):
    m = load(M)
    assert m.find_counterexample(m.first_ge) is None
    assert m.find_counterexample(m.first_ge, trials=1000, seed=99) is None
    assert all(m.first_ge(*c) == w for c, w in m.EDGE_CASES)


@pytest.mark.parametrize("a, x", [([], 0), ([1], 0), ([1], 1), ([1], 2), ([1, 1, 1], 1),
                                  (list(range(0, 2000, 2)), 1999), (list(range(1000)), 5000)])
def test_fix_matches_bisect(load, a, x):
    assert load(M).first_ge(a, x) == bisect.bisect_left(a, x)


def test_fix_is_logarithmic(load):
    m = load(M)

    class Reads(list):
        count = 0

        def __getitem__(self, i):
            Reads.count += 1
            return list.__getitem__(self, i)

        def __iter__(self):                                          # a linear scan
            raise AssertionError("iterated the whole list")

        def __contains__(self, x):
            raise AssertionError("linear `in` on the list")

    a = Reads(range(1 << 16))
    assert m.first_ge(a, 40000) == 40000
    assert m.first_ge(a, 1 << 20) == 1 << 16
    assert Reads.count <= 2 * 17                                      # log2(65536) + 1 each


def test_complexity_stated(load):
    c = load(M).COMPLEXITY
    norm = {k: v.replace(" ", "").lower() for k, v in c.items()}
    assert norm == {"time": "o(logn)", "space": "o(1)"}
