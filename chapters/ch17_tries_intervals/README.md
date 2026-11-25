# Chapter 17 — Tries and Intervals (code)

Manuscript: `manuscript/ch17_tries_intervals.md`. Standard library only.

| Id | Title | Tier | Pattern | Section |
|---|---|---|---|---|
| ex01 | Trie: insert, search, starts_with, delete with pruning (+ 26-slot array trie) | ★ | trie | 17.1 |
| ex02 | Word dictionary with `.` wildcards | ★ | trie + DFS over branches | 17.2 |
| ex03 | Prefix counting and top-3 suggestions (sort + bisect vs trie) | ★ | trie with per-node aggregates | 17.3 |
| ex04 | Word Search II: many words, one grid | ◆ | trie + grid backtracking, prune found words | 17.4 |
| ex05 | Merge intervals (closed; touching endpoints switch) | ★ | sort by start, extend last | 17.5, 17.6 |
| ex06 | Insert an interval into a sorted disjoint list | ★ | three-phase linear scan | 17.6 |
| ex07 | Intersection of two interval lists | ★ | two pointers | 17.7 |
| ex08 | Minimum removals for non-overlapping intervals (half-open vs closed) | ★ | sort by end, greedy keep | 17.7 |
| ex09 | Meeting rooms: brute / heap / two pointers / line sweep, busiest time, room assignment | ★ | min-heap; +1/−1 events, end-before-start ties | 17.8, 17.9 |
| ex10 | The skyline | ◆ | sweep + max-heap with lazy deletion | 17.9 |

Every solution implements each rung of its approach ladder (`brute_force`, intermediate rungs,
`solve`), and every test file cross-checks the rungs on seeded random inputs that are dense in
touching endpoints and duplicates.

Related exercises elsewhere (not repeated here):
- Single-word grid search: `chapters/ch18_backtracking/solutions/ex10_word_search.py` (ex04 builds on it).
- Greedy proofs (activity selection, min arrows, rooms as a greedy warm-up):
  `chapters/ch20_greedy/solutions/ex01_activity_selection.py`, `chapters/ch20_greedy/solutions/ex10_min_arrows.py`.
- Autocomplete as a *service* (ranking, caching, updates) is Chapter 29; here only the trie mechanics.

## Run

```bash
.venv/Scripts/python chapters/ch17_tries_intervals/solutions/ex09_meeting_rooms.py   # one demo
.venv/Scripts/python tools/run_all.py --chapter 17                                   # all demos -> outputs/
.venv/Scripts/python -m pytest chapters/ch17_tries_intervals                         # tests vs solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch17_tries_intervals        # tests vs your stubs
```
