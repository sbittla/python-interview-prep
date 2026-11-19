# Chapter 15. Heaps and Top-K

Tier ★ Core · Tracks S, M, L · Study time ≈ 5 h · Prerequisites: Ch 6 (`heapq`, §6.8), Ch 7 (§7.20), Ch 8 (Big-O)

**Learning objectives**

- Draw a binary heap as an array, apply the index formulas, and explain why heapify is O(n).
- Use `heapq` as a min-heap, a max-heap and a priority queue with safe tie-breakers.
- Pick between sort, size-k heap, bucket sort and quickselect for top-K, and justify it.
- Solve the k-way merge, two-heap median and scheduling problems with an approach ladder.

> **Recognise it**
>
> | Signal in the prompt | Reach for |
> |---|---|
> | "k largest / smallest / closest / most frequent", k ≪ n | size-k heap, O(n log k) (15.3, 15.4, 15.9) |
> | "stream", "after each insertion", "data does not fit in memory" | heap of bounded size; never re-sort |
> | "merge k sorted …" | heap of one head per source (15.6) |
> | "running median", "balance two halves" | two heaps (15.7) |
> | "next job / earliest free room / cheapest next step" | priority queue simulation (15.8) |
> | "k-th element, one shot, O(n) expected" | quickselect (15.5, → §11.13) |

## 15.1 Heap property and array representation

A **min-heap** is a complete binary tree where every parent is ≤ its children. Complete means
every level is full except the last, which fills left to right — so the tree packs into a list
with no pointers. For index `i` (0-based): parent `(i - 1) // 2`, children `2i + 1` and `2i + 2`.

```text
index:  0  1  2  3  4  5  6                1(0)
value: [1, 4, 2, 9, 8, 7, 6]             /      \
                                      4(1)      2(2)
                                      /  \      /  \
                                   9(3) 8(4)  7(5) 6(6)
```

Only the root is guaranteed to be the minimum; siblings are unordered. Two repairs keep the
property: **sift up** (after appending, swap with the parent while smaller) and **sift down**
(after replacing the root, swap with the *smaller* child while larger). Both walk one
root-to-leaf path: O(log n). Push = append + sift up; pop = move the last item to the root +
sift down. **Heapify** sifts down every internal node, from the last (`n // 2 - 1`) to the root:

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

**Why heapify is O(n), not O(n log n).** A node at height h sifts down at most h levels, and
there are about n / 2^(h+1) nodes at height h. Half the nodes are leaves (zero work), a quarter
move one level, and so on: total ≤ n · Σ h/2^(h+1) = n. Building by n pushes is different: the
*deep* nodes are the ones that may travel far, so it is O(n log n). The ex01 demo counts swaps on
descending input, the worst case for both:

```text
      n   heapify   n pushes   heapify/n
    127       120        642   0.94
   1023      1013       8194   0.99
   8191      8178      90114   1.00
```

→ repo: `chapters/ch15_heaps_top_k/solutions/ex01_min_heap.py` (full `MinHeap` with `pushpop`,
`replace`, empty-heap errors). Heap sort itself lives in §11.8.

## 15.2 `heapq` in practice (max-heap by negation, tuples, tie-breakers)

`heapq` (API in §6.8) is a set of functions over a plain list, min-heap only, and compares items
with `<` alone. Three habits cover almost every interview use (pitfalls in §7.20):

1. **Max-heap**: push `-x`, negate on the way out. Strings cannot be negated — wrap them (15.4).
   Python 3.14 adds public `heappush_max`/`heappop_max` and friends; don't rely on them for 3.10+ code.
2. **Priority + payload**: push `(priority, tie_breaker, payload)`. Tuples compare field by
   field, so when priorities tie Python compares the *next* field. If that is a dict or a custom
   object, you get a `TypeError` — at some later pop, not necessarily the first push.
3. **The counter trick**: make the tie-breaker a unique, increasing `itertools.count()` value.
   The comparison never reaches the payload, and equal priorities come out FIFO.

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

