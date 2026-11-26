"""
Exercise 03 — Quiz Runner over Scripted Answers                [Tier: ◆ Extended]
Chapter 44 · Pattern: stratified sampling + keyword grading · Target time: 25 min

Problem
-------
Build a quiz runner that can be tested without a human at the keyboard:
responses come from a script (a dict ``id -> text``) instead of ``input()``.

- ``normalise(text)`` — lowercase; every run of characters that is not a
  letter or digit becomes one space; strip. ``"O(log n), `heapify`!"`` →
  ``"o log n heapify"``.
- ``grade(entry, response, threshold=0.5)`` — a keyword *hits* if its
  normalised form appears in the normalised response as whole words.
  Return ``(hits, total, passed)``, where ``passed = hits / total >= threshold``.
- ``pick(bank, n, seed, sections=None)`` — choose n distinct ids, spread
  across sections: group entries by section (sections in sorted order,
  optionally only those listed), shuffle each group with one
  ``random.Random(seed)`` (groups in order), then deal round-robin one id per
  section until n are chosen or the groups run out.
- ``run_quiz(bank, ids, responses, threshold=0.5)`` — grade each id (a
  missing response is ``""``) and return a dict with ``rows`` (id, section,
  hits, total, passed, xref), ``score`` (passed, asked), ``by_section``
  ({section: [passed, asked]}) and ``review`` — the xrefs of failed
  questions, unique, sorted by (chapter, section) numerically.

Examples
--------
>>> grade({"keywords": ["min-heap", "negated"]}, "heapq is a min heap; push negated keys")
(2, 2, True)
>>> grade({"keywords": ["once"]}, "evaluated at import")
(0, 1, False)

Constraints
-----------
- ``n`` <= number of eligible entries (else ``ValueError``); unknown ids in
  ``run_quiz`` raise ``KeyError``.
- Whole-word matching: keyword "rank" must not hit "ranking".

Hints
-----
- One ``re.sub`` over the lowercased text does most of ``normalise``.
- Whole-word phrase test: pad both strings with spaces before ``in``.
- ``pick``: build one list per section, shuffle them in sorted-section order
  with a single seeded ``Random``, then pop from the front in turn.
- Sort review xrefs with a key that splits ``"§16.10"`` into ``(16, 10)``.

Follow-ups
----------
- Keyword grading rewards vocabulary, not understanding; use it to triage,
  then self-grade the misses against the model answer.
- Weight sections by your Leitner lapses (ex02) instead of round-robin.
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

BANK_PATH = Path(__file__).resolve().parent.parent / "data" / "qa_bank.json"


def normalise(text: str) -> str:
    raise NotImplementedError("TODO")


def grade(entry: dict, response: str, threshold: float = 0.5) -> tuple[int, int, bool]:
    raise NotImplementedError("TODO")


def pick(bank: list[dict], n: int, seed: int, sections: list[str] | None = None) -> list[str]:
    raise NotImplementedError("TODO")


def run_quiz(bank: list[dict], ids: list[str], responses: dict[str, str],
             threshold: float = 0.5) -> dict:
    raise NotImplementedError("TODO")


SCRIPT = {   # a learner's typed answers for the seed-44 quiz below
    "py05": "the lambda reads i when called, so bind it with a default argument i=i",
    "ds14": "key a dict by a signature such as the letter counts",
    "al04": "BFS explores in order of distance, so the first visit is a shortest path",
    "cc07": "it is fine because asyncio is fast",
    "te03": "patch where the name is looked up: app.fetch",
    "ml04": "resample with replacement and take the percentiles",
    "ai17": "r squared parameters",
}


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    ids = pick(bank, 7, seed=44)
    print("picked:", ids)
    report = run_quiz(bank, ids, SCRIPT)
    for qid, sec, hits, total, passed, xref in report["rows"]:
        print(f"  {qid} {sec}  keywords {hits}/{total}  {'PASS' if passed else 'MISS'}  {xref}")
    print("score: {}/{}".format(*report["score"]))
    print("review next:", report["review"])
    print("pick is deterministic:", pick(bank, 7, 44) == ids)
    print("two sections only:", pick(bank, 4, seed=1, sections=["44.6", "44.7"]))
    print("whole words only:", grade({"keywords": ["rank"]}, "ranking"))


if __name__ == "__main__":
    main()
