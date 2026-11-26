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

Hints
-----
- min_window: two pointers; grow ``right``, and while every needed term is covered record the
  width and advance ``left`` (→ §10.5).
- rerank: sort the head by ``(-score, original_position)``; leave the tail alone.
- MMR: precompute ``sim = vecs @ vecs.T``; each step pick the best remaining by
  ``(-value, id)``.

Wrong-but-tempting
------------------
- Rescoring every document with the expensive scorer.
- Giving the proximity bonus when only one term matched (every single-term match "is adjacent").
- MMR with ``max`` over *all* documents instead of the selected ones.

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
    raise NotImplementedError("TODO")


def idf_weights(docs: list[tuple[str, str]]) -> Callable[[str], float]:
    """Term -> ln(1 + (N - df + 0.5) / (df + 0.5)); unseen terms get the df = 0 value."""
    raise NotImplementedError("TODO")


def cross_score(query: str, text: str, weight: Callable[[str], float] | None = None) -> float:
    raise NotImplementedError("TODO")


def rerank(query: str, ranked_ids: list[str], texts: dict[str, str], top_n: int,
           weight: Callable[[str], float] | None = None) -> tuple[list[str], int]:
    raise NotImplementedError("TODO")


def mmr(query_vec: np.ndarray, vecs: np.ndarray, ids: list[str], k: int,
        lam: float = 0.7) -> list[str]:
    raise NotImplementedError("TODO")


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
