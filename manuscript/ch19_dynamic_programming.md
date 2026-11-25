# Chapter 19. Dynamic Programming

★ Core · Tracks S, M, L · Study time ≈ 10 h · Prerequisites: Ch. 8 (Big-O), Ch. 14 (recursion, §14.3 memoisation preview), §6.11 (`functools.cache`)

**Learning objectives**

- Spot DP (overlapping subproblems, optimal substructure) and its family from the wording.
- State the recipe — state, transition, base, order, answer — then climb recursion → memo →
  table → rolling array, costing each rung as *states × work*.
- Reconstruct the answer (houses, items, edit script), not just its value.

> **Recognise it**
>
> | Signal in the problem | Reach for |
> |---|---|
> | "How many ways", "minimum/maximum cost", "is it possible", and choices at each step | DP (not greedy) |
> | "Can't take two adjacent", "after selling you must wait" | 1D DP / state machine |
> | Capacity, budget or target sum with items used once / unlimited times | Knapsack |
> | Two strings or sequences, "subsequence", "edits" | 2D table over prefixes |
> | "Burst/merge/cut, cost depends on neighbours" | Interval DP |
> | n ≤ ~16–18 (in Python) and "visit all" / "assign each" | Bitmask DP |
> | "Count numbers ≤ N (N up to 10¹⁸) with a digit property" | Digit DP |
>
> Constraint hint: n ≤ ~18 → 2ⁿ states; n ≤ ~5,000 → O(n²); n ≈ 10⁵ → O(n log n). A capacity
> or amount up to 10⁴ makes an O(n·cap) table affordable.

## 19.1 Recognising DP: overlapping subproblems and optimal substructure

DP applies when the best answer is built from best answers to smaller versions of the problem
(*optimal substructure*) and those versions recur (*overlapping subproblems*). Count how often
plain recursion for climbing stairs (steps 1 or 2) meets each argument:

```python
from collections import Counter

seen = Counter()

def ways(i: int) -> int:                     # plain recursion, steps of 1 or 2
    seen[i] += 1
    return 1 if i <= 1 else ways(i - 1) + ways(i - 2)

print("ways(20) =", ways(20), "calls:", sum(seen.values()), "distinct states:", len(seen))
print("ways(2) was called", seen[2], "times")
```

```text
ways(20) = 10946 calls: 21891 distinct states: 21
ways(2) was called 4181 times
```

Twenty-one states, tens of thousands of calls: that gap is the opportunity. Merge sort's halves
never overlap (caching buys nothing); in greedy (Ch. 20) one local choice is provably safe.

## 19.2 Top-down (memoisation with `lru_cache`) vs bottom-up

Top-down caches the recursion; bottom-up fills a table in an order where every dependency is
ready.

```python
from functools import cache

@cache
def ways(i: int) -> int:                     # top-down
    return 1 if i <= 1 else ways(i - 1) + ways(i - 2)

def ways_table(n: int) -> int:               # bottom-up
    table = [1, 1] + [0] * max(0, n - 1)
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
    return table[n]

print(ways(30) == ways_table(30), ways_table(30))
ways.cache_clear()
try:
    ways(5000)
except RecursionError:
    print("top-down ways(5000): RecursionError")
for i in range(0, 5001, 500):                # warm the cache in increasing order
    ways(i)
print("after warming, ways(5000) has", len(str(ways(5000))), "digits")
```

```text
True 1346269
top-down ways(5000): RecursionError
after warming, ways(5000) has 1045 digits
```

| | Top-down (`@cache`) | Bottom-up table |
|---|---|---|
| States computed | only the reachable ones | all of them |
| Limits | recursion limit ≈ 1000 (→ §7.21); call overhead | none; easy to roll (§19.15) |

`@cache` (3.9+) is `@lru_cache(maxsize=None)`; plain `@lru_cache` keeps 128 entries (correct,
may recompute). Arguments must be hashable (→ §7.22). Define the cached helper inside the
solver so each call gets a fresh cache.

