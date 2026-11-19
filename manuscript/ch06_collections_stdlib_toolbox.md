# Chapter 6. Built-in Collections, Idioms and the Stdlib Toolbox

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 6–8 hours · **Prerequisites:** Chapter 5

This chapter is the **canonical home** for hashing internals (§6.5), `collections` (§6.7), `heapq`
(§6.8) and `bisect` (§6.9). Later chapters use these tools and point back here.

**Learning objectives**

- State the cost of every common operation on `list`, `tuple`, `set`, `dict`, `str` and `deque`.
- Explain how a CPython `dict` finds a key: hash, mask, perturbed probing, compact entries, resize.
- Reach for `Counter`, `defaultdict`, `deque`, `heapq`, `bisect`, `itertools` and `functools`
  instead of hand-rolled loops, and justify each choice in big-O terms.
- Write multi-key and comparator-based sorts that are correct on ties.

> **Recognise it**
>
> | You hear / see | Reach for |
> |---|---|
> | "count", "frequency", "anagram", "enough letters" | `Counter` (multiset algebra) |
> | "group by", "index of", "for each key a list" | `defaultdict(list/set)` |
> | "last k", "sliding window", "queue", "pop from the front" | `deque` |
> | "top k", "k-th largest", "merge k sorted", "repeatedly the smallest" | `heapq` |
> | "sorted list", "rank", "grade band", "how many ≤ x" | `bisect` |
> | "consecutive runs", "all pairs", "running total" | `itertools` |
> | "order by A then B descending", "custom order" | `key=` tuple, stable passes, `cmp_to_key` |
> | "seen before?", "membership", "dedupe" | `set` / `dict` |

## 6.1 Lists: operations, slicing, complexity of each operation

A `list` is a dynamic array of references. Indexing and `append` are O(1) (append is
*amortised*: CPython over-allocates and occasionally copies). Anything that shifts elements —
`insert(0, x)`, `pop(0)`, `del a[i]` in the middle — is O(n). `x in a` is a linear scan.

```python
a = [10, 20, 30, 40, 50]
print(a[1:4], a[::-1], a[-2:], a[::2])
b = a[:]                     # shallow copy
b[0] = 99
print(a[0], b[0])
a[1:3] = [7]                 # slice assignment can change the length
print(a)
```

```text
[20, 30, 40] [50, 40, 30, 20, 10] [40, 50] [10, 30, 50]
10 99
[10, 7, 40, 50]
```

Slicing **copies** (O(k) for k elements), so `a[1:]` inside a recursive call turns an O(n)
algorithm into O(n²); pass indices instead (→ §7.17). Copies are shallow (→ §7.2).

## 6.2 Tuples, unpacking, named tuples

Tuples are immutable sequences; when every element is hashable the tuple is hashable, which makes
it the natural composite dict key (`(row, col)`) and the natural sort key.

```python
from collections import namedtuple
point = 3, 4
x, y = point
first, *middle, last = [1, 2, 3, 4, 5]
print(x, y, middle, last)
Point = namedtuple("Point", "x y")
p = Point(3, 4)
print(p, p.x, p._replace(y=0), p._asdict())
```

```text
3 4 [2, 3, 4] 5
Point(x=3, y=4) 3 Point(x=3, y=0) {'x': 3, 'y': 4}
```

A `namedtuple` is still a tuple: it unpacks, compares and sorts field by field, and costs no more
memory than a plain tuple. Use it for read-only records in interviews; `dataclass` is Chapter 24.

## 6.3 Sets and frozensets: membership, set algebra

`set` gives average O(1) `add`, `remove`, `in`. Operators: `|` union, `&` intersection, `-`
difference, `^` symmetric difference, `<=` subset. A `frozenset` is immutable and hashable, so it
can be a dict key or live inside another set (e.g. "have I seen this unordered pair?").

```text
>>> a, b = {1, 2, 3}, {2, 3, 4}
>>> sorted(a | b), sorted(a & b), sorted(a - b), sorted(a ^ b), {1, 2} <= a
([1, 2, 3, 4], [2, 3], [1], [1, 4], True)
>>> frozenset({"y", "x"}) in {frozenset({"x", "y"})}
True
```

