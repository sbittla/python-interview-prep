"""
Exercise 08 — Retrieval Evaluation Harness: Recall@K, MRR, Regression Gate   [Tier: ★ Core]
Chapter 40 · Pattern: offline evaluation over a labelled query set · Target time: 35 min

Problem
-------
Metric definitions are in §35.9 (ranks 1-based); here we wire them into a harness.

1. ``recall_at_k(ranked, relevant, k)`` = |top-k ∩ relevant| / |relevant|;
   ``reciprocal_rank(ranked, relevant, k=None)`` = 1 / rank of the first relevant id (0 if none,
   or if it lies beyond ``k`` when ``k`` is given). Both first drop repeated ids (``dedupe``):
   a ranking that lists the same doc twice must not get credit twice.
2. ``to_docs(chunk_ids)``: ``"d06#1" -> "d06"``, deduplicated in order, so a chunk retriever can
   be scored against document-level labels.
3. ``evaluate(retriever, queries, ks=(1, 3, 5))``: run ``retriever(query) -> ranked ids`` on
   every labelled query; return the mean ``recall@k`` for each k and mean ``mrr`` (rounded to
   4 places), ``n`` (queries scored), ``skipped`` (qids with an empty relevant set: they are
   excluded, not scored 0 or 1) and ``per_query`` rows.
4. ``regressions(baseline, candidate, tolerance=0.02)``: every metric where the candidate is
   more than ``tolerance`` below the baseline, as ``(metric, base, cand)`` sorted by metric name.

Examples
--------
>>> recall_at_k(["d3", "d1", "d1", "d2"], {"d1", "d2"}, 3)
1.0
>>> reciprocal_rank(["d3", "d1"], {"d1"})
0.5

Constraints
-----------
- Deterministic; no division by zero for empty labels or empty rankings.

Approach ladder
---------------
1. Brute force — eyeball a few queries ("looks good"): not repeatable, catches nothing.
2. Improved   — one aggregate number on a labelled set: repeatable but hides which queries
   broke and whether a change is noise.
3. Optimal    — per-query rows + several metrics + a regression gate vs a stored baseline, run
   on every change: O(Q · (retrieval cost + K)).
   Why move up: retrieval changes (chunk size, embedder, k) silently trade one query for another.

Follow-ups
----------
- Where do labels come from? Real user queries + human judgments; synthetic questions generated
  from chunks are cheap but easier than real traffic.
- 12 queries is far too few: with n queries a single query moves MRR by up to 1/n. Report a
  bootstrap confidence interval (→ §35.5) before calling a change a win.
- Recall@K of the retriever is the ceiling for answer quality: the generator cannot cite what
  was not retrieved. Evaluate retrieval and generation separately (ex09).
"""
from __future__ import annotations

from typing import Callable, Iterable

from ragkit import dense_ranking, keyword_ranking, load_chunks, load_corpus, load_queries


def dedupe(ranked: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(ranked))


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        raise ValueError("recall is undefined for an empty relevant set")
    return len(set(dedupe(ranked)[:k]) & relevant) / len(relevant)


def reciprocal_rank(ranked: list[str], relevant: set[str], k: int | None = None) -> float:
    for rank, d in enumerate(dedupe(ranked), start=1):
        if k is not None and rank > k:
            break
        if d in relevant:
            return 1.0 / rank
    return 0.0


def to_docs(chunk_ids: list[str]) -> list[str]:
    return dedupe(c.split("#", 1)[0] for c in chunk_ids)


def evaluate(retriever: Callable[[str], list[str]], queries: list[dict],
             ks: tuple[int, ...] = (1, 3, 5)) -> dict:
    rows, skipped = [], []
    for q in queries:
        relevant = set(q["relevant"])
        if not relevant:
            skipped.append(q["qid"])
            continue
        ranked = retriever(q["query"])
        row = {"qid": q["qid"], "mrr": reciprocal_rank(ranked, relevant)}
        row.update({f"recall@{k}": recall_at_k(ranked, relevant, k) for k in ks})
        rows.append(row)
    metrics = [f"recall@{k}" for k in ks] + ["mrr"]
    n = len(rows)
    out = {m: round(sum(r[m] for r in rows) / n, 4) if n else 0.0 for m in metrics}
    out.update({"n": n, "skipped": skipped, "per_query": rows})
    return out


def regressions(baseline: dict, candidate: dict,
                tolerance: float = 0.02) -> list[tuple[str, float, float]]:
    names = sorted(k for k, v in baseline.items() if isinstance(v, float) and k in candidate)
    return [(k, baseline[k], candidate[k]) for k in names if candidate[k] < baseline[k] - tolerance]


def main() -> None:
    print(recall_at_k(["d3", "d1", "d1", "d2"], {"d1", "d2"}, 3),
          reciprocal_rank(["d3", "d1"], {"d1"}), reciprocal_rank(["d3", "d1"], {"d1"}, k=1),
          to_docs(["d06#1", "d06#0", "d15#0"]))

    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    chunks = [(c["id"], c["text"]) for c in load_chunks()]
    retrievers = {
        "keyword (docs)": lambda q: keyword_ranking(q, docs),
        "dense (docs)": lambda q: [d for d, _ in dense_ranking(q, docs)],
        "dense (chunks->docs)": lambda q: to_docs(c for c, _ in dense_ranking(q, chunks)),
    }
    queries = load_queries() + [{"qid": "q13", "query": "unlabelled query", "relevant": []}]
    results = {name: evaluate(r, queries) for name, r in retrievers.items()}
    print(f"\n{'retriever':<22}{'R@1':>7}{'R@3':>7}{'R@5':>7}{'MRR':>7}   n  skipped")
    for name, res in results.items():
        print(f"{name:<22}{res['recall@1']:>7.4f}{res['recall@3']:>7.4f}{res['recall@5']:>7.4f}"
              f"{res['mrr']:>7.4f}  {res['n']:>2}  {res['skipped']}")

    base = results["dense (docs)"]
    print("\nqueries where dense (docs) has recall@1 < 1:",
          [(r["qid"], round(r["recall@1"], 4)) for r in base["per_query"] if r["recall@1"] < 1])
    for name in ("keyword (docs)", "dense (chunks->docs)"):
        print(f"regressions of {name!r} vs dense (docs):", regressions(base, results[name]))


if __name__ == "__main__":
    main()
