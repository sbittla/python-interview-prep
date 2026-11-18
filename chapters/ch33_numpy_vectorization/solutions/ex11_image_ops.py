"""
Exercise 11 — Image-like Array Operations                        [Tier: ◆ Extended]
Chapter 33 · Pattern: axis manipulation / dtype safety / reshape pooling · Target time: 20 min

Problem
-------
Treat a ``uint8`` array of shape (H, W, 3) as an RGB image. Implement:

1. ``to_grayscale(img)`` → float (H, W): 0.299 R + 0.587 G + 0.114 B.
2. ``adjust_brightness(img, delta)`` → uint8 with values clipped to [0, 255] (no wrap-around).
3. ``avg_pool_2x2(gray)`` → (H//2, W//2) mean of each non-overlapping 2x2 block (crop odd edges).
4. ``normalize_channels(img)`` → float32 (H, W, 3), each channel standardised to mean 0, std 1.
5. ``to_chw(img)`` → (3, H, W) layout as deep-learning frameworks expect (``transpose``).

Examples
--------
>>> adjust_brightness(np.array([[[250, 10, 0]]], dtype=np.uint8), 10).tolist()
[[[255, 20, 10]]]

Constraints
-----------
- H, W up to 4096.

Hints
-----
- ``img @ np.array([0.299, 0.587, 0.114])`` contracts the last axis.
- Convert to a wider int (``int16``) before adding, then ``np.clip`` and cast back.
- ``g.reshape(H//2, 2, W//2, 2).mean(axis=(1, 3))``.
- ``img.mean(axis=(0, 1))`` gives one mean per channel.

Approach ladder
---------------
1. Brute force — loop over pixels / blocks: O(HW) Python steps (~10^7 for a 4K image).
2. Improved   — loops over channels or rows only, vectorised inside.
3. Optimal    — whole-array ops: matmul over the channel axis, reshape-based pooling (a view, no
   copy until the mean), axis tuples for per-channel stats.

Follow-ups
----------
- Why is ``img + 10`` on uint8 dangerous? (modular wrap-around: 250 + 10 = 4)
- How would you do 3x3 convolution? (``sliding_window_view`` + ``einsum``)
"""
from __future__ import annotations

import numpy as np

_LUMA = np.array([0.299, 0.587, 0.114])


def to_grayscale(img: np.ndarray) -> np.ndarray:
    return img.astype(float) @ _LUMA


def adjust_brightness(img: np.ndarray, delta: int) -> np.ndarray:
    return np.clip(img.astype(np.int16) + delta, 0, 255).astype(np.uint8)


def avg_pool_loop(gray):
    H, W = gray.shape[0] // 2, gray.shape[1] // 2
    out = np.empty((H, W))
    for i in range(H):
        for j in range(W):
            out[i, j] = gray[2 * i:2 * i + 2, 2 * j:2 * j + 2].mean()
    return out


def avg_pool_2x2(gray: np.ndarray) -> np.ndarray:
    H, W = gray.shape[0] // 2, gray.shape[1] // 2
    g = gray[: 2 * H, : 2 * W]
    return g.reshape(H, 2, W, 2).mean(axis=(1, 3))


def normalize_channels(img: np.ndarray) -> np.ndarray:
    x = img.astype(np.float32)
    mu = x.mean(axis=(0, 1), keepdims=True)
    sd = x.std(axis=(0, 1), keepdims=True)
    return (x - mu) / np.where(sd == 0, 1.0, sd).astype(np.float32)


def to_chw(img: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(img.transpose(2, 0, 1))


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    rng = np.random.default_rng(11)
    img = rng.integers(0, 256, size=(5, 6, 3), dtype=np.uint8)
    print("img shape/dtype:", img.shape, img.dtype)
    print("red channel:\n", img[:, :, 0], sep="")

    print("\n== uint8 wrap-around ==")
    px = np.array([[[250, 10, 0]]], dtype=np.uint8)
    print("px + 10 (wrong):", (px + np.uint8(10)).tolist())
    print("adjust (right) :", adjust_brightness(px, 10).tolist())
    print("adjust -20     :", adjust_brightness(px, -20).tolist())

    gray = to_grayscale(img)
    print("\ngray (5x6):\n", gray, sep="")
    pooled = avg_pool_2x2(gray)
    print("pooled (2x3), odd row cropped:\n", pooled, sep="")
    print("pool loop agrees:", np.allclose(pooled, avg_pool_loop(gray)))

    norm = normalize_channels(img)
    print("\nnormalised dtype:", norm.dtype)
    print("per-channel mean:", norm.mean(axis=(0, 1)).round(4) + 0.0)
    print("per-channel std :", norm.std(axis=(0, 1)).round(4))

    chw = to_chw(img)
    print("\nCHW shape:", chw.shape, " same pixel:", chw[2, 1, 3] == img[1, 3, 2])
    print("flip horizontal first row R:", img[0, ::-1, 0])
    print("crop [1:3, 2:5] shape      :", img[1:3, 2:5].shape)
    batch = np.stack([img, img[::-1]])
    print("stacked batch NHWC shape   :", batch.shape)


if __name__ == "__main__":
    main()
