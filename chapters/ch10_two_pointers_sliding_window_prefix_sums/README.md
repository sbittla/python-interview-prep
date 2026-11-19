# Chapter 10 — Two Pointers, Sliding Window and Prefix Sums

Manuscript: `manuscript/ch10_two_pointers_sliding_window_prefix_sums.md`

Every solution implements each rung of its approach ladder (brute force → improved → optimal) plus
at least one *wrong-but-tempting* variant, and every test file cross-checks the rungs against each
other on seeded random inputs.

| # | File | Title | Tier | Section | Pattern |
|---|---|---|---|---|---|
| 01 | `ex01_three_sum.py` | Three sum to zero (unique triplets) | ★ Core | 10.1 | sort + opposite-direction pointers |
| 02 | `ex02_container_most_water.py` | Container with most water | ★ Core | 10.1 | opposite pointers, discard the short wall |
| 03 | `ex03_remove_duplicates_in_place.py` | Keep at most k copies, in place | ★ Core | 10.2 | read/write pointers |
| 04 | `ex04_dutch_flag_partition.py` | Three-way partition (Dutch flag) | ◆ Extended | 10.2 | three regions, one pass |
| 05 | `ex05_find_duplicate_floyd.py` | Find the duplicate; happy numbers | ◆ Extended | 10.3 | fast/slow pointers (Floyd) |
| 06 | `ex06_max_average_window.py` | Best fixed-size window; window maxima | ★ Core | 10.4, 10.7 | fixed window; deque bridge (→ Ch 12.6) |
| 07 | `ex07_longest_unique_substring.py` | Longest substring without repeats | ★ Core | 10.5 | variable window (longest) |
| 08 | `ex08_permutation_in_string.py` | Permutation in string / anagram windows | ★ Core | 10.6 | fixed window + counts |
| 09 | `ex09_min_window_substring.py` | Minimum window containing all of t | ◆ Extended | 10.5, 10.6 | variable window (shortest) + counts |
| 10 | `ex10_subarray_sum_k.py` | Count subarrays summing to k | ★ Core | 10.9 | prefix sum + hash map |
| 11 | `ex11_range_sum_2d.py` | Range-sum queries in 1D and 2D | ★ Core | 10.8 | prefix sums, inclusion-exclusion |
| 12 | `ex12_range_update_difference.py` | Batch range updates; peak load | ◆ Extended | 10.10 | difference array |

## How to run

```bash
.venv/Scripts/python chapters/ch10_two_pointers_sliding_window_prefix_sums/solutions/ex10_subarray_sum_k.py
.venv/Scripts/python -m pytest chapters/ch10_two_pointers_sliding_window_prefix_sums          # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch10_two_pointers_sliding_window_prefix_sums   # your stubs
.venv/Scripts/python tools/run_all.py --chapter 10                                            # regenerate outputs/
```

Stubs in `exercises/` keep the same signatures and `main()`; implement the bodies that raise
`NotImplementedError`. The `wrong_*` functions are left implemented on purpose: run them to see
how they fail.
