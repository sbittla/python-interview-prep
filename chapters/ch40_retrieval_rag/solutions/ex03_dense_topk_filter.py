"""
Exercise 03 — Dense Top-K with Normalisation and Metadata Filters  [Tier: ★ Core]
Chapter 40 · Pattern: matrix-vector scores + partial selection · Target time: 30 min

Problem
-------
1. ``normalize_rows(M)``: divide each row by its L2 norm; an all-zero row stays zero (no NaN).
2. ``top_k(scores, ids, k)``: the k best ``(id, score)`` pairs, exact even with ties. Scores
   are rounded to 6 places *before* ranking so that last-bit floating-point noise cannot reorder
   ties; ties go to the smaller id; reported scores are rounded to 4 places. Use
   ``np.argpartition``/``np.partition`` (O(N)) instead of sorting all N scores.
3. ``DenseIndex(chunks)`` embeds every chunk text with ``ragkit.embed`` once.
   ``search(query, k, where=None, mode="pre")`` returns cosine top-k. ``where`` maps a metadata
   field to an allowed value, a collection of allowed values, or a predicate. ``mode="pre"``
   filters *before* ranking; ``mode="post"`` ranks everything, keeps the top k, then filters
   (and may return fewer than k).

Examples
--------
>>> top_k(np.array([0.2, 0.9, 0.9, 0.1]), ["a", "b", "c", "d"], 2)
[('b', 0.9), ('c', 0.9)]

Constraints
-----------
- N up to ~10^6 rows of dimension d in production; here N = 32.
- k > N returns all N; k <= 0 returns [].

Approach ladder
---------------
1. Brute force — Python loop: cosine per row (dot / (|q| |d|)), then sort all N.
   O(N d) Python-level work + O(N log N).
2. Improved   — normalise rows once at index time; a query is one matrix-vector product
   ``M @ q`` (dot = cosine for unit vectors). O(N d) in BLAS + O(N log N) sort.
3. Optimal    — partial selection: ``np.partition`` finds the k-th largest score in O(N), then
   only the m >= k candidates scoring at least that much are sorted: O(N d + N + m log m).
   Why move up: at N = 10^6 the sort dominates once the scores are computed; and exact ties at
   the k-th place must be broken by id, not by whatever argpartition happened to return.

Follow-ups
----------
- Why normalise? With raw count vectors the dot product grows with document length, so long
  documents win (see ``main``). Cosine = dot of unit vectors.
- Pre- vs post-filtering: post-filtering can return 0 results when the filter is selective; pre-
  filtering always fills k but may surface weak matches -> add a minimum-score threshold.
  Permission filters (``access``) must be pre-filters so restricted text never reaches ranking.
- Past ~10^5–10^6 vectors use an ANN index (ex06); filtered ANN search is harder because the
  filter can remove most of the probed candidates.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from ragkit import embed, load_chunks, tokenize


def normalize_rows(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return np.divide(m, norms, out=np.zeros_like(m, dtype=float), where=norms > 0)


def top_k(scores: np.ndarray, ids: list[str], k: int) -> list[tuple[str, float]]:
    n = len(ids)
    if k <= 0 or n == 0:
        return []
    r = np.round(np.asarray(scores, dtype=float), 6)
    if k < n:
        kth = np.partition(r, n - k)[n - k]           # k-th largest value, O(N)
        cand = np.flatnonzero(r >= kth)                # every tie at the boundary survives
    else:
        cand = np.arange(n)
    best = sorted(cand.tolist(), key=lambda i: (-r[i], ids[i]))[:k]
    return [(ids[i], round(float(r[i]), 4)) for i in best]


def brute_force_search(query: str, texts: list[str], ids: list[str], k: int) -> list[tuple[str, float]]:
    q = embed(query)
    scored = []
    for i, t in zip(ids, texts):
        v = embed(t)
        nq, nv = np.linalg.norm(q), np.linalg.norm(v)
        scored.append((i, round(float(q @ v / (nq * nv)) if nq and nv else 0.0, 6)))
    return [(i, round(s, 4)) for i, s in sorted(scored, key=lambda p: (-p[1], p[0]))[:k]]


def _allowed(value, rule) -> bool:
    if callable(rule):
        return bool(rule(value))
    if isinstance(rule, (set, frozenset, list, tuple)):
        return value in rule
    return value == rule


def matches(meta: dict, where: dict | None) -> bool:
    return all(f in meta and _allowed(meta[f], rule) for f, rule in (where or {}).items())


class DenseIndex:
    def __init__(self, chunks: list[dict], dim: int = 256) -> None:
        self.chunks = chunks
        self.ids = [c["id"] for c in chunks]
        self.matrix = normalize_rows(np.stack([embed(c["text"], dim) for c in chunks]))
        self.dim = dim

    def search(self, query: str, k: int, where: dict | None = None,
               mode: str = "pre") -> list[tuple[str, float]]:
        scores = self.matrix @ embed(query, self.dim)
        if mode == "pre":
            keep = [i for i, c in enumerate(self.chunks) if matches(c, where)]
            return top_k(scores[keep], [self.ids[i] for i in keep], k)
        if mode == "post":
            by_id = {c["id"]: c for c in self.chunks}
            return [(i, s) for i, s in top_k(scores, self.ids, k) if matches(by_id[i], where)]
        raise ValueError(f"mode must be 'pre' or 'post', not {mode!r}")


def main() -> None:
    print("top_k with a tie at the boundary:",
          top_k(np.array([0.2, 0.9, 0.9, 0.1]), ["a", "b", "c", "d"], 2),
          top_k(np.array([0.5, 0.7, 0.5, 0.5]), ["z", "y", "x", "w"], 2))
    print("zero row stays zero:", normalize_rows(np.array([[3.0, 4.0], [0.0, 0.0]])).tolist())

    texts = {"short": "rotate keys every 90 days",
             "long": "access keys, storage keys, object keys and bucket keys are listed in the console "
                     "with their names, creation dates, owners and tags"}
    vocab = sorted({w for t in texts.values() for w in tokenize(t)})
    raw = np.array([[Counter(tokenize(t))[w] for w in vocab] for t in texts.values()], float)
    q = np.array([Counter(tokenize("rotate keys"))[w] for w in vocab], float)
    print("raw dot   :", dict(zip(texts, (raw @ q).tolist())))
    print("cosine    :", dict(zip(texts, np.round(normalize_rows(raw) @ (q / np.linalg.norm(q)), 4).tolist())))

    chunks = load_chunks()
    index = DenseIndex(chunks)
    query = "how often should I rotate credentials"
    fast = index.search(query, 3)
    slow = brute_force_search(query, [c["text"] for c in chunks], index.ids, 3)
    print(f"\n{query!r}\n  top-3: {fast}  same as brute force: {fast == slow}")
    for mode in ("post", "pre"):
        print(f"  where year == 2025, {mode}-filter:", index.search(query, 3, {"year": 2025}, mode))
    print("  where access in {internal}, area startswith 'sup':",
          index.search("who answers urgent tickets", 2,
                       {"access": {"internal"}, "area": lambda a: a.startswith("sup")}))
    print("  filter matching nothing:", index.search(query, 3, {"area": "billing"}))


if __name__ == "__main__":
    main()