Pitfalls: `{}` is an empty **dict**, use `set()`; set iteration order is arbitrary, so sort before
printing; `a & b` costs O(min(len(a), len(b))) — intersect the smallest set first (ex02).

## 6.4 Dictionaries: methods, iteration order, dict views

Since Python 3.7 a `dict` **remembers insertion order** (language guarantee). Updating an existing
key keeps its position; delete-then-reinsert moves it to the end.

```python
stock = {"apple": 3, "pear": 0}
print(stock.get("kiwi", 0), stock.setdefault("kiwi", 5), stock)
keys = stock.keys()
stock["fig"] = 1
print(keys, list(stock.items())[0])
print(stock.pop("pear"), stock | {"apple": 9})
print(stock.keys() & {"fig", "plum"})
```

```text
0 5 {'apple': 3, 'pear': 0, 'kiwi': 5}
dict_keys(['apple', 'pear', 'kiwi', 'fig']) ('apple', 3)
0 {'apple': 9, 'kiwi': 5, 'fig': 1}
{'fig'}
```

`keys()`, `values()` and `items()` are **live views**: `keys` saw `fig` added after it was created.
Key views support set operators. `d | other` (3.9+) builds a merged dict; right side wins.
Never add or delete keys while iterating a dict (→ §7.11).

## 6.5 Hashing and collisions — how dict/set work internally

Every interviewer who asks "why is dict lookup O(1)?" wants this mechanism, not the word "hashing".

**Hash contract.** `hash(x)` returns an int. If `a == b` then `hash(a) == hash(b)`, so
`1`, `1.0` and `True` are the same key. Mutable built-ins (`list`, `dict`, `set`) are unhashable.
Small ints hash to themselves except `hash(-1) == -2` (−1 is the C error code). `str` and `bytes`
hashes are salted per process (`PYTHONHASHSEED`) to block hash-flooding attacks, which is one
reason set order changes between runs.

**CPython's compact dict** (3.6+) keeps two arrays:

```text
indices  (size 2**k, 1-8 bytes per slot)   entries (dense, insertion order)
 slot: 0   1   2   3   4   5   6   7        #  hash  key  value
      [0] [1] [-] [-] [-] [-] [2] [-]       0   0     0    'v0'
                                            1   8     8    'v8'
 -1 = EMPTY, -2 = DUMMY (deleted)           2   16    16   'v16'
```

Since 3.11, a dict whose keys are all `str` uses smaller entries (key, value only) and reads each
key's hash from the string object, which caches it.

1. **Slot:** `i = hash & mask` where `mask = size - 1` (sizes are powers of two).
2. **Collision → open addressing**, no linked lists. CPython probes
   `perturb >>= 5; i = (5*i + perturb + 1) & mask`, starting with `perturb = hash`. The shifted
   `perturb` mixes in the high bits, so keys that share low bits split up quickly; once it reaches 0
   the recurrence `5*i + 1` still visits every slot.
3. **Match:** same object (`is`), else equal hash (stored in the entry, or cached on a `str` key)
   **and** `==`. Comparing hashes first makes most mismatches one int comparison.
4. **Delete** writes DUMMY, not EMPTY: a lookup stops at EMPTY, so emptying a slot would cut the
   probe chain of every key inserted after it.
5. **Resize:** the entries array holds at most 2/3 of the index size (live + deleted). When a new key
   does not fit, CPython rebuilds with an index size of the next power of two ≥ 3 × live keys, dropping
   DUMMYs. Deletions never trigger a resize.

**Sets** probe the same way but store (hash, key) in one table: no compact index, so no insertion
order. They also try up to 9 adjacent slots first and resize at about 60 % full.

**Worked problem (ex09): build a tiny dict.**
- *Rung 1 — association list:* list of pairs, O(n) per lookup.
- *Rung 2 — separate chaining:* bucket per slot holding a small list; O(1) average, but a list
  object per bucket and pointer chasing.
