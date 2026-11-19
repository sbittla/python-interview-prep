import math
import random
from itertools import combinations


def test_examples(load):
    m = load("ex07_subsets_bitmask")
    assert m.subsets([1, 2, 3]) == [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
    assert m.submasks(0b101) == [5, 4, 1, 0]
    assert m.k_subset_masks(4, 2)[:3] == [0b11, 0b101, 0b110]


def test_empty(load):
    m = load("ex07_subsets_bitmask")
    assert m.subsets([]) == [[]]
    assert m.subset_sums([]) == m.subset_sums_brute([]) == [0]
    assert m.submasks(0) == [0]


def test_subsets_match_itertools(load):
    m = load("ex07_subsets_bitmask")
    nums = [4, 8, 15, 16, 23]
    got = sorted(tuple(s) for s in m.subsets(nums))
    expected = sorted(c for r in range(6) for c in combinations(nums, r))
    assert got == expected


def test_subset_sums_random(load):
    m = load("ex07_subsets_bitmask")
    rng = random.Random(9)
    for _ in range(50):
        nums = [rng.randint(-20, 20) for _ in range(rng.randint(0, 10))]
        assert m.subset_sums(nums) == m.subset_sums_brute(nums)


def test_submasks_exact(load):
    m = load("ex07_subsets_bitmask")
    for mask in range(1 << 7):
        expected = sorted((s for s in range(1 << 7) if s & mask == s), reverse=True)
        assert m.submasks(mask) == expected


def test_k_subsets(load):
    m = load("ex07_subsets_bitmask")
    for n in range(0, 9):
        for k in range(-1, n + 2):
            expected = [x for x in range(1 << n) if bin(x).count("1") == k]
            got = m.k_subset_masks(n, k)
            assert got == expected
            assert len(got) == (math.comb(n, k) if 0 <= k <= n else 0)
