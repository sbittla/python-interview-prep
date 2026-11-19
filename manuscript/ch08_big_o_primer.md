# Chapter 8. Big-O Primer

★ Core · Tracks S M L · Study time ≈ 3 h · Prerequisites: Chapters 5–6 (loops, built-in collections)

**Learning objectives**

- State time and space complexity of a loop-and-recursion snippet in under a minute.
- Turn a constraints line ("n ≤ 2·10⁵") into the slowest acceptable algorithm.
- Quote built-in operation costs and spot hidden O(n) lines.

> **Recognise it.** Triggers: a constraints line; "what is the complexity?"; "can you do better?";
> a time-out. Full theory: Chapter 22 (→ §22.2–§22.8).

## 8.1 Why complexity matters in interviews

Interviewers score three behaviours: you **state** time and space unprompted, you **compare**
approaches before coding ("brute force is O(n²); a hash map gets O(n)"), and you **choose** by the
constraints. A correct O(n²) answer when n = 10⁵ is usually graded incomplete.

## 8.2 Big-O, Big-Θ, Big-Ω in plain language

| Notation | Plain meaning | Example |
|---|---|---|
| O(g) | grows **no faster** than g (upper bound) | linear search is O(n) |
| Ω(g) | grows **at least** as fast as g (lower bound) | any comparison sort is Ω(n log n) in the worst case |
| Θ(g) | both: grows **exactly like** g, up to constants | summing a list is Θ(n) |

Interviewers say "Big-O" but mean the **tight** bound (linear search is O(n²), uselessly). Bounds are separate from *cases*: linear search is Θ(1) in its best case, Θ(n) in its worst.
Quote the worst case unless told otherwise; say "average" for hashing. Drop constants and lower-order
terms: 3n + 5 is Θ(n).

## 8.3 Counting operations: loops, nested loops, halving

Count how often the innermost step runs, as a function of n:

- **Sequential** blocks add: O(n) + O(n) = O(n). Different inputs stay separate: O(n + m).
- **Nested** loops multiply: n × n = O(n²). An inner `range(i)` gives 0+1+…+(n−1) = n(n−1)/2, still O(n²).
- **Halving or doubling** a variable gives log₂ n iterations: O(log n).
- **Geometric** work n + n/2 + n/4 + … ≤ 2n is O(n), even though it *looks* nested (snippet 7 in §8.8).
- **Branching recursion**: b calls per level, depth d → about bᵈ calls (→ §22.4).

Timings are noisy; counts are exact. Exercise 01 records counts at several n and picks the class
g(n) that keeps count/g(n) most nearly constant (in log space, so 2ⁿ and n! never overflow).
Excerpt (`CLASSES` maps each label to ln g(n); `_validate` sorts and checks the points):

```python
def fit_growth(points: dict[int, int]) -> str:
    items = _validate(points)
    best_label, best_spread = "", math.inf
    for label, ln_g in CLASSES.items():
        residuals = [math.log(c) - ln_g(n) for n, c in items]
        spread = max(residuals) - min(residuals)
        if spread < best_spread - 1e-9:          # ties keep the slower-growing (earlier-listed) class
            best_label, best_spread = label, spread
    return best_label
```

→ repo: `chapters/ch08_big_o_primer/solutions/ex01_op_counter.py`. Why this rung: eyeballing counts
does not automate, and doubling ratios blur n vs n log n; the residual spread works for any sizes.

## 8.4 Common classes: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ), O(n!)

Typical sources: hash lookup, binary search, one pass, sorting, all pairs, all subsets, all
permutations. Ex01 output (excerpt; counts at the listed n, then ratios between consecutive sizes):

```text
halving             counts=[6, 7, 8, 9, 10]
                    ratios=[1.17, 1.14, 1.12, 1.11] -> O(log n)
merge_sort_count    counts=[384, 896, 2048, 4608, 10240]
                    ratios=[2.33, 2.29, 2.25, 2.22] -> O(n log n)
all_pairs           counts=[2016, 8128, 32640, 130816]
                    ratios=[4.03, 4.02, 4.01] -> O(n^2)
subsets_count       counts=[256, 1024, 4096, 16384]
                    ratios=[4.0, 4.0, 4.0] -> O(2^n)
permutations_count  counts=[24, 120, 720, 5040]
                    ratios=[5.0, 6.0, 7.0] -> O(n!)
```

## 8.5 Space complexity and the call stack

Space complexity counts **extra** memory beyond the input: new containers *and* stack frames, since
every active recursive call holds one. Exercise 05 sums a list three ways, all O(n) time:

