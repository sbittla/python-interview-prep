# Chapter 15. Heaps and Top-K

Tier ★ Core · Tracks S, M, L · Study time ≈ 5 h · Prerequisites: Ch 6 (`heapq`, §6.8), Ch 7 (§7.20), Ch 8 (Big-O)

**Learning objectives**

- Draw a heap as an array, use the index formulas, and explain why heapify is O(n).
- Use `heapq` as a min-heap, max-heap and priority queue with safe tie-breakers.
- Choose between sort, size-k heap, buckets and quickselect for top-K.
- Solve k-way merge, two-heap median and scheduling problems with an approach ladder.

> **Recognise it**
>
> | Signal in the prompt | Reach for |
> |---|---|
> | "k largest / smallest / closest / most frequent", k ≪ n | size-k heap, O(n log k) (§15.3, §15.4, §15.9) |
> | "stream", "after each insertion", "too big for memory" | bounded heap; never re-sort |
> | "merge k sorted …" | heap of one head per source (§15.6) |
> | "running median", "balance two halves" | two heaps (§15.7) |
> | "next job / earliest free room" | priority-queue simulation (§15.8) |
> | "k-th element, one shot, O(n) expected" | quickselect (§15.5, → §11.13) |

## 15.1 Heap property and array representation

A **min-heap** is a complete binary tree where every parent is ≤ its children. Complete (every
level full except the last, filled left to right) means it packs into a list with no pointers.
For 0-based index `i`: parent `(i - 1) // 2`, children `2i + 1` and `2i + 2`.

```text
index:  0  1  2  3  4  5  6                1(0)
value: [1, 4, 2, 9, 8, 7, 6]             /      \
                                      4(1)      2(2)
                                      /  \      /  \
                                   9(3) 8(4)  7(5) 6(6)
```

Siblings are unordered. Push = append + **sift up** (swap with the parent while smaller);
pop = move the last item to the root + **sift down** (swap with the *smaller* child while
larger): O(log n) each. **Heapify** sifts down every internal node, last first:

```python
def sift_down(a: list, i: int, n: int) -> None:
    while (c := 2 * i + 1) < n:              # left child exists
        if c + 1 < n and a[c + 1] < a[c]:
            c += 1                           # pick the smaller child
        if not a[c] < a[i]:
            break
        a[i], a[c] = a[c], a[i]
        i = c


def heapify(a: list) -> None:
    for i in range(len(a) // 2 - 1, -1, -1):  # last internal node -> root
        sift_down(a, i, len(a))


a = [9, 4, 7, 1, 8, 2, 6]
heapify(a)
print(a)
```

```text
[1, 4, 2, 9, 8, 7, 6]
```

**Why heapify is O(n).** About n / 2^(h+1) nodes have height h, each sifting down ≤ h levels:
total ≤ n · Σ h/2^(h+1) = n. Pushes sift *up*; the many deep nodes may climb the full height:
O(n log n). ex01 counts swaps on descending input: n = 8191 → heapify 8,178, pushes 90,114.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex01_min_heap.py`. Heap sort: §11.8.

## 15.2 `heapq` in practice (max-heap by negation, tuples, tie-breakers)

`heapq` (API in §6.8) is functions over a plain list: min-heap only, comparing with `<` alone.
Three habits cover most interview uses (pitfalls in §7.20):

1. **Max-heap**: push `-x`, negate on the way out (§15.7); wrap strings instead (§15.4). Python
   3.14 adds public `heappush_max`/`heappop_max`; don't rely on them in 3.10+ code.
2. **Priority + payload**: tuples compare field by field, so a priority tie compares the
   payloads — a `TypeError` for dicts, raised by whichever push or pop first compares two
   tied entries, often far from the line that caused it.
3. **Counter trick**: push `(priority, next(seq), payload)`, `seq = itertools.count()`. The
   unique tie-breaker ends the comparison before the payload; ties come out FIFO.

```python
import heapq
from itertools import count

jobs = [(2, {"name": "b"}), (1, {"name": "a"}), (2, {"name": "c"})]
bad = list(jobs)
heapq.heapify(bad)
try:
    heapq.heappop(bad)                        # two priority-2 entries meet -> dicts compared
except TypeError as e:
    print("TypeError:", e)

heap: list = []
seq = count()                                 # unique, increasing tie-breaker
for pri, payload in jobs:
    heapq.heappush(heap, (pri, next(seq), payload))
