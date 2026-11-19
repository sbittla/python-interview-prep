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
| 14 | writing | resumed |
| 15 | writing | resumed |
| 17 | writing | resumed |
| 19 | writing | resumed |
| 21 | writing | resumed |
| 22 | writing | resumed |

Queue (new chapters): 24 25 27 28 30 32 34 35 37 39 40 43 44 46 47
Queue (ch45 bank code): A 001–024 · B 025–048 · C 057–078 · D 079–098 · E 099–120 · F 121–150 · G lab01–30 · then ch45 manuscript
Queue (complete existing chapters + manuscript): 01 05 07 09 11 16 18 20 23 26 29 31 33 36 38 41 42 48
Last: front matter + appendices A–H, full-book check, BOOK.md build.

Recurring reviewer catches (put in every writer brief): overstated CPython claims; untested timing numbers;
ladder rungs w/o complexity; listings that don't run standalone (missing imports/helpers); wrong § cross-refs;
over budget.

Cross-chapter TODOs:
- (done) ch48 ex02 sorts attempts by date only (stable), matching ch03 ex05.
