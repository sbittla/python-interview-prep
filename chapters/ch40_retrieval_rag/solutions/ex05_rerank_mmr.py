"""
Exercise 05 — Second-Stage Reranking and MMR Diversity            [Tier: ★ Core (MMR: ◆)]
Chapter 40 · Pattern: retrieve-then-rerank; greedy selection · Target time: 35 min

Problem
-------
A cross-encoder reads (query, passage) *together*, so it is more accurate than comparing two
independently computed vectors, but it costs one model call per passage. We mock it with
``cross_score(query, text, weight)``, a deterministic scorer over ``ragkit.content_terms``.
``weight(term)`` stands in for the term importance a trained model learns; ``idf_weights(docs)``
builds one from corpus document frequencies (default: every term weighs 1.0).

- each distinct query term t earns weight(t) if it occurs in the passage, 0.5 * weight(t) if it
  only shares a 4-letter prefix with a passage term (``rotate``/``rotation``), else 0;
  ``coverage`` = earned / sum of the query terms' weights;
- ``proximity`` = (number of exactly matched distinct terms) / (length of the shortest window
  of passage terms containing all of them) when at least 2 terms match, else 0;
- ``cross_score = round(coverage + 0.05 * proximity, 4)`` (proximity mostly breaks near-ties).

1. ``min_window(tokens, needed)``: length of the shortest contiguous slice of ``tokens``
   containing every term in ``needed`` (0 if ``needed`` is empty; ``None`` if impossible).
2. ``rerank(query, ranked_ids, texts, top_n, weight=None)``: rescore only the first ``top_n`` ids, sort them by
   score desc (ties keep their first-stage order), and append the rest unchanged.
   Returns ``(new_order, scorer_calls)``.
3. ◆ ``mmr(query_vec, vecs, ids, k, lam)``: Maximal Marginal Relevance. Repeatedly pick
   argmax  lam * sim(q, d) - (1 - lam) * max_{s selected} sim(d, s)  (max term = 0 when
   nothing is selected yet); vectors are unit length so sim = dot; values rounded to 6 places,
   ties -> smaller id.

Examples
--------
>>> min_window("a x b a c".split(), {"a", "c"})
2
>>> cross_score("rotate keys", "Rotation of access keys")
0.75

Approach ladder
---------------
1. Brute force — run the expensive scorer on every document: N calls per query.
2. Optimal    — cheap first stage (BM25 / ANN) to top_n (50–200 in practice), expensive scorer
   on those only: top_n calls. min_window is a sliding window: O(L) per passage (→ §10.5).
   MMR: O(k · n) similarity look-ups with an n × n matrix precomputed in O(n² d).
   Why move up: rerank quality at a cost bounded by top_n, not N. Recall of the first stage
   caps the final quality: a document the first stage misses can never be reranked up.

Follow-ups
----------
- How do you pick top_n? Plot recall@top_n of the first stage (ex08) against reranker latency.
- lam = 1 is plain relevance order; lam = 0 ignores relevance entirely (even the first pick
  is then decided by the tie rule).
- MMR or "one chunk per document" both reduce near-duplicate context in the prompt.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Callable

import numpy as np

from ragkit import content_terms, dense_ranking, embed, load_corpus, load_queries


def min_window(tokens: list[str], needed: set[str]) -> int | None:
    if not needed:
        return 0
    have: Counter[str] = Counter()
    missing = len(needed)
    best = None
    left = 0
    for right, tok in enumerate(tokens):
        if tok in needed:
            have[tok] += 1
            if have[tok] == 1:
                missing -= 1
        while missing == 0:                      # shrink from the left while still covering
            width = right - left + 1
            best = width if best is None else min(best, width)
            out = tokens[left]
            if out in needed:
                have[out] -= 1
                if have[out] == 0:
                    missing += 1
            left += 1
    return best


def idf_weights(docs: list[tuple[str, str]]) -> Callable[[str], float]:
    """Term -> ln(1 + (N - df + 0.5) / (df + 0.5)); unseen terms get the df = 0 value."""
    n = len(docs)
    df = Counter(t for _, text in docs for t in set(content_terms(text)))
    return lambda t: math.log(1 + (n - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5))


def cross_score(query: str, text: str, weight: Callable[[str], float] | None = None) -> float:
    weight = weight or (lambda t: 1.0)
    q = sorted(set(content_terms(query)))
    toks = content_terms(text)
    if not q or not toks:
        return 0.0
    doc = set(toks)
    prefixes = {t[:4] for t in doc if len(t) >= 4}
    exact = {t for t in q if t in doc}
    soft = [t for t in q if t not in doc and len(t) >= 4 and t[:4] in prefixes]
    total = sum(weight(t) for t in q)
    coverage = (sum(weight(t) for t in exact) + 0.5 * sum(weight(t) for t in soft)) / total
    proximity = len(exact) / min_window(toks, exact) if len(exact) >= 2 else 0.0
    return round(coverage + 0.05 * proximity, 4)


def rerank(query: str, ranked_ids: list[str], texts: dict[str, str], top_n: int,
           weight: Callable[[str], float] | None = None) -> tuple[list[str], int]:
    head, tail = ranked_ids[:top_n], ranked_ids[top_n:]
    scored = [(-cross_score(query, texts[d], weight), pos, d) for pos, d in enumerate(head)]
    return [d for _, _, d in sorted(scored)] + tail, len(head)


def mmr(query_vec: np.ndarray, vecs: np.ndarray, ids: list[str], k: int,
        lam: float = 0.7) -> list[str]:
    rel = vecs @ query_vec
    sim = vecs @ vecs.T
    chosen: list[int] = []
    left = list(range(len(ids)))
    while left and len(chosen) < k:
        def value(i: int) -> float:
            red = max((sim[i, j] for j in chosen), default=0.0)
            return round(float(lam * rel[i] - (1 - lam) * red), 6)
        best = min(left, key=lambda i: (-value(i), ids[i]))
        chosen.append(best)
        left.remove(best)
    return [ids[i] for i in chosen]


def _first_hit(ranked: list[str], relevant: list[str]) -> int | None:
    return next((i for i, d in enumerate(ranked, 1) if d in relevant), None)


def main() -> None:
    print("min_window:", min_window("a x b a c".split(), {"a", "c"}),
          min_window("a b".split(), {"z"}), min_window([], set()))
    for text in ["Rotation of access keys", "Rotate access keys every 90 days",
                 "keys are rotated by the team; access is logged", "Pricing per GB"]:
        print(f"cross_score('rotate access keys', {text!r}) = {cross_score('rotate access keys', text)}")

    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    texts = dict(docs)
    w = idf_weights(docs)
    print("idf weight bucket / e409:", round(w("bucket"), 4), round(w("e409"), 4))
    print("\nfirst relevant rank: dense only -> dense top-5 reranked")
    calls = 0
    mrr = {"dense": 0.0, "rerank": 0.0}
    for q in load_queries():
        first = [d for d, _ in dense_ranking(q["query"], docs)]
        new, c = rerank(q["query"], first, texts, top_n=5, weight=w)
        calls += c
        a, b = _first_hit(first, q["relevant"]), _first_hit(new, q["relevant"])
        mrr["dense"] += 1 / a
        mrr["rerank"] += 1 / b
        if a != b:
            print(f"  {q['qid']} {a} -> {b}  {q['query']}")
    n = len(load_queries())
    print("MRR:", {k: round(v / n, 4) for k, v in mrr.items()},
          f"scorer calls: {calls} (vs {n * len(docs)} to score every doc)")

    snippets = {"s1": "Rotate access keys every 90 days.",
                "s2": "Rotate your access keys every 90 days.",
                "s3": "Deactivate the old access key after deploying the new one.",
                "s4": "Presigned URLs are signed with an access key."}
    ids = sorted(snippets)
    vecs = np.stack([embed(snippets[i]) for i in ids])
    qv = embed("rotate access keys")
    print("\nrelevance order:", [i for i, _ in dense_ranking("rotate access keys", list(snippets.items()))])
    for lam in (1.0, 0.5, 0.0):
        print(f"mmr lam={lam}:", mmr(qv, vecs, ids, 3, lam))


if __name__ == "__main__":
    main()