- *Rung 3 — open addressing + compact entries:* one flat index table, dense ordered entries.
  Why move up: less memory, better cache behaviour, ordered iteration for free.

```python
def _find(self, key, h):
    mask = len(self._indices) - 1
    perturb = h & MASK64                     # treat the hash as unsigned 64-bit
    i = perturb & mask
    free = -1
    while True:
        ix = self._indices[i]
        if ix == EMPTY:
            return (i if free < 0 else free), -1      # absent: first reusable slot
        if ix == DUMMY:
            if free < 0:
                free = i
        else:
            eh, ek, _ = self._entries[ix]
            if ek is key or (eh == h and ek == key):
                return i, ix                          # found
        self.collisions += 1
        perturb >>= PERTURB_SHIFT
        i = (5 * i + perturb + 1) & mask

def __setitem__(self, key, value):
    h = hash(key)
    slot, ix = self._find(key, h)
    if ix >= 0:
        self._entries[ix][2] = value          # update keeps the old position
        return
    if len(self._entries) >= len(self._indices) * 2 // 3:
        self._resize()                        # rebuild: 2**k >= 3 * live keys
        slot, _ = self._find(key, h)
    self._indices[slot] = len(self._entries)
    self._entries.append([h, key, value])
    self._used += 1
```

```text
  hash  8 -> [0, 1, 6, 7, 4, 5]
indices: [0, 1, -1, -1, -1, -1, 2, -1]
after del 8 -> indices: [0, -2, -1, -1, -1, -1, 2, -1] | 16 still found: True
re-insert 8 reuses the DUMMY slot -> indices: [0, 3, -1, -1, -1, -1, 2, -1]
model grew at len: [6, 11, 22, 43, 86] | final table size: 256
real dict grew at len: [6, 11, 22, 43, 86] | matches model: True
```

(Excerpt.) The resize points match a real CPython 3.13 dict (`sys.getsizeof`). Keys 0, 8, 16 share
one chain: small ints have no high bits to perturb. Heavy collisions degrade operations to O(n).
→ repo: `chapters/ch06_collections_stdlib_toolbox/solutions/ex09_open_addressing_map.py`

## 6.6 Strings as sequences: `join`, `split`, `ord`/`chr`, character counting

Strings are immutable sequences of code points: index, slice, iterate, `in`. Build output with a
list and `"".join(parts)` (O(total)); `+=` in a loop may copy each time (→ §7.17).
`split()` with no argument splits on runs of whitespace and drops empties; `split(",")` keeps them.

```text
>>> ord("a"), chr(90), "-".join("abc")
(97, 'Z', 'a-b-c')
>>> "a,b,,c".split(","), " a  b ".split()
(['a', 'b', '', 'c'], ['a', 'b'])
```

`ord(ch) - ord("a")` maps letters to 0–25 for a 26-slot count array (ex11's anagram profile, a
tuple of counts); `(ord(ch) - base + k) % 26 + base` rotates a letter, negative k included.
`str.maketrans` + `translate` maps a whole string in one C-level pass.

## 6.7 `collections`: `Counter`, `defaultdict`, `deque`, `OrderedDict`, `namedtuple`

| Type | What it adds to dict/list | Interview use |
|---|---|---|
| `Counter` | counts; `most_common`, `+ - & \|`, `<=` (3.10+) | frequencies, anagrams, "enough letters" |
| `defaultdict(f)` | missing key → `f()` inserted on **read** | grouping, adjacency lists, inverted index |
| `deque` | O(1) at both ends; `maxlen` | BFS queue, sliding window, last-k |
| `OrderedDict` | `move_to_end`, `popitem(last=False)` | LRU / recency order |
| `namedtuple` | named fields on a tuple | records, readable sort keys (§6.2) |

**Counter as a multiset (ex01).** `-` keeps only positive counts — exactly "what is still missing";
`&` is per-key min, `|` per-key max.

```python
def can_spell(word, sheet):
    return Counter(_letters(word)) <= Counter(_letters(sheet))   # Python 3.10+

def shortfall(word, sheet):
    missing = Counter(_letters(word)) - Counter(_letters(sheet))  # drops counts <= 0
    return dict(sorted(missing.items()))
```