```text
n=0    sum=0      depth linear=1    halves=1   loop=0
n=1    sum=0      depth linear=2    halves=1   loop=0
n=8    sum=28     depth linear=9    halves=4   loop=0
n=100  sum=4950   depth linear=101  halves=8   loop=0
n=900  sum=404550 depth linear=901  halves=11  loop=0
sum_linear n=5000 raises RecursionError: True
sum_halves n=5000 raises RecursionError: False
sum_loop   n=5000 raises RecursionError: False
sum_halves depth at n=10**6: 21
```

Linear recursion uses O(n) stack and dies at CPython's default limit of 1000 frames (no tail-call
elimination, → §7.21); halving needs O(log n); the loop O(1). Pitfall: slicing `xs[1:]` per call adds
O(n) time and space per level (ex04). Space trade-offs: → §22.6.

## 8.6 Complexity of Python built-in operations (cheat table)

n = container size, k = size of the other argument or slice. "avg" assumes reasonable hashes (→ §6.5);
choosing between containers is §6.14.

| Type | O(1) | O(log n) | O(n) or more |
|---|---|---|---|
| `list` | `xs[i]`, `xs[i] = v`, `len`, `append`* , `pop()` | — | `pop(0)`, `insert(i, v)`, `remove`, `x in xs`, `index`, `min`/`max`, copy; slice O(k); `extend` O(k); `sort` O(n log n) |
| `dict` | get/set/`del`/`in`: avg O(1), **worst O(n)** | — | iteration, `x in d.values()`, copy |
| `set` | `add`/`discard`/`in`: avg O(1), **worst O(n)** | — | `s \| t` O(n+k), `s & t` O(min(n, k)), `s - t` O(n) |
| `deque` | `append`, `appendleft`, `pop`, `popleft`, `d[0]`, `d[-1]` | — | `d[i]` in the middle O(n), `x in d`, `rotate(k)` O(k) |
| `str` | `len`, `s[i]` | — | `s + t`, slice O(k), `==`, `split`, `"".join(parts)` O(total); `sub in s` O(n·k) worst, ~O(n) typical; `s += c` in a loop O(n²) worst |
| `heapq` | `h[0]` (peek min) | `heappush`, `heappop`, `heappushpop`, `heapreplace` | `heapify` O(n); `nlargest(k, it)` O(n log k) |

\* **Amortised** O(1): a rare resize copies everything, but averaged over all appends the cost is
constant (→ §22.3). Timsort is O(n) on already-sorted input. Exercise 04 counts hidden costs (excerpt):

```text
n=4000  1000 lookups: list eq-calls=2125250  set eq-calls=500
list cost doubles with n: True
drain n=2000: list shifts=1999000  deque shifts=0
deque.popleft beats list.pop(0) by >3x at n=30000: True
```

The set's 500 `==` calls confirm the 500 hits; misses cost none. More traps:
→ §7.15–§7.18, §22.7.

## 8.7 Reading constraints: input size → acceptable complexity

Read the constraints **before** designing. The classic judge rule assumes ≈10⁸ simple operations
(compiled languages; it rounds generously, 500³ = 1.25·10⁸). CPython manages roughly 10⁷ simple steps
per second, so for a 1–2 s limit use the CPython column, or lean on C-implemented built-ins
(`sorted`, `sum`, set operations):

| Slowest acceptable | Classic max n (~10⁸ ops) | CPython max n (~10⁷ steps) | Typical technique |
|---|---|---|---|
| O(n!) | 10 | 10 | all permutations |
| O(2ⁿ) (n·2ⁿ) | 20 | 18 | all subsets, bitmask DP |
| O(n³) | 500 | 200 | triple loops, interval DP |
| O(n²) | 5,000 | 3,000 | all pairs, 2-D DP |
| O(n log n) | 10⁶ | 5·10⁵ | sort, heap |
| O(n) | 10⁸ | 10⁷ | one pass, hashing, two pointers |
| O(log n), O(1) | larger | larger | formula, binary search on the answer |

Exercise 02 parses constraint text, applies both columns, and checks the CPython column against
estimated steps (excerpt):

```text
n <= 5,000                               n=5,000         classic O(n^2)     CPython O(n log n) (sort, heap, binary search per item)
  O(n^3)     n<=200        ~8.0e+06 steps  exact max n=215        within budget: True
```

With two inputs budget both: a grid is O(m·n); q queries cost preprocessing + q × per-query.

## 8.8 Quick quiz: estimate complexity of 10 snippets

Each snippet returns how often its innermost step ran. Classify each before opening the answers.