## 19.3 Defining state, transition, base case — the DP recipe

Say these five lines out loud before coding; the code is a translation of them.

| Step | Question | House robber (below) |
|---|---|---|
| State | What does one answer mean, in words? | `best(i)` = most cash from the first `i` houses |
| Transition | How do smaller states combine? | `max(best(i-1), nums[i-1] + best(i-2))` |
| Base case | What is known directly? | `best(0) = 0`, `best(1) = nums[0]` |
| Order | What must be ready first? | `i` ascending |
| Answer | Which state is returned? | `best(n)` |

**Complexity = states × work per transition** (→ §22.5), plus O(depth) stack when top-down.
Most bugs are a vague state (ending *at* `i` or *within* the first `i`?) or an off-by-one base.

## 19.4 1D DP: climbing stairs, house robber, decode ways

**Worked problem 1 — House robber.** Houses in a row hold `nums[i] ≥ 0`; you may not rob two
neighbours. Maximise the take, and say which houses.

*Rung 1.* Plain recursion, two calls per house: O(φⁿ) ≈ O(1.618ⁿ).
*Rung 2.* Memoised: n states × O(1) = O(n) time and space, but O(n) stack — fails past ~1000 houses.
*Rung 3.* Table: O(n), no recursion, and it can be walked back to list the houses.
*Rung 4.* Two variables (`best(i)` reads only the previous two): O(1) space, value only — the
expected final answer when the houses are not asked for.

```python
def rob(nums: list[int]) -> int:             # rung 4: O(n) time, O(1) space
    prev2 = prev1 = 0                        # best(i - 2), best(i - 1)
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

def rob_with_houses(nums: list[int]) -> tuple[int, list[int]]:   # rung 3
    best = [0] * (len(nums) + 1)
    for i in range(1, len(nums) + 1):
        best[i] = max(best[i - 1], nums[i - 1] + (best[i - 2] if i >= 2 else 0))
    chosen, i = [], len(nums)
    while i > 0:                             # walk back: did the value change here?
        if best[i] == best[i - 1]:
            i -= 1                           # house i-1 skipped
        else:
            chosen.append(i - 1)             # house i-1 taken, its neighbour skipped
            i -= 2
    return best[-1], chosen[::-1]

for nums in ([2, 7, 9, 3, 1], [2, 1, 1, 2], [], [5], [0, 0, 0]):
    print(nums, rob(nums), rob_with_houses(nums))
```

```text
[2, 7, 9, 3, 1] 12 (12, [0, 2, 4])
[2, 1, 1, 2] 4 (4, [0, 3])
[] 0 (0, [])
[5] 5 (5, [0])
[0, 0, 0] 0 (0, [])
```

Edge cases (above): `[]`, `[x]`, all zeros. Follow-up "which houses?": keep the table and walk
back.

**Circle variant:** some optimal answer skips house 0 or skips house n−1, so return
`max(rob(nums[1:]), rob(nums[:-1]))` (one house: take it). **Wrong but tempting:** "take every
other house" (fails on `[2, 1, 1, 2]`); splitting the tuple assignment into `prev1 = max(...)`
then `prev2 = prev1`, which copies the *new* value.

**Climbing stairs** with step set `S` counts instead: `ways(i) = Σ ways(i − s)`, `ways(0) = 1`;
O(n·|S|) time, O(max S) space. For steps {1, 2} (Fibonacci) the count first exceeds 2⁶³−1 at
n = 92; larger step sets overflow sooner — exact in Python, but interviews may ask mod 10⁹+7.

**Decode ways** (`"1"`→A … `"26"`→Z) is climbing stairs where a step is legal only if its digits
form a code: `f(i) = f(i+1)` if `s[i] != "0"`, plus `f(i+2)` if `10 ≤ int(s[i:i+2]) ≤ 26`;
`f(n) = 1`; two variables, right to left, O(n). Edge cases: `"06"` → 0, `"100"` → 0, `""` → 1. → repo: `chapters/ch19_dynamic_programming/solutions/ex01_stairs_decode_ways.py`

