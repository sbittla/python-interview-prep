"""
Exercise 09 — Lab: Greedy, Temperature, Top-k, Top-p (Nucleus) Sampling   [Tier: ★ Core]
Chapter 39 · Pattern: logits -> filter -> softmax -> inverse-CDF draw · Target time: 30 min

Problem
-------
``logits`` is a 1-D float array over the vocabulary. Implement

- ``greedy(logits)``: argmax (ties -> lowest index).
- ``apply_temperature(logits, T)``: logits / T for T > 0; ValueError for T <= 0 (callers treat
  "temperature 0" as greedy).
- ``top_k_filter(logits, k)``: keep the k largest logits, set the rest to -inf. Ties at the
  k-th value are all kept (value threshold), so more than k may survive. k >= vocabulary
  size keeps everything; k < 1 raises.
- ``top_p_filter(logits, p)``: sort probabilities in descending order (stable); keep the
  *smallest prefix whose cumulative probability is >= p* — i.e. keep token i iff the mass
  strictly before it is < p. The token that crosses p is included; at least one token is
  always kept. 0 < p <= 1.
- ``filtered_probs(logits, temperature, top_k, top_p)``: temperature, then top-k, then top-p
  (the usual order; changing it changes the result), then softmax.
- ``sample(logits, rng, ...)``: one draw by inverse CDF with ``rng.random()``.

Examples
--------
>>> lg = np.log(np.array([0.5, 0.25, 0.125, 0.125]))
>>> np.isfinite(top_p_filter(lg, 0.6)).tolist(), np.isfinite(top_p_filter(lg, 0.75)).tolist()
([True, True, False, False], [True, True, False, False])

Constraints
-----------
- V >= 1. Use ``np.random.default_rng(seed)`` for reproducible draws.

Hints
-----
- ``np.partition(z, -k)[-k]`` is the k-th largest value in O(V).
- For top-p, the mass *before* a token is ``cumsum - p_token``; keep it while that is < p.
- Sort with ``kind="stable"`` so ties are deterministic.
- Inverse CDF: ``np.searchsorted(cdf, u * cdf[-1], side="right")`` with ``u = rng.random()``.
- ``top_p_wrong_le`` is the tempting inclusive-cumsum version: write it too, and see which p it breaks.

Follow-ups
----------
- Boundary: with the inclusive cumsum, ``cum <= p`` keeps the crossing token only when the
  sum lands exactly on p, and ``cum < p`` never keeps it; with p = 0.6 on [0.5, 0.25, ...]
  both keep only 0.5 of the mass. Testing ``cum - p_token < p`` is right; tested.
- Temperature -> 0 approaches greedy; T > 1 flattens; T changes *which* tokens top-p keeps.
- Greedy and beam search are deterministic; sampling needs a seed to be reproducible, and
  batched/parallel generation needs one generator per stream.
- Min-p: keep tokens with prob >= min_p · max prob (a relative threshold).
- Edge cases: V = 1, all-equal logits, -inf logits already present, k = 1 (== greedy), p = 1.
"""
from __future__ import annotations

import numpy as np


def greedy(logits) -> int:
    raise NotImplementedError("TODO")


def apply_temperature(logits, T: float) -> np.ndarray:
    raise NotImplementedError("TODO")


def softmax(z) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    e = np.exp(z - z.max())
    return e / e.sum()


def top_k_filter(logits, k: int) -> np.ndarray:
    raise NotImplementedError("TODO")


def top_p_filter(logits, p: float) -> np.ndarray:
    raise NotImplementedError("TODO")


def top_p_loop(logits, p: float) -> np.ndarray:
    """Rung 1: the same rule, written as a loop."""
    raise NotImplementedError("TODO")


def top_p_wrong_le(logits, p: float) -> np.ndarray:
    """Wrong-but-tempting: keep tokens whose *inclusive* cumulative mass is <= p."""
    raise NotImplementedError("TODO")


def filtered_probs(logits, temperature: float = 1.0, top_k: int | None = None,
                   top_p: float | None = None) -> np.ndarray:
    raise NotImplementedError("TODO")


def sample(logits, rng: np.random.Generator, temperature: float = 1.0,
           top_k: int | None = None, top_p: float | None = None) -> int:
    raise NotImplementedError("TODO")


def entropy(probs) -> float:
    p = probs[probs > 0]
    return float(-(p * np.log(p)).sum())


def main() -> None:
    lg = np.log(np.array([0.5, 0.25, 0.125, 0.125]))
    for p in (0.4, 0.5, 0.6, 0.75, 0.9, 1.0):
        print(f"p={p:<4} keep={np.isfinite(top_p_filter(lg, p)).astype(int).tolist()}"
              f"  loop={np.isfinite(top_p_loop(lg, p)).astype(int).tolist()}"
              f"  wrong(cum<=p)={np.isfinite(top_p_wrong_le(lg, p)).astype(int).tolist()}")

    logits = np.array([2.0, 1.0, 0.5, 0.5, -1.0, -3.0])
    print("\ngreedy:", greedy(logits), " top_k(2):", np.isfinite(top_k_filter(logits, 2)).astype(int).tolist(),
          " top_k(3) with tie:", np.isfinite(top_k_filter(logits, 3)).astype(int).tolist())
    for T in (0.25, 1.0, 4.0):
        pr = filtered_probs(logits, T)
        print(f"T={T:<4} probs={pr.round(3).tolist()}  entropy={entropy(pr):.3f}")
    print("top_p=0.8 at T=1:", np.isfinite(top_p_filter(apply_temperature(logits, 1.0), 0.8)).astype(int).tolist(),
          " at T=4:", np.isfinite(top_p_filter(apply_temperature(logits, 4.0), 0.8)).astype(int).tolist())

    rng = np.random.default_rng(399)
    target = filtered_probs(logits, 0.8, top_k=4, top_p=0.9)
    draws = np.array([sample(logits, rng, 0.8, top_k=4, top_p=0.9) for _ in range(20000)])
    freq = np.bincount(draws, minlength=logits.size) / draws.size
    print("\nfiltered probs (T=0.8, k=4, p=0.9):", target.round(3).tolist())
    print("empirical freq over 20000 draws    :", freq.round(3).tolist())
    print("max |freq - prob| < 0.01:", bool(np.abs(freq - target).max() < 0.01))
    r1, r2 = np.random.default_rng(7), np.random.default_rng(7)
    print("same seed, same draws:", [sample(logits, r1) for _ in range(8)] == [sample(logits, r2) for _ in range(8)])
    try:
        apply_temperature(logits, 0)
    except ValueError as e:
        print("T=0:", e)


if __name__ == "__main__":
    main()
