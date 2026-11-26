"""
Exercise 05 — Section, Tag and Chapter Coverage Report          [Tier: ○ Reference]
Chapter 44 · Pattern: group-and-count reporting · Target time: 15 min

Problem
-------
A bank is only useful if it covers the course evenly. Given the bank entries
(see ex01 for the schema) write:

- ``section_counts(bank)`` — ``{section: (total, in_book)}`` for every
  section present, keys sorted (``book`` missing counts as False);
- ``chapter_refs(bank)`` — ``{chapter: count}`` of the chapters the xrefs
  point at (``"§16.10"`` → 16), keys sorted numerically;
- ``top_tags(bank, k)`` — the k most frequent tags as ``(tag, count)``,
  ties broken alphabetically;
- ``gaps(bank, sections, min_total, min_book)`` — the sections (from the
  given list, so empty sections are caught too) whose totals fall short,
  as ``(section, total, in_book)``;
- ``uncited(bank, chapters)`` — the chapters in ``chapters`` that no entry
  cites, sorted.

Examples
--------
>>> bank = [{"section": "44.1", "xref": "§7.1", "tags": ["a"], "book": True},
...         {"section": "44.1", "xref": "§16.10", "tags": ["a", "b"]}]
>>> section_counts(bank)
{'44.1': (2, 1)}
>>> chapter_refs(bank)
{7: 1, 16: 1}
>>> gaps(bank, ["44.1", "44.2"], 1, 1)
[('44.2', 0, 0)]

Constraints
-----------
- O(n) counting passes plus a sort of the (small) result sets.
- Sort chapters numerically: as strings "16" < "7".

Approach ladder
---------------
1. Count by hand in the JSON — O(n) human time and error-prone.
2. One loop per question you ask (sections, then tags, ...) — O(n) each and
   repetitive, but clear; that is the reference here.
3. A single pass filling several ``Counter`` objects — same O(n), fewer
   passes; only matters for far larger banks.

Follow-ups
----------
- Join with your Leitner lapses (ex02) to rank weak sections, not just thin
  ones.
- Wrong-but-tempting: ``gaps`` that iterates only over sections *present* in
  the bank never reports an empty section.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

BANK_PATH = Path(__file__).resolve().parent.parent / "data" / "qa_bank.json"
SECTIONS = ["44.1", "44.2", "44.3", "44.4", "44.5", "44.6", "44.7"]
TITLES = {"44.1": "Python language and internals", "44.2": "Data structures and complexity",
          "44.3": "Algorithms and patterns", "44.4": "Concurrency and performance",
          "44.5": "Testing and engineering practice", "44.6": "ML and statistics",
          "44.7": "GenAI and LLM engineering"}


def section_counts(bank: list[dict]) -> dict[str, tuple[int, int]]:
    total, book = Counter(), Counter()
    for e in bank:
        total[e["section"]] += 1
        book[e["section"]] += bool(e.get("book", False))
    return {s: (total[s], book[s]) for s in sorted(total)}


def chapter_refs(bank: list[dict]) -> dict[int, int]:
    c = Counter(int(e["xref"].lstrip("§").split(".")[0]) for e in bank)
    return dict(sorted(c.items()))


def top_tags(bank: list[dict], k: int) -> list[tuple[str, int]]:
    c = Counter(t for e in bank for t in e["tags"])
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def gaps(bank: list[dict], sections: list[str], min_total: int,
         min_book: int) -> list[tuple[str, int, int]]:
    counts = section_counts(bank)
    out = []
    for s in sections:
        total, book = counts.get(s, (0, 0))
        if total < min_total or book < min_book:
            out.append((s, total, book))
    return out


def uncited(bank: list[dict], chapters: list[int]) -> list[int]:
    cited = chapter_refs(bank)
    return sorted(ch for ch in chapters if ch not in cited)


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    counts = section_counts(bank)
    print(f"{'section':<8}{'title':<34}{'bank':>5}{'book':>6}")
    for s in SECTIONS:
        total, book = counts.get(s, (0, 0))
        print(f"{s:<8}{TITLES[s]:<34}{total:>5}{book:>6}")
    print(f"{'all':<42}{len(bank):>5}{sum(b for _, b in counts.values()):>6}")
    print("gaps (need >= 10 in bank, >= 8 in book):", gaps(bank, SECTIONS, 10, 8))
    refs = chapter_refs(bank)
    print("chapters cited:", len(refs), "| most cited:",
          sorted(refs.items(), key=lambda kv: (-kv[1], kv[0]))[:5])
    print("teaching chapters 5-43 never cited:", uncited(bank, list(range(5, 44))))
    print("top tags:", top_tags(bank, 6))


if __name__ == "__main__":
    main()
