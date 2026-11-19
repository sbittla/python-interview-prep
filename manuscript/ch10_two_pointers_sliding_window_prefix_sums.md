# Chapter 10. Two Pointers, Sliding Window and Prefix Sums

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 5–7 hours · **Prerequisites:** Chapters 8–9

Three techniques turn "check every pair / every subarray" brute forces from O(n²) into O(n):
two pointers discard candidates in bulk, a sliding window reuses the previous window's work, and
prefix sums turn a range sum into one subtraction. The code is short; what is tested is the
*argument* for why a pointer move can never skip the answer.

**Learning objectives**

- Choose two pointers, a sliding window or prefix sums from the wording and constraints.
- State the invariant of every pointer or window, and use it to justify each move.
- Write the variable-window template for "longest" and "shortest" problems.
- Spot when a window is *wrong* (negatives, exact-sum counting) and use prefix sum + hash map.
- Apply 2D prefix sums and difference arrays.

> **Recognise it**
>
> | Signal in the problem | Technique | Section |
> |---|---|---|
> | Sorted array; pair/triple with a target sum; "closest to" | Opposite-direction pointers | §10.1 |
> | "In place", "O(1) extra space", remove/partition/compact | Read/write (same-direction) pointers | §10.2 |
> | Values in 1..n used as indices; "cycle", "eventually repeats" | Fast and slow pointers | §10.3 |
> | "Every window of size k", moving average | Fixed window | §10.4 |
> | "Longest/shortest *contiguous* … such that …", all values ≥ 0 | Variable window | §10.5 |
> | Characters, anagrams, "contains all of", "at most k distinct" | Window + hash map | §10.6 |
> | "Max/min of every window" | Monotonic deque | §10.7 → §12.6 |
> | Many range-sum queries on fixed data; submatrix sums | Prefix sums (1D/2D) | §10.8 |
> | "Count subarrays with sum = k", negatives allowed | Prefix sum + hash map | §10.9 |
> | Many "add d to range [l, r]" updates, one read at the end | Difference array | §10.10 |

## 10.1 Opposite-direction two pointers (sorted pair/triple sum)

Put `lo` at the start and `hi` at the end of a **sorted** array. If `nums[lo] + nums[hi]` is too
small, every pair using `nums[lo]` with anything left of `hi` is also too small, so `lo` is finished:
`lo += 1`. Symmetrically, too big → `hi -= 1`. Each step discards a whole row of the n × n pair grid,
so the scan is O(n). **Invariant:** every pair that could still be the answer lies inside `[lo, hi]`.

### Worked problem 1: three sum to zero

*Return all distinct value triplets `(a, b, c)` with `a ≤ b ≤ c` and `a + b + c == 0`.*

| Rung | Idea | Time | Extra space | Why move up |
|---|---|---|---|---|
| Brute | all `combinations(nums, 3)`, set of sorted tuples | O(n³) | O(answer) | 3,000 values → 4.5 × 10⁹ triples |
| Improved | fix `i`, hash-set two-sum on the suffix | O(n²) | O(n) | fiddly set de-duplication |
| Optimal | sort, fix `i`, two pointers on the suffix | O(n²) | O(1)* | de-duplication is free |

\*Besides the sorted copy and the output. No O(n^(2−ε)) algorithm is known, so O(n²) is the
target; say so.

```python
def solve(nums: list[int]) -> list[tuple[int, int, int]]:
    nums = sorted(nums)
    n, out = len(nums), []
    for i in range(n - 2):
        if nums[i] > 0:                   # smallest value positive: done
            break
        if i > 0 and nums[i] == nums[i - 1]:
            continue                      # same anchor -> same triplets
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1                   # need a bigger sum
            elif s > 0:
                hi -= 1                   # need a smaller sum
            else:
                out.append((nums[i], nums[lo], nums[hi]))
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1               # skip duplicate middles
    return out
```

```text
nums=[-1, 0, 1, 2, -1, -4]  -> [(-1, -1, 2), (-1, 0, 1)]
                           brute agrees: True  hash agrees: True  lookahead-skip(wrong): [(-1, 0, 1)]
```

**Wrong but tempting:** skipping the anchor when it equals the *next* value (`nums[i] == nums[i+1]`)
throws away `-1` before it can pair with the other `-1`, losing `(-1, -1, 2)`. Compare with the
*previous* anchor. **Edge cases:** fewer than 3 values, all zeros, no solution, many duplicates.
**Follow-ups:** 3-sum closest (track best `|s - target|`), k-sum (recurse to the 2-pointer base).
→ repo: `chapters/ch10_two_pointers_sliding_window_prefix_sums/solutions/ex01_three_sum.py`

