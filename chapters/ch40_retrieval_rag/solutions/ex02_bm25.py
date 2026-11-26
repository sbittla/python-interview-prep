"""
Exercise 02 — BM25 from Scratch with an Inverted Index             [Tier: ★ Core]
Chapter 40 · Pattern: inverted index + term-at-a-time scoring · Target time: 35 min

Problem
-------
Build ``BM25(docs, k1=1.2, b=0.75)`` over ``docs = [(doc_id, text), ...]``. Terms are
``ragkit.content_terms`` (lowercase alphanumerics, stop words dropped).

    score(q, d) = sum over DISTINCT query terms t of
                  idf(t) * tf(t, d) * (k1 + 1) / (tf(t, d) + k1 * (1 - b + b * |d| / avgdl))

    idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))       # the "+1 inside the log" variant

N = number of docs, df = docs containing t, |d| = terms in d, avgdl = mean |d|.

- ``idf(term)``; ``score(query, doc_id)``.
- ``search(query, k)``: the top-k ``(doc_id, score)`` with score > 0, score rounded to 4 places,
  sorted by score descending then doc id. It must touch only the postings of the query terms.
- ``tfidf_search(docs, query, k)`` (rung 2) and ``bm25_scan(docs, query, k)`` (scores every doc
  without an index; used to cross-check ``search``).

Examples
--------
>>> idx = BM25([("a", "red apple"), ("b", "green apple"), ("c", "red red car")])
>>> idx.search("red", k=2)
[('c', 0.5982), ('a', 0.4992)]

Constraints
-----------
- Empty corpus, empty query or unknown terms -> [].
- Counting each distinct query term once is Robertson's query-tf factor with k3 = 0.

Approach ladder
---------------
1. Brute force — count shared terms (``ragkit.keyword_ranking``): O(N · L). A word in every doc
   ("bucket") counts as much as a rare code ("e409").
2. Improved   — TF-IDF: weight by rarity. Still linear in tf (repeating a word 10 times is 10×
   the evidence) and long documents win by having more words.
3. Optimal    — BM25: tf saturates (k1) and is normalised by length (b). With an inverted index
   (term -> [(doc, tf)]) a query costs O(sum of the query terms' posting lengths) + O(m log k)
   for the m scored docs, instead of O(N · |q|). Build: O(total tokens).
   Why move up: rare-term weighting, saturation and length normalisation are exactly the three
   things a keyword ranker gets wrong.

Follow-ups
----------
- k1 controls saturation: k1 = 0 -> tf ignored (binary match); large k1 -> nearly linear tf.
- b controls length normalisation: b = 0 -> none; b = 1 -> full. 1.2 / 0.75 are common defaults.
- The classic Robertson–Spärck Jones idf ln((N - df + 0.5) / (df + 0.5)) is NEGATIVE when
  df > N/2; the +1 variant used here (as in Lucene) stays positive.
- Updates: append postings for new docs; recompute avgdl and N lazily. Deletes: tombstones.
- Phrase queries need positions in the postings; BM25F weights fields (title vs body).
"""
from __future__ import annotations

import heapq
import math
from collections import Counter, defaultdict

from ragkit import content_terms, load_corpus


def _top(scored: dict[str, float], k: int) -> list[tuple[str, float]]:
    pairs = [(d, round(s, 4)) for d, s in scored.items() if s > 0]
    return heapq.nsmallest(k, pairs, key=lambda p: (-p[1], p[0]))


