# Chapter 19 — Dynamic Programming

Manuscript: `manuscript/ch19_dynamic_programming.md`. Standard library only.

| # | Exercise | Tier | Pattern | Rungs implemented | Section |
|---|---|---|---|---|---|
| 01 | [Climbing stairs variants and decode ways](solutions/ex01_stairs_decode_ways.py) | ★ | 1D DP, counting | recursion → memo → table → rolling window | 19.2–19.4 |
| 02 | [House robber: line and circle](solutions/ex02_house_robber.py) | ★ | 1D take/skip | recursion → memo → table (+ houses) → two variables; circle = two lines | 19.4 |
| 03 | [Grid paths with rocks; minimum path sum](solutions/ex03_grid_paths.py) | ★ | 2D grid DP | recursion → memo → table (+ path) → rolling row | 19.5, 19.15 |
| 04 | [0/1 knapsack, unbounded knapsack, coin change](solutions/ex04_knapsack_coin_change.py) | ★ | knapsack over capacity | recursion → memo → table (+ items) → one row; greedy counter-example; combinations vs permutations | 19.6 |
| 05 | [Longest increasing subsequence with reconstruction](solutions/ex05_lis.py) | ★ | subsequence DP | recursion → memo → O(n²) table → patience sorting O(n log n) | 19.7 |
| 06 | [LCS and edit distance with reconstruction](solutions/ex06_lcs_edit_distance.py) | ★ | two-sequence table | recursion → memo → table (+ script) → two rows | 19.7, 19.8 |
| 07 | [Word break; palindromic substrings and subsequence](solutions/ex07_word_break_palindromes.py) | ★ | prefix DP, interval-on-string | recursion → memo → table → centre expansion / two rows | 19.9 |
| 08 | [Burst balloons](solutions/ex08_burst_balloons.py) | ◆ | interval DP ("last action") | orders O(n!) → subset memo → interval memo → by-length table | 19.10 |
| 09 | [Stock trading with cooldown](solutions/ex09_stock_cooldown.py) | ◆ | state machine DP | recursion → memo → table → three variables | 19.11 |
| 10 | [House robber on a tree](solutions/ex10_house_robber_tree.py) | ◆ | tree DP, (take, skip) pair | recursion → dict memo → pair recursion → iterative reverse-BFS | 19.12 |
| 11 | [Shortest round trip (TSP-lite)](solutions/ex11_tsp_bitmask.py) | ◆ | bitmask DP over subsets | permutations → memo f(mask, last) → table + tour | 19.13 |
| 12 | [Numbers without equal adjacent digits](solutions/ex12_digit_dp.py) | ○ | digit DP | loop over x → digit recursion → memo (pos, prev, tight, started) → closed-form walk | 19.14 |

Every solution checks its rungs against each other in `main()`; every test file compares the
fast rung with the brute force on seeded random inputs and covers empty/degenerate inputs.

## How to run

```bash
.venv/Scripts/python chapters/ch19_dynamic_programming/solutions/ex04_knapsack_coin_change.py
.venv/Scripts/python -m pytest chapters/ch19_dynamic_programming            # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch19_dynamic_programming  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 19                           # regenerate outputs/
```

Work in `exercises/` (stubs raise `NotImplementedError` and carry hints instead of the full
approach ladder); compare with `solutions/`; expected program output is in `outputs/`.
More DP practice: Chapter 45 problem bank, numbers 107–120.