nums = [5, 1, 9, 3]
mx = [-x for x in nums]                       # max-heap by negation
heapq.heapify(mx)
print(-mx[0], heapq.nlargest(2, nums), heapq.nsmallest(2, nums))
```

```text
TypeError: '<' not supported between instances of 'dict' and 'dict'
['a', 'b', 'c']
9 [9, 5] [1, 3]
```

`heapreplace(h, x)` pops then pushes (the root may be bigger than x); `heappushpop(h, x)` pushes
then pops (returns x at once if x ≤ root). Both do one sift instead of two.

## 15.3 Kth largest / smallest element

The k-th largest is the **minimum of the k largest**. So keep a *min*-heap of size k: a new
value enters only if it beats the root, which it evicts. O(n log k) time, O(k) memory, and it
works on a stream — the class below absorbs an initial batch and answers after every `add`:

```python
import heapq


class KthLargest:
    def __init__(self, k: int, initial: list[int]) -> None:
        self.k, self.heap = k, list(initial)
        heapq.heapify(self.heap)                     # O(m)
        while len(self.heap) > k:
            heapq.heappop(self.heap)                 # keep only the k largest

    def add(self, x: int) -> int | None:
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, x)
        elif x > self.heap[0]:
            heapq.heapreplace(self.heap, x)          # evict the old k-th largest
        return self.heap[0] if len(self.heap) == self.k else None


t = KthLargest(3, [4, 5, 8, 2])
print([t.add(x) for x in [3, 5, 10, 9, 4]])
```

```text
[4, 5, 5, 8, 8]
```

Ladder: re-sort per add O(n log n) → `bisect.insort` O(n) per add (memory still grows) → size-k
heap O(log k) per add, bounded memory. k-th *smallest* mirrors it with a max-heap of size k.

## 15.4 Top-K frequent: heap vs bucket sort vs sort trade-offs

**Worked problem 1 — top-K frequent words.** Return the k most frequent words, highest count
first, ties alphabetical. (Ch 9 ex04 does the integer version with buckets.)

| Rung | Idea | Time | Extra space | Why move on |
|---|---|---|---|---|
| Sort | `Counter`, sort d words by `(-count, word)` | O(n + d log d) | O(d) | sorts words you will discard |
| `nsmallest` | `heapq.nsmallest(k, c, key=lambda w: (-c[w], w))` | O(n + d log k) | O(k) | one line; best default |
| Size-k heap | hand-rolled; root = worst kept word | O(n + d log k) | O(k) | streams; what the follow-up asks |
| Bucket | `bucket[count]` → words, scan high to low | O(n) + sort per bucket | O(n) | ties force a sort: O(d log d) worst |

The hand-rolled heap has a trap: the root must be the *worst* kept word — lowest count, and among
equal counts the alphabetically **latest**. Counts ascend but words must descend, and you cannot
negate a string. Wrap it:

```python
import heapq
from collections import Counter


class Rev:                                    # reverses string order inside the heap
    __slots__ = ("word",)

    def __init__(self, word: str) -> None:
        self.word = word

    def __lt__(self, other: "Rev") -> bool:
        return self.word > other.word


def top_k_words(words: list[str], k: int) -> list[str]:
    heap: list[tuple[int, Rev]] = []          # root = worst kept word
    for word, c in Counter(words).items():
        heapq.heappush(heap, (c, Rev(word)))
        if len(heap) > k:
            heapq.heappop(heap)
    return [heapq.heappop(heap)[1].word for _ in range(len(heap))][::-1]


words = ["to", "be", "or", "not", "to", "be"]
print(top_k_words(words, 3))
c = Counter(words)
print(heapq.nsmallest(3, c, key=lambda w: (-c[w], w)))
```

```text
['be', 'to', 'not']
['be', 'to', 'not']
```

**Wrong but tempting.** `(count, word)` tuples in a size-k heap evict the alphabetically
*smaller* word on a tie — the one you wanted. `(-count, word)` with eviction pops the *most*
frequent word. The repo demo prints the first bug on `k=1`, `["b","b","a","a","c"]`: it keeps
`b`. **Trade-off answer:** k ≪ d → heap; k ≈ d → sort; small integer counts and no tie rule →
buckets. → repo: `chapters/ch15_heaps_top_k/solutions/ex03_top_k_frequent_words.py`

## 15.5 Quickselect as the Top-K follow-up ◆

After a heap answer the interviewer often asks, "can you beat O(n log k)?" Quickselect
(algorithm in §11.13) partitions around a random pivot and recurses into only the side holding
index n − k: expected O(n), worst O(n²). Afterwards `a[n-k:]` holds the k largest, unordered;
sort just those for O(n + k log k). Use a three-way partition so all-equal input stays linear,
and copy the input — quickselect reorders the list.

| | Sort | Size-k heap | Quickselect |
|---|---|---|---|
| Time | O(n log n) | O(n log k) | O(n) expected, O(n²) worst |
| Extra space | O(n) | O(k) | O(n) copy, or O(1) in place |
| Stream / out of memory | no | **yes** | no |

→ repo: `chapters/ch15_heaps_top_k/solutions/ex10_top_k_quickselect.py`

## 15.6 Merge K sorted lists/arrays

**Worked problem 2 — merge k sorted iterators lazily.** Yield all items in order, pulling at most
one item ahead per source, so it works on huge files and infinite generators; items may be
non-comparable (dicts with a key), and equal keys come out in source order.

1. **Concatenate and sort** — O(N log N); reads everything, so infinite sources hang.
2. **Merge one source at a time** — O(N·k), still eager (divide-and-conquer pairs give O(N log k),
   also eager).
3. **Heap of heads** — one `(key, source_index, item)` per live source; pop, yield, refill from the
   same source. O(N log k) time, O(k) memory, lazy. `source_index` is the counter trick: it breaks
   ties so `item` is never compared, and makes ties stable.

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
logs = [[{"t": 1, "m": "boot"}, {"t": 4, "m": "ready"}], [{"t": 1, "m": "db"}]]
print([d["m"] for d in merge_lazy(logs, key=lambda d: d["t"])])
```