**Container with most water** (ex02) uses the same discard argument unsorted: start widest; every
narrower pair keeping the *shorter* wall is capped by it, so that wall is finished. Moving the
taller wall instead returns 8, not 49, on `[1, 8, 6, 2, 5, 4, 8, 3, 7]`.

## 10.2 Same-direction pointers (remove duplicates, partitioning)

A **read** pointer scans everything; a **write** pointer `w` marks the end of the finished prefix.
Invariant: *`nums[:w]` is the answer for the elements read so far.* The result is in place, stable,
O(n) time and O(1) space. For "keep each value at most `k` times" in a sorted list (ex03):

```python
def solve(nums: list[int], k: int) -> int:
    w = 0                                 # nums[:w] is the kept prefix
    for x in nums:                        # read pointer is implicit
        if w < k or nums[w - k] != x:
            nums[w] = x
            w += 1
    return w
```

Compare against the **kept** prefix (`nums[w - k]`), not the read side (`nums[r - k]`): the writer
may already have overwritten that slot, and `[1, 1, 1, 2, 2]` with `k = 2` loses a `2`. Lower
rungs: `del nums[i]` in a loop (O(n²)); a filtered copy (O(n) extra space).

**Three-way partition (Dutch national flag, ex04)** keeps four regions with three pointers:

```text
[ < pivot | == pivot | unknown ...... | > pivot ]
 0        lt         i               gt        n
```

`nums[i] < pivot` → swap to `lt`, advance both; `==` → advance `i`; `>` → swap with `gt - 1`,
shrink `gt`, and **do not** advance `i`, because the element that arrived from the right is
unexamined. One pass, O(1) space; `sort()` (O(n log n)) and collect-then-overwrite (O(n) space)
are the lower rungs. (→ §11.7 for quicksort).

## 10.3 Fast and slow pointers

Two pointers walk the same sequence at speeds 1 and 2. Inside a cycle the fast one closes the gap
by one step per move, so they must meet (Floyd). Linked lists are the canonical home (→ §13.4);
here the "list" is an array or a number sequence.

**Find the duplicate** (ex05): `n + 1` values in `1..n`, one value repeated (possibly many times);
don't modify the array (so §9.7's in-place marking is out); O(1) space. Treat `i → nums[i]` as a
linked structure from index 0. Index 0 has no incoming arrow (values ≥ 1), so the walk ends in a
cycle whose **entrance** has two incoming arrows: it is the duplicate.

```python
def solve(nums: list[int]) -> int:
    slow = fast = 0
    while True:                           # phase 1: meet inside the cycle
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = 0                              # phase 2: find the entrance
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
```

Why phase 2 works: with tail length `a`, meeting `b` steps into the cycle and cycle length `c`,
fast walked twice as far as slow, so `a + b` is a multiple of `c`; `a` more steps from the meeting
point land on the entrance, exactly where a pointer restarted at 0 arrives after `a` steps.

Ladder: all pairs, O(n²) → sorted copy or seen-set, O(n) extra space → binary search on the
value range, counting values ≤ mid, O(n log n) with O(1) space (a solid fallback) → Floyd, O(n).

The tempting `sum(nums) - n(n+1)/2` only works if the duplicate appears exactly twice (it returns
0 for `[2, 2, 2, 2, 2]`). The same loop detects whether a **happy number** reaches 1: the
digit-square sequence is eventually periodic, so Floyd replaces a seen-set.

## 10.4 Fixed-size sliding window

When every window has the same length `k`, slide by adding the entering element and subtracting
the leaving one: O(n) instead of O(n·k). Initialise `best` from the first window, not 0, or
all-negative inputs break.

```python
def solve(nums: list[int], k: int) -> int:
    if not 1 <= k <= len(nums):
        raise ValueError("need 1 <= k <= len(nums)")
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):         # i enters, i - k leaves
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best
```

Negative numbers are harmless: a fixed window never decides *when* to shrink. For a "maximum
average", keep the integer sum and divide once at the end. The trick needs an invertible update
(`+`/`−`, or `±1` on counts); a **max** cannot be subtracted (§10.7).

## 10.5 Variable-size sliding window (longest/shortest with condition)

