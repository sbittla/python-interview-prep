# Chapter 15 — Heaps and Top-K (code)

Manuscript: `manuscript/ch15_heaps_top_k.md`. Standard library only.

| Id | Title | Tier | Pattern | Section |
|---|---|---|---|---|
| ex01 | Array-backed min-heap from scratch (sift up/down, O(n) heapify, swap counts) | ★ | binary heap in a list | 15.1 |
| ex02 | K-th largest in a stream (sort vs insort vs size-k heap) | ★ | size-k min-heap | 15.3 |
| ex03 | Top-K frequent words, ties alphabetical (sort, nsmallest, size-k heap, bucket) | ★ | Counter + heap, reversed-order wrapper | 15.2, 15.4 |
| ex04 | Merge K sorted iterators lazily (key, stable ties, infinite inputs) | ★ | k-way merge heap | 15.2, 15.6 |
| ex05 | Streaming median with two heaps | ★ | two heaps | 15.7 |
| ex06 | K closest points to a target, deterministic ties | ★ | size-k max-heap via negation | 15.9 |
| ex07 | Minimum meeting rooms + lowest-free-room assignment | ★ | heap of end times | 15.8 |
| ex08 | Smallest range covering K sorted lists | ◆ | k-way merge heap + running max | 15.6 |
| ex09 | Single-CPU shortest-job-first scheduler | ★ | arrival queue + ready heap | 15.8 |
| ex10 | Top-K largest: sort vs heap vs quickselect | ◆ | partition-based selection | 15.5 |

Every solution implements each approach-ladder rung; every test file cross-checks all rungs
against a sort-based reference on seeded random, tie-heavy inputs.

Related exercises elsewhere (not repeated here): `heapq` API → Ch 6 ex04; heap gotchas
(min-only, tuple tie-breaks) → Ch 7 ex14; heap sort → Ch 11 ex08; quickselect for the k-th
element → Ch 11 ex13; top-K frequent integers with bucket sort → Ch 9 ex04; cooldown task
scheduler → Ch 20 ex07; merge k linked lists → Ch 13 ex06.

## Run

```bash
.venv/Scripts/python chapters/ch15_heaps_top_k/solutions/ex05_streaming_median.py   # one demo
.venv/Scripts/python tools/run_all.py --chapter 15                                  # all demos -> outputs/
.venv/Scripts/python -m pytest chapters/ch15_heaps_top_k                            # tests vs solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch15_heaps_top_k           # tests vs your stubs
```
