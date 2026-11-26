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

Approach ladder
---------------
1. Brute force (top-p) — Python loop over the sorted list accumulating probability:
   O(V log V) sort + O(V) Python steps.
2. Optimal    — ``argsort`` + ``cumsum`` + one comparison: O(V log V), vectorised.
   For very large V, ``np.argpartition`` for top-k is O(V) and you only sort the k survivors
   (O(V + k log k)); top-p after top-k then sorts only k items.

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
    return int(np.argmax(logits))


def apply_temperature(logits, T: float) -> np.ndarray:
    if T <= 0:
        raise ValueError("temperature must be > 0 (use greedy for T = 0)")
    return np.asarray(logits, dtype=float) / T


def softmax(z) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    e = np.exp(z - z.max())
    return e / e.sum()


def top_k_filter(logits, k: int) -> np.ndarray:
    z = np.asarray(logits, dtype=float)
    if k < 1:
        raise ValueError("k must be >= 1")
    if k >= z.size:
        return z.copy()
    kth = np.partition(z, -k)[-k]                     # k-th largest value, O(V)
    return np.where(z >= kth, z, -np.inf)


def top_p_filter(logits, p: float) -> np.ndarray:
    if not 0 < p <= 1:
        raise ValueError("p must be in (0, 1]")
    z = np.asarray(logits, dtype=float)
    probs = softmax(z)
    order = np.argsort(-probs, kind="stable")
    before = np.cumsum(probs[order]) - probs[order]   # mass strictly before each token
    keep_sorted = before < p                          # first token always kept (before = 0)
    keep = np.zeros(z.size, bool)
    keep[order[keep_sorted]] = True
    return np.where(keep, z, -np.inf)


def top_p_loop(logits, p: float) -> np.ndarray:
    """Rung 1: the same rule, written as a loop."""
    z = np.asarray(logits, dtype=float)
    probs = softmax(z)
    out = np.full(z.size, -np.inf)
    mass = 0.0
    for i in sorted(range(z.size), key=lambda j: -probs[j]):   # sorted() is stable
        if mass >= p:
            break
        out[i] = z[i]
        mass += probs[i]
    return out


def top_p_wrong_le(logits, p: float) -> np.ndarray:
    """Wrong-but-tempting: keep tokens whose *inclusive* cumulative mass is <= p."""
    z = np.asarray(logits, dtype=float)
    probs = softmax(z)
    order = np.argsort(-probs, kind="stable")
    keep = np.zeros(z.size, bool)
    keep[order[np.cumsum(probs[order]) <= p]] = True
    return np.where(keep, z, -np.inf)


def filtered_probs(logits, temperature: float = 1.0, top_k: int | None = None,
                   top_p: float | None = None) -> np.ndarray:
    z = apply_temperature(logits, temperature)
    if top_k is not None:
        z = top_k_filter(z, top_k)
    if top_p is not None:
        z = top_p_filter(z, top_p)
    return softmax(z)


def sample(logits, rng: np.random.Generator, temperature: float = 1.0,
           top_k: int | None = None, top_p: float | None = None) -> int:
    probs = filtered_probs(logits, temperature, top_k, top_p)
    cdf = np.cumsum(probs)
    idx = int(np.searchsorted(cdf, rng.random() * cdf[-1], side="right"))
    return min(idx, probs.size - 1)


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