print([heapq.heappop(heap)[2]["name"] for _ in range(len(heap))])
```

```text
TypeError: '<' not supported between instances of 'dict' and 'dict'
['a', 'b', 'c']
```

One sift instead of two: `heapreplace(h, x)` pops then pushes (may return more than x);
`heappushpop(h, x)` pushes then pops (returns x at once if x ≤ root).

## 15.3 Kth largest / smallest element

The k-th largest is the **minimum of the k largest**: keep a size-k *min*-heap; a new value
enters only if it beats the root, which it evicts. O(n log k), O(k) memory, streamable:

```python
import heapq


class KthLargest:
    def __init__(self, k: int) -> None:
        self.k, self.heap = k, []

    def add(self, x: int) -> int | None:
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, x)
        elif x > self.heap[0]:
            heapq.heapreplace(self.heap, x)          # evict the old k-th largest
        return self.heap[0] if len(self.heap) == self.k else None


t = KthLargest(3)
print([t.add(x) for x in [4, 5, 8, 2, 3, 5, 10, 9, 4]])
```

```text
[None, None, 4, 4, 4, 5, 5, 8, 8]
```

Ladder, cost per add: re-sort, O(n log n) → `bisect.insort`, O(n), memory grows → size-k heap,
O(log k), O(k) memory. k-th *smallest*: size-k max-heap.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex02_kth_largest_stream.py` (also seeds from a batch)

## 15.4 Top-K frequent: heap vs bucket sort vs sort trade-offs

**Worked problem 1 — top-K frequent words.** Return the k most frequent words, highest count
first, ties alphabetical (integer version: Ch 9 ex04).

| Rung | Idea | Time | Space beyond `Counter` | Why move on |
|---|---|---|---|---|
| Sort | sort d words by `(-count, word)` | O(n + d log d) | O(d) | sorts words you discard |
| `nsmallest` | `nsmallest(k, c, key=lambda w: (-c[w], w))` | O(n + d log k) | O(k) | one-shot: no running top-k as counts arrive |
| Size-k heap | hand-rolled; root = worst kept word | O(n + d log k) | O(k) | streams; the usual follow-up |
| Bucket | `bucket[count]` → words, scan high to low | O(n) + sort within buckets | O(n) | ties force a sort |

The hand-rolled root must be the *worst* kept word: lowest count, then alphabetically
**latest**. Counts ascend, words descend, and strings can't be negated:

```python
import heapq
from collections import Counter


class Rev(str):                               # a str that sorts in reverse
    def __lt__(self, other: str) -> bool:
        return str.__gt__(self, other)


def top_k_words(words: list[str], k: int) -> list[str]:
    heap: list[tuple[int, Rev]] = []          # root = worst kept word
    for word, c in Counter(words).items():
        heapq.heappush(heap, (c, Rev(word)))
        if len(heap) > k:
            heapq.heappop(heap)
    return [str(heapq.heappop(heap)[1]) for _ in range(len(heap))][::-1]


words = ["to", "be", "or", "not", "to", "be"]
print(top_k_words(words, 3))
c = Counter(words)
print(heapq.nsmallest(3, c, key=lambda w: (-c[w], w)))
```

```text
['be', 'to', 'not']
['be', 'to', 'not']
```

**Wrong but tempting.** Plain `(count, word)` tuples evict the alphabetically *smaller* word on a
tie — the one you wanted (repo demo: k = 1 on `["b","b","a","a","c"]` keeps `b`).
`(-count, word)` with eviction pops the *most* frequent. **Choose:** k ≪ d → heap; k ≈ d →
sort; small counts, no tie rule → buckets. **Edge cases:** all words tie, k = d, one
word, k = 1 with a tie. **Follow-up:** per-shard top-k can't give the global top-k (merge full
counts); lazy deletion when counts change.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex03_top_k_frequent_words.py`

## 15.5 Quickselect as the Top-K follow-up ◆

"Can you beat O(n log k)?" Quickselect (§11.13) partitions around a random pivot and continues
only into the side holding index n − k: O(n) expected, O(n²) worst. Then `a[n-k:]` holds the k
largest, unordered (sort them: O(n + k log k)). Partition three ways (duplicates stay linear)
on a copy.

| | Sort | Size-k heap | Quickselect |
|---|---|---|---|
| Time | O(n log n) | O(n log k) | O(n) expected, O(n²) worst |
| Extra space | O(n) | O(k) | O(n) copy, or O(1) in place |
| Stream / out of memory | no | **yes** | no |

→ repo: `chapters/ch15_heaps_top_k/solutions/ex10_top_k_quickselect.py`

## 15.6 Merge K sorted lists/arrays

**Worked problem 2 — merge k sorted iterators lazily.** Yield all N items in order, holding one
item per source (huge files, infinite generators); take a `key`; equal keys keep source order.

1. **Concatenate and sort** — O(N log N); eager, so infinite sources hang.
2. **Merge pairwise** — O(N·k) one by one, O(N log k) divide and conquer; still eager.
3. **Heap of heads** — one `(key, source_index, item)` per live source; pop, yield, refill from
   that source: O(N log k), O(k) memory, lazy. `source_index` is the counter trick.

```python
import heapq
from itertools import count, islice

