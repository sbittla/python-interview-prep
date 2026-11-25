"""
Exercise 10 — Ranking Metrics: P@K, R@K, MRR, MAP, NDCG         [Tier: ★ Core]
Chapter 35 · Pattern: position-weighted counting · Target time: 25 min

Problem
-------
A search system returns a ranked list of document ids per query. Judgements are a set of
relevant ids (binary) or a dict id -> graded gain (NDCG). Ranks are 1-based.

1. ``precision_at_k(ranked, relevant, k)`` = |top-k ∩ relevant| / k (divide by k even if
   fewer than k results came back: missing slots count as misses).
2. ``recall_at_k`` = |top-k ∩ relevant| / |relevant|; ValueError if no relevant items.
3. ``reciprocal_rank`` = 1 / rank of the first relevant hit, 0 if none; ``mrr`` averages.
4. ``ap_at_k`` = (1 / min(|relevant|, k)) * sum_{i <= k, item i relevant} P@i.
   ``map_at_k`` averages over queries. (Other libraries divide by |relevant| or by the hits
   found; state the definition you use.)
5. ``ndcg_at_k(ranked, gains, k)`` = DCG@k / IDCG@k with
   DCG@k = sum_{i=1..k} (2^g_i - 1) / log2(i + 1) (``exp_gain=False`` uses g_i), IDCG@k =
   DCG of the best possible ordering of all judged items. 0.0 when IDCG == 0.

Examples
--------
>>> precision_at_k(["a", "b", "c", "d"], {"a", "c", "x"}, 3), recall_at_k(["a", "b", "c", "d"], {"a", "c", "x"}, 3)
(0.6666666666666666, 0.6666666666666666)
>>> reciprocal_rank(["b", "a"], {"a"})
0.5

Constraints
-----------
- Ranked lists have no duplicates; k >= 1.

Hints
-----
- Turn the relevant ids into a set once; membership is O(1).
- AP@K: walk the top k keeping a running hit count; at each hit add hits / rank.
- NDCG: discount position i (1-based) by log2(i + 1); IDCG sorts all judged gains descending.
- Brute rungs: recompute P@i for AP; try all permutations for IDCG.

Wrong-but-tempting
------------------
- IDCG from re-sorting only the *retrieved* items: a system that misses relevant docs
  then scores NDCG 1.0.
- 0-based log2(i) discount: divides by log2(1) = 0 at the top rank.
- Dividing P@K by the number of returned results instead of K.

Follow-ups
----------
- Which metric for which product: MRR when only the first hit matters (QA, navigation);
  Recall@K for a retrieval stage feeding a reranker (→ §40); NDCG for graded relevance.
- Precision@K ignores order inside the top k; AP and NDCG reward early hits.
- Exponential vs linear gain changes how much a "highly relevant" beats "relevant".
- Edge cases: no relevant items, fewer than k results, k larger than the list, all gains 0.
"""
from __future__ import annotations

from itertools import permutations
from math import log2


def precision_at_k(ranked, relevant, k: int) -> float:
    raise NotImplementedError("TODO")


def recall_at_k(ranked, relevant, k: int) -> float:
    raise NotImplementedError("TODO")


def reciprocal_rank(ranked, relevant) -> float:
    raise NotImplementedError("TODO")


def mrr(runs) -> float:
    raise NotImplementedError("TODO")


def ap_at_k_brute(ranked, relevant, k: int) -> float:
    raise NotImplementedError("TODO")


def ap_at_k(ranked, relevant, k: int) -> float:
    raise NotImplementedError("TODO")


def map_at_k(runs, k: int) -> float:
    raise NotImplementedError("TODO")


def _dcg(gs, exp_gain: bool) -> float:
    raise NotImplementedError("TODO")


def ndcg_at_k(ranked, gains: dict, k: int, exp_gain: bool = True) -> float:
    raise NotImplementedError("TODO")


def idcg_brute(gains: dict, k: int, exp_gain: bool = True) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    ranked = ["d3", "d1", "d7", "d2", "d9"]
    relevant = {"d1", "d2", "d4"}
    for k in (1, 3, 5):
        print(f"k={k}: P@k={precision_at_k(ranked, relevant, k):.4f}  R@k={recall_at_k(ranked, relevant, k):.4f}"
              f"  AP@k={ap_at_k(ranked, relevant, k):.4f}  brute={ap_at_k_brute(ranked, relevant, k):.4f}")
    runs = [(ranked, relevant), (["a", "b"], {"a"}), (["x", "y", "z"], {"q"})]
    print("RR per query:", [round(reciprocal_rank(r, rel), 4) for r, rel in runs], " MRR:", round(mrr(runs), 4))
    print("MAP@5:", round(map_at_k(runs, 5), 4))

    gains = {"d1": 3, "d2": 2, "d3": 0, "d4": 1, "d7": 1}
    for exp in (True, False):
        print(f"NDCG@3 ({'2^g-1' if exp else 'linear'} gain): {ndcg_at_k(ranked, gains, 3, exp):.4f}"
              f"  ideal ordering: {ndcg_at_k(['d1', 'd2', 'd4'], gains, 3, exp):.4f}")
    ideal = _dcg(sorted(gains.values(), reverse=True)[:3], True)
    print("sorted IDCG == brute-force max over orderings:", abs(ideal - idcg_brute(gains, 3)) < 1e-12)
    print("fewer than k results: P@5 of ['d1'] =", precision_at_k(["d1"], relevant, 5))
    print("all gains zero -> NDCG", ndcg_at_k(ranked, {"d3": 0}, 3))


if __name__ == "__main__":
    main()