```text
'banana'  from 'ban'    can_spell=False brute=False shortfall={'a': 2, 'n': 1}
shared_stickers('aabbc', 'abbbd') = 'abb'
combined_need(['moon', 'mono', 'nom']) = 'mnoo'
```

The brute-force rung (`list.remove` per letter) is O(len(word) × len(sheet)); Counter is linear.

**deque window (ex03).** Expire old events from the left in O(1); `list.pop(0)` would be O(n).

```python
class HitCounter:
    def __init__(self, window):
        self.window, self.hits = window, deque()

    def _expire(self, t):
        while self.hits and self.hits[0] <= t - self.window:
            self.hits.popleft()

    def hit(self, t):
        self._expire(t)
        self.hits.append(t)

    def count(self, t):
        self._expire(t)
        return len(self.hits)
```

```text
count(300) = 4 | count(301) = 3 | count(700) = 0
```

Pitfalls: reading `d[k]` on a `defaultdict` creates the key — query with `.get` (ex02, → §7.14);
`deque[i]` in the middle is O(n) (→ §7.18).

## 6.8 `heapq` toolbox: `heappush`, `heappop`, `heapify`, `nlargest`, `nsmallest`

`heapq` turns a plain list into a binary **min-heap**: `heap[0]` is the smallest. `heappush`/`heappop`
are O(log n), `heapify` is O(n), `heappushpop`/`heapreplace` do both in one O(log n) step.
`nlargest(k, it)`/`nsmallest(k, it)` cost O(n log k) and accept `key=`. For a max-heap push negated
keys; tuples compare field by field, so add a tie-breaker before any non-comparable payload (→ §7.20).

**Merge k sorted feeds (ex04).** Rung 1 concatenates and sorts, O(N log N), wasting the existing order.
Rung 2 keeps one head per feed in a heap, O(N log k):

```python
def merge_feeds(feeds):
    heap = [(feed[0], i, 0) for i, feed in enumerate(feeds) if feed]
    heapq.heapify(heap)                                   # O(k)
    out = []
    while heap:
        item, i, pos = heapq.heappop(heap)                # O(log k)
        out.append(item)
        if pos + 1 < len(feeds[i]):
            heapq.heappush(heap, (feeds[i][pos + 1], i, pos + 1))
    return out
```

```text
merged: [(1, 'boot'), (2, 'cron'), (3, 'deploy'), (4, 'alert'), (4, 'login'), (9, 'logout')]
same as sort: True | same as heapq.merge: True
running 3rd largest: [None, None, 1, 3, 5, 7, 7]
heapify -> [1, 3, 2, 5, 9, 7] | root = 1
```

`heapq.merge(*feeds)` is the lazy one-liner. "k-th largest so far" keeps a **min**-heap of size k
whose root is the answer. Heap patterns (two heaps, scheduling) are Chapter 15.

## 6.9 `bisect` toolbox: `bisect_left`, `bisect_right`, `insort`

On a sorted list, `bisect_left(a, x)` is the first index with `a[i] >= x`; `bisect_right(a, x)` the
first with `a[i] > x`. So `bisect_right - bisect_left` counts copies of x, and
`bisect_right(a, hi) - bisect_left(a, lo)` counts values in `[lo, hi]`. `insort` finds the spot in
O(log n) but the insert shifts elements, O(n). `key=` is available since 3.10.

**Worked problem (ex05): grade bands and a leaderboard.** Rung 1 is an `if/elif` chain or a linear
scan; rung 2 re-sorts after every add (O(n log n)); rung 3 below. Why move up: queries drop to
O(log n), and `bisect_right` encodes "a boundary score belongs to the higher band" with no
off-by-one reasoning.

