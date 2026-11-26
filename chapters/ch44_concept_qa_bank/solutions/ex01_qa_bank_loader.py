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

Approach ladder
---------------
1. Eyeball the JSON — O(n) human time, misses wrong § numbers. Reject.
2. Check fields and formats only — O(n), but a ``§7.31`` typo still passes.
3. Also parse the outline into a set and check membership — O(n + outline
   lines). Moving up a rung turns "plausible" cross-references into ones
   proven to exist.

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
ID_RE = re.compile(r"^([a-z]{2})(\d{2})$")
XREF_RE = re.compile(r"^§(\d+)\.(\d+)$")
TAG_RE = re.compile(r"^[a-z0-9-]+$")
# A sentence ends at . ! or ? followed by whitespace or the end of the text.
SENTENCE_END = re.compile(r"[.!?](?=\s|$)")
MAX_WORDS = 60


def parse_outline(text: str) -> set[str]:
    sections: set[str] = set()
    current = None
    for line in text.splitlines():
        m = re.match(r"^### Chapter (\d+)\.", line)
        if m:
            current = int(m.group(1))
            continue
        if line.startswith("## "):
            current = None
        if current is None:
            continue
        m = re.match(r"^(\d+)\.(\d+)(?:[–-](\d+)\.(\d+))?\s", line)
        if m and int(m.group(1)) == current:
            lo = int(m.group(2))
            hi = int(m.group(4)) if m.group(4) else lo
            sections.update(f"{current}.{k}" for k in range(lo, hi + 1))
    return sections


def load_bank(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(e, dict) for e in data):
        raise ValueError("bank must be a JSON list of objects")
    return data


def count_sentences(text: str) -> int:
    return len(SENTENCE_END.findall(text.strip()))


def _check_entry(e: dict, sections: set[str]) -> list[str]:
    errs: list[str] = []
    for k in STR_KEYS:
        if not isinstance(e.get(k), str) or not e[k].strip():
            errs.append(f"missing or non-string {k!r}")
    for k in LIST_KEYS:
        v = e.get(k)
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            errs.append(f"{k!r} must be a list of strings")
    if "book" in e and not isinstance(e["book"], bool):
        errs.append("'book' must be a bool")
    if errs:                                  # later rules need sound types
        return errs

    m = ID_RE.match(e["id"])
    if not m or m.group(1) not in PREFIX_SECTION:
        errs.append("bad id format")
    elif PREFIX_SECTION[m.group(1)] != e["section"]:
        errs.append(f"id prefix {m.group(1)!r} belongs in {PREFIX_SECTION[m.group(1)]}, "
                    f"not {e['section']}")
    if e["section"] not in PREFIX_SECTION.values():
        errs.append(f"unknown section {e['section']}")
    if not e["question"].rstrip().endswith("?"):
        errs.append("question must end with '?'")

    ans = e["answer"].strip()
    n = count_sentences(ans)
    if not ans.endswith("."):
        errs.append("answer must end with '.'")
    if not 1 <= n <= 3:
        errs.append(f"answer has {n} sentences (want 1-3)")
    if len(ans.split()) > MAX_WORDS:
        errs.append(f"answer has {len(ans.split())} words (max {MAX_WORDS})")

    x = XREF_RE.match(e["xref"])
    if not x:
        errs.append(f"bad xref format {e['xref']!r}")
    elif int(x.group(1)) == 44:
        errs.append("xref points at chapter 44 itself")
    elif f"{x.group(1)}.{x.group(2)}" not in sections:
        errs.append(f"xref {e['xref']} not in COURSE_OUTLINE.md")

    if not e["tags"] or not all(TAG_RE.match(t) for t in e["tags"]):
        errs.append("tags must be 1+ lowercase slugs")
    kws = e["keywords"]
    if not 1 <= len(kws) <= 4:
        errs.append(f"{len(kws)} keywords (want 1-4)")
    low = ans.lower()
    for kw in kws:
        if kw.lower() not in low:
            errs.append(f"keyword {kw!r} not in answer")
    return errs


def _text(value) -> str:
    """The stripped string, or "" for anything that is not a string."""
    return value.strip() if isinstance(value, str) else ""


def validate(entries: list[dict], sections: set[str]) -> list[str]:
    errors: list[str] = []
    # Count only usable strings: missing ids are not duplicates of each other,
    # and a non-string id (say a list) must not crash the Counter.
    ids = [_text(e.get("id")) for e in entries]
    qs = [_text(e.get("question")).casefold() for e in entries]
    id_counts = Counter(i for i in ids if i)
    q_counts = Counter(q for q in qs if q)
    for i, e in enumerate(entries):
        label = ids[i] or f"#{i}"
        problems = _check_entry(e, sections)
        if ids[i] and id_counts[ids[i]] > 1:
            problems.append("duplicate id")
        if qs[i] and q_counts[qs[i]] > 1:
            problems.append("duplicate question")
        errors.extend(f"{label}: {p}" for p in problems)
    return errors


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
