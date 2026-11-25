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

Approach ladder
---------------
1. Brute force — ``log(exp(z).sum())``, ``-log(softmax(z)[y])``: exp(710) overflows to
   inf and the loss becomes inf or NaN; a tiny probability underflows to 0 and log gives -inf.
2. Improved   — subtract the row max before exp (stable softmax, the Chapter 33 exercise);
   fixes overflow, but log(softmax) still underflows for very negative logits.
3. Optimal    — compute in log space: log_softmax = z - logsumexp(z); CE picks one entry.
   O(nC) time, O(nC) space, finite for any finite logits.

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
    return np.log(np.sum(np.exp(z), axis=axis))


def logsumexp(z, axis=-1):
    z = np.asarray(z, dtype=float)
    m = np.max(z, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)          # all -inf (or +inf) row: shift by 0, not NaN
    with np.errstate(divide="ignore"):            # log(0) = -inf is the right answer there
        out = m + np.log(np.sum(np.exp(z - m), axis=axis, keepdims=True))
    return np.squeeze(out, axis=axis)


def log_softmax(z, axis=-1):
    z = np.asarray(z, dtype=float)
    return z - np.expand_dims(logsumexp(z, axis), axis)


def softmax(z, axis=-1):
    return np.exp(log_softmax(z, axis))


def cross_entropy(Z, y) -> float:
    Z = np.asarray(Z, dtype=float)
    return float(np.mean(logsumexp(Z) - Z[np.arange(len(y)), y]))


def cross_entropy_grad(Z, y) -> np.ndarray:
    G = softmax(Z)
    G[np.arange(len(y)), y] -= 1.0
    return G / len(y)


def cross_entropy_naive(Z, y) -> float:
    P = np.exp(Z) / np.exp(Z).sum(axis=1, keepdims=True)
    return float(-np.mean(np.log(P[np.arange(len(y)), y])))


def binary_log_loss_from_logits(z, y) -> float:
    z, y = np.asarray(z, float), np.asarray(y, float)
    softplus = np.maximum(z, 0) + np.log1p(np.exp(-np.abs(z)))
    return float(np.mean(softplus - y * z))


def binary_log_loss_from_probs(p, y, eps: float = 1e-15) -> float:
    p = np.clip(np.asarray(p, float), eps, 1 - eps)
    y = np.asarray(y, float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


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