```python
class Probe:
    """Int wrapper that counts how often == is called on it."""
    eq_calls = 0

    def __init__(self, v: int) -> None:
        self.v = v

    def __eq__(self, other: object) -> bool:
        Probe.eq_calls += 1
        return isinstance(other, Probe) and self.v == other.v

    def __hash__(self) -> int:
        return hash(self.v)

def s01(n):
    ops = 0
    for i in range(n):
        ops += 1
    return ops

def s02(n):
    ops = 0
    for i in range(n):
        ops += 1
    for j in range(n):
        ops += 1
    return ops

def s03(n):
    ops = 0
    for i in range(n):
        for j in range(n):
            ops += 1
    return ops

def s04(n):
    ops = 0
    for i in range(n):
        for j in range(i):
            ops += 1
    return ops

def s05(n):
    ops = 0
    while n > 1:
        n //= 2
        ops += 1
    return ops

def s06(n):
    ops = 0
    for i in range(n):
        j = 1
        while j < n:
            j *= 2
            ops += 1
    return ops

def s07(n):
    ops = 0
    i = n
    while i > 0:
        for j in range(i):
            ops += 1
        i //= 2
    return ops

def s08(n):
    ops = 0
    for i in range(100):
        ops += 1
    return ops

def s09(n):
    if n == 0:
        return 1
    return s09(n - 1) + s09(n - 1)

def s10(n):
    Probe.eq_calls = 0
    seen = []
    for x in [Probe(i) for i in range(n)]:
        if x not in seen:
            seen.append(x)
    return max(1, Probe.eq_calls)
```

<details><summary>Answers (verified by counting, ex03)</summary>

```text
s01: answer=O(n)        measured=O(n)        match=True
s02: answer=O(n)        measured=O(n)        match=True
s03: answer=O(n^2)      measured=O(n^2)      match=True
s04: answer=O(n^2)      measured=O(n^2)      match=True
s05: answer=O(log n)    measured=O(log n)    match=True
s06: answer=O(n log n)  measured=O(n log n)  match=True
s07: answer=O(n)        measured=O(n)        match=True
s08: answer=O(1)        measured=O(1)        match=True
s09: answer=O(2^n)      measured=O(2^n)      match=True
s10: answer=O(n^2)      measured=O(n^2)      match=True
score 10/10
```

Traps: s02 adds; s04 is n²/2, still O(n²); s07 is n + n/2 + … < 2n; s08 ignores n; s09 has 2ⁿ
leaves (≈2ⁿ⁺¹ calls) but depth n (O(n) space); s10's `not in` scans the list (`Probe` counts `==`); a `set` fixes it.
</details>

**Wrong-but-tempting answers**

- "Two nested loops, so O(n²)" — check the bounds first (s07 is O(n)).
- "Halving recursion is O(log n) time" — recursing on *both* halves visits all n items: O(n) time, O(log n) stack.
- "Dict lookups are always O(1)" — average only; `x in d.values()` is O(n).
- "Sorting is free" — `sorted` inside a loop is O(n² log n).

## Interviewer's view

- Rewarded: time **and** space for every rung, unprompted; target class named from the constraints; hidden costs fixed.
- Penalised: loose bounds, forgotten stack space, ignoring a second input size.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Operation counter and growth fitter | ★ | count steps, fit the class |
| 02 | Constraint-to-complexity advisor | ★ | input size → acceptable complexity |
| 03 | Classify ten snippets, then prove it | ★ | shape → growth class |
| 04 | Hidden costs: list vs set, pop(0) vs deque | ◆ | hidden O(n) lines |
| 05 | Space on the call stack | ★ | depth = stack space |

Index: `chapters/ch08_big_o_primer/README.md`.

## Checkpoint quiz

1. Complexity of `for i in range(n): for j in range(i, i + 5):`?
2. n ≤ 2·10⁵: is O(n²) acceptable?
3. Space of recursive DFS on a path of n nodes?
4. Why is `list.append` called *amortised* O(1)?
5. FIFO queue, 10⁶ operations: `list` or `deque`?

<details><summary>Answers</summary>

1. O(n): the inner loop runs 5 times.
2. No: 4·10¹⁰ steps. Aim for O(n log n).
3. O(n) stack frames; past ~1000 it raises RecursionError, so use an explicit stack.
4. Rare resizes copy everything, but capacity grows proportionally, so n appends cost O(n) in total.
5. `deque`: `popleft` is O(1); `list.pop(0)` is O(n), making the run O(n²).
</details>

## Summary card

- Sequential adds, nested multiplies, halving gives log n, geometric sums are O(n).
- O = upper bound, Ω = lower bound, Θ = tight; quote the tight worst case (average for hashing).
- Space = extra containers + recursion depth; CPython's default recursion limit is 1000.
- Hidden O(n): `pop(0)`, `insert(0, x)`, `x in list`, slicing, `x in d.values()`, string `+=` in loops.
- Max n per class, classic ~10⁸ / CPython ~10⁷: n! 10/10, 2ⁿ 20/18, n³ 500/200, n² 5,000/3,000, n log n 10⁶/5·10⁵, n 10⁸/10⁷.
