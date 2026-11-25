import numpy as np
import pytest


def test_examples(load):
    m = load("ex07_roc_auc")
    assert m.auc_pairs([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]) == 0.75
    assert m.auc_rank([0, 1], [0.5, 0.5]) == 0.5


def test_ties_by_hand(load):
    m = load("ex07_roc_auc")
    y, s = [1, 0, 1, 0, 1, 0], [0.9, 0.9, 0.5, 0.5, 0.5, 0.1]
    # positive 0.9: 0.5 + 1 + 1; each positive 0.5: 0 + 0.5 + 1  -> 5.5 / 9
    for fn in (m.auc_pairs, m.auc_trapezoid, m.auc_rank):
        assert fn(y, s) == pytest.approx(5.5 / 9)


def test_roc_points_one_per_distinct_threshold(load):
    m = load("ex07_roc_auc")
    fpr, tpr = m.roc_curve([1, 0, 1, 0], [0.9, 0.9, 0.5, 0.2])
    assert fpr.tolist() == [0.0, 0.5, 0.5, 1.0]
    assert tpr.tolist() == [0.0, 0.5, 1.0, 1.0]


@pytest.mark.parametrize("seed", range(5))
def test_three_methods_agree_on_random_tied_data(load, seed):
    m = load("ex07_roc_auc")
    rng = np.random.default_rng(seed)
    y = (rng.random(300) < 0.4).astype(int)
    y[:2] = [0, 1]
    s = rng.integers(0, 6, size=300).astype(float)          # heavy ties
    a = m.auc_pairs(y, s)
    assert m.auc_trapezoid(y, s) == pytest.approx(a, abs=1e-12)
    assert m.auc_rank(y, s) == pytest.approx(a, abs=1e-12)


def test_average_ranks(load):
    m = load("ex07_roc_auc")
    assert m.average_ranks([10, 20, 20, 5, 20]).tolist() == [2.0, 4.0, 4.0, 1.0, 4.0]


def test_tie_fix_matters(load):
    m = load("ex07_roc_auc")
    y, s = [1, 0, 1, 0, 1, 0], [0.9, 0.9, 0.5, 0.5, 0.5, 0.1]
    wrong = {m.auc_rank_no_tie_fix(y, s), m.auc_rank_no_tie_fix(y[::-1], s[::-1])}
    assert len(wrong) == 2                                   # order dependent
    assert m.auc_rank(y[::-1], s[::-1]) == pytest.approx(m.auc_rank(y, s))


def test_perfect_inverted_and_constant(load):
    m = load("ex07_roc_auc")
    assert m.auc_rank([0, 0, 1, 1], [1, 2, 3, 4]) == 1.0
    assert m.auc_rank([0, 0, 1, 1], [4, 3, 2, 1]) == 0.0
    assert m.auc_trapezoid([0, 1, 0, 1], [7, 7, 7, 7]) == 0.5


def test_invariant_to_monotone_transform(load):
    m = load("ex07_roc_auc")
    rng = np.random.default_rng(9)
    y = (rng.random(200) < 0.5).astype(int)
    s = y + rng.normal(size=200)
    assert m.auc_rank(y, 1 / (1 + np.exp(-s))) == pytest.approx(m.auc_rank(y, s))


@pytest.mark.parametrize("fn", ["auc_pairs", "auc_trapezoid", "auc_rank"])
def test_single_class_raises(load, fn):
    with pytest.raises(ValueError):
        getattr(load("ex07_roc_auc"), fn)([0, 0, 0], [0.1, 0.2, 0.3])