A window `[left, right]` grows on the right every step and shrinks from the left only as needed.
The template is correct only when validity is **monotone**: shrinking a valid window keeps it valid
("longest"), or growing a valid window keeps it valid ("shortest"). Each index enters and leaves
once, so the scan is O(n) despite the inner `while`.

```text
Template — longest valid window          Template — shortest valid window
left = 0                                 left = 0
for right, x in enumerate(seq):          for right, x in enumerate(seq):
    add x to state                           add x to state
    while state is INVALID:                  while state is VALID:
        remove seq[left]; left += 1              record right - left + 1
    record right - left + 1                      remove seq[left]; left += 1
```

Invariant (longest): *after the inner loop, `seq[left:right+1]` is the longest valid window ending
at `right`*.

### Worked problem 2: longest substring without repeats

| Rung | Idea | Time | Why move up |
|---|---|---|---|
| Brute | every substring, `len(set(sub)) == len(sub)` | O(n³) | n = 5 × 10⁴ |
| Improved | from each start, extend until the first repeat | O(n·min(n, σ)) | restarts from scratch after each repeat |
| Optimal | window + set; shrink while the new char is inside | O(n) | — |

```python
def solve(s: str) -> int:
    window: set[str] = set()
    left = best = 0
    for right, c in enumerate(s):
        while c in window:                # shrink until valid again
            window.remove(s[left])
            left += 1
        window.add(c)
        best = max(best, right - left + 1)
    return best
```

```text
s='abcabcbb'  -> 3 'abc'    brute=3  jump=3  jump-without-max(wrong)=3
s='abba'      -> 2 'ab'     brute=2  jump=2  jump-without-max(wrong)=3
s='tmmzuxt'   -> 5 'mzuxt'  brute=5  jump=5  jump-without-max(wrong)=6
```

A faster-constant variant stores each character's last index and jumps
`left = max(left, last[c] + 1)`. **Wrong but tempting:** dropping the `max` lets `left` jump
*backwards* to a stale index — `"abba"` gives 3. Follow-ups: "at most k distinct" (shrink while
`len(counter) > k`) and "replace up to k characters" (shrink while `length - max_count > k`).
→ repo: `chapters/ch10_two_pointers_sliding_window_prefix_sums/solutions/ex07_longest_unique_substring.py`

**Wrong but tempting, part 2:** using this template for "longest subarray with sum ≤ k" when values
can be negative. Adding a negative number *lowers* the sum, so an invalid window can become valid
again by growing; the monotonicity is gone. Use prefix sums instead: for each `j`, binary-search
the running maximum of earlier prefixes for the first `i` with `P[i] ≥ P[j] − k`, O(n log n).

## 10.6 Window with hash map (distinct characters, anagram windows)

When validity depends on counts, keep a window `Counter` plus one integer summarising it, so the
validity test stays O(1). **Permutation in string** (ex08) is a *fixed* window of length `len(p)`
tracking `matched`, the number of characters whose count equals the target. The tempting
`set(window) == set(p)` ignores multiplicities.

### Worked problem 3: minimum window containing all of `t`

*Shortest substring of `s` containing every character of `t` with multiplicity; leftmost on ties;
`""` if none.*

| Rung | Idea | Time | Why move up |
|---|---|---|---|
| Brute | every substring, Counter "covers" check | O(n²·(n + m)) | cubic |
| Improved | from each start, extend until it covers, then stop | O(n²) | restarts per start |
| Optimal | shortest-window template + `missing` counter | O(n + m) | — |

```python
from collections import Counter


def solve(s: str, t: str) -> str:
    if not t:
        return ""
    need = Counter(t)
    missing = len(t)                      # required chars still absent
    left, best_len, best_start = 0, len(s) + 1, 0
    for right, c in enumerate(s):
        if need[c] > 0:
            missing -= 1                  # c was still needed
        need[c] -= 1                      # negative = surplus in window
        while missing == 0:               # valid: try to shrink
            if right - left + 1 < best_len:
                best_len, best_start = right - left + 1, left
            d = s[left]
            need[d] += 1
            if need[d] > 0:
                missing += 1              # removing d broke validity
            left += 1
    return "" if best_len > len(s) else s[best_start:best_start + best_len]
```

```text
s='ADOBECODEBANC'      t='ABC'  -> 'BANC'  brute='BANC'  extend='BANC'  any-required(wrong)='BANC'
s='bbaac'              t='aba'  -> 'baa'   brute='baa'   extend='baa'   any-required(wrong)='bba'
```