## 19.5 2D grid DP: unique paths, min path sum

Moving only right or down, `ways(r, c) = ways(r−1, c) + ways(r, c−1)`, 0 on a rock. A cell
needs only the row above and its left neighbour, so one row suffices: `row[c]` still holds
"above" when read, and `row[c−1]` already holds "left":

```python
def unique_paths(grid: list[list[int]]) -> int:   # 1 = rock
    n = len(grid[0])
    row = [1] + [0] * (n - 1)                # a virtual 1 above the start
    for cells in grid:
        for c in range(n):
            if cells[c]:
                row[c] = 0
            elif c:
                row[c] += row[c - 1]         # above (old row[c]) + left (new row[c-1])
    return row[-1]

print(unique_paths([[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
      unique_paths([[0] * 7 for _ in range(3)]), unique_paths([[1]]))
```

```text
2 28 0
```

O(mn) time, O(n) space. Without rocks the count is `math.comb(m + n − 2, m − 1)`.
**Min path sum** has the same shape with `min(above, left) + cost[r][c]`; to output the moves,
keep the full table and step back to the neighbour that gave the minimum (repo: `(7, 'RRDD')`).
Pitfalls: a rock in the first row blocks everything after it; `[[0] * n] * m` shares rows
(→ §7.3). With up/left moves too, no fill order exists — use Dijkstra (§16.10).
→ repo: `chapters/ch19_dynamic_programming/solutions/ex03_grid_paths.py`

## 19.6 0/1 knapsack and unbounded knapsack (coin change)

**Worked problem 2 — Knapsack.** Items are `(weight, value)`; capacity `cap`. In 0/1 knapsack
each item is used at most once.

*Rung 1.* Take or skip each item: O(2ⁿ). Why move up: 2ⁿ at n = 100 is hopeless, yet the states
`(i, room)` repeat.
*Rung 2.* Memoise on `(i, room)`: O(n·cap) time and space — *pseudo-polynomial*, since `cap` is
a value, not an input length.
*Rung 3.* Table `best[i][c] = max(best[i−1][c], v + best[i−1][c−w])`; same bounds; where the
value changes walking back from `best[n][cap]`, item `i−1` was taken. Why move up: n·cap cells,
but row `i` reads only row `i−1`, so one row suffices.
*Rung 4.* One row — and the loop direction decides everything:

```python
def knapsack(items: list[tuple[int, int]], cap: int, reuse: bool = False) -> int:
    best = [0] * (cap + 1)                   # best[c]: most value within capacity c
    for w, v in items:
        # 0/1: DOWN, so best[c - w] is still "without this item".
        # Unbounded: UP, so best[c - w] may already contain this item.
        caps = range(w, cap + 1) if reuse else range(cap, w - 1, -1)
        for c in caps:
            best[c] = max(best[c], v + best[c - w])
    return best[cap]

items = [(1, 1), (3, 4), (4, 5), (5, 7)]
print(knapsack(items, 7), knapsack(items, 7, reuse=True))
print("one item (2, 3), cap 6:", knapsack([(2, 3)], 6), knapsack([(2, 3)], 6, reuse=True))
print("edge cases:", knapsack(items, 0), knapsack([(9, 9)], 5), knapsack([], 5))
```

```text
9 9
one item (2, 3), cap 6: 3 9
edge cases: 0 0 0
```

O(n·cap) time, O(cap) space. Looping upward in the 0/1 version is the classic bug: it silently
solves the unbounded problem (3 vs 9 above). Edge cases: cap 0, an item heavier than `cap`, no
items — all 0. Follow-ups: reconstruct the items (keep the 2D table); partition equal subset sum
(boolean knapsack up to `total // 2`); target sum (count subsets summing to `(total + target) / 2`).

