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

Hints
-----
- re.search(pattern, text, flags=re.IGNORECASE) for each pattern; any() is
  enough per item.
- Build hits and missing in one pass over the checklist to keep its order.
- Write MY_EXPLANATION as you would say it: what changed, why the old one
  was slow and wrong, the new cost, an alternative, the assumption, the edge
  cases, and how you know it works. Then cut it to the word budget.

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
    raise NotImplementedError("TODO")


MY_EXPLANATION = ""   # TODO: your 30-60 second answer, at most MAX_WORDS words


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
