# Chapter 44 — Concept Q&A Bank (code)

Manuscript: `manuscript/ch44_concept_qa_bank.md`. The book prints 8 Q&As per section (56); the
repository bank holds all of them plus repo-only extras (102 in total). Every answer cross-references
the section that teaches it; nothing here re-teaches a topic.

## Data

| File | Contents |
|---|---|
| `data/qa_bank.json` | 102 entries: `id`, `section` (44.1–44.7), `question`, `answer` (1–3 sentences), `xref` (`§N.k`), `tags`, `keywords` (graded by ex03), `book` (printed in the manuscript?) |
| `data/predict_output.json` | 18 "predict the output" snippets in 6 sets, each with `xref` and the `expected` stdout |

Id prefixes: `py` 44.1 Python, `ds` 44.2 data structures, `al` 44.3 algorithms, `cc` 44.4
concurrency, `te` 44.5 testing and engineering, `ml` 44.6 ML and statistics, `ai` 44.7 GenAI.

## Exercises

| # | File | Title | Tier | Pattern |
|---|---|---|---|---|
| 01 | `ex01_qa_bank_loader.py` | Q&A bank loader and validator (xrefs checked against `COURSE_OUTLINE.md`) | ★ Core | schema validation, cross-reference checking |
| 02 | `ex02_leitner_scheduler.py` | Seeded Leitner scheduler on the §3.4 ladder (1, 3, 7, 21 days) | ★ Core | state machine, priority ordering |
| 03 | `ex03_quiz_runner.py` | Quiz runner over scripted answers | ◆ Extended | stratified sampling, keyword grading |
| 04 | `ex04_predict_output.py` | "Predict the output" sets, verified by execution | ★ Core | executable answer key |
| 05 | `ex05_coverage_report.py` | Section, tag and chapter coverage report | ○ Reference | group-and-count reporting |

The tests keep the data honest. `test_ex01` validates the whole bank against the real outline.
`test_ex03` checks that every model answer passes its own keyword grading. `test_ex04` re-runs every
snippet and compares its output with `expected`. `test_ex05` fails if a section drops below 10
entries (8 in the book) or a teaching chapter 5–43 is never cited.

## How to run

```bash
.venv/Scripts/python chapters/ch44_concept_qa_bank/solutions/ex04_predict_output.py   # one solution
.venv/Scripts/python tools/run_all.py --chapter 44                                    # regenerate outputs/
.venv/Scripts/python -m pytest chapters/ch44_concept_qa_bank                          # test solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch44_concept_qa_bank         # test your stubs
```
