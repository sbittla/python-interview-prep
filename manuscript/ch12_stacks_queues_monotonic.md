# Chapter 12. Stacks, Queues and Monotonic Structures

★ Core · Tracks S, M, L · Study time ≈ 6 h · Prerequisites: Ch. 6 (`deque`), Ch. 8 (Big-O), Ch. 10 (sliding windows)

**Learning objectives**

- Choose `list` for a stack and `collections.deque` for a queue, and know the cost of each operation.
- Solve matching and evaluation problems with an explicit stack.
- Recognise "next greater / previous smaller" problems and write the monotonic-stack template from memory.
- Prove the template is O(n) with the push-once / pop-once argument.
- Design small containers (min stack, queue from stacks, ring buffer) with stated amortised bounds.

> **Recognise it**
>
> | Signal in the problem | Reach for |
> |---|---|
> | Nested / matching pairs, "most recent unmatched", undo, DFS without recursion | Stack |
> | Process in arrival order, BFS, "first come first served" | `deque` queue |
> | "Next/previous greater/smaller", "how many days until", "span", nearest blocker | Monotonic stack |
> | Area/water bounded by the nearest lower/higher bar on each side | Monotonic stack (or two pointers) |
> | Max/min of every window of size k, n up to 10⁵ | Monotonic deque |
> | "O(1) get_min", "queue with only stacks", fixed-size buffer | Stack/queue design |
>
> Constraint hint: n ≈ 10⁵ with an obvious O(n²) "scan right for each i" solution almost always
> means a monotonic stack or deque.

## 12.1 Stack with a list; queue with `deque`

```python
from collections import deque
stack = []
stack.append('a'); stack.append('b')
print(stack.pop(), stack[-1], len(stack))
q = deque(['a', 'b'])
q.append('c')
print(q.popleft(), q[0], list(q))
```

```text
b a 1
a b ['b', 'c']
```

| Operation | `list` | `deque` |
|---|---|---|
| push/pop at the right end | O(1) amortised | O(1) |
| pop/insert at the left end | **O(n)** (`pop(0)`, `insert(0, x)`) | O(1) (`popleft`, `appendleft`) |
| index `x[i]` in the middle | O(1) | O(n) (O(1) at either end) |

Pitfalls: `list.pop(0)` as a queue turns an O(n) BFS into O(n²); an empty `pop()` raises
`IndexError`, so guard with `if stack:`. For producer/consumer threads use `queue.Queue`
(blocking `get`/`put` with timeouts); `deque` is the tool inside single-threaded algorithms.

## 12.2 Balanced parentheses and expression evaluation

A stack answers "what is the most recent thing still open?" Our version also reports *where*
the first error is, which is what an editor needs — so the stack holds indices, not characters.

```python
PAIRS = {")": "(", "]": "[", "}": "{"}
OPENERS = set(PAIRS.values())

def first_error(s: str) -> int:
    stack: list[int] = []                      # indices of unmatched openers
    for i, ch in enumerate(s):
        if ch in OPENERS:
            stack.append(i)
        elif ch in PAIRS:
            if not stack or s[stack[-1]] != PAIRS[ch]:
                return i                       # stray or wrong-kind closer
            stack.pop()
    return stack[0] if stack else -1           # leftmost unclosed opener
```

(`agree` confirms the brute-force rung gives the same answer; `^` marks the error.)

```text
'(]'              ->  1  agree=True
  ^
'x = (a + [b)'    -> 11  agree=True
            ^
```

The brute-force rung deletes adjacent matching pairs until nothing changes, O(n²); the stack is
O(n). **Wrong but tempting:** comparing counts of `(` and `)` accepts `")("` and `"([)]"`;
forgetting the end-of-string check reports `"(("` as balanced.

**Expression evaluation.** Reverse Polish Notation needs one operand stack: push numbers; an
operator pops `b` *then* `a` and pushes `a op b`. Infix (a "basic calculator") has two rungs:
(1) shunting-yard converts to RPN with an operator stack, then evaluate — two passes; (2) one
pass with a stack of *terms to sum*: `+x` pushes `x`, `-x` pushes `-x`, `*`/`/` combine with the
top, and `(` recurses. Both are O(n). The classic trap is division:

