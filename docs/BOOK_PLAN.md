# Book Plan — page budget, content split, quality bar

Read this together with `AUTHORING_GUIDE.md`. Where the two disagree, **this file wins**
(it replaces the guide's old "4,000–9,000 words per chapter" target).

## 1. Hard limit: the whole book is under 450 pages

Page estimate used by `tools/check_book.py`: **1 page = 330 words** of manuscript Markdown
(code and tables included). Budget below totals **438 pages**, leaving a 12-page safety margin.
**Aim for 90–100 % of the budget.** Budget + 10 % is an emergency ceiling, not a target: early chapters
averaged ~5 % over, which across 48 chapters would break the 450-page limit. Any chapter over 100 %
must be trimmed back unless another chapter is correspondingly under.

| Ch | Pages | Words (≈) | Ch | Pages | Words (≈) | Ch | Pages | Words (≈) |
|---|---|---|---|---|---|---|---|---|
| Front matter | 3 | 1,000 | 17 | 9 | 3,000 | 33 | 8 | 2,650 |
| 01 | 6 | 2,000 | 18 | 9 | 3,000 | 34 | 9 | 3,000 |
| 02 | 8 | 2,650 | 19 | 14 | 4,600 | 35 | 10 | 3,300 |
| 03 | 8 | 2,650 | 20 | 7 | 2,300 | 36 | 10 | 3,300 |
| 04 | 6 | 2,000 | 21 | 8 | 2,650 | 37 | 9 | 3,000 |
| 05 | 9 | 3,000 | 22 | 6 | 2,000 | 38 | 7 | 2,300 |
| 06 | 12 | 4,000 | 23 | 7 | 2,300 | 39 | 10 | 3,300 |
| 07 | 12 | 4,000 | 24 | 9 | 3,000 | 40 | 9 | 3,000 |
| 08 | 6 | 2,000 | 25 | 7 | 2,300 | 41 | 7 | 2,300 |
| 09 | 12 | 4,000 | 26 | 8 | 2,650 | 42 | 9 | 3,000 |
| 10 | 11 | 3,600 | 27 | 6 | 2,000 | 43 | 6 | 2,000 |
| 11 | 12 | 4,000 | 28 | 9 | 3,000 | 44 | 8 | 2,650 |
| 12 | 10 | 3,300 | 29 | 11 | 3,600 | 45 | 14 | 4,600 |
| 13 | 8 | 2,650 | 30 | 10 | 3,300 | 46 | 5 | 1,650 |
| 14 | 13 | 4,300 | 31 | 8 | 2,650 | 47 | 8 | 2,650 |
| 15 | 8 | 2,650 | 32 | 5 | 1,650 | 48 | 3 | 1,000 |
| 16 | 14 | 4,600 | | | | Appendices A–H | 15 | 5,000 |

Totals: Part 0 = 28 · I = 39 · II = 97 · III = 44 · IV = 46 · V = 34 · VI = 46 · VII = 48 ·
VIII = 38 · front + appendices = 18 → **438 pages**.

Staying in budget is a *design* constraint, not a trimming step: decide up front which 2–4 problems
the chapter teaches in full and push everything else to the repo.

## 2. What goes where

The manuscript **teaches**; the repository **trains**. A reader of the book alone must be able to
learn every outline section; a reader of the repo gets the full practice set and every detail.

| Content | Manuscript | Repository |
|---|---|---|
| Concept explanation, mental models, diagrams | **Yes** (concise) | Docstring summary only |
| "Recognise it" box, interviewer's view, quiz, summary card | **Yes** | No |
| Key worked problems (2–4 per pattern chapter) | Full approach ladder; optimal code ≤ 35 lines per listing; real output | Same problem as an exercise, every rung implemented |
| Remaining exercises | One row each in the Exercises table (id, title, tier, pattern) | Full statement, ladder, follow-ups, wrong-but-tempting answers, tests |
| Brute-force / intermediate rungs | Described in 1–3 sentences + complexity | Implemented and tested |
| Long edge-case lists, extra follow-ups | Top 5 only | Complete list in the docstring |
| Data files, mock LLM clients, helpers | Show the interface only | Full code |

Rules:
- Never paste a whole repo solution file into the manuscript. Show the core function, then point to
  the file: `→ repo: chapters/ch09_arrays_strings_hashing/solutions/ex05_two_sum.py`.
- **Canonical homes** (named in `COURSE_OUTLINE.md`) teach a topic once; everyone else cross-references
  it as `(→ §12.6)` in one sentence instead of re-teaching.
- Each outline section gets a `## NN.k Title` heading. A ○ Reference section may be 2–6 lines.
  ★ sections get the most space; ◆ sections roughly half; ○ sections a paragraph.
- Use tables for comparisons, not paragraphs. No filler, no motivational padding, no repetition of
  the summary card in the body.

## 3. Exercise targets per chapter (repo)

| Chapter kind | Exercises |
|---|---|
| Pattern / teaching chapters (5–7, 9–21, 23–31, 33–42) | 8–12 (keep existing ones; fill gaps) |
| Short chapters (2, 3, 4, 8, 22, 32, 43, 46, 47, 48) | 4–6 |
| 44 Concept Q&A bank | 4–6 (quiz/flashcard tooling + "predict the output" sets) |
| 45 Problem bank | 150 problems `exNNN_*` + 30 AI labs `labNN_*` (see §5) |

Every exercise has **all four files** (exercises/, solutions/, tests/, outputs/) plus a row in the
chapter `README.md`. Stubs import cleanly and run (`main()` may hit `NotImplementedError`).

## 4. Quality bar: every chapter must score ≥ 9.5 / 10

Scored by an independent reviewer who did not write the chapter.

| # | Criterion | Points | What a full score means |
|---|---|---|---|
| 1 | Technical accuracy | 2.5 | No wrong claim, complexity, API detail, or version fact. Code correct on edge cases. |
| 2 | Verified & runnable | 1.5 | `run_all.py --chapter NN` and the chapter's pytest pass; manuscript code blocks were actually run and output blocks are real; deterministic. |
| 3 | Outline coverage | 1.0 | Every `NN.k` section in `COURSE_OUTLINE.md` present with the right depth for its tier. |
| 4 | Teaching quality | 2.0 | Clear progression, approach ladders with "why move up a rung", recognise-it box, pitfalls, wrong-but-tempting answers, interviewer's view. |
| 5 | Clarity & concision | 1.5 | Within the page budget (±10 %); plain language; no padding or repetition. |
| 6 | Book/repo split | 1.0 | Follows §2; no duplicated full solutions; correct cross-references and repo paths. |
| 7 | Exercise quality | 0.5 | Original statements, graded tiers, meaningful tests incl. edge cases, README index complete. |

Any criterion-1 error caps the score at 9.0 until fixed. Reviewer output: score per criterion, total,
and a numbered list of concrete required fixes (file + location).

## 5. Chapter 45 problem-bank numbering (fixed — do not renumber)

| Range | Category | Count | | Range | Category | Count |
|---|---|---|---|---|---|---|
| 001–014 | Arrays and strings | 14 | | 091–098 | Heaps | 8 |
| 015–024 | Hash maps and sets | 10 | | 099–106 | Recursion and backtracking | 8 |
| 025–032 | Two pointers | 8 | | 107–120 | Dynamic programming | 14 |
| 033–040 | Sliding window | 8 | | 121–127 | Greedy and intervals | 7 |
| 041–048 | Binary search | 8 | | 128–132 | Bit manipulation and math | 5 |
| 049–056 | Linked lists (done) | 8 | | 133–138 | Design-style problems | 6 |
| 057–066 | Stacks and queues | 10 | | 139–150 | Matrix, tensor, AI/ML implementation | 12 |
| 067–078 | Trees | 12 | | lab01–lab30 | AI engineering labs | 30 |
| 079–090 | Graphs | 12 | | | | |

Within each category order problems Beginner → Intermediate → Advanced (counts per
`COURSE_OUTLINE.md`). Docstring header adds `Level: Beginner|Intermediate|Advanced` and each solution
also defines `minimal(...)`, the short version you would write in an interview. Prefer problems that
are *not* already a chapter exercise; when a classic must repeat, give it a twist and cross-reference
the chapter. Files: `solutions/ex001_<slug>.py`, `tests/test_ex001_<slug>.py`, etc.

## 6. Workflow for one chapter

1. Read the chapter's outline section, this file, `AUTHORING_GUIDE.md`, and any existing code in the
   chapter folder (review it: fix bugs, keep good work, don't rewrite for style alone).
2. Complete the repo: exercises/solutions/tests/README; `python tools/run_all.py --chapter NN`;
   `python -m pytest chapters/chNN_<slug>`.
3. Write `manuscript/chNN_<slug>.md` inside the budget; copy outputs from real runs.
4. `python tools/check_book.py --chapter NN` must print no errors.
5. Self-score against §4; fix anything below full marks before handing off.

## 7. Environment notes (Windows, Git Bash)

- Always use `.venv/Scripts/python`. When running a numpy/pandas/torch file directly, prefix
  `OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4` (this 24-core machine fails OpenBLAS init otherwise;
  `run_all.py` and the pytest conftest already set it).
- Several chapter authors work in parallel: touch only your own `chapters/chNN_<slug>/` folder and
  `manuscript/chNN_<slug>.md`, run only your chapter's commands, never edit `tools/`, `docs/`,
  `chapters/conftest.py` or another chapter, and never commit.
- Scratch/helper scripts (stub generators etc.) must live in a per-chapter name such as
  `<scratchpad>/chNN_mkstubs.py` — never a generic name: parallel authors share the scratchpad and a
  collision once overwrote another chapter's stubs.
