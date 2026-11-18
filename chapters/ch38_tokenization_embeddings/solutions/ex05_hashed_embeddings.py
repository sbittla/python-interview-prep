"""
Exercise 05 — Hashed Bag-of-Words Embeddings                      [Tier: ★ Core]
Chapter 38 · Pattern: feature hashing / deterministic embedder · Target time: 20 min

Problem
-------
Build a tiny, fully deterministic text embedder with the *hashing trick*:

- ``features(text)``: lowercase word unigrams plus character trigrams of each word padded
  with ``#`` (``"cat" -> "#ca", "cat", "at#"``), prefixed ``w:`` and ``c:`` so they never
  collide by construction.
- ``stable_hash(s)``: ``zlib.crc32`` of the UTF-8 bytes. (Python's ``hash()`` is salted per
  process for strings, so it would give different vectors every run.)
- ``embed(text, dim)``: for each feature, bucket ``h % dim`` and sign ``+1/-1`` from bit
  31 of the hash (the *signed* hashing trick, which makes collisions cancel in
  expectation instead of always adding). Return the L2-normalised vector (all-zero text
  -> zero vector).

This is **not** a learned embedding — it captures surface overlap only. Real systems use
a trained neural encoder; we use this stand-in because it is reproducible, needs no
downloads, and has the same interface (text -> unit vector).

Examples
--------
>>> features("Cat")
['w:cat', 'c:#ca', 'c:cat', 'c:at#']
>>> float(np.linalg.norm(embed("the cat sleeps", 64)))
1.0

Constraints
-----------
- Same text -> bit-identical vector across runs and machines.

Hints
-----
- ``np.add.at`` or a plain loop over features is fine; texts are short.
- Collisions: with F features and D buckets, expected colliding pairs ≈ F^2 / (2D).

Approach ladder
---------------
1. Brute force — build an explicit vocabulary and one-hot/TF vectors: dimension grows with
   the corpus and unseen words are dropped.
2. Optimal    — hash features into a fixed D: O(F) per text, O(D) memory, no vocabulary,
   handles unseen words and typos via character n-grams. Cost: collisions, and no
   semantics beyond overlap.

Follow-ups
----------
- Why add character n-grams? (Robust to typos/morphology: "repair" vs "repairs".)
- How would you weight common words down? (IDF weights per bucket, fitted on a corpus.)
"""
from __future__ import annotations

import re
import zlib

import numpy as np


def stable_hash(s: str) -> int:
    return zlib.crc32(s.encode("utf-8"))


def features(text: str) -> list[str]:
    feats: list[str] = []
    for w in re.findall(r"\w+", text.lower()):
        feats.append("w:" + w)
        padded = f"#{w}#"
        feats.extend("c:" + padded[i:i + 3] for i in range(len(padded) - 2))
    return feats


def embed(text: str, dim: int = 256) -> np.ndarray:
    v = np.zeros(dim, dtype=np.float64)
    for f in features(text):
        h = stable_hash(f)
        sign = 1.0 if (h >> 31) & 1 == 0 else -1.0
        v[h % dim] += sign
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def embed_many(texts: list[str], dim: int = 256) -> np.ndarray:
    return np.stack([embed(t, dim) for t in texts]) if texts else np.zeros((0, dim))


def collision_rate(words: list[str], dim: int) -> float:
    """Fraction of distinct words whose bucket is shared with another word."""
    buckets: dict[int, int] = {}
    uniq = sorted(set(words))
    for w in uniq:
        b = stable_hash("w:" + w) % dim
        buckets[b] = buckets.get(b, 0) + 1
    shared = sum(1 for w in uniq if buckets[stable_hash("w:" + w) % dim] > 1)
    return shared / len(uniq) if uniq else 0.0


def main() -> None:
    print(f"features('Cat'): {features('Cat')}")
    print(f"stable_hash('w:cat') = {stable_hash('w:cat')}  (same every run)")
    v = embed("the cat sleeps", 16)
    print(f"embed dim=16: {np.round(v, 3).tolist()}")
    print(f"norm: {np.linalg.norm(v):.4f}  empty text norm: {np.linalg.norm(embed('', 16)):.1f}")

    texts = ["the engineer repairs the laptop",
             "an engineer repaired my laptops",
             "the farmer feeds the goat",
             "stock prices fell sharply today"]
    E = embed_many(texts, 256)
    sims = E @ E[0]
    print("\ncosine to text[0] (dim=256):")
    for t, s in zip(texts, sims):
        print(f"  {s:6.3f}  {t}")

    vocab = [f"word{i}" for i in range(200)]
    for dim in [64, 256, 1024, 4096]:
        print(f"collision rate, 200 words into dim={dim:4d}: {collision_rate(vocab, dim):.3f}")


if __name__ == "__main__":
    main()
