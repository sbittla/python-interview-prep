import random

import numpy as np
import pytest


def test_examples(load):
    m = load("ex06_confusion_prf")
    p, r, f = m.binary_prf([1, 1, 0, 0, 1], [1, 0, 1, 0, 1])
    assert (p, r, f) == pytest.approx((2 / 3, 2 / 3, 2 / 3))
    assert m.binary_prf([0, 0, 0], [0, 0, 0]) == (0.0, 0.0, 0.0)


def test_confusion_matrix_by_hand(load):
    m = load("ex06_confusion_prf")
    y_true = ["cat", "cat", "dog", "dog", "dog", "bird", "bird", "cat", "dog", "bird"]
    y_pred = ["cat", "dog", "dog", "dog", "cat", "bird", "cat", "cat", "dog", "dog"]
    C = m.confusion_matrix(y_true, y_pred, ["bird", "cat", "dog"])
    assert C.tolist() == [[1, 1, 1], [0, 2, 1], [0, 1, 3]]
    # per class F1: bird 0.5, cat 4/7, dog 2/3
    assert m.multiclass_prf(y_true, y_pred, ["bird", "cat", "dog"], "macro") == pytest.approx(
        (0.7, (1 / 3 + 2 / 3 + 3 / 4) / 3, (0.5 + 4 / 7 + 2 / 3) / 3))


def test_random_against_brute_force(load):
    m = load("ex06_confusion_prf")
    rng = random.Random(6)
    for _ in range(100):
        labels = list(range(rng.randint(2, 5)))
        n = rng.randint(1, 40)
        t = [rng.choice(labels) for _ in range(n)]
        p = [rng.choice(labels) for _ in range(n)]
        C = m.confusion_matrix(t, p, labels)
        assert np.array_equal(C, m.confusion_matrix_brute(t, p, labels))
        assert C.sum() == n
        acc = sum(a == b for a, b in zip(t, p)) / n
        assert m.multiclass_prf(t, p, labels, "micro")[2] == pytest.approx(acc)


def test_binary_matches_multiclass_per_class(load):
    m = load("ex06_confusion_prf")
    t = [1, 0, 1, 1, 0, 0, 1]
    p = [1, 1, 0, 1, 0, 0, 0]
    pr, rc, f1 = m.binary_prf(t, p)
    assert (pr, rc) == pytest.approx((2 / 3, 1 / 2))
    assert f1 == pytest.approx(2 * pr * rc / (pr + rc))


@pytest.mark.parametrize("t, p, expected", [
    ([1, 0, 0], [0, 0, 0], (0.0, 0.0, 0.0)),          # no predicted positives
    ([0, 0, 0], [1, 0, 0], (0.0, 0.0, 0.0)),          # no actual positives
    ([1, 0], [0, 1], (0.0, 0.0, 0.0)),                # P + R == 0
    ([1, 1], [1, 1], (1.0, 1.0, 1.0)),
])
def test_zero_division_conventions(load, t, p, expected):
    assert load("ex06_confusion_prf").binary_prf(t, p) == expected


def test_f_beta(load):
    m = load("ex06_confusion_prf")
    assert m.f_beta(0.5, 0.8, 1) == pytest.approx(2 * 0.4 / 1.3)
    assert m.f_beta(0.5, 0.8, 2) > m.f_beta(0.5, 0.8, 1) > m.f_beta(0.5, 0.8, 0.5)
    assert m.f_beta(0.0, 0.0, 2) == 0.0


def test_weighted_uses_support(load):
    m = load("ex06_confusion_prf")
    t = [0, 0, 0, 1]
    p = [0, 0, 0, 0]
    _, _, f_macro = m.multiclass_prf(t, p, [0, 1], "macro")
    _, _, f_weighted = m.multiclass_prf(t, p, [0, 1], "weighted")
    f0 = 2 * 0.75 * 1 / 1.75
    assert f_macro == pytest.approx(f0 / 2) and f_weighted == pytest.approx(0.75 * f0)


def test_invalid_inputs(load):
    m = load("ex06_confusion_prf")
    with pytest.raises(ValueError):
        m.confusion_matrix([], [], [0, 1])
    with pytest.raises(ValueError):
        m.confusion_matrix([0, 2], [0, 1], [0, 1])
    with pytest.raises(ValueError):
        m.multiclass_prf([0], [0], [0, 1], "median")