class BM25:
    def __init__(self, docs: list[tuple[str, str]], k1: float = 1.2, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.ids = [doc_id for doc_id, _ in docs]
        self.lengths: list[int] = []
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for i, (_, text) in enumerate(docs):
            terms = content_terms(text)
            self.lengths.append(len(terms))
            for term, tf in Counter(terms).items():
                self.postings[term].append((i, tf))
        self.n = len(docs)
        self.avgdl = sum(self.lengths) / self.n if self.n else 0.0

    def idf(self, term: str) -> float:
        df = len(self.postings.get(term, ()))
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def _term_score(self, idf: float, tf: int, length: int) -> float:
        norm = 1 - self.b + self.b * length / self.avgdl if self.avgdl else 1.0
        return idf * tf * (self.k1 + 1) / (tf + self.k1 * norm)

    def score(self, query: str, doc_id: str) -> float:
        i = self.ids.index(doc_id)
        total = 0.0
        for term in set(content_terms(query)):
            tf = dict(self.postings.get(term, ())).get(i, 0)
            if tf:
                total += self._term_score(self.idf(term), tf, self.lengths[i])
        return total

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        acc: dict[str, float] = defaultdict(float)
        for term in set(content_terms(query)):
            plist = self.postings.get(term)
            if not plist:
                continue
            idf = self.idf(term)
            for i, tf in plist:                        # only docs that contain the term
                acc[self.ids[i]] += self._term_score(idf, tf, self.lengths[i])
        return _top(acc, k)


def bm25_scan(docs: list[tuple[str, str]], query: str, k: int = 10,
              k1: float = 1.2, b: float = 0.75) -> list[tuple[str, float]]:
    """No index: count every doc's terms for every query. O(N · L)."""
    toks = {d: Counter(content_terms(t)) for d, t in docs}
    n = len(docs)
    avgdl = sum(sum(c.values()) for c in toks.values()) / n if n else 0.0
    scores: dict[str, float] = {}
    for d, counts in toks.items():
        dl, s = sum(counts.values()), 0.0
        for term in set(content_terms(query)):
            df = sum(1 for c in toks.values() if term in c)
            tf = counts.get(term, 0)
            if tf:
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                s += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))
        scores[d] = s
    return _top(scores, k)


def tfidf_search(docs: list[tuple[str, str]], query: str, k: int = 10) -> list[tuple[str, float]]:
    """Rung 2: raw tf times the same idf; no saturation, no length normalisation."""
    toks = {d: Counter(content_terms(t)) for d, t in docs}
    n = len(docs)
    scores = {}
    for d, counts in toks.items():
        s = 0.0
        for term in set(content_terms(query)):
            df = sum(1 for c in toks.values() if term in c)
            if counts.get(term):
                s += counts[term] * math.log(1 + (n - df + 0.5) / (df + 0.5))
        scores[d] = s
    return _top(scores, k)


def main() -> None:
    idx = BM25([("a", "red apple"), ("b", "green apple"), ("c", "red red car")])
    print("toy search('red'):", idx.search("red", k=2))
    print("idf red/apple/zebra:", [round(idx.idf(t), 4) for t in ("red", "apple", "zebra")])

    filler = " ".join(f"note{i}" for i in range(30))
    toy = [("short", "bucket error e409"), ("long", "bucket error e409 " + filler),
           ("spam", "e409 " * 8 + "bucket")]
    print("\nquery 'e409 bucket' on short / long / keyword-stuffed docs")
    for k1, b in [(1.2, 0.75), (1.2, 0.0), (0.0, 0.75), (100.0, 0.75)]:
        res = BM25(toy, k1=k1, b=b).search("e409 bucket", k=3)
        print(f"  k1={k1:<5} b={b:<4} {res}")
    print("  tf-idf        ", tfidf_search(toy, "e409 bucket", k=3))

    n, df = 10, 8
    print("\nN=10, df=8: RSJ idf =", round(math.log((n - df + 0.5) / (df + 0.5)), 4),
          " +1 variant =", round(math.log(1 + (n - df + 0.5) / (df + 0.5)), 4))

    docs = [(d["id"], d["title"] + " " + d["text"]) for d in load_corpus()]
    index = BM25(docs)
    for q in ["why does deleting my bucket fail with E409", "how often should I rotate credentials",
              "too many requests error 429"]:
        hits = index.search(q, k=3)
        same = hits == bm25_scan(docs, q, k=3)
        print(f"\n{q!r}\n  index: {hits}  (matches full scan: {same})")
    print("unknown term:", index.search("zebra", 3), " empty query:", index.search("", 3))


if __name__ == "__main__":
    main()
