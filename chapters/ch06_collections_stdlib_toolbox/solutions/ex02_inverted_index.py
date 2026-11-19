"""
Exercise 02 — Inverted Index with defaultdict                 [Tier: ★ Core]
Chapter 06 · Pattern: defaultdict grouping + set algebra · Target time: 15 min

Problem
-------
You are given documents as a dict {doc_id: text}. Build an inverted index that
maps each lowercase word to the set of document ids containing it. Words are
split on whitespace and stripped of the punctuation characters .,!?;:'" at both
ends. Then answer:

- `search_all(index, query)` — ids containing EVERY query word (AND).
- `search_any(index, query)` — ids containing AT LEAST ONE query word (OR).

Both return a sorted list. An empty query returns []. Queries must not add
keys to the index.

Examples
--------
>>> idx = build_index({1: "Red fox.", 2: "red hen", 3: "Blue fox!"})
>>> search_all(idx, "red fox"), search_any(idx, "hen blue")
([1], [2, 3])

Constraints
-----------
- Up to 10**4 documents, 10**3 words each; many queries.

Approach ladder
---------------
1. Brute force — for each query, re-tokenise every document and check the
   words: O(total words) per query.
2. Improved   — build the index once with `setdefault(word, set()).add(id)`:
   O(total words) once, then each query touches only the posting sets.
3. Optimal    — same index via `defaultdict(set)` (clearer, no throwaway set
   per call), and for AND start from the SMALLEST posting set so the
   intersection costs about O(min posting size * number of query words).

Hints
-----
- Read with `index.get(word, empty)`, never `index[word]`: on a defaultdict a
  read of a missing key inserts it (→ §7.14).
- `set.intersection(*others)` accepts many sets at once.

Follow-ups
----------
- Rank results by how many query words matched (a Counter over ids).
- Phrase queries: store positions, `defaultdict(lambda: defaultdict(list))`.
- Stop words and stemming.
"""
from __future__ import annotations

from collections import defaultdict

PUNCT = ".,!?;:'\""


def tokenize(text: str) -> list[str]:
    words = (w.strip(PUNCT).lower() for w in text.split())
    return [w for w in words if w]


def brute_force_all(docs: dict[int, str], query: str) -> list[int]:
    q = set(tokenize(query))
    if not q:
        return []
    return sorted(d for d, text in docs.items() if q <= set(tokenize(text)))


def build_index(docs: dict[int, str]) -> dict[str, set[int]]:
    index: defaultdict[str, set[int]] = defaultdict(set)
    for doc_id, text in docs.items():
        for word in tokenize(text):
            index[word].add(doc_id)
    return dict(index)          # plain dict: later reads cannot create phantom keys


def search_all(index: dict[str, set[int]], query: str) -> list[int]:
    words = set(tokenize(query))
    if not words:
        return []
    postings = sorted((index.get(w, set()) for w in words), key=len)
    return sorted(postings[0].intersection(*postings[1:]))


def search_any(index: dict[str, set[int]], query: str) -> list[int]:
    return sorted(set().union(*(index.get(w, set()) for w in tokenize(query))))


def main() -> None:
    docs = {
        1: "The quick brown fox.",
        2: "A quick red hen!",
        3: "Brown hens, brown foxes; the end.",
        4: "Red fox meets red hen.",
    }
    idx = build_index(docs)
    print("index['brown'] =", sorted(idx["brown"]))
    print("vocabulary size =", len(idx))
    for q in ["quick", "red hen", "brown fox", "fox hen", "zebra", ""]:
        print(f"{q!r:12} all={search_all(idx, q)} any={search_any(idx, q)} "
              f"brute_ok={search_all(idx, q) == brute_force_all(docs, q)}")
    print("vocabulary size after queries =", len(idx))


if __name__ == "__main__":
    main()