`need[c] > 0` means "still missing", negative means "surplus". Invariant: *while `missing == 0` the window covers `t`*, and we record it before every shrink.
**Wrong but tempting:** decrementing `missing` for *every* entering character of `t`, even a
surplus one — `'bba'` "covers" `aba` with a single `a`. Edge cases: empty `t`, `t` longer than `s`,
case sensitivity, repeated characters in `t`. → repo: `chapters/ch10_two_pointers_sliding_window_prefix_sums/solutions/ex09_min_window_substring.py`

## 10.7 Sliding window maximum → links to monotonic deque (Ch. 12)

The fixed-window trick fails for max/min: you cannot subtract the leaving element. Brute force is
O(n·k); a heap with lazy deletion is O(n log n). The O(n) answer keeps a deque of indices with
decreasing values; the front is the window max, and smaller values behind a newcomer are popped
because they can never be a maximum again. ex06 (`window_maxima`) implements it; §12.6 teaches it.

## 10.8 Prefix sums: 1D and 2D

Let `P[0] = 0` and `P[i+1] = P[i] + nums[i]`; then `sum(nums[i:j]) == P[j] - P[i]`. One O(n) pass
buys O(1) range queries, and `itertools.accumulate` builds it: `P = [0, *accumulate(nums)]`. The
leading zero removes every `i == 0` special case.

In 2D, `P[i][j]` is the sum of the rectangle above-left of `(i, j)`, again padded with a zero row
and column. Build by inclusion–exclusion, query with four corners:

```python
class NumMatrix:
    def __init__(self, grid: list[list[int]]) -> None:
        rows, cols = len(grid), len(grid[0]) if grid else 0
        p = [[0] * (cols + 1) for _ in range(rows + 1)]
        for i in range(rows):
            for j in range(cols):
                p[i + 1][j + 1] = grid[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j]
        self.p = p

    def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
        p = self.p
        return p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1]
```

```text
grid=[[3, 0, 1], [5, 6, 3], [1, 2, 0]] sum_region(1, 1, 2, 2) -> 11  brute=11
```

The ladder is per query: O(r·c) by summing, O(r) with one prefix array per row, O(1) with the 2D
table after an O(r·c) build. Without padding, `P[r1 - 1]` with `r1 = 0` silently reads `P[-1]`,
the **last** row — a Python-specific bug that raises no error. Prefix sums suit *static* data; with
interleaved point updates use a Fenwick tree (→ §22.9).

## 10.9 Prefix sum + hash map (count subarrays with sum k)

### Worked problem 4: count subarrays summing to k

*Count non-empty contiguous subarrays with sum exactly `k`; negatives and zeros allowed.*

| Rung | Idea | Time | Why move up |
|---|---|---|---|
| Brute | `sum(nums[i:j])` for every pair | O(n³) | recomputes every sum |
| Improved | fix `i`, extend `j` with a running sum | O(n²) | n = 2 × 10⁴ → 2 × 10⁸ steps |
| Optimal | `P[j] - P[i] == k` ⇔ `P[i] == P[j] - k`; count earlier prefixes | O(n), O(n) space | — |

It is two-sum (→ §9.3) on prefix sums: for each `j`, ask how many earlier prefixes equal
`P[j] - k`.

```python
from collections import Counter


def solve(nums: list[int], k: int) -> int:
    seen = Counter({0: 1})                # prefix sum of the empty prefix
    prefix = count = 0
    for x in nums:
        prefix += x
        count += seen[prefix - k]         # earlier prefixes P[i] = P[j] - k
        seen[prefix] += 1                 # record AFTER the lookup
    return count
```

```text
nums=[3, 4, -7, 3, 1, 3, 1, -4]   k=7 -> 3  brute=3  longest=6  sliding-window(wrong)=2
nums=[1, -1, 1, -1]               k=0 -> 4  brute=4  longest=4  sliding-window(wrong)=1
nums=[0, 0, 0]                    k=0 -> 6  brute=6  longest=3  sliding-window(wrong)=3
```

**Wrong but tempting:** a sliding window ("shrink while sum > k"). It is correct only for strictly
positive values; the last column shows it under-counting with negatives or zeros, because a "too
big" window can become exact again by growing. Also: without the `{0: 1}` seed, subarrays starting
at index 0 are missed; recording `prefix` before the lookup counts empty subarrays when `k == 0`.
For the *longest* such subarray, store each prefix sum's **first** index. Follow-ups: sum divisible
by `m` (key on `P mod m`); equal 0s and 1s (map 0 → −1, find sum 0).
→ repo: `chapters/ch10_two_pointers_sliding_window_prefix_sums/solutions/ex10_subarray_sum_k.py`