```text
[1, 2, 3, 4, 5, 6, 7, 9]
[0, 0, 1, 3, 5, 6, 8, 9, 10, 12]
['boot', 'db', 'ready']
```

In production say "`heapq.merge(*its, key=...)` does exactly this". Edge cases: no sources,
empty sources, duplicates across sources, a source that ends first. Follow-up: external sort
(sort chunks to disk, k-way merge them). For linked lists see §13.5.

**Extension ◆ — smallest range covering k lists.** Same heap of heads plus a running *maximum*:
each step `[heap min, max]` is a candidate; advance the list holding the minimum; stop when any
list is exhausted. O(N log k). The tempting bug is advancing the maximum instead — the range
can never shrink. → repo: `chapters/ch15_heaps_top_k/solutions/ex08_smallest_range_k_lists.py`

## 15.7 Two heaps: streaming median

**Worked problem 3.** Support `add(x)` and `median()` over a stream.

1. **Sort on every query** — O(n log n) per call.
2. **`bisect.insort`** — O(n) per add (list shifting), O(1) median: O(n²) over the stream.
3. **Two heaps** — `low`, a max-heap (negated) of the smaller half; `high`, a min-heap of the
   larger half; `len(low)` equals `len(high)` or exceeds it by one. Route every new value through
   `low` into `high`, so every value in low ≤ every value in high without comparing anything
   yourself, then rebalance. O(log n) add, O(1) median.

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

**Wrong but tempting:** pushing x into "whichever heap is smaller" (add 10 then 1 puts 10 in low
and 1 in high — inverted halves); forgetting to negate when *reading* `low[0]`. Follow-up,
sliding-window median: add lazy deletion, or use a sorted list with `bisect` (O(k) per step).
The tests cross-check against `statistics.median`, including int-vs-float results.

## 15.8 Scheduling with heaps: task scheduler, meeting rooms

The shape: sort events by time, keep a heap of "what frees up / runs next". **Minimum meeting
rooms** (half-open `[start, end)`): a min-heap of end times of rooms in use.

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

Ladder: count overlaps at every start, O(n²) → heap, O(n log n). The two-pointer sweep over sorted
starts and ends (→ §17.8) is equally fast but cannot say *which* room a meeting gets; ex07 adds
that with a second heap of free room ids. Use `<=`, not `<`: back-to-back meetings share a room.

**CPU simulation (heap + queue).** In ex09 jobs have arrival times and durations; a free CPU runs
the arrived job with the shortest duration. A deque of jobs sorted by arrival answers "who
arrives next?"; a heap of `(duration, index)` answers "who runs next?". When the heap is empty,
jump the clock to the next arrival — never tick by 1. O(n log n). The cooldown **task scheduler**
(same letter n ticks apart) is the same heap + queue loop, taught with its counting formula in §20.6.

## 15.9 K closest points

Rank by **squared** distance (exact ints, no `sqrt`) and break ties by `(x, y)`. A size-k
*max*-heap keeps the k best with the worst at the root; negating the whole key turns `heapq`
into one:

