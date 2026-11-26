"""
Exercise 05 — LayerNorm vs RMSNorm                               [Tier: ★ Core]
Chapter 39 · Pattern: normalise over the feature axis, per token · Target time: 15 min

Problem
-------
x has shape (..., d). Normalise every token vector over its last axis:

- ``layer_norm(x, gamma, beta, eps=1e-5)`` = (x - mean) / sqrt(var + eps) * gamma + beta,
  with the *population* variance (divide by d, not d - 1).
- ``rms_norm(x, gamma, eps=1e-6)`` = x / sqrt(mean(x²) + eps) * gamma. No mean subtraction,
  no beta.
- ``norm_params(d, kind)``: 2·d for LayerNorm, d for RMSNorm.

Examples
--------
>>> layer_norm(np.array([1.0, 2.0, 3.0]), np.ones(3), np.zeros(3)).round(4).tolist()
[-1.2247, 0.0, 1.2247]
>>> rms_norm(np.array([3.0, 4.0]), np.ones(2), eps=0.0).round(4).tolist()
[0.8485, 1.1314]

Constraints
-----------
- d >= 1, float64. eps > 0 keeps a constant (all-equal) vector finite for LayerNorm and an
  all-zero vector finite for RMSNorm.

Approach ladder
---------------
1. Brute force — a loop over tokens computing mean/var with Python sums: O(N·d) with
   interpreter overhead.
2. Optimal    — ``mean(axis=-1, keepdims=True)`` and broadcasting: O(N·d) time, O(N·d) memory.
   RMSNorm skips one reduction (the mean), which is why it is a little cheaper.

Follow-ups
----------
- LayerNorm vs BatchNorm: LN reduces over features of *one* token, so it behaves identically
  at batch size 1 and in training/eval; BatchNorm reduces over the batch (→ §37.3).
- Invariances: LN output is unchanged by x -> a·x + c (a > 0, up to eps); RMSNorm only by
  x -> a·x. Tested below.
- Pre-LN (norm inside the residual branch) vs Post-LN (norm after the residual add): §39.5.
- Wrong-but-tempting: ``np.var(x, ddof=1)``; normalising over axis 0 (the batch);
  eps outside the sqrt; forgetting keepdims so the broadcast silently goes wrong.
- Edge cases: constant vector (LN gives beta), zero vector (RMSNorm gives 0), d = 1.
"""
from __future__ import annotations

import numpy as np


def layer_norm(x, gamma, beta, eps: float = 1e-5):
    x = np.asarray(x, dtype=float)
    mu = x.mean(axis=-1, keepdims=True)
    var = ((x - mu) ** 2).mean(axis=-1, keepdims=True)    # population variance
    return (x - mu) / np.sqrt(var + eps) * gamma + beta


def rms_norm(x, gamma, eps: float = 1e-6):
    x = np.asarray(x, dtype=float)
    return x / np.sqrt((x * x).mean(axis=-1, keepdims=True) + eps) * gamma


def layer_norm_loop(x, gamma, beta, eps: float = 1e-5):
    x = np.asarray(x, dtype=float)
    flat = x.reshape(-1, x.shape[-1])
    out = np.empty_like(flat)
    for r, row in enumerate(flat):
        mu = sum(row) / len(row)
        var = sum((v - mu) ** 2 for v in row) / len(row)
        out[r] = [(v - mu) / (var + eps) ** 0.5 * g + b for v, g, b in zip(row, gamma, beta)]
    return out.reshape(x.shape)


def norm_params(d: int, kind: str) -> int:
    return {"layernorm": 2 * d, "rmsnorm": d}[kind]


def main() -> None:
    print("LN [1, 2, 3]:", layer_norm(np.array([1.0, 2.0, 3.0]), np.ones(3), np.zeros(3)).round(4).tolist())
    print("RMS [3, 4]  :", rms_norm(np.array([3.0, 4.0]), np.ones(2), eps=0.0).round(4).tolist())

    rng = np.random.default_rng(395)
    x = rng.standard_normal((2, 3, 6)) * 3 + 1
    g, b = rng.standard_normal(6), rng.standard_normal(6)
    y = layer_norm(x, np.ones(6), np.zeros(6))
    print("LN per-token mean ~0:", np.allclose(y.mean(-1), 0), " std ~1:", np.allclose(y.std(-1), 1, atol=1e-5))
    print("loop == vectorised:", np.allclose(layer_norm(x, g, b), layer_norm_loop(x, g, b)))

    shifted, scaled = x + 5.0, 2.5 * x
    print("LN  invariant to shift:", np.allclose(layer_norm(shifted, g, b), layer_norm(x, g, b), atol=1e-6),
          " to scale:", np.allclose(layer_norm(scaled, g, b), layer_norm(x, g, b), atol=1e-6))
    print("RMS invariant to shift:", np.allclose(rms_norm(shifted, g), rms_norm(x, g), atol=1e-6),
          " to scale:", np.allclose(rms_norm(scaled, g), rms_norm(x, g), atol=1e-6))
    print("constant vector, LN -> beta:", np.allclose(layer_norm(np.full(6, 7.0), g, b), b),
          "| zero vector, RMS -> 0:", np.allclose(rms_norm(np.zeros(6), g), 0))
    ddof1 = (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, ddof=1, keepdims=True) + 1e-5)
    print("ddof=1 variance gives a different answer:", not np.allclose(ddof1, y))
    print("params d=768: LN", norm_params(768, "layernorm"), " RMS", norm_params(768, "rmsnorm"))

    try:
        import torch
        import torch.nn.functional as F
    except ImportError:
        print("torch not installed: skipping cross-check")
        return
    xt, gt, bt = (torch.from_numpy(a) for a in (x, g, b))
    print("matches torch layer_norm:", np.allclose(F.layer_norm(xt, (6,), gt, bt, eps=1e-5).numpy(), layer_norm(x, g, b)))
    print("matches torch rms_norm  :", np.allclose(F.rms_norm(xt, (6,), gt, eps=1e-6).numpy(), rms_norm(x, g)))


if __name__ == "__main__":
    main()
