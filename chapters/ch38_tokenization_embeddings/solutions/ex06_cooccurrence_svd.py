"""
Exercise 06 — Word Embeddings from Co-occurrence + SVD            [Tier: ◆ Extended]
Chapter 38 · Pattern: count-based embeddings / matrix factorisation · Target time: 35 min

Problem
-------
Learn small word vectors from ``data/corpus.txt`` without any neural network:

1. ``build_vocab(sentences, min_count)``: words with count >= ``min_count``, sorted
   alphabetically -> ids.
2. ``cooccurrence(sentences, vocab, window)``: symmetric matrix ``C[i, j]`` = sum over
   co-occurrences within ``window`` positions of ``1 / distance``.
3. ``ppmi(C)``: positive pointwise mutual information
   ``max(0, log(P(i,j) / (P(i) P(j))))`` (0 where ``C`` is 0).
4. ``svd_embeddings(M, k)``: ``U[:, :k] * sqrt(S[:k])``, with each column's sign fixed so
   its largest-magnitude entry is positive (SVD signs are otherwise arbitrary), rows
   L2-normalised.
5. ``nearest(word, k)``: the k most cosine-similar other words.

Words used in the same contexts ("the ___ sleeps in the barn") end up close together —
the distributional hypothesis. Word2vec/GloVe learn essentially the same factorisation.

Examples
--------
>>> nearest(E, vocab, "cat", 3)   # doctest: +SKIP
[('goat', 0.9...), ('rabbit', ...), ...]

Constraints
-----------
- Deterministic (no random init; SVD sign fixed).

Hints
-----
- ``P(i,j) = C / C.sum()``, ``P(i) = C.sum(1) / C.sum()``; use ``np.errstate`` around the log.
- ``np.linalg.svd(M)`` returns ``U, S, Vt`` with S sorted descending.

Approach ladder
---------------
1. Brute force — raw co-occurrence counts as vectors: dimension = |V|, dominated by "the".
2. Improved   — PPMI reweighting removes the frequency bias.
3. Optimal    — truncated SVD compresses to k dims, merging correlated contexts so that
   words that never co-occur directly but share neighbours become similar. O(|V|^3) for
   dense SVD — fine for |V| ~ 100; use randomized/sparse SVD at scale.

Follow-ups
----------
- Why do learned (neural) embeddings beat this? (Scale, subword info, contextual vectors.)
- Static vs contextual embeddings: "bank" gets one vector here, many in a transformer.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data" / "corpus.txt"


def tokenize(sentence: str) -> list[str]:
    return re.findall(r"[a-z]+", sentence.lower())


def build_vocab(sentences: list[str], min_count: int = 1) -> dict[str, int]:
    counts = Counter(w for s in sentences for w in tokenize(s))
    words = sorted(w for w, c in counts.items() if c >= min_count)
    return {w: i for i, w in enumerate(words)}


def cooccurrence(sentences: list[str], vocab: dict[str, int], window: int = 2) -> np.ndarray:
    C = np.zeros((len(vocab), len(vocab)))
    for s in sentences:
        ids = [vocab[w] for w in tokenize(s) if w in vocab]
        for i, a in enumerate(ids):
            for d in range(1, window + 1):
                if i + d < len(ids):
                    b = ids[i + d]
                    C[a, b] += 1.0 / d
                    C[b, a] += 1.0 / d
    return C


def ppmi(C: np.ndarray) -> np.ndarray:
    total = C.sum()
    if total == 0:
        return np.zeros_like(C)
    p_ij = C / total
    p_i = C.sum(axis=1, keepdims=True) / total
    p_j = C.sum(axis=0, keepdims=True) / total
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(p_ij / (p_i * p_j))
    pmi[~np.isfinite(pmi)] = 0.0
    return np.maximum(pmi, 0.0)


def svd_embeddings(M: np.ndarray, k: int) -> np.ndarray:
    U, S, _ = np.linalg.svd(M)
    E = U[:, :k] * np.sqrt(S[:k])
    for j in range(k):
        col = E[:, j]
        if col[np.argmax(np.abs(col))] < 0:
            E[:, j] = -col
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return E / norms


def nearest(E: np.ndarray, vocab: dict[str, int], word: str, k: int = 5) -> list[tuple[str, float]]:
    inv = sorted(vocab, key=vocab.get)
    sims = E @ E[vocab[word]]
    order = sorted(range(len(inv)), key=lambda i: (-sims[i], inv[i]))
    return [(inv[i], round(float(sims[i]), 3)) for i in order if inv[i] != word][:k]


def main() -> None:
    sentences = DATA.read_text(encoding="utf-8").splitlines()
    vocab = build_vocab(sentences, min_count=2)
    C = cooccurrence(sentences, vocab, window=2)
    M = ppmi(C)
    E = svd_embeddings(M, k=12)
    print(f"vocab: {len(vocab)} words  C nonzeros: {int((C > 0).sum())}  E shape: {E.shape}")
    print(f"C symmetric: {np.allclose(C, C.T)}  PPMI min: {M.min():.1f}")
    for w in ["cat", "bread", "train", "laptop", "cooks"]:
        print(f"nearest({w!r}): {nearest(E, vocab, w, 4)}")

    groups = {"animal": ["cat", "dog", "horse", "rabbit", "goat"],
              "food": ["bread", "rice", "soup", "cheese", "pasta"],
              "vehicle": ["car", "bus", "train", "truck", "bicycle"],
              "computer": ["laptop", "server", "keyboard", "printer", "router"]}
    label = {w: g for g, ws in groups.items() for w in ws}
    hits = total = 0
    raw = C / np.maximum(np.linalg.norm(C, axis=1, keepdims=True), 1e-12)
    raw_hits = 0
    for w in sorted(label):
        hits += sum(label.get(n) == label[w] for n, _ in nearest(E, vocab, w, 4))
        raw_hits += sum(label.get(n) == label[w] for n, _ in nearest(raw, vocab, w, 4))
        total += 4
    print(f"\nsame-category precision@4 over {len(label)} nouns:")
    print(f"  raw co-occurrence rows: {raw_hits / total:.3f}")
    print(f"  PPMI + SVD (k=12):      {hits / total:.3f}")


if __name__ == "__main__":
    main()