```python
import heapq


def k_closest(points: list[tuple[int, int]], k: int) -> list[tuple[int, int]]:
    heap: list[tuple[int, int, int]] = []     # negated (d2, x, y): root = worst kept
    for x, y in points:
        item = (-(x * x + y * y), -x, -y)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    return [(-x, -y) for _, x, y in sorted(heap, reverse=True)]


print(k_closest([(1, 3), (-2, 2), (2, -2), (3, 4), (5, 0)], 3))
```

```text
[(-2, 2), (2, -2), (1, 3)]
```

Sort is O(n log n); this is O(n log k) and streams; quickselect on the key (15.5) is O(n)
expected. A size-k *min*-heap here is the classic bug: its root is the nearest point.

## 15.10 Practice set

Work in this order; each row's file has the full ladder, follow-ups and tests.

| Step | Do | Exercise |
|---|---|---|
| 1 | Build the heap by hand, check against `heapq` | ex01 |
| 2 | Size-k heap patterns | ex02, ex06, ex03 |
| 3 | Merge and multi-pointer heaps | ex04, then ex08 ◆ |
| 4 | Two heaps and simulations | ex05, ex07, ex09 |
| 5 | Defend heap vs quickselect aloud | ex10 ◆ |

### Interviewer's view

The rubric rewards: saying "min-heap of size k" (not "max-heap of everything") for k largest,
with O(n log k); naming tie-breakers *before* the `TypeError`; knowing `heapq` is min-only and
how to flip it; explaining when sort, bucket or quickselect beats the heap; and testing ties,
duplicates, k = 0 and k = n. Writing sift-down from scratch is asked less often than explaining it.

## Exercises

Code: `chapters/ch15_heaps_top_k/` (stubs in `exercises/`, run with `TARGET=exercises`).

| Id | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Array-backed min-heap from scratch | ★ | sift up/down, O(n) heapify |
| ex02 | K-th largest in a stream | ★ | size-k min-heap |
| ex03 | Top-K frequent words, alphabetical ties | ★ | heap vs bucket vs sort |
| ex04 | Merge K sorted iterators lazily | ★ | k-way merge heap |
| ex05 | Streaming median | ★ | two heaps |
| ex06 | K closest points to a target | ★ | size-k max-heap |
| ex07 | Minimum meeting rooms + room assignment | ★ | heap of end times |
| ex08 | Smallest range covering K lists | ◆ | heap + running max |
| ex09 | Single-CPU shortest-job-first scheduler | ★ | arrival queue + ready heap |
| ex10 | Top-K: heap vs quickselect | ◆ | partition selection |

## Checkpoint quiz

1. In the array heap, what are the parent and children of index 5?
2. Why does `heapify` cost O(n) while n pushes cost O(n log n)?
3. For the k *largest* values of a stream, which heap and what size?
4. Why push `(priority, next(counter), task)` instead of `(priority, task)`?
5. When would you choose quickselect over a size-k heap, and when never?

<details>
<summary>Answers</summary>

1. Parent `(5 - 1) // 2 = 2`; children 11 and 12.
2. Sift-down cost is a node's height; most nodes are near the bottom, so the sum Σ h·n/2^(h+1)
   is ≤ n. Pushes sift *up*, and the many deep nodes may travel the full log n.
3. A min-heap of size k: its root is the k-th largest and the first thing to evict.
4. On equal priorities the tuple compares the task, which may raise `TypeError`; a unique
   counter ends the comparison and gives FIFO order among ties.
5. Quickselect when all data is in memory, one-shot, and k is large (O(n) expected vs
   O(n log k)). Never for streams or data that does not fit in memory.

</details>

## Summary card

- Array heap: parent `(i-1)//2`, children `2i+1`, `2i+2`; only the root is ordered.
- Push/pop O(log n); peek O(1); heapify O(n); n pushes O(n log n).
- `heapq` is min-only: negate numbers, wrap strings with a reversed `__lt__`.
- Tuple entries: `(key, unique_counter, payload)` — never let the payload be compared.
- k largest → min-heap size k; k smallest / k closest → max-heap size k. O(n log k), O(k).
- Top-K choice: heap (k ≪ n, streams) · sort (k ≈ n) · buckets (small counts) · quickselect (O(n) expected, in memory).
- Merge k sorted → heap of heads with source index, O(N log k); `heapq.merge` in production.
- Median → two heaps, sizes equal or low +1, route through low.
- Scheduling → sort by time + heap of "next free / next to run"; use `<=` for half-open intervals.