_DONE = object()


def merge_lazy(iterables, key=lambda x: x):
    iters = [iter(src) for src in iterables]
    heap = []
    for idx, it in enumerate(iters):
        first = next(it, _DONE)
        if first is not _DONE:
            heap.append((key(first), idx, first))  # idx breaks ties: item never compared
    heapq.heapify(heap)
    while heap:
        _, idx, item = heap[0]
        yield item
        nxt = next(iters[idx], _DONE)
        if nxt is _DONE:
            heapq.heappop(heap)                    # source exhausted
        else:
            heapq.heapreplace(heap, (key(nxt), idx, nxt))


print(list(merge_lazy([[1, 4, 7], [2, 5], [], [3, 6, 9]])))
print(list(islice(merge_lazy([count(0, 3), count(0, 5), count(1, 7)]), 10)))
```

```text
[1, 2, 3, 4, 5, 6, 7, 9]
[0, 0, 1, 3, 5, 6, 8, 9, 10, 12]
```

→ repo: `chapters/ch15_heaps_top_k/solutions/ex04_merge_k_iterators.py`

In production, `heapq.merge(*its, key=...)` does this. Edge cases: no or empty sources,
cross-source duplicates. Follow-up: external sort (sorted chunks on disk, k-way merged).
Linked lists: §13.5.

**Extension ◆ — smallest range covering k lists.** Heap of heads plus a running *maximum*: each
`[heap min, max]` is a candidate; advance the minimum's list until one runs out. O(N log k).
Advancing the maximum instead never shrinks the range.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex08_smallest_range_k_lists.py`

## 15.7 Two heaps: streaming median

**Worked problem 3.** Support `add(x)` and `median()` over a stream.

1. **Sort per query** — O(n log n) per call.
2. **`bisect.insort`** — O(1) median, O(n) per add (shifting): O(n²) over the stream.
3. **Two heaps** — `low`, negated max-heap of the smaller half; `high`, min-heap of the larger;
   `len(low)` is `len(high)` or one more. Route each value through `low` into `high` (keeps
   low ≤ high), then rebalance. O(log n) add, O(1) median.

```python
import heapq


class MedianFinder:
    def __init__(self) -> None:
        self.low: list[int] = []    # max-heap (negated): smaller half
        self.high: list[int] = []   # min-heap: larger half

    def add(self, x: int) -> None:
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))   # low's max -> high
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self) -> float:
        if not self.low:
            raise ValueError("median of empty stream")
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2


mf, out = MedianFinder(), []
for x in [5, 15, 1, 3]:
    mf.add(x)
    out.append(mf.median())
print(out)
```

```text
[5, 10.0, 5, 4.0]
```

**Wrong but tempting:** pushing x into "the smaller heap" (add 10 then 1: low = [10], high = [1],
inverted); forgetting to negate when *reading* `low[0]`. Follow-up, sliding-window median: lazy
deletion, or `bisect` on a sorted window (O(k) per step). An odd count returns the int top, an
even count a float mean — matching `statistics.median`. **Edge cases:** empty stream raises
`ValueError`, duplicates, negatives, one element.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex05_streaming_median.py`

## 15.8 Scheduling with heaps: task scheduler, meeting rooms

Sort by time; heap what frees up or runs next. **Minimum meeting rooms** (half-open
`[start, end)`): a min-heap of in-use end times.

```python
import heapq


def min_rooms(meetings: list[tuple[int, int]]) -> int:
    ends: list[int] = []                      # end times of rooms in use
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:         # earliest-ending room is free
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)


