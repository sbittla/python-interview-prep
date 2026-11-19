import random

NAME = "ex11_range_sum_2d"


def test_examples(load):
    m = load(NAME)
    assert m.NumMatrix([[3, 0, 1], [5, 6, 3], [1, 2, 0]]).sum_region(1, 1, 2, 2) == 11
    assert m.RangeSum1D([-2, 0, 3, -5, 2, -1]).sum_range(2, 5) == -1


def test_edge_cases(load):
    m = load(NAME)
    assert m.NumMatrix([[-7]]).sum_region(0, 0, 0, 0) == -7
    assert m.NumMatrix([[1, 2, 3, 4]]).sum_region(0, 1, 0, 3) == 9
    assert m.NumMatrix([[1], [2], [3]]).sum_region(0, 0, 2, 0) == 6
    assert m.RangeSum1D([4]).sum_range(0, 0) == 4


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1011)
    for _ in range(60):
        r, c = rng.randint(1, 7), rng.randint(1, 7)
        grid = [[rng.randint(-9, 9) for _ in range(c)] for _ in range(r)]
        fast, rows, brute = m.NumMatrix(grid), m.RowPrefixMatrix(grid), m.BruteMatrix(grid)
        for _ in range(25):
            r1, r2 = sorted(rng.randint(0, r - 1) for _ in range(2))
            c1, c2 = sorted(rng.randint(0, c - 1) for _ in range(2))
            want = brute.sum_region(r1, c1, r2, c2)
            assert fast.sum_region(r1, c1, r2, c2) == want
            assert rows.sum_region(r1, c1, r2, c2) == want
        one = m.RangeSum1D(grid[0])
        i, j = sorted(rng.randint(0, c - 1) for _ in range(2))
        assert one.sum_range(i, j) == sum(grid[0][i:j + 1])
