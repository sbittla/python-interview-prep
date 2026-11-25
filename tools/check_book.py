"""Check manuscript budgets, outline coverage and repo completeness.

Usage:
    python tools/check_book.py                  # whole book: per-chapter table + total pages
    python tools/check_book.py --chapter 09     # one chapter (repeatable); exit 1 on any error

Checks per chapter NN:
- manuscript/chNN_<slug>.md exists; page estimate (words / 330) within budget + 10 %
- one "## NN.k" heading for every NN.k section listed in COURSE_OUTLINE.md
- has an Exercises table, a <details> quiz block and a Summary card
- every repo path cited in the manuscript (chapters/...py|md|txt|csv|json) exists
- chapters/chNN_<slug>/README.md exists
- every solutions/(ex|lab)*.py has matching exercises/, tests/test_*, outputs/*.txt (and vice versa)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MS = ROOT / "manuscript"
CODE = ROOT / "chapters"
WORDS_PER_PAGE = 330
LIMIT_PAGES = 450

BUDGET = {
    1: 6, 2: 8, 3: 8, 4: 6, 5: 9, 6: 12, 7: 12, 8: 6, 9: 12, 10: 11, 11: 12, 12: 10,
    13: 8, 14: 13, 15: 8, 16: 14, 17: 9, 18: 9, 19: 14, 20: 7, 21: 8, 22: 6, 23: 7, 24: 9,
    25: 7, 26: 8, 27: 6, 28: 9, 29: 11, 30: 10, 31: 8, 32: 5, 33: 8, 34: 9, 35: 10, 36: 10,
    37: 9, 38: 7, 39: 10, 40: 9, 41: 7, 42: 9, 43: 6, 44: 8, 45: 14, 46: 5, 47: 8, 48: 3,
}
FRONT_BUDGET, APPENDIX_BUDGET = 3, 15
SLUGS = {
    1: "interview_landscape", 2: "interview_playbook", 3: "diagnostic_test", 4: "setup_io_baseline",
    5: "syntax_types_functions", 6: "collections_stdlib_toolbox", 7: "python_gotchas",
    8: "big_o_primer", 9: "arrays_strings_hashing", 10: "two_pointers_sliding_window_prefix_sums",
    11: "binary_search_sorting", 12: "stacks_queues_monotonic", 13: "linked_lists",
    14: "recursion_trees_bst", 15: "heaps_top_k", 16: "graphs", 17: "tries_intervals",
    18: "backtracking", 19: "dynamic_programming", 20: "greedy", 21: "math_bits_strings",
    22: "complexity_analysis", 23: "iterators_generators_comprehensions",
    24: "oop_dataclasses_abcs", 25: "decorators_closures_functools", 26: "exceptions_stdlib_files",
    27: "memory_gil_performance", 28: "concurrency_asyncio", 29: "design_style_problems",
    30: "log_text_processing_sql", 31: "testing_debugging_code_review",
    32: "take_home_pair_programming", 33: "numpy_vectorization", 34: "pandas_sql_analysis",
    35: "ml_math_stats_metrics", 36: "classical_ml_from_scratch", 37: "pytorch_training_debugging",
    38: "tokenization_embeddings", 39: "attention_transformers_decoding", 40: "retrieval_rag",
    41: "agents_tool_calling", 42: "llm_production_patterns", 43: "llm_system_design",
    44: "concept_qa_bank", 45: "problem_bank", 46: "ai_assisted_practice", 47: "mock_interviews",
    48: "final_roadmap",
}
EXERCISE_RE = re.compile(r"^(ex|lab)\d+_\w+\.py$")
REPO_PATH_RE = re.compile(r"chapters/ch\d\d_[\w./-]+\.(?:py|md|txt|csv|json|log|jsonl)")


def outline_sections() -> dict[int, list[str]]:
    sections: dict[int, list[str]] = {}
    current = None
    for line in (ROOT / "COURSE_OUTLINE.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^### Chapter (\d+)\.", line)
        if m:
            current = int(m.group(1))
            sections[current] = []
            continue
        if line.startswith("## "):
            current = None
        if current is None:
            continue
        m = re.match(r"^(\d+)\.(\d+)(?:[–-](\d+)\.(\d+))?\s", line)
        if m and int(m.group(1)) == current:
            lo = int(m.group(2))
            hi = int(m.group(4)) if m.group(4) else lo
            sections[current].extend(f"{current}.{k}" for k in range(lo, hi + 1))
    return sections


def pages_of(path: Path) -> float:
    return len(path.read_text(encoding="utf-8").split()) / WORDS_PER_PAGE


def check_chapter(n: int, sections: list[str]) -> tuple[float, list[str]]:
    errors: list[str] = []
    slug = SLUGS[n]
    ms = MS / f"ch{n:02d}_{slug}.md"
    pages = 0.0
    if not ms.exists():
        errors.append(f"missing manuscript {ms.relative_to(ROOT).as_posix()}")
    else:
        text = ms.read_text(encoding="utf-8")
        pages = pages_of(ms)
        if pages > BUDGET[n] * 1.10:
            errors.append(f"over budget: {pages:.1f} pages > {BUDGET[n]} + 10%")
        headings = set(re.findall(r"^##\s+(\d+\.\d+)\b", text, flags=re.M))
        missing = [s for s in sections if s not in headings]
        if missing:
            errors.append(f"missing section headings: {', '.join(missing)}")
        if not re.search(r"^#\s+Chapter\s+%d\." % n, text, flags=re.M):
            errors.append(f"first heading must be '# Chapter {n}. <Title>'")
        placeholders = len(re.findall(r"^```text\s*\n\s*TODO\b", text, flags=re.M))
        if placeholders:
            errors.append(f"{placeholders} placeholder output block(s) (```text TODO) — paste real output")
        if "<details>" not in text:
            errors.append("no <details> quiz-answer block")
        if not re.search(r"^##+ .*Summary card", text, flags=re.M | re.I):
            errors.append("no 'Summary card' heading")
        if not re.search(r"^##+ .*Exercises", text, flags=re.M):
            errors.append("no 'Exercises' heading")
        for ref in sorted(set(REPO_PATH_RE.findall(text))):
            if not (ROOT / ref).exists():
                errors.append(f"cited path does not exist: {ref}")

    folder = CODE / f"ch{n:02d}_{slug}"
    if not folder.is_dir():
        errors.append(f"missing code folder chapters/{folder.name}")
        return pages, errors
    if not (folder / "README.md").exists():
        errors.append("missing chapter README.md")
    sols = {p.name for p in (folder / "solutions").glob("*.py") if EXERCISE_RE.match(p.name)}
    stubs = {p.name for p in (folder / "exercises").glob("*.py") if EXERCISE_RE.match(p.name)}
    tests = {p.name[5:] for p in (folder / "tests").glob("test_*.py")}
    outs = {p.stem + ".py" for p in (folder / "outputs").glob("*.txt")}
    if not sols:
        errors.append("no solutions")
    for label, have in (("exercises/", stubs), ("tests/test_", tests), ("outputs/(.txt)", outs)):
        lacking = sorted(sols - have)
        if lacking:
            errors.append(f"{len(lacking)} solution(s) lack {label}: {', '.join(lacking[:6])}"
                          + (" ..." if len(lacking) > 6 else ""))
        orphans = sorted(have - sols)
        if orphans:
            errors.append(f"orphan {label} without solution: {', '.join(orphans[:6])}")
    return pages, errors


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", action="append", default=[])
    args = parser.parse_args()
    sections = outline_sections()
    selected = [int(c) for c in args.chapter] or sorted(BUDGET)

    total_pages = 0.0
    failed = 0
    for n in selected:
        pages, errors = check_chapter(n, sections.get(n, []))
        total_pages += pages
        status = "ok " if not errors else "ERR"
        print(f"{status} ch{n:02d} {pages:5.1f}/{BUDGET[n]:>2} pages  {SLUGS[n]}")
        for e in errors:
            print(f"      - {e}")
        failed += bool(errors)

    if not args.chapter:
        front = MS / "00_front_matter.md"
        fp = pages_of(front) if front.exists() else 0.0
        ap = sum(pages_of(p) for p in MS.glob("appendix_*.md"))
        print(f"{'ok ' if fp <= FRONT_BUDGET * 1.1 else 'ERR'} front matter {fp:5.1f}/{FRONT_BUDGET}")
        print(f"{'ok ' if ap <= APPENDIX_BUDGET * 1.1 else 'ERR'} appendices   {ap:5.1f}/{APPENDIX_BUDGET}")
        total_pages += fp + ap
        print(f"\nTOTAL ≈ {total_pages:.0f} pages (limit {LIMIT_PAGES}); chapters with errors: {failed}")
        if total_pages > LIMIT_PAGES:
            print("ERROR: book exceeds the page limit")
            return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
