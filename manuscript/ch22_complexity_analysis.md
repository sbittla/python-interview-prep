# Chapter 22. Full Complexity Analysis

◆ Extended · Tracks S M L · Study time ≈ 4 h · Prerequisites: Chapter 8, §18.1, §19.3

**Learning objectives**

- Solve recurrences with a recursion tree and the Master Theorem; prove amortised bounds.
- Cost recursion as nodes × work, DP as states × transitions.
- Find a hotspot with `cProfile`; confirm the fix with `timeit`.

> **Recognise it.** "Prove that bound"; "is append really O(1)?"; "why O(n·2ⁿ)?"; "where is the
> time going?".

## 22.1 Recap of the Big-O primer

Chapter 8 covers notation, loop counting, stack space, built-in costs (→ §8.6) and constraints
(→ §8.7). Here we derive bounds that loops hide.

## 22.2 Recurrence relations and the Master Theorem

An algorithm making a calls on size n/b plus f(n) = n^c·logᵏ n work satisfies T(n) = a·T(n/b) + f(n).
**Ladder:** (1) unroll by hand: slow, error-prone; (2) **recursion tree**: level i has aⁱ nodes of size
n/bⁱ, costing aⁱ·f(n/bⁱ); (3) **Master Theorem**: compare c with the critical exponent e = log_b a
(there are n^e leaves). Rung 3 is O(1) to apply; rung 2 explains why it works.

| Case | Condition | Level costs | T(n) | Example |
|---|---|---|---|---|
| 1 | c < e | grow toward the leaves | Θ(n^e) | Karatsuba 3T(n/2)+n → Θ(n^1.585) |
| 2 | c = e, k ≥ 0 | equal on all log_b n levels | Θ(n^e·log^(k+1) n) | merge sort → Θ(n log n) |
| 3 | c > e | shrink toward the leaves | Θ(n^c·logᵏ n) | 2T(n/2)+n² → Θ(n²) |

Case 3 also needs regularity (a·f(n/b) ≤ δ·f(n), δ < 1), which f = n^c·logᵏ n with c > e always meets.

```python
import math


def master(a: int, b: int, c: float, k: int = 0) -> str:
    """Tight bound of T(n) = a*T(n/b) + n^c * log^k n."""
    e = math.log(a, b)                          # critical exponent: n^e leaves
    if math.isclose(c, e, abs_tol=1e-9):
        return f"case 2: n^{e:.3g} log^{k + 1} n"   # every level costs the same
    if c < e:
        return f"case 1: n^{e:.3g}"                  # leaves dominate
    return f"case 3: n^{c:g}" + (f" log^{k} n" if k else "")  # root dominates


for a, b, c in [(1, 2, 0), (2, 2, 1), (3, 2, 1), (2, 2, 2)]:
    print(f"T(n) = {a}T(n/{b}) + n^{c}  ->  {master(a, b, c)}")
```

```text
T(n) = 1T(n/2) + n^0  ->  case 2: n^0 log^1 n
T(n) = 2T(n/2) + n^1  ->  case 2: n^1 log^1 n
T(n) = 3T(n/2) + n^1  ->  case 1: n^1.58
T(n) = 2T(n/2) + n^2  ->  case 3: n^2
```

Rows: binary search (n⁰·log n), merge sort, Karatsuba, root-heavy.

Exercise 01 checks the theorem numerically: T(n)/g(n) must vary under 1.3× over n = 2⁸…2¹⁶.
Tightness matters: merge sort claimed as n drifts only 1.89×, Karatsuba as n log n 13.14×.
If n is not a power of b, floors and ceilings keep the same Θ.
→ repo: `chapters/ch22_complexity_analysis/solutions/ex01_master_theorem.py`.

**Wrong-but-tempting.** T(n) = T(n−1) + n subtracts, so it is not Master form: Θ(n²) (quicksort's
worst case). Uneven splits, T(n/3) + T(2n/3) + n, need the tree: ≤ n per level, O(log n) levels.

## 22.3 Amortised analysis (dynamic arrays, union-find)

Amortised cost = worst-case total cost of a sequence ÷ its length: a guarantee, not a
random-input average. Three proofs for a doubling array:

- **Aggregate**: n appends copy 1 + 2 + 4 + … < 2n elements.
- **Accounting**: charge 3 credits per append (the write, its own future copy, one older element's
  copy); the bank never goes negative.
- **Potential**: Φ = 2·size − capacity; actual cost + ΔΦ = 3 per append, resize or not.

Growth-policy ladder: +1 slot (n²/2 copies) → +k slots (≈ n²/2k: a bigger constant never fixes
quadratic) → ×2 (< 2n copies; amortised O(1), worst single append O(n)):