```text
python -7 // 2 = -4   trunc_div(-7, 2) = -3
```

Python's `//` floors; interview specs usually want truncation toward zero. `int(a / b)` truncates
but goes through a float and breaks on large integers, so the repo uses exact integer logic.
→ repo: `chapters/ch12_stacks_queues_monotonic/solutions/ex02_expression_evaluation.py`

## 12.3 Min stack and stack design problems

Need `push`, `pop`, `top`, `get_min` all O(1). Rung 1 scans with `min()` — O(n). A single
`self.min` fails because after popping the minimum you cannot recover the previous one. The key
fact: *while an entry is on the stack, the minimum of everything below it never changes*, so
store it with the entry.

```python
class MinStack:
    def __init__(self) -> None:
        self._items: list[tuple[int, int]] = []     # (value, min of stack up to here)

    def push(self, x: int) -> None:
        current = min(x, self._items[-1][1]) if self._items else x
        self._items.append((x, current))

    def pop(self) -> int:
        return self._items.pop()[0]
```

(`top` and `get_min` read `self._items[-1]`.) The space-saving variant keeps a second stack of
minimums and pushes when `x <= current_min`; writing `<` instead loses duplicate minimums.
The same "cache the answer per entry" idea gives a max stack, and a queue with `get_min` is
two min-stacks glued together as in §12.7.

## 12.4 Monotonic stack: next greater/smaller element, stock span

**Worked problem 1 — Days until warmer.** For each day, how many days until a strictly warmer
one (0 if never)?

*Rung 1, brute force.* Scan right from every day: O(n²) on a cooling streak.

*Rung 2, jump back.* Fill answers right to left; to find the next warmer day after `i`, hop
`j += ans[j]` over days already known to be no warmer (`<=`) than day `i`. O(n) amortised, but hard to justify aloud.

*Rung 3, monotonic stack.* Keep the indices of days *still waiting* for an answer. Their
temperatures are non-increasing from bottom to top — if a warmer day were above a colder one, the
colder one would already have been answered. A new day pops every colder waiting day and answers
it.

```python
def days_until_warmer(temps: list[int]) -> list[int]:
    out = [0] * len(temps)
    stack: list[int] = []                      # indices waiting for a warmer day
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out
```

Trace for `[73, 74, 75, 71, 69, 72, 76, 73]` (real output of `trace()` in the repo file):

```text
 i   t  popped (day:wait)    stack after (temps)
 0  73  -                    [73]
 1  74  0:1                  [74]
 2  75  1:1                  [75]
 3  71  -                    [75, 71]
 4  69  -                    [75, 71, 69]
 5  72  4:1 3:2              [75, 72]
 6  76  5:1 2:4              [76]
 7  73  -                    [76, 73]
answer [1, 1, 4, 2, 1, 1, 0, 0]
```

Day 5 (72) resolves two waiting days at once; day 6 (76) resolves day 2 after four days.

**Why O(n), not O(n²).** The inner `while` can pop many items in one step, but count the work
per *index* instead of per step: every index is pushed exactly once and popped at most once.
Total pushes ≤ n, total pops ≤ n, so the whole loop does at most 2n stack operations plus n
comparisons that end a `while` — O(n) total, O(1) amortised per element. Use this argument
verbatim in interviews; "nested loop, therefore O(n²)" is the classic wrong answer.

**The template's knobs.**

| Want | Scan | Pop while top is … | Answer written |
|---|---|---|---|
| next greater | left→right | `< x` | at pop time |
| next smaller | left→right | `> x` | at pop time |
| previous greater | left→right | `<= x` | stack top *after* popping |
| distance instead of value | — | — | `i - j` |

Strict vs non-strict comparison decides how equal values behave: the question says "strictly
warmer", so equal temperatures must not pop.

**Circular next greater.** Walk `2n` positions using `nums[k % n]` and push only when `k < n`;
the second lap lets the tail see the head. Same O(n).

