"""
Exercise 06 — Confusion Matrix, Precision, Recall, F1            [Tier: ★ Core]
Chapter 35 · Pattern: counting + averaging conventions · Target time: 20 min

Problem
-------
1. ``confusion_matrix(y_true, y_pred, labels)``: C[i, j] = #(true labels[i], predicted
   labels[j]). Rows are truth, columns predictions.
2. ``binary_prf(y_true, y_pred, positive=1)`` -> (precision, recall, f1).
   precision = TP / (TP + FP), recall = TP / (TP + FN), F1 = 2PR / (P + R).
   Convention for 0/0 (no predicted positives, no actual positives, or P + R == 0): 0.0.
3. ``f_beta(p, r, beta)`` = (1 + b^2) P R / (b^2 P + R); beta > 1 weights recall more.
4. ``multiclass_prf(y_true, y_pred, labels, average)`` with average in
   {"macro", "micro", "weighted"}; weighted uses each class's true count (support).

Examples
--------
>>> binary_prf([1, 1, 0, 0, 1], [1, 0, 1, 0, 1])
(0.6666666666666666, 0.6666666666666666, 0.6666666666666666)
>>> binary_prf([0, 0, 0], [0, 0, 0])            # no positives anywhere -> 0 by convention
(0.0, 0.0, 0.0)

Constraints
-----------
- Labels may be any hashable values; a label in y but not in ``labels`` is an error.

Approach ladder
---------------
1. Brute force — for every (i, j) pair of labels count matching rows: O(k^2 n).
2. Optimal    — map labels to 0..k-1 once, then ``np.add.at`` (or bincount on
   i * k + j): O(n + k^2). Every metric is then O(k) arithmetic on C.

Follow-ups
----------
- Micro-F1 equals accuracy for single-label multiclass (every error is one FP and one FN).
- Accuracy paradox: 99 % negatives; "always negative" scores 0.99 accuracy, 0 recall.
- Macro averages treat rare classes as equal citizens; weighted hides them.
- Some libraries warn or return NaN for 0/0; say which convention you use.
- Edge cases: empty input (error), single class, every prediction wrong, P + R == 0.
"""
from __future__ import annotations

import numpy as np


def _div(a: float, b: float) -> float:
    return a / b if b else 0.0


def confusion_matrix_brute(y_true, y_pred, labels) -> np.ndarray:
    k = len(labels)
    C = np.zeros((k, k), dtype=int)
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            C[i, j] = sum(1 for t, p in zip(y_true, y_pred) if t == a and p == b)
    return C


def confusion_matrix(y_true, y_pred, labels) -> np.ndarray:
    if len(y_true) != len(y_pred) or not len(y_true):
        raise ValueError("y_true and y_pred must be non-empty and equal length")
    index = {lab: i for i, lab in enumerate(labels)}
    try:
        t = np.array([index[v] for v in y_true])
        p = np.array([index[v] for v in y_pred])
    except KeyError as e:
        raise ValueError(f"label {e} not in labels") from None
    C = np.zeros((len(labels), len(labels)), dtype=int)
    np.add.at(C, (t, p), 1)            # unbuffered: repeated (t, p) pairs all count
    return C


def binary_prf(y_true, y_pred, positive=1) -> tuple[float, float, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == positive and p == positive)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t != positive and p == positive)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == positive and p != positive)
    precision, recall = _div(tp, tp + fp), _div(tp, tp + fn)
    return precision, recall, _div(2 * precision * recall, precision + recall)


def f_beta(precision: float, recall: float, beta: float = 1.0) -> float:
    b2 = beta * beta
    return _div((1 + b2) * precision * recall, b2 * precision + recall)


def multiclass_prf(y_true, y_pred, labels, average: str = "macro") -> tuple[float, float, float]:
    C = confusion_matrix(y_true, y_pred, labels)
    tp = np.diag(C).astype(float)
    pred_count, true_count = C.sum(axis=0), C.sum(axis=1)
    if average == "micro":
        P = R = _div(float(tp.sum()), float(C.sum()))   # sum FP == sum FN == off-diagonal
        return P, R, _div(2 * P * R, P + R)
    prec = np.array([_div(a, b) for a, b in zip(tp, pred_count)])
    rec = np.array([_div(a, b) for a, b in zip(tp, true_count)])
    f1 = np.array([_div(2 * a * b, a + b) for a, b in zip(prec, rec)])
    if average == "macro":
        w = np.full(len(labels), 1 / len(labels))
    elif average == "weighted":
        w = true_count / true_count.sum()
    else:
        raise ValueError("average must be macro, micro or weighted")
    return float(w @ prec), float(w @ rec), float(w @ f1)


def main() -> None:
    y_true = ["cat", "cat", "dog", "dog", "dog", "bird", "bird", "cat", "dog", "bird"]
    y_pred = ["cat", "dog", "dog", "dog", "cat", "bird", "cat", "cat", "dog", "dog"]
    labels = ["bird", "cat", "dog"]
    C = confusion_matrix(y_true, y_pred, labels)
    print("labels", labels)
    print(C)
    print("brute force agrees:", np.array_equal(C, confusion_matrix_brute(y_true, y_pred, labels)))
    for avg in ("macro", "micro", "weighted"):
        print(f"{avg:<8}", tuple(round(v, 4) for v in multiclass_prf(y_true, y_pred, labels, avg)))
    acc = np.trace(C) / C.sum()
    print("accuracy", acc, " == micro F1:", abs(acc - multiclass_prf(y_true, y_pred, labels, "micro")[2]) < 1e-12)

    print("binary", tuple(round(v, 4) for v in binary_prf([1, 1, 0, 0, 1], [1, 0, 1, 0, 1])))
    print("no predicted positives:", binary_prf([1, 0, 0], [0, 0, 0]))
    p, r = 0.5, 0.8
    print("F0.5, F1, F2 at P=0.5 R=0.8:", round(f_beta(p, r, 0.5), 4), round(f_beta(p, r), 4), round(f_beta(p, r, 2), 4))
    y = [1] * 10 + [0] * 990
    always_neg = [0] * 1000
    print("accuracy paradox: accuracy", sum(a == b for a, b in zip(y, always_neg)) / 1000,
          " recall", binary_prf(y, always_neg)[1])


if __name__ == "__main__":
    main()