print(min_rooms([(0, 30), (5, 10), (15, 20)]), min_rooms([(1, 5), (5, 8)]))
```

```text
2 1
```

Ladder: count overlaps per start, O(n²) → heap, O(n log n). `<=` reuses a room back to back.
The start/end sweep (→ §17.8) is as fast but can't assign rooms; ex07 does:
→ repo: `chapters/ch15_heaps_top_k/solutions/ex07_meeting_rooms.py`

**CPU simulation** runs the shortest arrived job next: arrivals deque + `(duration, index)`
heap; on an empty heap jump the clock to the next arrival. O(n log n). The cooldown
**task scheduler** is the same loop; formula in §20.6.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex09_cpu_scheduler.py`

## 15.9 K closest points

Rank by **squared** distance (exact ints, no `sqrt`), ties by `(x, y)`. To stream, hand-roll a
size-k *max*-heap of negated keys `(-d2, -x, -y)`: worst kept at the root.

```python
import heapq

pts = [(1, 3), (-2, 2), (2, -2), (3, 4), (5, 0)]
print(heapq.nsmallest(3, pts, key=lambda p: (p[0] ** 2 + p[1] ** 2, p)))
```

```text
[(-2, 2), (2, -2), (1, 3)]
```

Ladder: sort, O(n log n) → size-k heap, O(n log k), streams → quickselect (§15.5), O(n)
expected. Classic bug: a size-k *min*-heap, whose root — the nearest point — gets evicted.
→ repo: `chapters/ch15_heaps_top_k/solutions/ex06_k_closest_points.py`

## 15.10 Practice set

Order: ex01 → ex02, ex06, ex03 → ex04, ex08 → ex05, ex07, ex09 → ex10. Tests cross-check
every rung against a sort. More: Chapter 45, problems 091–098.

## Interviewer's view

- "Min-heap of size k, O(n log k)" for k largest — not "max-heap of everything".
- Name the tie-breaker *before* the `TypeError`; flip min-only `heapq` fluently.
- Say when sort, buckets or quickselect win; test ties, duplicates, k = 0, k = n.
- Explaining sift-down beats writing it from scratch.

## Exercises

Code and stubs: `chapters/ch15_heaps_top_k/` (index in `README.md`).

| Id | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Min-heap from scratch | ★ | sift up/down, heapify |
| ex02 | K-th largest in a stream | ★ | size-k min-heap |
| ex03 | Top-K frequent words | ★ | heap vs bucket vs sort |
| ex04 | Merge K sorted iterators lazily | ★ | k-way merge |
| ex05 | Streaming median | ★ | two heaps |
| ex06 | K closest points | ★ | size-k max-heap |
| ex07 | Meeting rooms + room assignment | ★ | heap of end times |
| ex08 | Smallest range covering K lists | ◆ | heads + running max |
| ex09 | Shortest-job-first CPU scheduler | ★ | queue + ready heap |
| ex10 | Top-K: heap vs quickselect | ◆ | partition selection |

## Checkpoint quiz

1. In the array heap, what are the parent and children of index 5?
2. Why does `heapify` cost O(n) while n pushes cost O(n log n)?
3. For the k *largest* values of a stream, which heap and what size?
4. Why push `(priority, next(counter), task)` instead of `(priority, task)`?
5. When would you choose quickselect over a size-k heap, and when never?

<details>
<summary>Answers</summary>

1. Parent 2; children 11 and 12.
2. Sift-down costs a node's height, and most nodes are near the bottom; a push sifts *up* and
   may climb the full log n.
3. A min-heap of size k: its root is the k-th largest and the first to evict.
4. Ties would compare tasks (possible `TypeError`); the unique counter decides first, FIFO.
5. In memory, one-shot, k large: O(n) expected beats O(n log k). Never for streams.

</details>

## Summary card

- Array heap: parent `(i-1)//2`, children `2i+1`, `2i+2`. Push/pop O(log n); heapify O(n).
- `heapq` is min-only: negate numbers, wrap strings with a reversed `__lt__`.
- Entries `(key, unique_counter, payload)` — never compare payloads.
- k largest → min-heap of size k; k smallest / closest → max-heap of size k. O(n log k), O(k).
- Top-K: heap (k ≪ n, streams) · sort (k ≈ n) · buckets (small counts) · quickselect (in memory).
- Merge k → heap of heads + source index, O(N log k). Median → two heaps. Scheduling → sort
  by time + heap of "next free"; `<=` for half-open intervals.
