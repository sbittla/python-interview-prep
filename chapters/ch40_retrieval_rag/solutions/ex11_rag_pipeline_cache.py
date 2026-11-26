"""
Exercise 11 — End-to-End RAG Pipeline with Filters and an Answer Cache   [Tier: ★ Core]
Chapter 40 · Pattern: pipeline + LRU cache with a versioned key · Target time: 40 min

Problem
-------
``RAGPipeline(chunks, llm, k=3, cache_size=128, min_score=0.1)`` answers questions over
``ragkit.load_chunks()``-style chunks with a ``MockLLM``:

  normalise query -> cache lookup -> metadata PRE-filter -> dense top-k (cosine >= min_score)
  -> ``format_prompt`` -> ``llm.complete`` -> citations -> cache store

1. ``normalize_query(q)``: lowercase, punctuation -> space, collapse whitespace.
   Empty after normalising -> ``ValueError`` in ``answer``.
2. ``answer(query, where=None)`` returns ``{"answer", "citations": {n: chunk_id}, "retrieved":
   [chunk ids], "cached": bool}``. ``citations`` holds only the numbers the answer actually cites.
   ``where`` is ``{field: allowed value or collection of values}`` (equality / membership).
3. The cache key is (normalised query, the filter in canonical sorted form, index version).
   The filter is part of the key: otherwise a public user could be served an answer that was
   built from internal documents for someone else. LRU eviction beyond ``cache_size``
   (``OrderedDict``, → §29.2).
4. If no chunk passes the filter and threshold, return ``ragkit.ABSTAIN`` **without** calling
   the LLM.
5. ``add_chunks(new)`` re-indexes and bumps ``version``, so stale cached answers can no longer hit.
   ``stats`` counts ``hit``, ``miss``, ``evicted``; ``llm.calls`` counts model calls.

Examples
--------
>>> normalize_query("  How often, rotate KEYS?? ")
'how often rotate keys'

Approach ladder
---------------
1. Brute force — call retrieval + LLM for every request: correct, pays full latency and cost
   for every repeated question.
2. Improved   — cache on the raw query string: misses trivial variants ("Keys?" vs "keys"),
   ignores the filter (data leak across permission scopes) and serves stale answers after
   re-indexing.
3. Optimal    — normalised, scope-aware, versioned key + LRU bound: O(1) lookup;
   O(N d) retrieval only on a miss. Why move up: same cost savings, no leaks, no staleness.

Follow-ups
----------
- Semantic cache: reuse an answer when a new query's embedding is within a threshold of a
  cached one; risk: near-miss queries with different answers ("enable" vs "disable"), → §42.8.
- TTL in addition to versioning for sources that change outside your index.
- Cache retrieval results and LLM answers separately; they invalidate for different reasons.
- Log (query, retrieved ids, answer, citations) for every request: that log becomes your eval set.
"""
from __future__ import annotations

import re
from collections import Counter, OrderedDict

import numpy as np

from ragkit import ABSTAIN, MockLLM, embed, format_prompt, load_chunks

CITE_RE = re.compile(r"\[(\d+)\]")


def normalize_query(q: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", q.lower()).split())


def _canonical(where: dict | None) -> tuple:
    items = []
    for field, rule in sorted((where or {}).items()):
        if isinstance(rule, (set, frozenset, list, tuple)):
            rule = ("in", tuple(sorted(rule)))
        items.append((field, rule))
    return tuple(items)


def _allowed(chunk: dict, where: tuple) -> bool:
    for field, rule in where:
        value = chunk.get(field)
        if isinstance(rule, tuple) and rule[:1] == ("in",):
            if value not in rule[1]:
                return False
        elif value != rule:
            return False
    return True


class RAGPipeline:
    def __init__(self, chunks: list[dict], llm: MockLLM, k: int = 3, cache_size: int = 128,
                 min_score: float = 0.1) -> None:
        self.llm, self.k, self.cache_size, self.min_score = llm, k, cache_size, min_score
        self.cache: OrderedDict[tuple, dict] = OrderedDict()
        self.stats: Counter[str] = Counter()
        self.version = -1
        self.chunks: list[dict] = []
        self.add_chunks(chunks)

    def add_chunks(self, new: list[dict]) -> None:
        self.chunks.extend(new)
        self.matrix = np.stack([embed(c["text"]) for c in self.chunks])
        self.version += 1

    def retrieve(self, query: str, where: tuple) -> list[dict]:
        scores = np.round(self.matrix @ embed(query), 6)
        ok = [i for i, c in enumerate(self.chunks) if _allowed(c, where) and scores[i] >= self.min_score]
        ok.sort(key=lambda i: (-scores[i], self.chunks[i]["id"]))
        return [self.chunks[i] for i in ok[:self.k]]

    def answer(self, query: str, where: dict | None = None) -> dict:
        norm = normalize_query(query)
        if not norm:
            raise ValueError("empty query")
        key = (norm, _canonical(where), self.version)
        if key in self.cache:
            self.cache.move_to_end(key)
            self.stats["hit"] += 1
            return {**self.cache[key], "cached": True}
        self.stats["miss"] += 1
        hits = self.retrieve(query, key[1])
        if not hits:
            result = {"answer": ABSTAIN, "citations": {}, "retrieved": []}
        else:
            text = self.llm.complete(format_prompt(query, [(c["id"], c["text"]) for c in hits]))
            cited = sorted({int(n) for n in CITE_RE.findall(text)})
            result = {"answer": text, "retrieved": [c["id"] for c in hits],
                      "citations": {n: hits[n - 1]["id"] for n in cited if 1 <= n <= len(hits)}}
        self.cache[key] = result
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
            self.stats["evicted"] += 1
        return {**result, "cached": False}


def main() -> None:
    print(repr(normalize_query("  How often, rotate KEYS?? ")))
    llm = MockLLM()
    rag = RAGPipeline(load_chunks(), llm, k=3)
    public = {"access": "public"}
    staff = {"access": {"public", "internal"}}

    for q in ["How often should I rotate access keys?", "how often should i ROTATE access keys"]:
        r = rag.answer(q, public)
        print(f"\n{q!r} cached={r['cached']} llm_calls={llm.calls}\n  {r['answer']}\n  citations={r['citations']}")

    q = "Who handles a P1 ticket at night?"
    for name, scope in [("public", public), ("staff", staff)]:
        r = rag.answer(q, scope)
        print(f"\n[{name}] {q} cached={r['cached']} retrieved={r['retrieved']}\n  {r['answer']}")
    r = rag.answer("Rotate access keys", {"area": "billing"})
    print(f"\nno chunk passes the filter: {r['answer']!r} llm_calls={llm.calls}")

    rag.add_chunks([{"id": "d17#0", "doc": "d17", "area": "security", "access": "public",
                     "year": 2026, "text": "Access keys / Policy update: From 2026, rotate access "
                                           "keys every 30 days instead of every 90 days."}])
    r = rag.answer("How often should I rotate access keys?", public)
    print(f"\nafter add_chunks (version {rag.version}): cached={r['cached']}\n  {r['answer']}")

    small = RAGPipeline(load_chunks(), MockLLM(), cache_size=2)
    for q in ["rotate keys", "encryption at rest", "rotate keys", "multipart upload", "encryption at rest"]:
        small.answer(q)
    print("\ncache_size=2 stats:", dict(sorted(small.stats.items())), "llm calls:", small.llm.calls)
    try:
        rag.answer(" ?! ")
    except ValueError as e:
        print("ValueError:", e)


if __name__ == "__main__":
    main()
