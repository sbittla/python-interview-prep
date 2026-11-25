# Chapter 22 — Full Complexity Analysis (code)

Manuscript: `manuscript/ch22_complexity_analysis.md`. The Big-O basics (notation, built-in costs,
constraints table) are in Chapter 8; this chapter proves bounds instead of quoting them.

Every exercise checks a complexity claim by **counting** (recurrence values, copies, pointer hops,
recursion-tree nodes, tree cells touched). The only timing is in ex06, and it prints booleans and
function names, never seconds, so every output file is deterministic.

| # | File | Title | Tier | Pattern | Section |
|---|---|---|---|---|---|
| 01 | `ex01_master_theorem.py` | Master-theorem solver with numeric check | ★ Core | divide-and-conquer recurrence | §22.2 |
| 02 | `ex02_dynamic_array.py` | Amortised dynamic array with cost accounting | ★ Core | aggregate + accounting method | §22.3 |
| 03 | `ex03_union_find_costs.py` | Union-find cost counter | ◆ Extended | amortised analysis, α(n) | §22.3 |
| 04 | `ex04_recursion_tree_counter.py` | Recursion-tree node counter | ★ Core | nodes × work per node | §22.4 |
| 05 | `ex05_fenwick_segment_tree.py` | Fenwick tree and segment tree, cross-checked | ○ Reference | range query + point update | §22.9 |
| 06 | `ex06_profile_hotspot.py` | Find the hotspot with cProfile and timeit | ◆ Extended | measure before optimising | §22.8 |

## How to run

```bash
.venv/Scripts/python chapters/ch22_complexity_analysis/solutions/ex01_master_theorem.py   # one solution
.venv/Scripts/python tools/run_all.py --chapter 22                                        # regenerate outputs/
.venv/Scripts/python -m pytest chapters/ch22_complexity_analysis                          # test solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch22_complexity_analysis         # test your stubs
```
