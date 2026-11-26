"""
Exercise 06 — Explain the Trade-offs: a Checklist Scorer            [Tier: ◆ Extended]
Chapter 46 · Pattern: rubric as data, word-boundary matching · Target time: 25 min

Problem
-------
After you fix generated code, the interviewer asks "why this version?". A
strong 30-60 second answer covers the same six points every time. Build a
scorer for that checklist, then write an answer that passes it.

1. score(text, checklist=CHECKLIST, max_words=MAX_WORDS) -> Report with
   - hits: names of checklist items the text covers, in checklist order;
   - missing: the other names, in checklist order;
   - words: the word count (text.split());
   - ok: True when nothing is missing and words <= max_words.
   An item is covered when ANY of its regex patterns matches the text,
   case-insensitively. Patterns are written with \\b word boundaries, so "vs"
   must not match "devs" and "test" must not match "contest".
2. MY_EXPLANATION: your spoken answer for exercise 02's fix (dedupe with a
   set instead of a list and a mutable default). It must pass score() AND
   name the specifics: O(n), O(n^2) for the old version, and hashable.

Examples
--------
>>> score("It is faster and cleaner.").missing
['complexity', 'space', 'alternative', 'edge cases', 'assumptions', 'evidence']
>>> score(MY_EXPLANATION).ok
True

Constraints
-----------
- The scorer checks that the points are MENTIONED, not that they are true or
  even sentences: the "keyword soup" row in main() passes. That is its limit;
  a partner (or you, re-reading) checks the content.

Approach ladder
---------------
1. Brute force — `"test" in text.lower()`: substring matching gives false
   hits ("contest", "devs") and a vague answer scores well.
2. Improved   — one keyword per item with word boundaries: misses synonyms
   ("linear" for O(n), "memory" for space).
3. Optimal    — each item is a tuple of alternative regexes searched with
   re.IGNORECASE (the re module caches each compiled pattern); about O(P·L)
   for P patterns over L characters of normal text. A word budget keeps the
   spoken answer short.

Follow-ups
----------
- Add an item for "what I would do with more time".
- Score a transcript per speaker turn to see where an answer drifted.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

MAX_WORDS = 90

CHECKLIST: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("complexity", (r"\bO\([^)]*\)", r"\blinear\b", r"\bquadratic\b", r"\blogarithmic\b")),
    ("space", (r"\bspace\b", r"\bmemory\b")),
    ("alternative", (r"\binstead of\b", r"\balternative\b", r"\bvs\.?(?!\w)",
                     r"\bversus\b", r"\bcompared\b", r"\brather than\b")),
    ("edge cases", (r"\bedge\b", r"\bempty\b", r"\bduplicates?\b", r"\bboundary\b")),
    ("assumptions", (r"\bassum\w*", r"\brequires?\b", r"\bonly if\b", r"\bunless\b",
                     r"\bbreaks?\b")),
    ("evidence", (r"\btests?\b", r"\btested\b", r"\boracle\b", r"\bcounterexample\b",
                  r"\bproperty\b")),
)


@dataclass(frozen=True)
class Report:
    hits: list[str]
    missing: list[str]
    words: int
    ok: bool


def score(text: str, checklist=CHECKLIST, max_words: int = MAX_WORDS) -> Report:
    hits, missing = [], []
    for name, patterns in checklist:
        covered = any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)
        (hits if covered else missing).append(name)
    words = len(text.split())
    return Report(hits, missing, words, not missing and words <= max_words)


MY_EXPLANATION = (
    "I replaced the list lookup with a local set. The old version was O(n^2) "
    "because `in` on a list scans it, and the mutable default leaked state "
    "between calls. Now it is O(n) expected time and O(n) extra space. The "
    "alternative, dict.fromkeys, is shorter but hides the loop. It requires "
    "hashable items; for unhashable ones I would dedupe on a key. Edge cases: "
    "empty input and repeated calls. A probe test counts __eq__ calls and a "
    "second-call test proves the leak is gone."
)


def main() -> None:
    answers = {
        "vague": "It is faster and cleaner now.",
        "substring trap": "The contest devs were pretty.",
        "rambling": "I tested it. " * 50,
        "keyword soup": "O(n) O(n^2) hashable space vs empty requires test",
        "mine": MY_EXPLANATION,
    }
    for label, text in answers.items():
        r = score(text)
        print(f"{label:15} ok={r.ok!s:5} words={r.words:3} missing={r.missing}")


if __name__ == "__main__":
    main()