```python
CUTOFFS, LETTERS = [60, 70, 80, 90], "FDCBA"

def grade(score):
    return LETTERS[bisect_right(CUTOFFS, score)]

class Leaderboard:
    def __init__(self):
        self.scores = []                        # always sorted ascending
    def add(self, score):
        insort(self.scores, score)              # O(log n) search + O(n) shift
    def rank(self, score):                      # 1 + number strictly greater
        return len(self.scores) - bisect_right(self.scores, score) + 1
    def count_between(self, lo, hi):
        if lo > hi:
            return 0
        return bisect_right(self.scores, hi) - bisect_left(self.scores, lo)
```

```text
grade( 59) = F  brute = F
grade( 60) = D  brute = D
grade( 90) = A  brute = A
scores: [50, 70, 80, 80, 95]
rank(95) = 1 | rank(80) = 2 | rank(81) = 2 | rank(10) = 6
count_between(70, 80) = 3 | count_between(81, 94) = 0
```

Edge cases: empty board, ties, `lo > hi`. Wrong-but-tempting: `bisect_left` for grades (60 → F).
Follow-up: heavy inserts → `sortedcontainers`. Hand-written binary search is Chapter 11.

## 6.10 `itertools` essentials: `accumulate`, `product`, `permutations`, `combinations`, `groupby`

`accumulate` yields running totals; `product(xs, repeat=r)` gives nʳ ordered tuples with reuse,
`permutations(xs, r)` n!/(n−r)! without, `combinations(xs, r)` C(n, r) unordered subsets.

`groupby` only merges neighbours — exactly what "consecutive runs" means; sort first if you want
global groups. Each group is an iterator that is exhausted when you advance (→ §7.12).

```python
def longest_outage(statuses):
    best = (-1, 0)
    for status, run in groupby(enumerate(statuses), key=itemgetter(1)):
        if status == "down":
            idx = [i for i, _ in run]
            if len(idx) > best[1]:
                best = (idx[0], len(idx))
    return best
```

```text
longest_outage: (4, 3) | brute: (4, 3)
running balances: [100, 70, 120, 30, 40]
```

`min(accumulate(deltas, initial=start))` replaces an O(n²) "sum every prefix" loop (ex06).

## 6.11 `functools` essentials: `lru_cache`, `cache`, `cmp_to_key`, `reduce`

`@lru_cache(maxsize=None)` / `@cache` (3.9+) memoise a pure function on its (hashable) arguments —
the fastest route from recursion to top-down DP (Chapter 19). `reduce(f, xs, init)` folds left.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def ways(n: int) -> int:          # stairs climbed 1 or 2 steps at a time
    return 1 if n <= 1 else ways(n - 1) + ways(n - 2)

print(ways(80), ways.cache_info())
```

```text
37889062373143906 CacheInfo(hits=78, misses=81, maxsize=None, currsize=81)
```

Uncached, the calls grow exponentially. Unbounded caches grow forever; unhashable arguments
raise `TypeError` (→ §7.22).

**Worked problem (ex07): Largest Number.** Arrange non-negative ints to form the largest number.
- *Rung 1:* try all permutations, O(n!·n) — fine for n ≤ 8 and useful as a test oracle.
- *Wrong-but-tempting:* reverse lexicographic sort. `[3, 30, 34]` gives `"34303"`, but `"34330"` wins:
  when one string is a prefix of another, plain string order cannot decide.
- *Rung 2:* `a` goes first iff `a + b > b + a`. This ordering is transitive with ties allowed
  (a total preorder: `"12"` and `"1212"` tie), so sort once with a comparator, O(n log n)
  comparisons:

```python
def _cmp(a: str, b: str) -> int:
    if a + b > b + a:
        return -1          # a first
    if a + b < b + a:
        return 1
    return 0

def solve(nums: list[int]) -> str:
    parts = sorted(map(str, nums), key=cmp_to_key(_cmp))
    return "".join(parts).lstrip("0") or "0"
