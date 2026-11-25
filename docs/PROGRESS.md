# Build progress (orchestrator log)

Status per chapter: `todo` → `writing` → `review` → `fixing` → `PASS (score)`.
Agent names: writer `wNN`, reviewer `rNN` (re-review by messaging the same reviewer).
Concurrency cap: ~6 agents (hit the 5-hour usage limit at ~11).

| Ch | Status | Notes |
|---|---|---|
| 02 | PASS 9.85 | r02 v1 9.0 → v2 9.85 |
| 03 | PASS 9.7 | v1 9.0 → v2 9.7; ch48 tie rule fixed by orchestrator |
| 04 | PASS 9.9 | |
| 06 | PASS 9.85 | 12.0 pages |
| 08 | PASS 9.75 | v1 9.3 → v2 9.75 |
| 10 | PASS 9.6 | 11.0 pages |
| 12 | PASS 9.8 | + to_rpn malformed-input fix |
| 13 | PASS 9.7 | final polish |
| 14 | PASS 9.75 | v1 8.35 (TODO outputs, recursion limits) → v2 9.75 |
| 15 | PASS 9.8 | v1 9.0 (2 tech errors) → v2 9.8 |
| 17 | PASS 9.8 | v1 9.0 (complexity claim) → v2 9.8 |
| 19 | PASS 9.8 | v1 9.4 → v2 9.8 (+2 small fixes by orchestrator) |
| 21 | PASS 9.9 | v1 9.0 (RK bound, period def, Fermat) → v2 9.9 |
| 22 | PASS 9.85 | v1 9.0 → v2 9.3 (flaky ex06) → v3 9.85 |
| 24 | PASS 9.8 | v1 9.0 → v2 9.8 (last IntEnum sentence fixed by orchestrator) |
| 25 | PASS 9.9 | v1 9.0 (class-decorator claim) → v2 9.9 |
| 27 | PASS 9.9 | v1 9.0 → v2 9.9 (+ lock assert tightened by orchestrator) |
| 28 | PASS 9.8 | v1 9.0 → v2 9.8 (+2 table/wording fixes by orchestrator) |
| 30 | PASS 9.8 | v1 9.0 → v2 9.8 (+ SUM-trap row by orchestrator) |
| 32 | PASS 9.7 | v1 8.65 → v2 9.7 (+4 final fixes) |
| 34 | fixing | r34 v1 9.0 (NaN != claim, "M" alias version) |
| 35 | fixing | r35 v1 9.4 (feature eng. gap, NDCG variants, test gaps) |
| 37 | writing | w37 (session 2) |
| 39 | writing | w39 (session 2) |
| 40 | writing | w40 (session 2) |

Queue (new chapters): 43 44 46 47
Queue (ch45 bank code): A 001–024 · B 025–048 · C 057–078 · D 079–098 · E 099–120 · F 121–150 · G lab01–30 · then ch45 manuscript
Queue (complete existing chapters + manuscript): 01 05 07 09 11 16 18 20 23 26 29 31 33 36 38 41 42 48
Last: front matter + appendices A–H, full-book check, BOOK.md build.

Recurring reviewer catches (put in every writer brief): overstated CPython claims; untested timing numbers;
ladder rungs w/o complexity; listings that don't run standalone (missing imports/helpers); wrong § cross-refs;
over budget.

Cross-chapter TODOs:
- (done) ch48 ex02 sorts attempts by date only (stable), matching ch03 ex05.
