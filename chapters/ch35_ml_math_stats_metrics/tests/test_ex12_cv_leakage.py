import numpy as np
import pytest


def _check_partition(splits, n):
    tests = np.concatenate([te for _, te in splits])
    assert sorted(tests.tolist()) == list(range(n))               # every row tested exactly once
    for tr, te in splits:
        assert not set(tr.tolist()) & set(te.tolist())
        assert len(tr) + len(te) == n


def test_example(load):
    assert [len(te) for _, te in load("ex12_cv_leakage").kfold(10, 3)] == [4, 3, 3]


@pytest.mark.parametrize("n, k", [(10, 2), (11, 3), (7, 7), (100, 10)])
def test_kfold_partition_and_sizes(load, n, k):
    splits = load("ex12_cv_leakage").kfold(n, k, seed=n)
    _check_partition(splits, n)
    sizes = [len(te) for _, te in splits]
    assert max(sizes) - min(sizes) <= 1


def test_stratified_balances_each_class(load):
    m = load("ex12_cv_leakage")
    rng = np.random.default_rng(1)
    y = rng.choice([0, 1, 2], size=97, p=[0.7, 0.2, 0.1])
    splits = m.stratified_kfold(y, 5, seed=3)
    _check_partition(splits, len(y))
    for c in np.unique(y):
        counts = [int((y[te] == c).sum()) for _, te in splits]
        assert max(counts) - min(counts) <= 1
    sizes = [len(te) for _, te in splits]
    assert max(sizes) - min(sizes) <= 1


def test_group_kfold_never_splits_a_group(load):
    m = load("ex12_cv_leakage")
    rng = np.random.default_rng(2)
    groups = rng.integers(0, 15, size=80)
    splits = m.group_kfold(groups, 4)
    _check_partition(splits, len(groups))
    for tr, te in splits:
        assert not set(groups[tr].tolist()) & set(groups[te].tolist())
    with pytest.raises(ValueError):
        m.group_kfold([1, 1, 2], 3)


def test_group_kfold_balances_fold_sizes(load):
    # groups sized 5, 4, 3, 3, 1; greedy largest-first gives 5+3 and 4+3+1
    groups = list("aaaaa" "bbbb" "ccc" "ddd" "e")
    sizes = sorted(len(te) for _, te in load("ex12_cv_leakage").group_kfold(groups, 2))
    assert sizes == [8, 8]


def test_time_series_split_never_trains_on_the_future(load):
    m = load("ex12_cv_leakage")
    splits = m.time_series_split(23, 4)
    for tr, te in splits:
        assert tr.max() < te.min()
        assert np.all(np.diff(te) == 1)
    assert splits[-1][1][-1] == 22
    with pytest.raises(ValueError):
        m.time_series_split(3, 5)


def test_class_weights(load):
    w = load("ex12_cv_leakage").class_weights(np.array([0] * 12 + [1] * 3))
    assert w == pytest.approx({0: 15 / 24, 1: 15 / 6})


@pytest.mark.parametrize("bad", [(5, 1), (3, 4)])
def test_invalid_k(load, bad):
    with pytest.raises(ValueError):
        load("ex12_cv_leakage").kfold(*bad)


def test_leakage_inflates_accuracy_on_random_labels(load):
    m = load("ex12_cv_leakage")
    rng = np.random.default_rng(7)
    X = rng.normal(size=(60, 1000))
    y = rng.permutation(np.r_[np.zeros(30, int), np.ones(30, int)])
    leaky, honest = m.cv_accuracy(X, y, False), m.cv_accuracy(X, y, True)
    assert leaky > 0.8
    assert 0.25 < honest < 0.75