```

```text
[3, 30, 34, 5, 9]  solve=9534330    brute=9534330    lexicographic=9534303
[0, 0]             solve=0          brute=0          lexicographic=0
[121, 12]          solve=12121      brute=12121      lexicographic=12112
```

Edge cases: all zeros (`"0"`, not `"00"`), single element, equal concatenations (`[12, 1212]`).
Follow-up the interviewer may ask: *why is it transitive?* `a+b > b+a` ⇔
`a/(10^|a|−1) > b/(10^|b|−1)`, a comparison of real numbers.

## 6.12 Sorting: `sorted` vs `.sort()`, `key=`, stability, multi-key sorts

`sorted(it)` returns a new list from any iterable; `list.sort()` sorts in place and **returns
`None`**. Both are Timsort: O(n log n) worst, O(n) on already-sorted runs, and **stable** — equal
keys keep their input order. `key=` is called once per element; `reverse=True` preserves stability.

```text
>>> words = ["pear", "Fig", "apple", "fig"]
>>> sorted(words), sorted(words, key=str.lower), sorted(words, key=len, reverse=True)
(['Fig', 'apple', 'fig', 'pear'], ['apple', 'Fig', 'fig', 'pear'], ['apple', 'pear', 'Fig', 'fig'])
```

Multi-key (ex08): when every descending field is numeric, one tuple key does it:
`key=lambda e: (e.dept, -e.salary, e.name)`. Strings cannot be negated, so use stability: sort by
the **least** important key first, one pass per key.

```python
def multi_sort(rows, spec):                 # spec: [(field, descending), ...] most important first
    out = list(rows)
    for field, desc in reversed(spec):
        out.sort(key=attrgetter(field), reverse=desc)
    return out
