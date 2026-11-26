"""
Exercise 01 — Q&A Bank Loader and Validator                    [Tier: ★ Core]
Chapter 44 · Pattern: schema validation + cross-reference checking · Target time: 25 min

Problem
-------
The concept bank lives in ``data/qa_bank.json``: a list of entries

    {"id": "py01", "section": "44.1", "question": "...?", "answer": "...",
     "xref": "§7.1", "tags": ["references"], "keywords": ["once", "None"],
     "book": true}

Write

- ``parse_outline(text)`` — the set of section numbers ("7.1", "16.10", ...)
  listed under each ``### Chapter N.`` heading of ``COURSE_OUTLINE.md``.
  A line counts only if it starts with ``N.k`` for the current chapter N;
  a range line ``N.a–N.b`` lists every section from a to b; a ``## `` heading
  ends the current chapter.
- ``load_bank(path)`` — read the JSON; it must be a list of objects
  (raise ``ValueError`` otherwise).
- ``validate(entries, sections)`` — return a list of error strings, one per
  broken rule, each prefixed with the entry id (``"#<index>"`` if the id is
  unusable). Rules:

  1. required keys with the right types: id, section, question, answer, xref
     (str); tags, keywords (list of str); optional ``book`` (bool);
  2. id matches ``<prefix><2 digits>`` and is unique; the prefix fixes the
     section (py 44.1, ds 44.2, al 44.3, cc 44.4, te 44.5, ml 44.6, ai 44.7).
     Only non-empty string ids take part in the uniqueness check: two
     entries with no id are two "missing id" errors, not duplicates, and an
     unhashable id such as ``["x"]`` must not crash the validator;
  3. the question ends with "?" and is unique (case-insensitive);
  4. the answer ends with "." and has 1–3 sentences and at most 60 words;
  5. xref looks like ``§N.k``, exists in the outline, and is not in Ch. 44;
  6. tags are 1+ lowercase slugs (``[a-z0-9-]+``);
  7. 1–4 keywords, each appearing in the answer (case-insensitive), so the
     quiz runner (ex03) can grade against them.

Examples
--------
>>> sorted(parse_outline("### Chapter 7. Gotchas\\n7.1 Defaults\\n7.2 Copies\\n"))
['7.1', '7.2']
>>> count_sentences("One. Two `x.y` here! Three?")
3

Constraints
-----------
- Standard library only; the bank is small (≈100 entries), so O(n) passes.
- Never stop at the first error: report all of them (a validator that hides
  errors forces fix-rerun loops).

Hints
-----
- Outline: remember the current chapter from ``### Chapter N.``; clear it on
  any ``## `` line; keep a line that starts with ``<number>.<number>``
  only when the first number equals the current chapter. Handle an optional ``–N.b`` range.
- Sentences: count ``.``, ``!`` or ``?`` only when followed by whitespace or
  the end of the text.
- Check types first; skip the content rules for an entry whose types are
  wrong, or the later checks crash.
- Count ids and casefolded questions with ``Counter`` before the main loop,
  feeding it only non-empty strings (``None`` and lists must be skipped).

Follow-ups
----------
- Also check the cited chapter's manuscript heading (when it exists).
- Run ``validate`` in CI so a renumbered outline breaks the build.
- Wrong-but-tempting: counting sentences with ``answer.count(".")`` —
  ``x.copy()`` and ``3.14`` contain dots that do not end sentences.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

CHAPTER_DIR = Path(__file__).resolve().parent.parent
BANK_PATH = CHAPTER_DIR / "data" / "qa_bank.json"
OUTLINE_PATH = CHAPTER_DIR.parent.parent / "COURSE_OUTLINE.md"

PREFIX_SECTION = {"py": "44.1", "ds": "44.2", "al": "44.3", "cc": "44.4",
                  "te": "44.5", "ml": "44.6", "ai": "44.7"}
STR_KEYS = ("id", "section", "question", "answer", "xref")
LIST_KEYS = ("tags", "keywords")
MAX_WORDS = 60


def parse_outline(text: str) -> set[str]:
    raise NotImplementedError("TODO")


def load_bank(path: Path) -> list[dict]:
    raise NotImplementedError("TODO")


def count_sentences(text: str) -> int:
    raise NotImplementedError("TODO")


def validate(entries: list[dict], sections: set[str]) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    sections = parse_outline(OUTLINE_PATH.read_text(encoding="utf-8"))
    bank = load_bank(BANK_PATH)
    print(f"outline sections parsed: {len(sections)}")
    print(f"bank entries: {len(bank)} (in book: {sum(e.get('book', False) for e in bank)})")
    per = Counter(e["section"] for e in bank)
    print("per section:", " ".join(f"{s}={per[s]}" for s in sorted(per)))
    errors = validate(bank, sections)
    print(f"validation errors: {len(errors)}")

    broken = [
        {"id": "py01", "section": "44.2", "question": "Why",
         "answer": "One. Two. Three. Four.", "xref": "§7.99",
         "tags": ["Refs"], "keywords": ["zebra"]},
        {"id": "py01", "section": "44.1", "question": "Dup?",
         "answer": "Calls `x.copy()` on 3.14 data.", "xref": "§44.1",
         "tags": ["refs"], "keywords": ["copy"], "book": "yes"},
        {"question": "No id?"},
    ]
    print("broken sample:")
    for err in validate(broken, sections):
        print("  " + err)


if __name__ == "__main__":
    main()