**Stock span** (days in a row, ending today, with price ≤ today's) is "previous greater" in
online form: store `(price, span)` pairs; a new price pops every entry `<=` it and *adds their
spans* to its own. Forgetting to add (counting popped entries instead) is the usual bug.
→ repo: `chapters/ch12_stacks_queues_monotonic/solutions/ex05_stock_span.py`

## 12.5 Largest rectangle in histogram; trapping rain water

**Worked problem 2 — Largest rectangle.** Bars of width 1; find the largest rectangle inside.

*Rung 1.* For every left edge, extend right while tracking the running minimum height:
O(n²).

*Rung 2.* Reframe: the best rectangle whose **shortest bar is `i`** stretches from the previous
smaller bar to the next smaller bar. Two monotonic-stack passes give both boundaries;
area = `h[i] * (right[i] - left[i] - 1)`. O(n), three passes.

*Rung 3.* Do it in one pass with a non-decreasing stack. When bar `i` is lower than the top, the
top has just found its right boundary (`i`), and its left boundary is the index *under it* on
the stack. A sentinel 0 at the end flushes everything.

```python
def largest_rectangle(heights: list[int]) -> int:
    best = 0
    stack: list[int] = []                      # indices; heights non-decreasing
    for i, h in enumerate(heights + [0]):      # sentinel 0 flushes the stack
        while stack and heights[stack[-1]] > h:
            top = stack.pop()
            left = stack[-1] if stack else -1  # previous smaller bar
            best = max(best, heights[top] * (i - left - 1))
        stack.append(i)
    return best
```

```text
[2, 1, 5, 6, 2, 3]       -> 10  agree=True
[2, 4]                   ->  4  agree=True
[1, 2, 3, 4, 5]          ->  9  agree=True
```

(`agree` checks rungs 1–3 against each other.) **Wrong but tempting:** width `i - top`
instead of `i - left - 1` ignores the bars between the previous smaller bar and `top`, which
were popped earlier and are at least as tall; dropping the sentinel misses every rectangle in an
increasing histogram. (With equal heights `left` may be an equal bar; its own pop later computes
the full width, so the maximum is unaffected.) Follow-up: maximal rectangle of 1s in a binary matrix = this function on
each row's column heights.

**Worked problem 3 — Trapping rain water.** Water above `i` rises to
`min(max left of i, max right of i)` minus the wall height.

| Rung | Idea | Time | Space |
|---|---|---|---|
| 1 Brute force | recompute both maxima for each `i` (index loops) | O(n²) | O(1) |
| 2 Prefix max | `left_max[]`, `right_max[]` in two passes | O(n) | O(n) |
| 3A Two pointers | settle the side whose running max is smaller | O(n) | O(1) |
| 3B Monotonic stack | fill horizontal layers when a taller wall arrives | O(n) | O(n) |

Why rung 3A works: if `left_max <= right_max`, the true maximum to the right of `lo` is at least
`right_max`, so the level at `lo` is decided by `left_max` alone.

```python
def trap(heights: list[int]) -> int:           # two pointers, O(1) extra space
    lo, hi = 0, len(heights) - 1
    left_max = right_max = total = 0
    while lo <= hi:
        if left_max <= right_max:              # left side is the bottleneck
            left_max = max(left_max, heights[lo])
            total += left_max - heights[lo]
            lo += 1
        else:
            right_max = max(right_max, heights[hi])
            total += right_max - heights[hi]
            hi -= 1
    return total
```

```text
[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]   ->  6  agree=True
[4, 2, 0, 3, 2, 5]                     ->  9  agree=True
```

**Wrong but tempting:** `max(left_max, right_max)` (water spills over the *lower* wall); moving
the pointer on the taller side. Rung 3B is worth knowing because it is the same stack as
Problem 2: pop a "floor", and the new top and the current bar are its walls.
→ repo: `chapters/ch12_stacks_queues_monotonic/solutions/ex08_trapping_rain_water.py`

## 12.6 Monotonic deque: sliding window maximum (canonical home)

**Worked problem 4.** Return the maximum of every window of size `k`.

*Rung 1.* `max(nums[i:i+k])` per window: O(nk).
*Rung 2.* Max-heap of `(-value, index)`, lazily popping entries whose index left the window:
O(n log n). Stale entries pile up and the log factor is avoidable.
*Rung 3.* A deque of indices whose values **decrease** front to back. A new value evicts every
smaller-or-equal value from the back — those can never be a maximum again, because the newcomer
is at least as large and leaves the window later. The front is the current maximum; drop it when
it expires.

```python
from collections import deque

def max_sliding_window(nums: list[int], k: int) -> list[int]:
    _check(nums, k)                            # ValueError unless 1 <= k <= len(nums)
    dq: deque[int] = deque()                   # indices; values decreasing front→back
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                           # dominated: can never be a max again
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                       # front left the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```

```text
 i   x  deque (values)   max
 0   1  [1]              -
 1   3  [3]              -
 2  -1  [3, -1]          3
 3  -3  [3, -1, -3]      3
 4   5  [5]              5
 5   3  [5, 3]           5
 6   6  [6]              6
 7   7  [7]              7
```

Each index is appended once and removed (from either end) at most once: O(n) time, O(k)
space — the same push-once/pop-once argument as §12.4. One `if` suffices for expiry because the
window moves by one, so at most one index leaves per step. Store indices, not values, or you
cannot tell when the front expired. For minimums flip the comparison; two deques (max and min)
handle "longest subarray with `max - min <= limit`" in a variable window (→ §10.5). This is also
the structure §10.7 points to.

## 12.7 Queue via stacks, stack via queues

Two lists: `inbox` receives pushes; `outbox` serves pops. Only when `outbox` is empty, pour all
of `inbox` into it, which reverses the order into FIFO.

```python
    def push(self, x: int) -> None:
        self._inbox.append(x)

    def pop(self) -> int:
        self._shift()
        return self._outbox.pop()

    def _shift(self) -> None:
        if not self._outbox:                    # only refill when empty
            while self._inbox:
                self._outbox.append(self._inbox.pop())
                self.moves += 1
        if not self._outbox:
            raise IndexError("queue is empty")
```

**Amortised O(1).** One pop after n pushes costs O(n), so the worst case per call is O(n). But
each element makes the trip `inbox → outbox` once in its life: push 1, move 1, pop 1 — three
O(1) steps per element, O(n) for any sequence of n operations. The repo counts it:

```text
1000 pushes -> moves=1000 (each element moved at most once: True)
```

Pouring while `outbox` is non-empty is the classic bug: new elements land on top of older ones.
The rungs below it are a list with `pop(0)` (O(n) per dequeue) and an eager version that pours
back and forth on every push.

**Stack via one queue:** after appending `x`, rotate the older `len - 1` items (`popleft` then
`append`) so `x` is at the front. Push is O(n), pop O(1); in the standard constructions one
operation always pays O(n) — there is no inbox/outbox-style amortised trick.

## 12.8 Circular queue design

A ring buffer pre-allocates `capacity` slots and moves indices instead of data. With `head` and
`tail` alone, `head == tail` means both empty and full; the textbook fix wastes a slot. Storing
`head` and `size` removes the ambiguity:

| Quantity | Formula |
|---|---|
| front slot | `head` |
| rear slot | `(head + size - 1) % cap` |
| next free slot | `(head + size) % cap` |
| empty / full | `size == 0` / `size == cap` |

`enqueue` returns `False` when full; `dequeue` advances `head = (head + 1) % cap` and clears
the slot so large objects can be garbage-collected. Do not substitute `deque(maxlen=...)`: it
silently drops the oldest item instead of rejecting the new one.

```text
deque(maxlen=3) after append(4): [2, 3, 4]  (oldest silently dropped)
```

→ repo: `chapters/ch12_stacks_queues_monotonic/solutions/ex11_circular_queue.py`

## 12.9 Practice set

Work the eleven exercises below in order; each stub lists hints and every test cross-checks the
slow rungs against the fast one on seeded random inputs. More stack and queue problems are in
the Chapter 45 problem bank, numbers 057–066.

## Interviewer's view

- **Name the invariant.** "The stack holds indices still waiting for an answer, values
  non-increasing" earns more than correct code with no explanation.
- **Prove the complexity.** State the push-once/pop-once argument; candidates who call the
  nested `while` O(n²) lose the optimisation signal.
- **Indices over values.** Distances, widths and window expiry all need indices.
- **Edge cases spoken aloud:** empty input, all equal, strictly increasing/decreasing, one
  element, `k == n`.
- **Design questions:** say "amortised" precisely and give the worst case too.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Balanced brackets with error position | ★ | stack matching |
| ex02 | RPN evaluation and basic calculator | ★ | operand/operator stacks |
| ex03 | Min stack in O(1) | ★ | augmented stack |
| ex04 | Next greater/smaller element, circular | ★ | monotonic stack |
| ex05 | Online stock span | ★ | monotonic stack, merged counts |
| ex06 | Days until warmer | ★ | monotonic stack (distance) |
| ex07 | Largest rectangle in histogram | ★ | previous/next smaller |
| ex08 | Trapping rain water | ★ | prefix max, two pointers, stack |
| ex09 | Sliding window maximum | ★ | monotonic deque |
| ex10 | Queue via two stacks; stack via queue | ★ | amortised design |
| ex11 | Fixed-capacity circular queue | ◆ | ring buffer |

Code: `chapters/ch12_stacks_queues_monotonic/` (index in
`chapters/ch12_stacks_queues_monotonic/README.md`).

## Checkpoint quiz

1. Why is `list.pop(0)` a poor queue operation, and what replaces it?
2. In next-greater-element, what does the stack contain, and in what order are its values?
3. A candidate says the monotonic-stack solution is O(n²) because of the nested loop. Refute it.
4. In the one-pass largest-rectangle algorithm, why is the width `i - left - 1` and not
   `i - top`?
5. A queue built from two stacks: what is the worst-case cost of one `pop`, and why is the
   amortised cost O(1)?

<details>
<summary>Answers</summary>

1. It shifts every remaining element: O(n) per call. Use `collections.deque.popleft()`, O(1).
2. Indices whose next greater element is not yet known; their values are non-increasing from
   bottom to top.
3. Each index is pushed once and popped at most once, so total stack operations ≤ 2n across the
   whole run: O(n), amortised O(1) per element.
4. The popped bar `top` is the shortest bar of a rectangle that reaches left to just after the
   previous smaller bar (`left`, the new stack top); bars between were popped earlier and are
   at least as tall.
5. O(n), when `outbox` is empty and `inbox` holds n items. Every element is moved from `inbox`
   to `outbox` at most once, so n operations cost O(n) total.

</details>

## Summary card

- **Stack = `list`** (`append`/`pop`/`[-1]`); **queue = `deque`** (`append`/`popleft`). Never `pop(0)`.
- **Matching:** stack of opener indices; check the end for leftovers.
- **Expressions:** RPN needs one operand stack (pop `b` then `a`); infix = shunting-yard or a
  one-pass term stack. Python `//` floors — truncate explicitly.
- **Min stack:** store `(value, min_so_far)`; the minimum below an entry never changes.
- **Monotonic stack:** indices waiting for an answer; pop while the new value beats the top;
  strict vs non-strict comparison controls ties; circular = 2n lap with `% n`.
- **O(n) proof:** each index pushed once, popped at most once.
- **Histogram:** area at pop time, `width = i - left - 1`, sentinel 0.
- **Rain water:** `min(left_max, right_max) - h`; two pointers settle the smaller side, O(1) space.
- **Sliding max:** deque of indices, values decreasing; evict `<=` from the back, expired from the front.
- **Queue via stacks:** refill `outbox` only when empty; amortised O(1), worst O(n).
- **Ring buffer:** `head` + `size`; rear `(head + size - 1) % cap`; `deque(maxlen)` drops, it does not reject.