```

```text
payroll_order: ['Cy', 'Ed', 'Di', 'Al', 'Bo', 'Fa']
dept asc, name desc: ['Ed', 'Cy', 'Di', 'Bo', 'Al', 'Fa']
agrees with comparator: True True
```

`cmp_to_key` (§6.11) is the general fallback but calls Python code O(n log n) times. Mixed types and
`None` raise `TypeError` (→ §7.19).

## 6.13 Pythonic idioms: swapping, `any`/`all`, `min`/`max` with key, `enumerate`

```python
a, b = 1, 2
a, b = b, a                                            # swap, no temp
scores = {"ann": 91, "bob": 78, "cy": 91}
print(max(scores, key=scores.get), min(scores.items(), key=lambda kv: kv[1]))
print(any(v < 80 for v in scores.values()), all(v > 50 for v in scores.values()))
print(list(enumerate(["x", "y"], start=1)))
print(dict(zip("abc", [1, 2, 3])), sum(x * x for x in range(4)))
```

```text
ann ('bob', 78)
True True
[(1, 'x'), (2, 'y')]
{'a': 1, 'b': 2, 'c': 3} 14
```

`max` with `key` returns the **first** maximal item (ann, not cy). `any`/`all` short-circuit on a
generator; `all([])` is `True`. `max([])` raises `ValueError` — pass `default=`.

## 6.14 Choosing the right built-in: complexity table

Average-case costs in CPython (n = size, k = argument size).

| Operation | list | deque | dict / set | heapq (list) | sorted list + bisect |
|---|---|---|---|---|---|
| index `a[i]` | O(1) | O(1) ends, O(n) middle | — | O(1) (`h[0]` = min) | O(1) |
| append / push | O(1)* | O(1) both ends | O(1)* insert | O(log n) | O(n) `insort` |
| pop end / pop min | O(1) | O(1) both ends | O(1) `del d[k]` | O(log n) | O(1) end |
| pop(0) / insert(0, x) | O(n) | O(1) | — | — | O(n) |
| `x in c` | O(n) | O(n) | **O(1)** | O(n) | O(log n) |
| build from n items | O(n) | O(n) | O(n) | O(n) `heapify` | O(n log n) sort |
| sort / k smallest | O(n log n) | — | — | O(n log k) `nsmallest` | already sorted |

\* amortised. Sets: `a | b` O(len a + len b); `a & b` O(min); dict/set worst case O(n) per operation
under heavy collisions. Strings: `s + t` O(len s + len t), `"".join(parts)` O(total), slicing O(k).
`Counter(xs)` O(n); `most_common(k)` O(d log k) for d distinct keys.

ex10 times each pair and prints only the comparison:

```text
set beats list for membership: True
deque beats list for popleft: True
bisect beats linear scan for rank: True
```

## 6.15 `array` module ○

`array.array("i", [1, 2, 3])` stores raw C numbers compactly (4 bytes each here instead of an
8-byte pointer to an int object); use NumPy (Chapter 33) when you need vector maths.

## Interviewer's view

- **Rewarded:** naming the cost of the operation you rely on ("`in` on a set, O(1) average");
  explaining dict internals at the level of §6.5; handling ties deliberately in sorts and heaps.
- **Penalised:** `list.pop(0)` in a BFS loop; `x in list` inside a loop; `defaultdict` reads that
  create keys; `sort()` assigned to a variable (`None`); comparator sorts where a tuple key would do.
- **Strong signal:** you justify the library call by complexity, not by "it's Pythonic".

## Exercises

All in `chapters/ch06_collections_stdlib_toolbox/` (statements, ladders, tests in the repo).

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Sticker sheets: multiset algebra | ★ | `Counter` `<= - & \|` |
| ex02 | Inverted index | ★ | `defaultdict(set)`, set algebra |
| ex03 | Recent-items windows | ★ | `deque`, `OrderedDict` |
| ex04 | Merge sorted feeds, running k-th largest | ★ | `heapq` |
| ex05 | Grade bands and a sorted leaderboard | ★ | `bisect`, `insort` |
| ex06 | Uptime and budget reports | ◆ | `groupby`, `accumulate`, `combinations`, `product` |
| ex07 | Largest concatenated number | ★ | `cmp_to_key` |
| ex08 | Multi-key stable sorting | ★ | tuple keys, stable passes |
| ex09 | Build a tiny dict | ◆ | open addressing, compact dict |
| ex10 | Choosing the right built-in | ◆ | complexity-driven choice |
| ex11 | Character toolbox | ★ | `ord`/`chr`, `join`, `translate` |

## Checkpoint quiz

1. What does `Counter("aab") - Counter("abbb")` return, and why?
2. Why does deleting a key leave a DUMMY marker instead of marking the slot EMPTY?
3. On a sorted list `a`, how do you count the values in `[lo, hi]`?
4. Why does reverse-lexicographic sorting fail for "Largest Number"? Give an input.
5. You need the 10 largest values of a 10⁷-element stream in O(1) extra memory per item. What
   structure and what cost?

<details>
<summary>Answers</summary>

1. `Counter({'a': 1})`. Subtraction gives a: 2−1 = 1, b: 1−3 = −2, and `-` drops counts ≤ 0.
2. Lookup stops at the first EMPTY slot. Emptying a slot in the middle of a probe chain would hide
   every key that was placed further along that chain.
3. `bisect_right(a, hi) - bisect_left(a, lo)` — O(log n).
4. Prefix cases: `[3, 30, 34]` gives `"34303"` but `"34330"` is larger. Use `a+b > b+a` via `cmp_to_key`.
5. A min-heap of size 10: push while small, then `heappushpop` when a value beats `heap[0]`.
   O(n log 10) time, O(10) memory.

</details>

## Summary card

- list: O(1) index/append/pop-end; O(n) front ops, `in`, middle insert/delete; slices copy.
- tuple: immutable, hashable if contents are; unpack with `*rest`; `namedtuple` for records.
- set/dict: O(1) average membership; dict keeps insertion order (3.7+); views are live.
- dict internals: `hash & mask` → perturbed open addressing → compact ordered entries → DUMMY on
  delete → rebuild to 2ᵏ ≥ 3 × live when 2/3 full. Sets: same probing, no order, ~60 % load.
- `Counter` multiset ops; `defaultdict` creates on read; `deque` O(1) both ends; `OrderedDict.move_to_end`.
- `heapq`: min-heap; heapify O(n); push/pop O(log n); top-k O(n log k); negate for max.
- `bisect_left` = first ≥ x, `bisect_right` = first > x; `insort` is O(n).
- `itertools`: `groupby` = adjacent runs; `accumulate` = prefix sums; `product`/`permutations`/`combinations`.
- Sorting is stable; tuple keys for mixed directions; multi-pass for string-descending; `cmp_to_key` last.
