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

Hints
-----
- Compare "a  b".split(" ") with "a  b".split() in a REPL.
- Read what Counter.most_common promises about equal counts.
- Classify each failure by comparing got and want: does got contain ""? Are
  the sorted counts equal while the lists differ?
- Sort cases by (len(text), case) before checking, and keep the first case
  per label (dict.setdefault).
- For the top k of d items, a heap of size k beats sorting everything when
  k << d; heapq has a function that takes a key.

Follow-ups
----------
- k close to d: which is simpler, and which would you pick?
- Punctuation ("cat," vs "cat") is a spec question: ask, don't guess.
- Streaming input too large for memory: what changes?
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
    raise NotImplementedError("TODO")


def random_text(rng: random.Random) -> str:
    raise NotImplementedError("TODO")


def find_counterexamples(candidate, trials: int = 400, seed: int = 0) -> dict[str, Case]:
    raise NotImplementedError("TODO")


# --- the fix ---------------------------------------------------------------------------
def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    raise NotImplementedError("TODO")


COMPLEXITY: dict[str, str] = {}   # TODO: in terms of L and d (and k)


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