## 10.10 Difference arrays for range updates ◆

A difference array is the inverse of a prefix sum. To add `d` to every position `lo..hi`, write
only the boundaries, then take one prefix sum at the end: O(n + q) instead of O(n·q).

```python
from itertools import accumulate


def solve(n: int, updates: list[tuple[int, int, int]]) -> list[int]:
    diff = [0] * (n + 1)                  # one spare slot for hi + 1
    for lo, hi, delta in updates:
        diff[lo] += delta
        diff[hi + 1] -= delta
    return list(accumulate(diff[:n]))
```

```text
n=5 updates=[(1, 3, 2), (2, 4, 3), (0, 2, -2)] -> [-2, 0, 3, 5, 3]  brute agrees: True
```

Prefix sums answer many **queries** on fixed data; difference arrays apply many **updates** and read
once. Watch interval conventions: passengers on a half-open trip `[start, end)` leave *at* `end`,
so subtract at `end`, not `end + 1`; ex12's `peak_load` shows the inclusive mistake reporting 5
passengers instead of 3. For huge, sparse coordinates, sort the boundary events instead (sweep
line, → §17.9).

## 10.11 Practice set

### Exercises

Details, patterns and run commands: `chapters/ch10_two_pointers_sliding_window_prefix_sums/README.md`.

| # | Title | Tier |
|---|---|---|
| ex01 | Three sum | ★ |
| ex02 | Container with most water | ★ |
| ex03 | At most k copies, in place | ★ |
| ex04 | Dutch flag partition | ◆ |
| ex05 | Find duplicate; happy number | ◆ |
| ex06 | Fixed window; window max | ★ |
| ex07 | Longest unique substring | ★ |
| ex08 | Permutation in string | ★ |
| ex09 | Minimum window substring | ◆ |
| ex10 | Subarray sum equals k | ★ |
| ex11 | Range sums, 1D and 2D | ★ |
| ex12 | Difference array updates | ◆ |

## Interviewer's view

- **Justify every pointer move** and **name the window invariant** before writing the `while`.
- **Check preconditions:** negatives before a window; sorted (or sortable) before opposite pointers.
- **State brute force first** and keep it as a test oracle.
- Points are lost on window length (`right - left + 1`), empty and all-equal input.

## Checkpoint quiz

1. Why may opposite-direction pointers move `lo` forward when the pair sum is too small?
2. You need the longest subarray with sum ≤ k, and values can be negative. Window or not?
3. In "count subarrays with sum k", why seed the counter with `{0: 1}`?
4. In the Dutch flag loop, why is `i` not advanced after swapping with `gt - 1`?
5. Why does the fixed-window "add one, subtract one" trick fail for window maximum?

<details>
<summary>Answers</summary>

1. The array is sorted, so `nums[lo]` paired with anything at or left of `hi` gives a sum no
   larger than the current one: every pair using `lo` is too small, and none can be the answer.
2. Not a window: negatives break monotonicity; see §10.5, part 2.
3. It is the empty prefix `P[0] = 0`; without it, subarrays that start at index 0 are never counted.
4. The element swapped in from the right has not been examined yet; advancing would skip it.
5. Max is not invertible: after the maximum leaves you cannot recover the next one from the old
   max. Use a monotonic deque (§12.6), O(n) amortised.

</details>

## Summary card

- **Opposite pointers:** sorted input; move the provably finished side. O(n) per scan; 3-sum O(n²).
- **Read/write pointers:** `nums[:w]` is the answer so far. Dutch flag: three regions; don't
  advance `i` after a right swap.
- **Fast/slow:** meet inside the cycle; restart one at the start to find the entrance.
- **Fixed window:** `+entering − leaving`; init `best` with the first window.
- **Variable window:** monotone validity; longest = shrink while invalid, shortest = shrink while
  valid. O(n).
- **Window + counts:** Counter plus one summary integer (`matched`, `missing`) keeps checks O(1).
- **Window max/min:** monotonic deque (§12.6).
- **Prefix sums:** `P = [0, *accumulate(nums)]`; 2D uses four corners; pad to avoid `P[-1]`.
- **Exact sum / negatives:** prefix sum + hash map, seed `{0: 1}`, look up before recording.
- **Range updates:** difference array, one prefix pass at the end; mind inclusive vs half-open.
