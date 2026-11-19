# Chapter 03 — Diagnostic Test and Track Selection

Take the diagnostic in the book (Section 3.1, 60 minutes, no interpreter) **before** opening
`ex01_diagnostic_bank.py`: that file is the question bank. Then grade yourself with ex01–ex04,
place yourself with ex02 and start your review log with ex05.

| Id | Title | Tier | Pattern | Target |
|---|---|---|---|---|
| [ex01](solutions/ex01_diagnostic_bank.py) | The 30-question diagnostic and its auto-grader (answers produced by executing the snippets) | ★ Core | data-driven grading, `exec` + `redirect_stdout` | 30 min |
| [ex02](solutions/ex02_placement.py) | Placement: area scores → fast / full / foundations path → weekly plan per track S/M/L | ★ Core | decision table + templating | 25 min |
| [ex03](solutions/ex03_first_unique.py) | Diagnostic Q29: first unique value (+ 0–4 point scorer) | ★ Core | frequency count with a hash map | 15 min |
| [ex04](solutions/ex04_merge_intervals.py) | Diagnostic Q30: merge booked intervals (+ 0–4 point scorer) | ★ Core | sort + linear sweep | 15 min |
| [ex05](solutions/ex05_review_log.py) | Setting up a spaced-repetition log (1, 3, 7, 21 days) | ★ Core | append-only log + date arithmetic | 25 min |

The log written by ex05 uses the same CSV format as Chapter 48's scheduler
(`chapters/ch48_final_roadmap/solutions/ex02_spaced_repetition.py`), which adds daily caps,
a 7-day agenda and a weakest-pattern ranking on top of it.

## How to run

```bash
.venv/Scripts/python chapters/ch03_diagnostic_test/solutions/ex01_diagnostic_bank.py
.venv/Scripts/python -m pytest chapters/ch03_diagnostic_test             # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch03_diagnostic_test   # your stubs
.venv/Scripts/python tools/run_all.py --chapter 03                         # regenerate outputs/
```

Standard library only; every output is deterministic ("today" is fixed at 2026-11-18).
