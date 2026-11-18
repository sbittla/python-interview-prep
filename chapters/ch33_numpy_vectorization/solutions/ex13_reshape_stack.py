"""
Exercise 13 — Reshape, Transpose, Stack: Batching and Patches    [Tier: ◆ Extended]
Chapter 33 · Pattern: reshape/transpose choreography · Target time: 20 min

Problem
-------
1. ``to_batches(X, batch_size, pad_value=0)``: (n, d) → (num_batches, batch_size, d), padding the
   last batch with ``pad_value``; also return a boolean mask (num_batches, batch_size) that is True
   for real rows.
2. ``patchify(img, p)``: (H, W, C) with H, W divisible by p → (num_patches, p*p*C) in row-major
   patch order (the first step of a Vision Transformer).
3. ``unpatchify(patches, H, W, C, p)``: exact inverse of ``patchify``.

Examples
--------
>>> to_batches(np.arange(10).reshape(5, 2), 2)[0].shape
(3, 2, 2)
>>> patchify(np.arange(16).reshape(4, 4, 1), 2)[0].tolist()
[0, 1, 4, 5]

Constraints
-----------
- Raise ``ValueError`` if H or W is not divisible by p.

Hints
-----
- ``np.concatenate`` along axis 0 with a padding block, then ``reshape``.
- Patchify: reshape (H/p, p, W/p, p, C) → transpose to (H/p, W/p, p, p, C) → reshape.
- ``reshape`` never moves data; ``transpose`` only changes strides; the final ``reshape`` of a
  non-contiguous array makes a copy.

Approach ladder
---------------
1. Brute force — loop over patch grid, slice and ``ravel`` each patch: O(HWC) with Python overhead
   per patch.
2. Improved   — list comprehension + ``np.stack``.
3. Optimal    — one reshape → transpose → reshape. Same O(HWC) copy, zero Python loops.

Follow-ups
----------
- ``stack`` vs ``concatenate`` vs ``vstack``/``hstack``: which adds an axis?
- Why does ``x.T.reshape(-1)`` differ from ``x.reshape(-1)``? (memory order)
"""
from __future__ import annotations

import numpy as np


def to_batches(X: np.ndarray, batch_size: int, pad_value=0) -> tuple[np.ndarray, np.ndarray]:
    X = np.asarray(X)
    n = X.shape[0]
    num = -(-n // batch_size)                          # ceil division
    pad = num * batch_size - n
    padded = np.concatenate([X, np.full((pad,) + X.shape[1:], pad_value, dtype=X.dtype)])
    mask = (np.arange(num * batch_size) < n).reshape(num, batch_size)
    return padded.reshape((num, batch_size) + X.shape[1:]), mask


def patchify_loop(img, p):
    H, W, _ = img.shape
    return np.stack([img[i:i + p, j:j + p].ravel()
                     for i in range(0, H, p) for j in range(0, W, p)])


def patchify(img: np.ndarray, p: int) -> np.ndarray:
    H, W, C = img.shape
    if H % p or W % p:
        raise ValueError("H and W must be divisible by p")
    x = img.reshape(H // p, p, W // p, p, C)
    x = x.transpose(0, 2, 1, 3, 4)                      # (H/p, W/p, p, p, C)
    return x.reshape(-1, p * p * C)


def unpatchify(patches: np.ndarray, H: int, W: int, C: int, p: int) -> np.ndarray:
    x = patches.reshape(H // p, W // p, p, p, C)
    return x.transpose(0, 2, 1, 3, 4).reshape(H, W, C)


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    a = np.arange(6)
    print("reshape(2, 3):\n", a.reshape(2, 3), sep="")
    print("reshape(3, -1):\n", a.reshape(3, -1), sep="")
    m = a.reshape(2, 3)
    print("m.T:\n", m.T, sep="")
    print("m.reshape(-1)  :", m.reshape(-1))
    print("m.T.reshape(-1):", m.T.reshape(-1))
    print("m.T is a view  :", np.shares_memory(m, m.T), " contiguous:", m.T.flags["C_CONTIGUOUS"])

    print("\n== stack vs concatenate ==")
    u, v = np.array([1, 2]), np.array([3, 4])
    print("stack axis0 :", np.stack([u, v]).shape, " stack axis1:", np.stack([u, v], axis=1).shape)
    print("concatenate :", np.concatenate([u, v]).shape)
    print("vstack/hstack:", np.vstack([u, v]).shape, np.hstack([u, v]).shape)
    print("u[:, None] / u[None, :]:", u[:, None].shape, u[None, :].shape)
    print("squeeze/expand_dims    :", np.zeros((1, 3, 1)).squeeze().shape, np.expand_dims(u, 0).shape)

    print("\n== to_batches ==")
    X = np.arange(10).reshape(5, 2)
    B, mask = to_batches(X, 2, pad_value=-1)
    print("batches shape:", B.shape)
    print(B)
    print("mask:\n", mask, sep="")
    print("real rows recovered:", np.array_equal(B[mask], X))

    print("\n== patchify ==")
    img = np.arange(4 * 4 * 1).reshape(4, 4, 1)
    P = patchify(img, 2)
    print(P)
    rng = np.random.default_rng(13)
    big = rng.integers(0, 255, size=(32, 48, 3))
    Pb = patchify(big, 8)
    print("(32,48,3) p=8 ->", Pb.shape)
    print("loop agrees     :", np.array_equal(Pb, patchify_loop(big, 8)))
    print("round trip exact:", np.array_equal(unpatchify(Pb, 32, 48, 3, 8), big))
    try:
        patchify(big, 5)
    except ValueError as e:
        print("p=5 -> ValueError:", e)


if __name__ == "__main__":
    main()
