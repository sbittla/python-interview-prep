"""
Exercise 04 — Positional Encodings: Sinusoidal and Rotary (RoPE)    [Tier: ★ Core]
Chapter 39 · Pattern: per-frequency sin/cos tables, pairwise 2-D rotations · Target time: 30 min

Problem
-------
Attention is permutation-equivariant: without position information, shuffling the tokens
shuffles the outputs the same way. Implement

1. ``sinusoidal(T, d, base=10000)``: (T, d) table, d even, with frequency
   w_i = base^(-2i/d) for i = 0 .. d/2 - 1 and
   PE[p, 2i] = sin(p·w_i), PE[p, 2i+1] = cos(p·w_i). Added to the token embeddings.
2. ``rope(x, positions, base=10000)``: x has shape (..., T, d), d even. Rotate each pair
   (x[2i], x[2i+1]) by the angle p·w_i (the "interleaved" layout of the RoFormer paper).
   Applied to queries and keys (not values) after the projection, before the dot product.
3. ``rope_half(x, positions)``: the "half-split" layout that pairs dimension i with i + d/2
   (used by GPT-NeoX-style code). Same maths up to a fixed permutation of the dimensions.

Examples
--------
>>> sinusoidal(2, 4).round(4).tolist()
[[0.0, 1.0, 0.0, 1.0], [0.8415, 0.5403, 0.01, 1.0]]

Constraints
-----------
- d even (ValueError otherwise); positions are non-negative integers.

Approach ladder
---------------
1. Brute force — double loop over positions and frequencies calling math.sin/cos:
   O(T·d) Python steps.
2. Optimal    — outer product of positions and frequencies (``np.outer``) then vectorised
   sin/cos: O(T·d) work with no Python loop. RoPE is O(T·d) per q/k tensor; in practice the
   cos/sin tables are cached for max length.

Key properties (tested)
-----------------------
- Sinusoidal: PE[p + k] is a fixed linear function (a rotation per frequency) of PE[p], the
  same for every p.
- RoPE preserves norms (rotations), and <rope(q, m), rope(k, n)> depends only on m - n:
  attention scores become relative-position aware.
- RoPE of position 0 is the identity.

Follow-ups
----------
- Learned absolute positions (a (T_max, d) table → §38.7-style lookup) cannot extrapolate past
  T_max; RoPE has no table but quality still degrades beyond the trained length, which is why
  context-extension methods rescale its frequencies.
- Why not rotate V? Only the q·k score needs relative position; V carries content.
- Mixing layouts: weights trained with one pairing and run with the other give wrong scores.
- Edge cases: T = 1, d = 2 (a single frequency, w_0 = 1), odd d.
"""
from __future__ import annotations

import math

import numpy as np


def _freqs(d: int, base: float) -> np.ndarray:
    if d % 2:
        raise ValueError("d must be even")
    return base ** (-np.arange(0, d, 2) / d)          # w_i = base^(-2i/d), i = 0 .. d/2-1


def sinusoidal(T: int, d: int, base: float = 10000.0) -> np.ndarray:
    ang = np.outer(np.arange(T), _freqs(d, base))      # (T, d/2)
    pe = np.empty((T, d))
    pe[:, 0::2] = np.sin(ang)
    pe[:, 1::2] = np.cos(ang)
    return pe


def sinusoidal_loop(T: int, d: int, base: float = 10000.0) -> np.ndarray:
    if d % 2:
        raise ValueError("d must be even")
    pe = np.zeros((T, d))
    for p in range(T):
        for i in range(d // 2):
            w = base ** (-2 * i / d)
            pe[p, 2 * i], pe[p, 2 * i + 1] = math.sin(p * w), math.cos(p * w)
    return pe


def rope(x: np.ndarray, positions, base: float = 10000.0) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    ang = np.outer(np.asarray(positions), _freqs(x.shape[-1], base))   # (T, d/2)
    cos, sin = np.cos(ang), np.sin(ang)
    x0, x1 = x[..., 0::2], x[..., 1::2]
    out = np.empty_like(x)
    out[..., 0::2] = x0 * cos - x1 * sin
    out[..., 1::2] = x0 * sin + x1 * cos
    return out


def rope_half(x: np.ndarray, positions, base: float = 10000.0) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    d = x.shape[-1]
    ang = np.outer(np.asarray(positions), _freqs(d, base))
    cos, sin = np.cos(ang), np.sin(ang)
    x0, x1 = x[..., : d // 2], x[..., d // 2:]
    return np.concatenate([x0 * cos - x1 * sin, x0 * sin + x1 * cos], axis=-1)


def interleaved_to_half(d: int) -> np.ndarray:
    """Permutation p with x_half = x_interleaved[..., p]: evens first, then odds."""
    return np.concatenate([np.arange(0, d, 2), np.arange(1, d, 2)])


def shift_matrix(k: int, d: int, base: float = 10000.0) -> np.ndarray:
    """M with PE[p + k] = M @ PE[p] for every p: a 2x2 rotation per frequency."""
    M = np.zeros((d, d))
    for i, w in enumerate(_freqs(d, base)):
        c, s = math.cos(k * w), math.sin(k * w)
        M[2 * i:2 * i + 2, 2 * i:2 * i + 2] = [[c, s], [-s, c]]   # (sin, cos) of a sum
    return M


def main() -> None:
    print("sinusoidal(2, 4):", sinusoidal(2, 4).round(4).tolist())
    pe = sinusoidal(50, 16)
    print("loop == vectorised:", np.allclose(pe, sinusoidal_loop(50, 16)))
    M = shift_matrix(7, 16)
    print("PE[p+7] == M @ PE[p] for all p:", np.allclose(pe[7:], pe[:-7] @ M.T))

    rng = np.random.default_rng(394)
    d = 8
    q, k = rng.standard_normal(d), rng.standard_normal(d)
    pairs = [(5, 2), (13, 10), (103, 100), (2, 5)]
    scores = [float(rope(q[None], [m])[0] @ rope(k[None], [n])[0]) for m, n in pairs]
    print("q.k after RoPE for (m, n) =", pairs, "->", [round(s, 6) for s in scores])
    print("  m - n = 3 gives the same score:", np.allclose(scores[:3], scores[0]),
          "| m - n = -3 differs:", not math.isclose(scores[3], scores[0]))
    x = rng.standard_normal((6, d))
    r = rope(x, np.arange(6))
    print("norms preserved:", np.allclose(np.linalg.norm(r, axis=1), np.linalg.norm(x, axis=1)),
          "| position 0 unchanged:", np.allclose(r[0], x[0]))
    p = interleaved_to_half(d)
    print("half-split layout == interleaved up to permutation:",
          np.allclose(rope_half(x[:, p], np.arange(6)), r[:, p]))
    print("mixing layouts breaks it:", not np.allclose(rope_half(x, np.arange(6)), r))
    try:
        sinusoidal(4, 5)
    except ValueError as e:
        print("odd d:", e)


if __name__ == "__main__":
    main()