**Coin change, fewest coins** is unbounded knapsack minimising count:
`fewest[x] = 1 + min(fewest[x − c])`, sentinel `amount + 1` for "impossible".

```python
def min_coins(coins: list[int], amount: int) -> int:
    sentinel = amount + 1                    # more coins than any real answer
    fewest = [0] + [sentinel] * amount
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x:
                fewest[x] = min(fewest[x], fewest[x - c] + 1)
    return -1 if fewest[amount] == sentinel else fewest[amount]

print(min_coins([1, 3, 4], 6), min_coins([5, 2], 6), min_coins([2], 3))
```

```text
2 3 -1
```

O(amount·k) time, O(amount) space. **Wrong but tempting:** largest coin first gives 4+1+1
instead of 3+3 for `[1, 3, 4]`, 6, and fails outright on `[5, 2]`, 6; it is optimal only for
"canonical" systems such as 1/5/10/25 (→ §20.7; repo `greedy_coins`).

**Counting ways: the loop order is the definition.**

| Question | Outer loop | Inner loop | `[1, 2, 5]`, amount 5 |
|---|---|---|---|
| Combinations (1+2 = 2+1) | coins | amounts ascending | 4 |
| Permutations (1+2 ≠ 2+1) | amounts | coins | 9 |

Both are `ways[x] += ways[x − c]`, `ways[0] = 1`. Coins outer builds each multiset in one fixed
coin order; amounts outer lets the *last* coin be any coin, so every ordering counts. → repo: `chapters/ch19_dynamic_programming/solutions/ex04_knapsack_coin_change.py`

## 19.7 Subsequences: LIS (O(n²) and O(n log n)), LCS

**Worked problem 3 — Longest increasing subsequence** (strictly increasing; return one).

*Rungs 1–2.* Recursion on `(i, previous taken)`: O(2ⁿ); memoised, O(n²) states.
*Rung 3.* `end(i)` = LIS length *ending at* `i` = `1 + max(end(j))` over `j < i` with
`nums[j] < nums[i]`; answer `max(end)`, not `end(n−1)`. O(n²) time, O(n) space. Why move up:
n = 10⁵ means 10¹⁰ steps.
*Rung 4, patience sorting.* `tails[k]` = smallest possible tail of an increasing subsequence of
length `k+1`. The tails are sorted, so each element finds its slot by binary search (→ §6.9):
extend if it beats every tail, otherwise lower the first tail ≥ it.

```python
from bisect import bisect_left

def lis(nums: list[int]) -> list[int]:
    tails: list[int] = []                    # indices; nums[tails[k]] strictly increasing
    tail_vals: list[int] = []
    parent = [-1] * len(nums)
    for i, x in enumerate(nums):
        k = bisect_left(tail_vals, x)        # bisect_left: equal values do not extend
        if k > 0:
            parent[i] = tails[k - 1]         # predecessor = current tail one shorter
        if k == len(tails):
            tails.append(i)
            tail_vals.append(x)
        else:
            tails[k], tail_vals[k] = i, x
        print(f"after {x}: tails = {tail_vals}")
    out, i = [], tails[-1] if tails else -1
    while i != -1:
        out.append(nums[i])
        i = parent[i]
    return out[::-1]

print("lis:", lis([3, 1, 2, 1, 8, 5, 6]))
```

```text
after 3: tails = [3]
after 1: tails = [1]
after 2: tails = [1, 2]
after 1: tails = [1, 2]
after 8: tails = [1, 2, 8]
after 5: tails = [1, 2, 5]
after 6: tails = [1, 2, 5, 6]
lis: [1, 2, 5, 6]
```

