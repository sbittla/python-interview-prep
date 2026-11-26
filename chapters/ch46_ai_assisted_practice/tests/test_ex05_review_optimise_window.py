import random

import pytest

M = "ex05_review_optimise_window"


def brute(nums, k):
    if not 1 <= k <= len(nums):
        raise ValueError
    return max(sum(nums[s:s + k]) for s in range(len(nums) - k + 1))


def run(fn, case):
    try:
        return fn(*case)
    except ValueError:
        return ValueError


def test_review_is_complete(load):
    m = load(M)
    cats = {c for c, _ in m.REVIEW}
    assert cats <= set(m.CATEGORIES)
    assert {"correctness", "complexity", "edge case"} <= cats
    assert all(len(text.split()) >= 8 for _, text in m.REVIEW)         # full sentences
    joined = " ".join(text for _, text in m.REVIEW)
    assert "range(" in joined or "len(nums) - k" in joined              # points at the code


def test_edge_cases_are_right_and_catch_the_bug(load):
    m = load(M)
    for case, want in m.EDGE_CASES:
        assert run(brute, case) == want
    assert any(run(m.generated_max_window_sum, c) != w for c, w in m.EDGE_CASES)
    assert any(w is ValueError for _, w in m.EDGE_CASES)
    assert any(len(c[0]) == c[1] for c, w in m.EDGE_CASES if w is not ValueError)


def test_reads_counts_element_access(load):
    m = load(M)
    assert m.reads(lambda s, k: s[0] + s[1], [1, 2, 3], 1) == 2
    assert m.reads(lambda s, k: sum(s[:k]), [1, 2, 3], 3) == 3


def test_generated_is_quadratic_fixed_is_linear(load):
    m = load(M)
    nums = list(range(1000))
    assert m.reads(m.generated_max_window_sum, nums, 500) >= 500 * 499
    assert m.reads(m.max_window_sum, nums, 500) <= 2 * len(nums)
    assert m.reads(m.max_window_sum, nums * 4, 2000) <= 2 * 4 * len(nums)


def test_fix_passes_edge_cases(load):
    m = load(M)
    assert len(m.EDGE_CASES) >= 4
    assert all(run(m.max_window_sum, c) == w for c, w in m.EDGE_CASES)


def test_fix_matches_brute_force_on_random_inputs(load):
    m = load(M)
    rng = random.Random(8)
    for _ in range(1000):
        nums = [rng.randint(-20, 20) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(nums))
        assert m.max_window_sum(nums, k) == brute(nums, k)


@pytest.mark.parametrize("nums, k", [([1, 2], 0), ([1, 2], -1), ([1, 2], 3), ([], 1)])
def test_fix_rejects_bad_k(load, nums, k):
    with pytest.raises(ValueError):
        load(M).max_window_sum(nums, k)


def test_complexity_stated(load):
    c = load(M).COMPLEXITY
    assert {k: v.replace(" ", "").lower() for k, v in c.items()} == {"time": "o(n)",
                                                                      "space": "o(1)"}
