# Chapter 12 — Stacks, Queues and Monotonic Structures

Manuscript: `manuscript/ch12_stacks_queues_monotonic.md`. Standard library only.

| # | Exercise | Tier | Pattern | Rungs implemented | Section |
|---|---|---|---|---|---|
| 01 | [Balanced brackets with error position](solutions/ex01_balanced_brackets.py) | ★ | stack matching | pair-deletion brute → index stack | 12.2 |
| 02 | [RPN evaluation and basic calculator](solutions/ex02_expression_evaluation.py) | ★ | operand / operator stacks | shunting-yard + RPN → one-pass term stack | 12.2 |
| 03 | [Min stack in O(1)](solutions/ex03_min_stack.py) | ★ | augmented stack | scan → two stacks → (value, min) pairs | 12.3 |
| 04 | [Next greater / smaller element (incl. circular)](solutions/ex04_next_greater_element.py) | ★ | monotonic stack | O(n²) scan → monotonic stack, 2n lap | 12.4 |
| 05 | [Online stock span](solutions/ex05_stock_span.py) | ★ | monotonic stack, merged counts | walk back → (price, span) stack | 12.4 |
| 06 | [Days until warmer](solutions/ex06_daily_temperatures.py) | ★ | monotonic stack (distance) | O(n²) → jump-back → stack (+ trace) | 12.4 |
| 07 | [Largest rectangle in histogram](solutions/ex07_largest_rectangle.py) | ★ | previous/next smaller | O(n²) → boundary arrays → one-pass stack | 12.5 |
| 08 | [Trapping rain water](solutions/ex08_trapping_rain_water.py) | ★ | prefix max → two pointers / stack | O(n²) → prefix max → two pointers, stack | 12.5 |
| 09 | [Sliding window maximum](solutions/ex09_sliding_window_max.py) | ★ | monotonic deque | O(nk) → lazy heap → deque (+ trace) | 12.6 |
| 10 | [Queue via two stacks; stack via a queue](solutions/ex10_queue_via_stacks.py) | ★ | amortised analysis | `pop(0)` → lazy two stacks; rotate-on-push | 12.7 |
| 11 | [Fixed-capacity circular queue](solutions/ex11_circular_queue.py) | ◆ | ring buffer | list + `pop(0)` → head + size ring | 12.8 |

Every solution cross-checks its optimal rung against the slower rungs in `main()`, and every test
file compares them on seeded random inputs.

## How to run

```bash
.venv/Scripts/python chapters/ch12_stacks_queues_monotonic/solutions/ex09_sliding_window_max.py
.venv/Scripts/python -m pytest chapters/ch12_stacks_queues_monotonic            # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch12_stacks_queues_monotonic  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 12                               # regenerate outputs/
```

Work in `exercises/` (stubs raise `NotImplementedError` and carry hints instead of the full
approach ladder); compare with `solutions/`; expected program output is in `outputs/`.
