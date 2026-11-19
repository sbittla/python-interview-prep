import copy

import pytest


@pytest.mark.parametrize("nums, target, expected", [
    ([], 0, 0), ([5], 10, 0), ([2, 2, 2], 4, 3), ([1, 3, 2, 2], 4, 2),
    ([0, 0, 0, 0], 0, 6), ([-1, 1, -1, 1], 0, 4), ([1, 2, 3], 100, 0),
])
def test_count_pairs(load, nums, target, expected):
    m = load("ex05_stress_tester")
    assert m.count_pairs_brute(nums, target) == expected
    assert m.count_pairs_fast(nums, target) == expected


def test_fast_agrees_with_brute(load):
    m = load("ex05_stress_tester")
    assert m.stress(m.count_pairs_fast, m.count_pairs_brute, m.gen_case,
                    trials=1000, seed=7) is None


def test_buggy_is_caught_and_shrunk(load):
    m = load("ex05_stress_tester")
    bad = m.stress(m.count_pairs_two_pointer_buggy, m.count_pairs_brute, m.gen_case)
    assert bad is not None

    def fails(args):
        return m.count_pairs_two_pointer_buggy(*copy.deepcopy(args)) != m.count_pairs_brute(*args)

    small = m.shrink(bad, fails)
    assert fails(small)
    assert len(small[0]) == 3                 # the bug needs a duplicate partner


def test_stress_is_deterministic(load):
    m = load("ex05_stress_tester")
    a = m.stress(m.count_pairs_two_pointer_buggy, m.count_pairs_brute, m.gen_case, seed=3)
    b = m.stress(m.count_pairs_two_pointer_buggy, m.count_pairs_brute, m.gen_case, seed=3)
    assert a is not None and a == b


def test_candidate_cannot_corrupt_args(load):
    m = load("ex05_stress_tester")

    def destructive(nums, target):
        nums.clear()
        return 0

    def gen(rng):
        return [1, 2], 3

    assert m.stress(destructive, m.count_pairs_brute, gen, trials=1) == ([1, 2], 3)


def test_shrink_generic(load):
    m = load("ex05_stress_tester")
    # fails whenever some value >= 4: minimal is a single 4
    assert m.shrink(([9, 1, 30, 2],), lambda a: any(v >= 4 for v in a[0])) == ([4],)
    # an int argument shrinks toward zero, negatives too
    assert m.shrink((-37,), lambda a: a[0] <= -5) == (-5,)
    # nothing smaller fails -> unchanged
    assert m.shrink(([1],), lambda a: a == ([1],)) == ([1],)
