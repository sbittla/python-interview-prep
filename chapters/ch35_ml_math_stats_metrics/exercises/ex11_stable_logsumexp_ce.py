"""
Exercise 11 — Lab: Log-Sum-Exp, Log-Softmax, Cross-Entropy       [Tier: ★ Core]
Chapter 35 · Pattern: shift by the max; never take log(exp(.)) · Target time: 25 min

Problem
-------
Logits Z have shape (n, C); labels y are ints in [0, C).

1. ``logsumexp(z, axis=-1)``: log(sum(exp(z))) without overflow:
   m + log(sum(exp(z - m))), m = max(z). If every entry is -inf the answer is -inf
   (not NaN); +inf anywhere gives +inf.
2. ``log_softmax(z)`` = z - logsumexp(z) and ``softmax`` = exp(log_softmax).
3. ``cross_entropy(Z, y)`` = mean_i [logsumexp(Z_i) - Z_i[y_i]] (natural log), and its
   gradient w.r.t. Z: (softmax(Z) - onehot(y)) / n.
4. ``binary_log_loss_from_logits(z, y)`` = mean(softplus(z) - y z), with
   softplus(z) = log(1 + e^z) = max(z, 0) + log1p(e^-|z|).
5. ``binary_log_loss_from_probs(p, y, eps=1e-15)`` = -mean(y log p + (1 - y) log(1 - p))
   after clipping p to [eps, 1 - eps]. Clipping caps the damage; working from logits avoids it.

Examples
--------
>>> float(logsumexp(np.array([1000.0, 1000.0])))      # 1000 + log 2
1000.6931471805599
>>> round(float(cross_entropy(np.array([[2.0, 1.0, 0.1]]), np.array([0]))), 6)
0.417030

Constraints
-----------
- float64; n, C >= 1.

Hints
-----
- logsumexp: subtract the max along the axis with keepdims, add it back after the log.
- A row of all -inf has max -inf; shift by 0 there so -inf - (-inf) never happens.
- cross_entropy: logsumexp of each row minus the logit of the true class; no softmax needed.
- Gradient: softmax(Z), subtract 1 at the true class, divide by n.

Wrong-but-tempting
------------------
- ``np.log(softmax(z))``: the stable softmax still underflows to 0 for logits 800 apart.
- Subtracting one global max for a whole batch: rows far below it underflow to 0/0.
- Clipping probabilities and believing the loss is now exact.

Follow-ups
----------
- Why is the CE gradient softmax - onehot? d/dz_j [lse(z) - z_y] = softmax_j - [j == y].
- Label smoothing: target (1 - a) onehot + a / C; the same log-softmax handles it.
- Frameworks fuse this: PyTorch ``cross_entropy`` takes logits, not probabilities (→ §37).
- Temperature: softmax(z / T); T -> 0 tends to argmax.
- Edge cases: all -inf row, +inf logit, one class (C = 1, loss 0), p exactly 0 or 1.
"""
from __future__ import annotations

import numpy as np


def logsumexp_naive(z, axis=-1):
    raise NotImplementedError("TODO")


def logsumexp(z, axis=-1):
    raise NotImplementedError("TODO")


def log_softmax(z, axis=-1):
    raise NotImplementedError("TODO")


def softmax(z, axis=-1):
    raise NotImplementedError("TODO")


def cross_entropy(Z, y) -> float:
    raise NotImplementedError("TODO")


def cross_entropy_grad(Z, y) -> np.ndarray:
    raise NotImplementedError("TODO")


def cross_entropy_naive(Z, y) -> float:
    raise NotImplementedError("TODO")


def binary_log_loss_from_logits(z, y) -> float:
    raise NotImplementedError("TODO")


def binary_log_loss_from_probs(p, y, eps: float = 1e-15) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    big = np.array([1000.0, 1000.0])
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        print("naive  lse([1000, 1000]):", float(logsumexp_naive(big)))
        print("naive  CE  logits [800, 0], y=1:", cross_entropy_naive(np.array([[800.0, 0.0]]), np.array([1])))
    print("stable lse([1000, 1000]):", float(logsumexp(big)))
    print("stable CE  logits [800, 0], y=1:", cross_entropy(np.array([[800.0, 0.0]]), np.array([1])))
    print("lse of all -inf row:", float(logsumexp(np.array([-np.inf, -np.inf]))))
    print("log_softmax([0, -800]):", log_softmax(np.array([0.0, -800.0])).tolist())

    Z = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, -1.0]])
    y = np.array([0, 1])
    print("CE:", round(cross_entropy(Z, y), 6), " softmax row 0:", softmax(Z)[0].round(4).tolist())

    eps, num = 1e-6, np.zeros_like(Z)                   # central differences (ex02)
    for idx in np.ndindex(Z.shape):
        e = np.zeros_like(Z)
        e[idx] = eps
        num[idx] = (cross_entropy(Z + e, y) - cross_entropy(Z - e, y)) / (2 * eps)
    print("grad = (softmax - onehot)/n, max abs diff vs finite differences:",
          f"{np.abs(num - cross_entropy_grad(Z, y)).max():.0e}")

    z = np.array([40.0, -3.0, 0.0])
    yb = np.array([0.0, 0.0, 1.0])
    p = 1 / (1 + np.exp(-z))                            # sigmoid(40) rounds to exactly 1.0
    print("p == 1.0 exactly:", bool(p[0] == 1.0))
    print("log loss from logits :", round(binary_log_loss_from_logits(z, yb), 4))
    print("log loss from probs  :", round(binary_log_loss_from_probs(p, yb), 4), "(clipped at 1e-15)")


if __name__ == "__main__":
    main()
