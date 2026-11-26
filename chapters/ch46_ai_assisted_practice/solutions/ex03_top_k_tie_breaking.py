"""
Exercise 03 — Fix a Generated Top-k Words (Ties, Tokens, Empty Input) [Tier: ◆ Extended]
Chapter 46 · Pattern: seeded random text vs oracle → fix → complexity · Target time: 25 min

Problem
-------
Spec: top_k_words(text, k) -> the k most frequent words as (word, count)
pairs, most frequent first, ties broken ALPHABETICALLY. Words are maximal runs
of non-whitespace, compared lowercase. k <= 0 gives []; k larger than the
number of distinct words gives them all. Empty or blank text gives [].

The assistant produced generated_top_k_words (below, given). It reads well and
works on a tidy sentence. It breaks the spec in three ways; find all three.

1. oracle(text, k) -> the spec, written the obvious way (count with
   list.count, sort by (-count, word)). Quadratic is fine for an oracle.
2. random_text(rng) -> 0..12 words from a SMALL vocabulary (so ties are
   common) joined by random separators drawn from " ", "  ", "\\n", "\\t",
   with an optional leading/trailing space and random capitalisation.
3. find_counterexamples(candidate, trials=400, seed=0) -> a dict mapping a
   short label to the shortest failing (text, k) for that kind of failure:
   "empty-token" when the candidate returns "" as a word, "tie-order" when it
   returns the right counts in the wrong order, "other" for anything else.
4. top_k_words(text, k) -> the fix. COMPLEXITY -> its time and space for
   L characters, d distinct words.

Examples
--------
>>> generated_top_k_words("b a b a c", 2)          # tie: spec says a before b
[('b', 2), ('a', 2)]
>>> top_k_words("b a b a c", 2)
[('a', 2), ('b', 2)]
>>> top_k_words("", 3), generated_top_k_words("", 3)
([], [('', 1)])

Constraints
-----------
- Deterministic: the same text and k always give the same list.

Approach ladder
---------------
1. Brute force — read most_common's docs: equal counts keep first-seen order,
   not alphabetical. You only catch this if you know it.
2. Improved   — hand cases: "", "a  b" (double space), "b a b a".
3. Optimal    — random texts with ties and messy whitespace, classified by
   failure kind, so one run reports every distinct bug. Fix: split() with no
   argument (any whitespace run, no empty tokens), Counter, then
   heapq.nsmallest(k, ..., key=(-count, word)): O(L + d log k) time, O(d)
   space for the counts (O(L) for the token list).

Follow-ups
----------
- k close to d: sorted(...)[:k] is O(d log d) and simpler; say which you pick.
- Punctuation ("cat," vs "cat") is a spec question: ask, don't guess.
- Streaming input too large for memory: count in one pass; top-k needs all
  counts, or an approximate sketch (Count-Min) if exactness can be traded.
"""
from __future__ import annotations

import heapq
import random
from collections import Counter

Case = tuple[str, int]
VOCAB = ("a", "b", "c", "the", "cat")


# --- given: the generated code (do not edit) -----------------------------------
def generated_top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    """AI-generated: the k most common words, most frequent first."""
    counts = Counter(text.lower().split(" "))
    return counts.most_common(k)


# --- your bug-finding tools --------------------------------------------------------
def oracle(text: str, k: int) -> list[tuple[str, int]]:
    words = text.lower().split()
    if k <= 0:
        return []
    ranked = sorted(set(words), key=lambda w: (-words.count(w), w))
    return [(w, words.count(w)) for w in ranked[:k]]


def random_text(rng: random.Random) -> str:
    words = [rng.choice(VOCAB) for _ in range(rng.randint(0, 12))]
    words = [w.upper() if rng.random() < 0.2 else w for w in words]
    text = ""
    for i, w in enumerate(words):
        text += (rng.choice([" ", "  ", "\n", "\t"]) if i else "") + w
    if rng.random() < 0.2:
        text = " " + text
    if rng.random() < 0.2:
        text += " "
    return text


def _kind(got: list, want: list) -> str:
    if any(w == "" for w, _ in got):
        return "empty-token"
    if sorted(c for _, c in got) == sorted(c for _, c in want) and got != want:
        return "tie-order"
    return "other"


def find_counterexamples(candidate, trials: int = 400, seed: int = 0) -> dict[str, Case]:
    rng = random.Random(seed)
    cases = [(random_text(rng), rng.randint(-1, 4)) for _ in range(trials)]
    found: dict[str, Case] = {}
    for text, k in sorted(cases, key=lambda c: (len(c[0]), c)):
        got, want = candidate(text, k), oracle(text, k)
        if got != want:
            found.setdefault(_kind(got, want), (text, k))
    return found


# --- the fix ---------------------------------------------------------------------------
def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    if k <= 0:
        return []
    counts = Counter(text.lower().split())          # any whitespace; no "" tokens
    return heapq.nsmallest(k, counts.items(), key=lambda wc: (-wc[1], wc[0]))


COMPLEXITY = {"time": "O(L + d log k)", "space": "O(L)"}


def main() -> None:
    print("tidy sentence:", generated_top_k_words("the cat sat on the mat", 2))
    for label, case in sorted(find_counterexamples(generated_top_k_words).items()):
        print(f"{label:12} {case!r}: generated={generated_top_k_words(*case)}"
              f" oracle={oracle(*case)}")
    print("fixed counterexamples:", find_counterexamples(top_k_words))
    print("fixed:", top_k_words("b a b a c", 2), top_k_words("", 3),
          top_k_words("A a  b", 5), top_k_words("a b", 0))
    print("complexity:", COMPLEXITY)


if __name__ == "__main__":
    main()