```python
def copies_for(n: int, grow) -> int:
    """Element copies caused by resizing during n appends (start capacity 1)."""
    cap, size, copies = 1, 0, 0
    for _ in range(n):
        if size == cap:                 # full: allocate grow(cap) slots, copy all
            copies += size
            cap = grow(cap)
        size += 1
    return copies


for n in (1_000, 2_000, 4_000):
    print(f"n={n}: doubling {copies_for(n, lambda c: 2 * c):>5}   "
          f"+10 slots {copies_for(n, lambda c: c + 10):>7}")
```

```text
n=1000: doubling  1023   +10 slots   49600
n=2000: doubling  2047   +10 slots  199200
n=4000: doubling  4095   +10 slots  798400
```

→ repo: `chapters/ch22_complexity_analysis/solutions/ex02_dynamic_array.py`.
Any factor > 1 works; CPython's list over-allocates by about 1/8 plus a small constant. Over 10⁵
appends, charge 2 bottoms out at −65534, charge 3 at 0. Shrink at ¼ full, not ½, or push/pop at the
boundary resizes every time.

**Union-find** (→ §16.9). Chain n unions, then find every node: at n = 4000 naive linking takes
7,998,000 hops (n(n−1)/2); compression, rank, or both take under 8,000. Rank bounds height by log₂ n;
compression alone gives O(log n) amortised; both give O(α(n)) amortised, α(n) ≤ 4 in practice:
effectively, not literally, O(1). One find can still cost O(log n); the bound is on the total. Link
by rank or size so α(n) applies.
→ repo: `chapters/ch22_complexity_analysis/solutions/ex03_union_find_costs.py`.

## 22.4 Complexity of recursion and backtracking trees

Time = nodes × work per node + leaves × leaf work. Space = depth + current path. Ladder:
(1) "two calls, so 2ⁿ": right for subsets' node count, loose for Fibonacci (Θ(φⁿ)), wrong for
permutations, because branching is not constant; (2) count nodes per level (permutations: n!/(n−k)!
at level k), which gives nodes but not time; (3) add the per-node loop and the O(n) copy at each leaf.

| Recursion | Nodes (calls) | Total time | Extra space |
|---|---|---|---|
| Subsets (include/exclude) | 2ⁿ⁺¹ − 1; copies n·2ⁿ⁻¹ | Θ(n·2ⁿ) | O(n) |
| Permutations (`used` array) | Σₖ n!/(n−k)! = ⌊e·n!⌋ | Θ(n·n!) | O(n) |
| Naive Fibonacci | 2F(n+1) − 1, F = Fibonacci | Θ(φⁿ), φ ≈ 1.618 | O(n) depth |
| Memoised Fibonacci | 2n − 1 | Θ(n) | O(n) |
| Word search, word length L | m·n starts × ≤ 4·3^(L−1) paths | O(m·n·3^L) | O(L) |

Pruning (→ §18.8) cuts subtrees but rarely the worst case: quote an upper bound. The first four rows
are counted by → repo: `chapters/ch22_complexity_analysis/solutions/ex04_recursion_tree_counter.py`.

## 22.5 DP complexity: states × transitions

Ladder: (1) count the distinct states; (2) multiply by the transition loop inside each. Space =
states stored, often reducible (→ §19.15).

| Problem | States | Transition | Time | Space after rolling |
|---|---|---|---|---|
| LCS / edit distance | m·n | O(1) | O(m·n) | O(min(m, n)) |
| LIS, quadratic DP | n | O(n) | O(n²) | O(n) |
| 0/1 knapsack, capacity W | n·W | O(1) | O(n·W) | O(W) |
| Bitmask TSP | 2ⁿ·n | O(n) | O(n²·2ⁿ) | O(n·2ⁿ) |

O(n·W) is **pseudo-polynomial**: polynomial in the value W, exponential in its bit length.
**Wrong-but-tempting:** "memoised LIS makes n calls, so O(n)": each call loops over O(n) transitions.
Slice or tuple memo keys of length k add O(k) per lookup.

## 22.6 Space trade-offs and in-place algorithms

| Trade | Time | Extra space |
|---|---|---|
| Duplicates: hash set vs sort, then scan | O(n) vs O(n log n) | O(n) vs O(1) (heapsort; Timsort ≤ n/2) |
| Range sums: rescan vs prefix array | O(n) vs O(1) per query | O(1) vs O(n) |
| Merge sort vs heapsort | both O(n log n) | O(n) vs O(1) |
| Quicksort, recurse on smaller side | O(n log n) expected | O(log n) stack |

"In place" means O(1) (sometimes O(log n)) extra memory. Ask whether input mutation is allowed and
whether output counts.

## 22.7 Python-specific costs: hidden O(n) operations

