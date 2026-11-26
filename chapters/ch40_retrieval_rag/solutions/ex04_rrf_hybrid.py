"""
Exercise 04 — Hybrid Retrieval with Reciprocal Rank Fusion        [Tier: ★ Core]
Chapter 40 · Pattern: rank fusion (merge several ranked lists) · Target time: 25 min

Problem
-------
1. ``rrf(rankings, k=60, top_n=None)``: fuse ranked id lists with
       RRF(d) = sum over lists r containing d of 1 / (k + rank_r(d)),   rank 1-based.
   A doc absent from a list contributes 0 for it; a repeated id inside one list counts only
   at its first position. Return ``(id, score)`` sorted by score desc then id, scores rounded
   to 6 places; ``top_n`` truncates. ``k = 60`` is the constant from the original RRF paper
   (Cormack, Clarke and Büttcher, SIGIR 2009); ``k <= 0`` -> ``ValueError``.
2. ``minmax_fusion(score_lists, weights)``: min-max normalise each list's scores to [0, 1]
   (a list whose scores are all equal maps to 1.0), missing docs count 0, weighted sum.
3. ``naive_sum(score_lists)``: add raw scores (the wrong-but-tempting version).
4. ``hybrid(query, docs, k)``: RRF of ``ragkit.keyword_ranking`` and ``ragkit.dense_ranking``.

Examples
--------
>>> rrf([["a", "b", "c"], ["b", "c", "a"]], k=60)
[('b', 0.032522), ('a', 0.032266), ('c', 0.032002)]

Constraints
-----------
- Lists may have different lengths and need not share ids.

Approach ladder
---------------
1. Brute force — ``naive_sum``: add the retrievers' raw scores. O(total length). Wrong: BM25 or
   overlap counts are unbounded while cosine lies in [-1, 1], so one retriever dominates.
2. Improved   — ``minmax_fusion``: rescale each list, then weight. O(total length). Depends on
   each list's min and max (one outlier squashes the rest) and needs tuned weights.
3. Optimal    — RRF: uses ranks only, so no calibration is needed. O(total length) with a dict
   + O(u log u) to sort u distinct ids. k damps the gap between rank 1 and rank 2
   (1/61 vs 1/62), so consistent placement counts for more than with a small k. It is not a
   guarantee: in [a, r, b] and [b, r, a], r is 2nd in both lists but 3rd after fusion.
   Why move up: scores from different retrievers are not comparable; ranks are.

Follow-ups
----------
- Weighted RRF: multiply each list's term by a weight.
- Small k (e.g. 1) makes the top rank dominate; large k flattens towards "count of lists".
- Fusion needs each retriever's candidate list, so its cost is the sum of the retrievers'.
"""
from __future__ import annotations

from collections import defaultdict

from ragkit import dense_ranking, keyword_ranking, load_corpus, load_queries


def _sorted(scores: dict[str, float], places: int = 6) -> list[tuple[str, float]]:
    return sorted(((d, round(s, places)) for d, s in scores.items()), key=lambda p: (-p[1], p[0]))


def rrf(rankings: list[list[str]], k: int = 60, top_n: int | None = None) -> list[tuple[str, float]]:
    if k <= 0:
        raise ValueError("k must be positive")
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        seen: set[str] = set()
        for rank, doc in enumerate(ranking, start=1):
            if doc not in seen:                       # a duplicate keeps its first rank
                seen.add(doc)
                scores[doc] += 1.0 / (k + rank)
    out = _sorted(scores)
    return out if top_n is None else out[:top_n]


def minmax_fusion(score_lists: list[list[tuple[str, float]]],
                  weights: list[float] | None = None) -> list[tuple[str, float]]:
    weights = weights or [1.0] * len(score_lists)
    fused: dict[str, float] = defaultdict(float)
    for w, pairs in zip(weights, score_lists):
        if not pairs:
            continue
        lo, hi = min(s for _, s in pairs), max(s for _, s in pairs)
        for d, s in pairs:
            fused[d] += w * ((s - lo) / (hi - lo) if hi > lo else 1.0)
    return _sorted(fused, 4)


def naive_sum(score_lists: list[list[tuple[str, float]]]) -> list[tuple[str, float]]:
    fused: dict[str, float] = defaultdict(float)
    for pairs in score_lists:
        for d, s in pairs:
            fused[d] += s
    return _sorted(fused, 4)


def hybrid(query: str, docs: list[tuple[str, str]], k: int = 60) -> list[str]:
    lists = [keyword_ranking(query, docs), [d for d, _ in dense_ranking(query, docs)]]
    return [d for d, _ in rrf(lists, k)]


def _first_hit(ranked: list[str], relevant: list[str]) -> int | None:
    return next((i for i, d in enumerate(ranked, 1) if d in relevant), None)


def main() -> None:
    print("rrf:", rrf([["a", "b", "c"], ["b", "c", "a"]]))
    print("rrf, missing + duplicate ids:", rrf([["a", "a", "b"], ["c"]]))
    print("k=1 vs k=60 on [[a, b, c, d], [c, b, d, a]]:")
    lists = [["a", "b", "c", "d"], ["c", "b", "d", "a"]]
    print("  k=1 :", rrf(lists, k=1))
    print("  k=60:", rrf(lists, k=60))

    overlap = [("d1", 4.0), ("d2", 3.0), ("d3", 1.0)]          # unbounded counts
    cosine = [("d3", 0.41), ("d2", 0.39), ("d1", 0.05)]        # [-1, 1]
    print("\nnaive sum :", naive_sum([overlap, cosine]))
    print("min-max   :", minmax_fusion([overlap, cosine]))
    print("rrf       :", rrf([[d for d, _ in overlap], [d for d, _ in cosine]]))

    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    print("\nfirst relevant rank per query (keyword / dense / hybrid RRF):")
    totals = {"keyword": 0.0, "dense": 0.0, "hybrid": 0.0}
    worse_than_both = False
    for q in load_queries():
        runs = {"keyword": keyword_ranking(q["query"], docs),
                "dense": [d for d, _ in dense_ranking(q["query"], docs)],
                "hybrid": hybrid(q["query"], docs)}
        ranks = {name: _first_hit(r, q["relevant"]) or 99 for name, r in runs.items()}
        worse_than_both |= ranks["hybrid"] > max(ranks["keyword"], ranks["dense"])
        for name, r in ranks.items():
            totals[name] += 1 / r if r != 99 else 0.0
        print(f"  {q['qid']} {ranks['keyword']!s:>4} {ranks['dense']!s:>4} {ranks['hybrid']!s:>4}"
              f"  {q['query']}")
    n = len(load_queries())
    print("MRR:", {name: round(t / n, 4) for name, t in totals.items()})
    print("hybrid below both retrievers on any query:", worse_than_both)


if __name__ == "__main__":
    main()
