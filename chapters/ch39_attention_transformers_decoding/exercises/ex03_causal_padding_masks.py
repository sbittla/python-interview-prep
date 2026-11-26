"""
Exercise 03 — Causal and Padding Masks                           [Tier: ★ Core]
Chapter 39 · Pattern: boolean masks built by broadcasting · Target time: 20 min

Problem
-------
All masks are boolean with True = "may attend".

- ``causal_mask(n_q, n_k=None)``: shape (n_q, n_k). The n_q queries are the *last* n_q
  positions of an n_k-long sequence (offset = n_k - n_q), so query i may see key j iff
  j <= i + offset. n_k defaults to n_q (plain lower-triangular). Raise ValueError if n_k < n_q.
- ``padding_mask(lengths, T, side="right")``: shape (B, T); True on real tokens. With
  side="left" the real tokens are the last ``lengths[b]`` positions.
- ``combine(causal, pad)``: shape (B, 1, T, T) = causal & key-is-real, ready to broadcast over
  heads.
- ``fully_masked_rows(mask)``: indices of query rows with no allowed key.
- ``additive_mask(mask)``: float version, 0 where allowed and -inf where blocked.

Examples
--------
>>> causal_mask(2, 4).astype(int).tolist()
[[1, 1, 1, 0], [1, 1, 1, 1]]
>>> padding_mask([2, 3], 3, "left").astype(int).tolist()
[[0, 1, 1], [1, 1, 1]]

Constraints
-----------
- 1 <= n_q <= n_k; 0 <= lengths[b] <= T.

Hints
-----
- Compare a column of query indices with a row of key indices: broadcasting builds the grid.
- Right padding: position < length. Left padding: position >= T - length.
- ``combine``: causal[None, None] & pad[:, None, None, :].
- ``np.argwhere(~mask.any(axis=-1))`` finds rows with no allowed key.

Follow-ups
----------
- Left padding + causal: the first pad *queries* have no allowed key at all (they are
  before every real token): fully masked rows -> NaN with a naive softmax (→ ex01 policy).
  Right padding never does this, because key 0 is real whenever length >= 1.
- Why is ``offset`` needed? With a KV cache (§39.7) or chunked prefill the new queries sit at
  positions offset .. n_k - 1, not 0 .. n_q - 1.
- Test causality, don't eyeball it: change a future token and check earlier outputs do not move.
- Padding queries still produce outputs; mask them out of the loss instead.
- Edge cases: n_q = 1 (a decode step: sees everything), length 0, length = T.
"""
from __future__ import annotations

import math

import numpy as np


def causal_mask(n_q: int, n_k: int | None = None) -> np.ndarray:
    raise NotImplementedError("TODO")


def causal_mask_loop(n_q: int, n_k: int | None = None) -> np.ndarray:
    raise NotImplementedError("TODO")


def padding_mask(lengths, T: int, side: str = "right") -> np.ndarray:
    raise NotImplementedError("TODO")


def combine(causal: np.ndarray, pad: np.ndarray) -> np.ndarray:
    raise NotImplementedError("TODO")


def fully_masked_rows(mask: np.ndarray) -> list:
    raise NotImplementedError("TODO")


def additive_mask(mask: np.ndarray) -> np.ndarray:
    raise NotImplementedError("TODO")


def naive_attention(q, k, v, mask):
    """Softmax without the fully-masked-row guard: what most first drafts write."""
    s = q @ np.swapaxes(k, -1, -2) / math.sqrt(q.shape[-1]) + additive_mask(mask)
    with np.errstate(invalid="ignore"):
        w = np.exp(s - s.max(axis=-1, keepdims=True))
        w = w / w.sum(axis=-1, keepdims=True)
    return w @ v


def main() -> None:
    print("causal_mask(4):\n", causal_mask(4).astype(int))
    print("causal_mask(2, 4) (2 new queries, 2 cached keys):", causal_mask(2, 4).astype(int).tolist())
    print("loop == broadcast:", all(np.array_equal(causal_mask(a, b), causal_mask_loop(a, b))
                                     for a in range(1, 6) for b in range(a, 8)))
    for side in ("right", "left"):
        pad = padding_mask([2, 4], 4, side)
        m = combine(causal_mask(4), pad)
        print(f"{side:>5} padding keys {pad.astype(int).tolist()}  fully masked (b, h, query): "
              f"{fully_masked_rows(m)}")

    rng = np.random.default_rng(393)
    T, d = 6, 4
    q, k, v = (rng.standard_normal((T, d)) for _ in range(3))
    left = combine(causal_mask(T), padding_mask([4], T, "left"))[0, 0]
    out = naive_attention(q, k, v, left)
    print("naive softmax, left padding: NaN rows =", np.where(np.isnan(out).any(axis=1))[0].tolist())

    cm = causal_mask(T)
    base = naive_attention(q, k, v, cm)
    k2, v2 = k.copy(), v.copy()
    k2[4:], v2[4:] = 99.0, -99.0                    # change keys/values at positions 4 and 5
    moved = ~np.isclose(naive_attention(q, k2, v2, cm), base).all(axis=1)
    print("changing positions 4-5 moves outputs at positions:", np.where(moved)[0].tolist())
    print("additive mask row 1:", additive_mask(cm)[1].tolist())
    try:
        causal_mask(3, 2)
    except ValueError as e:
        print("causal_mask(3, 2):", e)


if __name__ == "__main__":
    main()