Cheat table: §8.6; traps: §7.15–§7.18. Lines that turn an O(n) loop into O(n²):

| Innocent line | Cost | Fix |
|---|---|---|
| `x in lst`, `lst.index(x)` | O(n) | set or dict |
| `lst.pop(0)`, `lst.insert(0, x)` | O(n) | `deque` |
| `xs[1:]` in recursion | O(n) per call | pass an index |
| `s += ch` building a string | O(n²) worst | `"".join(parts)` |

## 22.8 Profiling and timing (`timeit`, `cProfile`)

Counting proves the class; profiling shows where *this* run spends time. Ladder: guess (usually
wrong) → `timeit` the program (says *that*, not *where*) → `cProfile` by own time (`tottime`), fix
that function, re-time.

```python
import cProfile
import pstats


def hottest(func, *args) -> str:
    """Name of the Python function with the largest own time (tottime)."""
    profiler = cProfile.Profile()
    profiler.runcall(func, *args)
    stats = pstats.Stats(profiler).stats   # {(file, line, name): (cc, nc, tt, ct, callers)}
    own = [(tt, name) for (file, _, name), (_, _, tt, _, _) in stats.items()
           if file != "~" and not name.startswith("<")]  # no built-ins, <genexpr>, <lambda>
    return max(own)[1]


def dedupe(items):
    seen = []
    for x in items:
        if x not in seen:               # O(len(seen)) scan hides here
            seen.append(x)
    return seen


def pipeline(n):
    return len(dedupe([i % (n // 2) for i in range(n)]))


print("hottest:", hottest(pipeline, 3000))
```

```text
hottest: dedupe
```

`x in seen` is an operator, not a call, so cProfile charges it to `dedupe` itself. With
`timeit.repeat`, compare the **minimum** of several runs (noise only adds time). cProfile's per-call
overhead exaggerates many tiny calls; memory needs `tracemalloc` (→ §27.9).
→ repo: `chapters/ch22_complexity_analysis/solutions/ex06_profile_hotspot.py`.

## 22.9 Segment trees and Fenwick trees (overview)

Mixed point updates and range queries: a list is O(1) update, O(n) query; a prefix array the
reverse. A **Fenwick tree** (n + 1 cells) does both in O(log n) but needs an invertible
operation (sum, xor). A **segment tree** (2n cells, iterative) handles min, max, gcd. At n = 256 a
query touches at most 15 Fenwick or 14 segment cells (2·log₂ n = 16).
→ repo: `chapters/ch22_complexity_analysis/solutions/ex05_fenwick_segment_tree.py`.

## Interviewer's view

- Rewarded: the recurrence before its solution; *amortised* vs *average*; output copying;
  measuring before optimising.
- Penalised: "two calls, so 2ⁿ" unchecked; unqualified "O(1)" for α(n) or hashing; one noisy timing.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Master-theorem solver with numeric check | ★ | recurrences |
| 02 | Amortised dynamic array with cost accounting | ★ | aggregate + accounting |
| 03 | Union-find cost counter | ◆ | amortised α(n) |
| 04 | Recursion-tree node counter | ★ | nodes × work per node |
| 05 | Fenwick tree and segment tree, cross-checked | ○ | range queries |
| 06 | Find the hotspot with cProfile and timeit | ◆ | profiling |

Index: `chapters/ch22_complexity_analysis/README.md`.

## Checkpoint quiz

1. Solve T(n) = 4T(n/2) + n².
2. Why does growing a list by 1,000 slots still cost O(n²) copying?
3. Generate and store all permutations of n items: time?
4. Coin change, amount A, k coin types: time? Polynomial?
5. Why can `dedupe` top `tottime` while calling nothing expensive?

<details><summary>Answers</summary>

1. e = log₂4 = 2 = c: case 2, Θ(n² log n).
2. n/1000 resizes copy 1000 + 2000 + … ≈ n²/2000 elements.
3. Θ(n·n!): ≈ e·n! nodes; each of n! leaves copies n items.
4. O(A·k); pseudo-polynomial, since A is a value, not an input length.
5. The list scan runs inside `dedupe`'s own bytecode; no separate function shows up to absorb it.
</details>

## Summary card

- T(n) = aT(n/b) + n^c logᵏ n: compare c with e = log_b a. Less → n^e; equal → n^e log^(k+1) n;
  more → f(n). Subtracting or uneven splits: draw the tree.
- Amortised = worst-case total ÷ operations. Doubling < 2n copies; constant growth Θ(n²).
- Union-find: rank → log n height; both optimisations → O(α(n)) amortised.
- Recursion: subsets Θ(n·2ⁿ), permutations Θ(n·n!), naive fib Θ(φⁿ). DP: states × transitions.
  Profile by `tottime`; confirm with `timeit` minima.
