import math

import pytest


def test_examples(load):
    m = load("ex05_fenwick_segment_tree")
    f = m.Fenwick([5, 1, 4, 2])
    assert f.range_sum(1, 3) == 5
    f.add(2, 10)
    assert f.prefix_sum(4) == 22
    assert m.SegmentTreeMin([5, 1, 4, 2]).range_min(2, 4) == 2


def test_all_ranges_small(load):
    m = load("ex05_fenwick_segment_tree")
    vals = [3, -1, 4, 1, -5, 9, 2, 6, -5]
    f, s = m.Fenwick(vals), m.SegmentTreeMin(vals)
    for lo in range(len(vals)):
        assert f.prefix_sum(lo) == sum(vals[:lo])
        for hi in range(lo + 1, len(vals) + 1):
            assert f.range_sum(lo, hi) == sum(vals[lo:hi])
            assert s.range_min(lo, hi) == min(vals[lo:hi])


def test_single_element(load):
    m = load("ex05_fenwick_segment_tree")
    f, s = m.Fenwick([7]), m.SegmentTreeMin([7])
    assert f.range_sum(0, 1) == 7 and s.range_min(0, 1) == 7
    f.add(0, -10)
    s.set(0, -3)
    assert f.prefix_sum(1) == -3 and s.range_min(0, 1) == -3


@pytest.mark.parametrize("n, ops, seed", [(1, 50, 1), (2, 200, 5), (13, 500, 6), (300, 1500, 7)])
def test_cross_check(load, n, ops, seed):
    assert load("ex05_fenwick_segment_tree").cross_check(n, ops, seed)


def test_logarithmic_cells(load):
    m = load("ex05_fenwick_segment_tree")
    for n in (16, 64, 256):
        wf, ws = m.max_touched_per_query(n)
        assert wf <= 2 * math.log2(n) and ws <= 2 * math.log2(n)
    f = m.Fenwick([0] * 1024)
    f.touched = 0
    f.add(0, 1)
    assert f.touched == 11                         # cells 1, 2, 4, ..., 1024


@pytest.mark.parametrize("lo, hi", [(2, 2), (3, 1), (-1, 2), (0, 5)])
def test_bad_range(load, lo, hi):
    with pytest.raises(ValueError):
        load("ex05_fenwick_segment_tree").SegmentTreeMin([1, 2, 3, 4]).range_min(lo, hi)
