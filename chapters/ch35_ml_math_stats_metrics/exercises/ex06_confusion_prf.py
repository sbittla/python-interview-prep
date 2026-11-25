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

Hints
-----
- Map labels to 0..k-1 with a dict, then ``np.add.at(C, (t, p), 1)``.
- Precision is per predicted column, recall per true row: TP = diag(C).
- Guard every division: 0/0 -> 0.0 by this exercise's convention.
- Micro averaging pools TP/FP/FN over classes before dividing.

Wrong-but-tempting
------------------
- ``C[t, p] += 1`` with fancy indexing: repeated (t, p) pairs count once.
- F1 as the mean of P and R (arithmetic, not harmonic).
- Reporting accuracy on a 99:1 dataset and calling the model good.

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
    raise NotImplementedError("TODO")


def confusion_matrix(y_true, y_pred, labels) -> np.ndarray:
    raise NotImplementedError("TODO")


def binary_prf(y_true, y_pred, positive=1) -> tuple[float, float, float]:
    raise NotImplementedError("TODO")


def f_beta(precision: float, recall: float, beta: float = 1.0) -> float:
    raise NotImplementedError("TODO")


def multiclass_prf(y_true, y_pred, labels, average: str = "macro") -> tuple[float, float, float]:
    raise NotImplementedError("TODO")


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
