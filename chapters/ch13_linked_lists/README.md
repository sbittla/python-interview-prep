# Chapter 13 — Linked Lists (code)

Manuscript: `manuscript/ch13_linked_lists.md`. Standard library only.

| Id | Title | Tier | Pattern | Section |
|---|---|---|---|---|
| ex01 | Linked-list toolkit: length, insert/delete at index, reverse (iterative + recursive) | ★ | pointer walking, dummy head | 13.1–13.3 |
| ex02 | Delete every node holding a value | ★ | dummy head | 13.2 |
| ex03 | Middle node and palindrome list (restore the list) | ★ | fast/slow + in-place reversal | 13.4, 13.6 |
| ex04 | Where does the cycle begin? (Floyd phase 2, cycle length) | ★ | fast/slow pointers | 13.4 |
| ex05 | Intersection of two lists | ★ | two pointers, length alignment | 13.6 |
| ex06 | Merge k sorted lists (one-by-one, divide & conquer, heap) | ★ | dummy tail + `heapq` | 13.5 |
| ex07 | Odd-even regroup | ★ | two running tails | 13.9 |
| ex08 | Partition a list around x (stable) | ★ | two dummy heads | 13.9 |
| ex09 | Rotate a list right by k | ★ | length, ring, cut | 13.9 |
| ex10 | Swap adjacent pairs | ◆ | dummy head + local reversal | 13.3 |
| ex11 | Doubly linked list with a sentinel (used by the LRU cache in Ch 29) | ★ | circular sentinel, O(1) unlink | 13.7 |

Shared helper: `solutions/listnode.py` (copy in `exercises/`) defines `ListNode`, `build`,
`to_list` (raises `ValueError` past a node limit, so an accidental cycle fails fast), `render`
and `nodes`. Every exercise imports it.

Classic problems already in the problem bank (not repeated here):
`chapters/ch45_problem_bank/solutions/ex049_reverse_linked_list.py` …
`ex056_reverse_k_group.py` — reverse, merge two sorted, cycle detection and entry, remove nth from end,
reorder, add two numbers, copy list with random pointer, reverse in k-groups.

## Run

```bash
.venv/Scripts/python chapters/ch13_linked_lists/solutions/ex04_cycle_start.py   # one demo
.venv/Scripts/python tools/run_all.py --chapter 13                               # all demos -> outputs/
.venv/Scripts/python -m pytest chapters/ch13_linked_lists                        # tests vs solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch13_linked_lists       # tests vs your stubs
```