O(n log n) time, O(n) space. **Wrong but tempting:** returning `tail_vals` — for `[3, 4, 1]`
it is `[1, 4]`, not a subsequence; only its *length* is meaningful. Non-decreasing variant:
`bisect_right`. Edge cases: `[]` → `[]`, all equal → one element, strictly decreasing → one
element. Follow-up: Russian-doll envelopes (sort by width ascending, height *descending*, then
LIS on heights). → repo: `chapters/ch19_dynamic_programming/solutions/ex05_lis.py`

**Longest common subsequence.** `L(i, j)` = LCS length of `a[:i]` and `b[:j]`:
`L(i−1, j−1) + 1` if `a[i−1] == b[j−1]`, else `max(L(i−1, j), L(i, j−1))`; row and column 0 are
0. The table for `a = "ABCBDAB"` (rows) and `b = "BDCABA"` (from the repo file's `main()`):

```text
       B  D  C  A  B  A
    0  0  0  0  0  0  0
A   0  0  0  0  1  1  1
B   0  1  1  1  1  2  2
C   0  1  1  2  2  2  2
B   0  1  1  2  2  3  3
D   0  1  2  2  2  3  3
A   0  1  2  2  3  3  4
B   0  1  2  2  3  4  4
```

Walk back from the corner: on a match take the character and go diagonally, otherwise move
toward the larger neighbour — on a tie, move up (`i−1`), as the repo does — giving `'BCBA'`. O(mn) time and space; O(min(m, n)) space for the length alone.

## 19.8 Edit distance

**Worked problem 4 — Edit distance.** Fewest single-character inserts, deletes and
substitutions turning `a` into `b`.

Recipe: `D(i, j)` = edits turning `a[:i]` into `b[:j]`. If the last characters match,
`D(i−1, j−1)`; otherwise `1 + min(D(i−1, j)` *delete*, `D(i, j−1)` *insert*,
`D(i−1, j−1)` *substitute*`)`. Base: `D(i, 0) = i`, `D(0, j) = j`. Order: rows top to bottom.
Answer `D(m, n)`. Ladder: recursion O(3^(m+n)) → memo O(mn), depth m+n → full table O(mn),
which yields the edit script → two rows, O(min(m, n)) space, value only.

```python
def edit_distance(a: str, b: str) -> int:
    if len(b) > len(a):
        a, b = b, a                          # symmetric: keep the shorter on the row
    prev = list(range(len(b) + 1))           # D(0, j) = j
    for i, ch in enumerate(a, start=1):
        cur = [i]                            # D(i, 0) = i
        for j, other in enumerate(b, start=1):
            if ch == other:
                cur.append(prev[j - 1])
            else:
                cur.append(1 + min(prev[j], cur[j - 1], prev[j - 1]))
        prev = cur
    return prev[-1]

pairs = [("horse", "ros"), ("kitten", "sitting"), ("", "abc"), ("same", "same"), ("abc", "xyz")]
print([edit_distance(a, b) for a, b in pairs])
```

```text
[3, 3, 3, 0, 3]
```

Edge cases: an empty string (distance = the other's length), identical strings (0), no common
characters (`max(m, n)`). The repo's `edit_ops` walks the full table back to a script; for
`horse → ros` its real output is `ops: sub:h>r del:r del:e`.

**Wrong but tempting:** adding 1 on a match; a base row of zeros (`""` → `"abc"` costs 3);
swapping insert and delete when reconstructing. With only inserts and deletes the distance is
`m + n − 2·LCS(a, b)`. Reconstruction in linear space is Hirschberg's algorithm — name it,
don't code it.
→ repo: `chapters/ch19_dynamic_programming/solutions/ex06_lcs_edit_distance.py`

## 19.9 String DP: palindromic substrings, word break

**Word break.** Can `s` be split into (reusable) dictionary words? `ok(i)` = `s[:i]` splits =
`any(ok(j) and s[j:i] in words)`, with `j` limited to the last `L` positions (`L` = longest
word). Storing the cut point rebuilds a split:

```python
def word_break_split(s: str, words: set[str]) -> list[str] | None:
    longest = max(map(len, words), default=0)
    parent: list[int | None] = [0] + [None] * len(s)     # parent[i] = start of last word
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - longest), i):
            if parent[j] is not None and s[j:i] in words:
                parent[i] = j
                break
    if parent[-1] is None:
        return None
    out, i = [], len(s)
    while i:
        out.append(s[parent[i]:i])
        i = parent[i]
    return out[::-1]

words = {"cats", "dog", "sand", "and", "cat"}
print(word_break_split("catsanddog", words), word_break_split("catsandog", words))
```

```text
['cat', 'sand', 'dog'] None
```

O(n·L²) time (L cut points, each slice O(L)), O(n) space; plain recursion is exponential on
`"aaa…ab"` with `{"a", "aa", "aaa"}`. *All* splits = backtracking plus this memo (Ch. 18).
→ repo: `chapters/ch19_dynamic_programming/solutions/ex07_word_break_palindromes.py`

**Palindromic substrings.** `pal(i, j) = s[i] == s[j] and (j − i < 2 or pal(i+1, j−1))`, with
`i` descending because row `i` reads row `i+1`: O(n²) time and space; expanding around the
2n − 1 centres gives O(1) space (→ §9.5). **Longest palindromic subsequence:**
`P(i, j) = 2 + P(i+1, j−1)` on a match, else `max(P(i+1, j), P(i, j−1))`; O(n²) time, O(n)
space with two rows; equivalently `LCS(s, s[::-1])`.

## 19.10 Interval DP ◆

**Burst balloons:** bursting `k` earns `left · nums[k] · right` from its *current* neighbours.
"Which first?" fails — neighbours change, so the halves are not independent. Ask **which balloon
goes last** inside the open interval `(l, r)`: while the rest is cleared, `l`, `k` and `r` all
stay, so the two sides are independent.

```python
def max_coins(nums: list[int]) -> int:
    vals = [1] + nums + [1]                  # padding: borders need no special case
    m = len(vals)
    best = [[0] * m for _ in range(m)]       # best[l][r]: burst all strictly inside
    for gap in range(2, m):                  # interval length, shortest first
        for l in range(m - gap):
            r = l + gap
            best[l][r] = max(vals[l] * vals[k] * vals[r] + best[l][k] + best[k][r]
                             for k in range(l + 1, r))
    return best[0][m - 1]

print(max_coins([3, 1, 5, 8]), max_coins([1, 5]), max_coins([]))
```

```text
167 10 0
```

O(n³) time, O(n²) space (repo ladder: O(n!) orders → O(2ⁿ·n) subset memo → this). Matrix-chain
multiplication and "minimum cost to cut a stick" use the same split-point recurrence.
→ repo: `chapters/ch19_dynamic_programming/solutions/ex08_burst_balloons.py`

## 19.11 State machine DP (stock problems) ◆

Stock problems differ only in their states. **Unlimited trades, one-day cooldown after a sale:**

```text
rest ──buy──▶ hold ──sell──▶ sold
  ▲                           │
  └───────── cooldown ────────┘   (rest and hold may also stay put)
```

```python
def max_profit(prices: list[int]) -> int:
    hold, sold, rest = float("-inf"), 0, 0   # no share can be held before day 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return int(max(sold, rest))

print(max_profit([1, 2, 3, 0, 2]), max_profit([5, 4, 3]), max_profit([]))
```

```text
3 0 0
```

On `[1, 2, 3, 0, 2]`: buy at 1, sell at 2, sit out the day priced 3, buy at 0, sell at 2.

O(n) time, O(1) space. Every new state must read the *old* values (one tuple assignment), or
you can buy and sell on the same day. Variants change only the machine:

| Variant | Change |
|---|---|
| One transaction | `hold = max(hold, -p)` (buy from zero, not from `rest`) |
| Unlimited, no cooldown (± fee) | two states: `hold = max(hold, free − p)`, `free = max(free, hold + p − fee)` |
| At most k transactions | states `hold[t]`, `free[t]` for t = 1..k: O(nk) |

→ repo: `chapters/ch19_dynamic_programming/solutions/ex09_stock_cooldown.py`

## 19.12 DP on trees ◆

**House robber on a tree** (never rob a node and its parent): return a *pair* per subtree —
best with this node taken, best with it skipped — combined in post-order (→ §14.5):

```python
class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def rob_tree(root: Node | None) -> int:
    def pair(node):                          # (take node, skip node)
        if node is None:
            return 0, 0
        lt, ls = pair(node.left)
        rt, rs = pair(node.right)
        return node.val + ls + rs, max(lt, ls) + max(rt, rs)
    return max(pair(root))

root = Node(3, Node(2, None, Node(3)), Node(3, None, Node(1)))
print(rob_tree(root), rob_tree(None))
```

```text
7 0
```

O(n) time, O(h) stack (repo's lower rungs: recursion over grandchildren, exponential; a memo
dict keyed by node). A 10⁴-deep chain exceeds the recursion limit, so the iterative rung
processes the BFS order *in reverse* — children before parents.
→ repo: `chapters/ch19_dynamic_programming/solutions/ex10_house_robber_tree.py`

## 19.13 Bitmask DP ◆

When n ≤ ~16–18 (in Python) and the state must remember *which* items are used, store the set as bits of an
int (→ §21.5). **Shortest round trip** (travelling salesperson from city 0): the cost of
finishing depends only on the visited set and the current city, not the order — so
`f(mask, last)` replaces n! orders with 2ⁿ·n states.

```python
from functools import cache

def tsp(dist: list[list[int]]) -> int:
    n = len(dist)
    full = (1 << n) - 1

    @cache
    def finish(mask: int, last: int) -> int:     # visit the rest, return to 0
        if mask == full:
            return dist[last][0]
        return min(dist[last][nxt] + finish(mask | 1 << nxt, nxt)
                   for nxt in range(n) if not mask >> nxt & 1)

    return finish(1, 0)                          # city 0 visited, standing at 0

d = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
print(tsp(d), tsp([[0, 1, 9], [9, 0, 1], [1, 9, 0]]))
```

```text
80 3
```

O(2ⁿ·n²) time, O(2ⁿ·n) space: n = 15 is ~7·10⁶ transitions versus 14! ≈ 8.7·10¹⁰ orders.
Bit idioms: `mask >> j & 1` tests, `mask | 1 << j` adds. Bottom-up, iterate masks in increasing
order — a subset is numerically smaller than its supersets.
→ repo: `chapters/ch19_dynamic_programming/solutions/ex11_tsp_bitmask.py`

## 19.14 Digit DP ○

To count `x ≤ N` (N up to 10¹⁸) with a digit property, recurse over N's digits with state
`(position, property state, tight, started)`: *tight* = prefix equals N's, so the next digit is
capped by N's digit; *started* skips leading zeros. Memoised: D × states × 10 steps for D
digits; ranges use `count(hi) − count(lo − 1)`. The repo counts numbers with no two equal
adjacent digits.
→ repo: `chapters/ch19_dynamic_programming/solutions/ex12_digit_dp.py`

## 19.15 Space optimisation (rolling arrays)

Look at which cells a cell reads; keep only those.

| Dependency | Keep | Example | Space |
|---|---|---|---|
| previous 1–2 values | variables | robber, stairs, decode ways | O(1) |
| row above + left | one row, left → right | grid paths | O(n) |
| previous row only, `c − w` | one row, **right → left** | 0/1 knapsack | O(cap) |
| previous row and diagonal | two rows (or one row + saved diagonal) | LCS, edit distance | O(min(m, n)) |
| all shorter intervals / subsets | nothing to drop | burst balloons, bitmask | — |

Costs: reconstruction is lost (keep the table or parent pointers when the answer is a path,
set or script), and overwrite order becomes a correctness issue (0/1 vs unbounded knapsack).
Write the table first, then roll it.

## 19.16 Practice set

Do ex01–ex07 (★), then the ◆ exercises; ex12 is optional. More: Chapter 45, problems 107–120.

## Interviewer's view

- **Recipe before code.** Stating state, transition, base, order and answer earns credit even
  if the code has a bug; a table with unexplained indices loses it.
- **Climb the ladder aloud**, costing each rung as states × work.
- **Edge cases:** empty input, one element, impossible target (−1), `"0"` in decode ways,
  capacity 0.
- **Reconstruction** ("which houses / items / edits?") is a common follow-up: keep the table.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Climbing stairs variants and decode ways | ★ | 1D DP, counting |
| ex02 | House robber: line and circle | ★ | 1D take/skip |
| ex03 | Grid paths with rocks; minimum path sum | ★ | 2D grid, rolling row |
| ex04 | 0/1 and unbounded knapsack; coin change | ★ | knapsack over capacity |
| ex05 | LIS with reconstruction | ★ | subsequence, patience sorting |
| ex06 | LCS and edit distance with reconstruction | ★ | two-sequence table |
| ex07 | Word break; palindromic substrings/subsequence | ★ | string DP |
| ex08 | Burst balloons | ◆ | interval DP |
| ex09 | Stock trading with cooldown | ◆ | state machine |
| ex10 | House robber on a tree | ◆ | tree DP |
| ex11 | Shortest round trip (TSP-lite) | ◆ | bitmask DP |
| ex12 | Numbers without equal adjacent digits | ○ | digit DP |

Index: `chapters/ch19_dynamic_programming/README.md`.

## Checkpoint quiz

1. What two properties make a problem suitable for DP, and which one does memoisation exploit?
2. In the one-row 0/1 knapsack, why must the capacity loop run downward?
3. Coin change counting: which loop goes outside to count combinations rather than orderings?
4. Patience sorting gives `tails = [1, 4]` for `[3, 4, 1]`. Is `[1, 4]` an answer? What is?
5. Why does burst balloons choose the *last* balloon in an interval rather than the first?

<details>
<summary>Answers</summary>

1. Optimal substructure and overlapping subproblems; memoisation exploits the overlap — each
   state is solved once.
2. `best[c − w]` must still mean "without this item". Downward reads cells not yet updated in
   this pass; upward lets the item be reused (that is unbounded knapsack).
3. Coins outer: each multiset is built in one fixed coin order, so it is counted once.
4. No — `1` comes after `4` in the input; only `len(tails)` is meaningful. A parent array
   rebuilds a real LIS, `[3, 4]`.
5. While `k` is still present, balloons left and right of it never become neighbours, so
   `(l, k)` and `(k, r)` are independent subproblems.

</details>

## Summary card

- **DP = optimal substructure + overlapping subproblems.** Recipe: state in words, transition,
  base, order, answer. Cost = states × work.
- **Ladder:** recursion → `@cache` (≤ ~1000 deep) → table → rolling array.
- **1D:** robber `max(skip, take + best(i−2))`; circle = two lines. **Grid:** above + left.
- **LCS / edit distance:** prefix tables; walk back from the corner (ties go up) to rebuild.
- **Knapsack:** 0/1 loops capacity **down**, unbounded **up**; pseudo-polynomial O(n·cap).
- **Coins:** sentinel for min; greedy fails on 1/3/4 → 6; coins outer = combinations.
- **LIS:** `end(i)` O(n²) → patience + `bisect_left` O(n log n); `tails` is not the answer.
- **Interval:** last action `k` in `(l, r)`, fill by length, O(n³). **State machine:** update all
  states from old values. **Tree:** (take, skip) per subtree. **Bitmask:** `f(mask, last)`.
  **Digit:** `(pos, state, tight, started)`.
