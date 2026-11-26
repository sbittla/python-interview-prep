# Chapter 7. Python Gotchas and Interview Traps

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 5 hours · **Prerequisites:** Chapters 5–6

Canonical home for Python's traps; later chapters cite these sections. **Every listing is a
predict-the-output quiz:** cover the `text` block, predict, then check. Each gotcha shows the
wrong-but-tempting code, its real output (CPython 3.13), the cause and the fix. Version-specific
behaviour is flagged in place and collected under **Version watch**.

**Learning objectives**

- Explain each trap by its mechanism ("the default is evaluated once"), then fix the cause.
- Separate language rules from CPython details and version-specific behaviour.
- Name the hidden O(n) in innocent lines: `pop(0)`, `x in list`, slicing, string `+=`.

> **Recognise it**
>
> | Symptom | Trap |
> |---|---|
> | State leaks between calls or instances | 7.1, 7.4 |
> | Changing the copy changed the original | 7.2, 7.3 |
> | Every callback sees the last loop value | 7.5 |
> | Equal objects, but `set`/`dict` fails | 7.7 |
> | Off by a cent, a half, or one on negatives | 7.8, 7.9 |
> | Second pass over data is empty | 7.12 |
> | Correct but times out at n = 10⁵ | 7.15–7.18 |

## 7.1 References: mutable default arguments

```python
def add_tag(tag, tags=[]):           # wrong-but-tempting
    tags.append(tag)
    return tags

print(add_tag("python"), add_tag("sql"), add_tag.__defaults__)

def add_tag_fixed(tag, tags=None):   # fix: fresh list per call
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

print(add_tag_fixed("python"), add_tag_fixed("sql"))
```

```text
['python', 'sql'] ['python', 'sql'] (['python', 'sql'],)
['python'] ['sql']
```

A default is evaluated **once**, when `def` runs, and stored in `__defaults__`; both calls return
that one list, so it prints twice. Default to `None` (or a private `_MISSING = object()` when `None`
is a legal value). Immutable defaults (`()`, `0`) are safe (ex01).

## 7.2 References: aliasing (`a = b = []`), shallow vs deep copy

```python
import copy

a = b = []
a.append(1)
x = y = [1]
x += [2]          # list += mutates in place: y sees it
x = x + [3]       # + builds a new list and rebinds x only
print(b, y, x)

cfg = {"db": {"port": 5432}, "tags": ["dev"]}
shallow, deep = cfg.copy(), copy.deepcopy(cfg)
shallow["db"]["port"] = 6543     # inner dict shared with cfg
deep["tags"].append("prod")      # independent
print(cfg, shallow["db"] is cfg["db"])
```

```text
[1] [1, 2] [1, 2, 3]
{'db': {'port': 6543}, 'tags': ['dev']} True
```

| Operation | New outer object? | Inner objects |
|---|---|---|
| `b = a` | no | shared |
| `a[:]`, `list(a)`, `.copy()`, `dict(d)`, `copy.copy` | yes | shared (shallow) |
| `copy.deepcopy` | yes | copied recursively (memo handles cycles), O(total size) |

Assignment never copies. A tuple is immutable but a list inside it is not. Deep-copy only what you
mutate, or copy just the changed path: `{**cfg, "db": {**cfg["db"], "port": 1}}` (ex02).

## 7.3 References: `[[0] * n] * m` shares rows

```python
grid = [[0] * 3] * 2                 # two references to ONE row
grid[0][0] = 9
fixed = [[0] * 3 for _ in range(2)]
fixed[0][0] = 9
print(grid, fixed)
```

```text
[[9, 0, 0], [9, 0, 0]] [[9, 0, 0], [0, 0, 0]]
```

`*` repeats references. The inner `[0] * 3` is safe because assigning a cell rebinds a slot; any
mutable element (a row, a `[]` cell) must be created per position (ex03).

## 7.4 References: mutable class variables shared across instances

```python
from dataclasses import dataclass

class Cart:
    items = []                     # ONE list, on the class
    def add(self, item):
        self.items.append(item)    # read falls back to the class

a, b = Cart(), Cart()
a.add("apple")
print(b.items, "items" in vars(a))
try:
    @dataclass
    class BadCart:
        items: list = []
except ValueError as e:
    print("ValueError:", e)
```

```text
['apple'] False
ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory
```

Attribute *reads* fall back to the class; *assignment* creates an instance attribute, so
`self.n += 1` on a class-level int quietly stops sharing. Create mutable state in `__init__` or use
`field(default_factory=list)` (ex04, → §24.2, §24.8).

## 7.5 Scope: late binding in closures and loop lambdas; `nonlocal`

```python
fs = [lambda x: x * i for i in range(3)]
fixed = [lambda x, i=i: x * i for i in range(3)]   # bind the value now
print([f(10) for f in fs], [f(10) for f in fixed])

def make_counter():
    count = 0
    def step():
        nonlocal count      # without it: UnboundLocalError
        count += 1
        return count
    return step

c = make_counter()
print(c(), c(), c())
```

```text
[20, 20, 20] [0, 10, 20]
1 2 3
```

A closure captures the **variable** and reads it when called, after the loop ended. Bind early with
a default argument or `functools.partial`. Assigning a name anywhere in a function makes it local
for the whole body; `nonlocal` rebinds the enclosing function's variable, `global` the module's
(ex05, → Ch. 25).

## 7.6 Equality: `is` vs `==`, small-integer caching, `bool` subclasses `int`

```python
import warnings

print([1] == [1], [1] is [1])
x, y, p, q = int("256"), int("256"), int("257"), int("257")
print(x is y, p is q)
print(True + True, isinstance(True, int), {1: "int", True: "bool", 1.0: "float"})
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    compile("n = 5\nn is 5", "<demo>", "exec")
print(caught[0].category.__name__, caught[0].message)
```

```text
True False
True False
2 True {1: 'float'}
SyntaxWarning "is" with 'int' literal. Did you mean "=="?
```

`==` compares values; `is` compares identity — use it only for `None` and sentinels. CPython
caches −5…256, an **implementation detail**; the compiler may also merge equal constants, so
`257 is 257` can be `True` (→ §27.1), which is why the values above are built at run time. `is`
with a literal warns since **3.8** (wording shown is 3.13's). `True`, `1` and `1.0` are equal with
equal hashes, so they are one dict key: the first key object stays, the last value wins.

## 7.7 Equality: `__eq__` without `__hash__`

```python
from dataclasses import dataclass

class P:
    def __init__(self, x): self.x = x
    def __eq__(self, o): return isinstance(o, P) and self.x == o.x

try:
    {P(1)}
except TypeError as e:
    print(P.__hash__, "TypeError:", e)

@dataclass(frozen=True)
class Q:
    x: int

@dataclass(unsafe_hash=True)     # hashes a mutable field
class M:
    x: int

m = M(1)
s = {m}
m.x = 2
print(len({Q(1), Q(1)}), m in s, M(1) in s)
```

```text
None TypeError: unhashable type: 'P'
1 False False
```

Defining `__eq__` sets `__hash__ = None`, because the identity hash would break the contract
**`a == b` ⇒ `hash(a) == hash(b)`** (collisions are fine). Hash exactly the fields `__eq__`
compares, and only immutable ones: after `m.x = 2` the key sits in hash-1's bucket but equals
nothing there — lost. `@dataclass(frozen=True)` generates a safe pair (ex06, → §24.6).

## 7.8 Numbers: floating-point error; `math.isclose`, `Decimal`, `Fraction`

```python
import math
from decimal import Decimal
from fractions import Fraction

print(0.1 + 0.2, int(0.29 * 100))
print(math.isclose(0.1 + 0.2, 0.3), math.isclose(1e-17, 0.0),
      math.isclose(1e-17, 0.0, abs_tol=1e-9))
print(Decimal("0.10") + Decimal("0.20"), Decimal(0.1) == Decimal("0.1"))
print(Fraction(1, 3) * 3 == 1, sum([0.1] * 10))
```

```text
0.30000000000000004 28
True False True
0.30 False
True 1.0
```

| Need | Use |
|---|---|
| Measurements, ML | `float` + `math.isclose` (defaults `rel_tol=1e-09, abs_tol=0.0`: pass `abs_tol` near 0) |
| Money | `Decimal` from **strings** (`Decimal(0.1)` keeps the error) or integer cents (ex07) |
| Exact ratios | `Fraction` (slower; denominators grow) |

Since **3.12** `sum()` of floats is compensated, so `sum([0.1] * 10)` is `1.0`; 3.11 and earlier
give `0.9999999999999999`. `math.fsum` is accurate on every version.

## 7.9 Numbers: `//` and `%` with negatives; banker's rounding in `round()`

```python
print(-7 // 2, -7 % 2, 7 % -2, int(-7 / 2))
print(round(0.5), round(1.5), round(2.5), round(2.675, 2))
```

```text
-4 1 -1 -3
0 2 2 2.67
```

`//` **floors** toward −∞ and `%` takes the divisor's sign, so `a == (a // b) * b + a % b` holds and
`i % n` is a safe wrap-around index; C, Java and SQL truncate toward zero. `round()` sends halves
**to even**, and 2.675 is stored just below itself.

### Worked problem — C-style division and receipt rounding (ex08)

*Task.* `div_toward_zero(a, b)` truncates like C for ints of any size; `round_half_up(value,
places)` rounds a decimal string half away from zero.

*Ladder.* (1) `a // b`: wrong when signs differ. (2) `int(a / b)`: `/` makes a float, wrong above 2⁵³
— move up for exactness. (3) Floor-divide absolute values, restore the sign: exact. Rounding:
`round(float(v), p)` fails twice (half-even, binary); `Decimal.quantize` with `ROUND_HALF_UP` is exact.

```python
from decimal import ROUND_HALF_UP, Decimal

def div_toward_zero(a: int, b: int) -> int:
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q

def round_half_up(value: str, places: int = 0) -> Decimal:
    step = Decimal(1).scaleb(-places)          # places=2 -> 0.01
    return Decimal(value).quantize(step, rounding=ROUND_HALF_UP)

print([div_toward_zero(a, b) for a, b in [(-7, 2), (7, -2), (0, -5)]])
big = 10**20 + 1
print(int(-big / 1) == -big, div_toward_zero(-big, 1) == -big)
for v, p in [("-2.5", 0), ("2.675", 2)]:
    print(v, round(float(v), p), round_half_up(v, p))
```

```text
[-3, -3, 0]
False True
-2.5 -2.0 -3
2.675 2.67 2.68
```

→ repo: `chapters/ch07_python_gotchas/solutions/ex08_rounding_and_division.py`

*Edge cases:* negative divisor, `a == 0`, exact division, ints beyond 2⁵³, negative halves.
*Wrong-but-tempting:* `math.floor(x + 0.5)` (−2.5 → −2). *Follow-ups:* C-style remainder
(`math.fmod`); when banks *want* `ROUND_HALF_EVEN`.

## 7.10 Numbers: unbounded ints, `float('inf')`, overflow assumptions from other languages

```python
inf, nan = float("inf"), float("nan")
print(2**64, inf > 10**400, inf - inf, nan == nan, max(nan, 1), max(1, nan))
for f, arg in [(float, 10**400), (str, 10**5000)]:
    try:
        f(arg)
    except (OverflowError, ValueError) as e:
        print(type(e).__name__, str(e).split(";")[0])
```

```text
18446744073709551616 True nan False nan 1
OverflowError int too large to convert to float
ValueError Exceeds the limit (4300 digits) for integer string conversion
```

Ints never overflow (`lo + (hi - lo) // 2` is habit, not need), but huge-int arithmetic is not
O(1) and conversion to `float` can overflow. `inf` is a good "no answer yet" sentinel — map an
untouched `inf` back to −1. NaN compares false, so `max` depends on argument order. Since
**3.11** (and security release 3.10.7) `int`↔`str` conversion stops at 4,300 digits
(`sys.set_int_max_str_digits` raises it). 32-bit wrap needs explicit masking (→ Ch. 21).

## 7.11 Iteration: mutating a list/dict while iterating

```python
nums = [2, 4, 6, 1]
for x in nums:
    if x % 2 == 0:
        nums.remove(x)
print(nums)                       # 4 was skipped, silently
counts = {"a": 0, "b": 2}
try:
    for k in counts:
        if counts[k] == 0:
            del counts[k]
except RuntimeError as e:
    print("RuntimeError:", e)
```

```text
[4, 1]
RuntimeError: dictionary changed size during iteration
```

The list iterator keeps an index; `remove` shifts the next item into the current slot. Dicts and
sets detect the size change and raise. Fix: rebuild (`nums[:] = [x for x in nums if x % 2]`, O(n))
or loop over a snapshot (`for k in list(counts)`). Updating values is safe (ex09).

## 7.12 Iteration: exhausted generators; `zip`/`map` return iterators

```python
from itertools import groupby

sq = (x * x for x in range(4))
pairs = zip("abc", [1, 2])               # also map, filter, enumerate, files
print(sum(sq), sum(sq), list(pairs), list(pairs))
it = iter([1, 2, 3])
print(2 in it, list(it))                 # `in` consumes up to the match
try:
    list(zip("ab", [1], strict=True))    # 3.10+
except ValueError as e:
    print("ValueError:", e)
groups = list(groupby("aab"))
print([(k, list(g)) for k, g in groups])
```

```text
14 0 [('a', 1), ('b', 2)] []
True [3]
ValueError: zip() argument 2 is shorter than argument 1
[('a', []), ('b', [])]
```

Iterators are single-pass and a second pass silently sees nothing; plain `zip` silently truncates.
`groupby` groups share one iterator, so stored groups come back empty — consume each as you go.
Fix: `list(...)` once, or do all the work in one pass (ex10).

## 7.13 Iteration: `for … else` semantics

```python
import math

def is_prime_buggy(n):
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
        else:                 # bound to the if: decides after ONE divisor
            return True
    return n >= 2

def first_divisor(n):
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            break
    else:                     # runs only if the loop did not break
        return None
    return d

print([n for n in range(2, 16) if is_prime_buggy(n)], first_divisor(91), first_divisor(3))
```

```text
[2, 3, 5, 7, 9, 11, 13, 15] 7 None
```

The loop's `else` means "no `break`" and also runs when the loop body never executes (`3` has an
empty range). `while … else` is the same. A flag or early `return` is often clearer (ex11).

## 7.14 Collections: `defaultdict` creates keys on read; `Counter` subtraction drops ≤0

```python
from collections import Counter, defaultdict

index = defaultdict(list, {"cat": [1]})
print(bool(index["dog"]), sorted(index), index.get("emu"), Counter()["x"])
stock, orders = Counter(apple=2, pear=1), Counter(apple=2, pear=3)
left = stock.copy()
left.subtract(orders)
print(stock - orders, left)
```

```text
False ['cat', 'dog'] None 0
Counter() Counter({'apple': 0, 'pear': -2})
```

`d[k]` on a `defaultdict` calls the factory and **stores** the result; check with `in` or `.get`
(a `Counter` read returns 0 without inserting). `+`, `-`, `&`, `|` on Counters drop counts ≤ 0;
`.subtract()` keeps them (ex12, → §6.7).

## 7.15 Collections: `list.pop(0)` / `insert(0, x)` are O(n) — use `deque`

```python
import time
from collections import deque

def drain(q, pop):
    while q:
        pop(q)

def best_of_3(make, pop, n=30_000):
    times = []
    for _ in range(3):
        q = make(range(n))
        t = time.perf_counter()
        drain(q, pop)
        times.append(time.perf_counter() - t)
    return min(times)

fast = best_of_3(deque, deque.popleft)
slow = best_of_3(list, lambda q: q.pop(0))
print("deque 10x faster:", fast * 10 < slow)
```

```text
deque 10x faster: True
```

A list is a contiguous array: a front pop or insert moves all n references, so a BFS on
`pop(0)` is O(n²). `deque.popleft`/`appendleft` are O(1).

## 7.16 Collections: `x in list` O(n) vs set/dict O(1)

```python
class Counted:
    calls = 0
    def __init__(self, v): self.v = v
    def __eq__(self, o):
        Counted.calls += 1
        return self.v == o.v
    def __hash__(self): return hash(self.v)

for n in (100, 200, 400):
    items, row = [Counted(i) for i in range(n)], [n]
    for seen in ([], set()):
        Counted.calls = 0
        add = seen.append if isinstance(seen, list) else seen.add
        for x in items:
            if x not in seen:
                add(x)
        row.append(Counted.calls)
    print(*row)
```

```text
100 4950 0
200 19900 0
400 79800 0
```

Columns: n, `==` calls with a list, with a set. Doubling n quadruples the list's n(n−1)/2 scans; a
set compares only on a hash match (average O(1), → §6.5). Ordered dedupe: `list(dict.fromkeys(xs))`
(ex13).

## 7.17 Collections: slicing copies; string `+=` in loops O(n²)

```python
copied = 0
def total(xs):
    global copied
    if not xs:
        return 0
    copied += len(xs) - 1
    return xs[0] + total(xs[1:])        # copies n-1 items per call

print(total(list(range(1, 101))), copied)
```

```text
5050 4950
```

Slicing inside recursion turns O(n) into O(n²); pass an index instead. Strings are immutable, so
`s += piece` may copy the whole string each time: O(n²) worst case. CPython often resizes in place
when only one reference exists — a detail not to rely on. `"".join(parts)` is reliably linear.

## 7.18 Collections: `deque` middle indexing is O(n)

```python
from collections import deque

d = deque(range(10))
try:
    print(d[0], d[5], d[2:4])
except TypeError as e:
    print("TypeError:", e)
```

```text
TypeError: sequence index must be integer, not 'slice'
```

CPython's `deque` is a doubly linked list of blocks: O(1) at the ends, O(n) toward the middle, no
slicing (use `itertools.islice`). Need both? A list plus a head index.

## 7.19 Sorting: stability, `key` vs `cmp_to_key`, mixed types and `None`

```python
rows = [("bo", 90), ("al", 90), ("cy", None)]
try:
    sorted(rows, key=lambda r: r[1])
except TypeError as e:
    print("TypeError:", e)
xs = [3, 1, 2]
print(sorted(rows[:2], key=lambda r: r[1]), xs.sort(), xs)
```

```text
TypeError: '<' not supported between instances of 'NoneType' and 'int'
[('bo', 90), ('al', 90)] None [1, 2, 3]
```

Python 3 will not order `None` against `int` (or `int` against `str`). Sorts are stable — equal keys
keep input order, even with `reverse=True`. `.sort()` returns `None`. A `key` runs once per item; a
`cmp_to_key` comparator runs O(n log n) times (→ §6.12).

### Worked problem — leaderboard with missing scores (ex16)

*Task.* Records `{"name", "score"}`, `score` possibly `None`: score descending, ties by name, `None`
last.

*Ladder.* (1) `key=score, reverse=True`: `TypeError`, and `reverse` flips the name order too.
(2) `key=score or -1`: a real 0 is falsy and joins the non-finishers. (3) Tuple key
`(score is None, -score, name)`: `False < True` puts finishers first; negation gives descending
numbers with ascending names. Alternatives in the repo: two stable passes (secondary key first) and
`cmp_to_key`, needed when no key works (descending *strings*).

```python
def leaderboard(records):
    def key(r):
        s = r["score"]
        return (s is None, -(s if s is not None else 0), r["name"])
    return [r["name"] for r in sorted(records, key=key)]

records = [{"name": n, "score": s} for n, s in
           [("cy", None), ("bo", 90), ("al", 90), ("ab", None), ("ed", 0)]]
print(leaderboard(records), leaderboard([]))
tempting = sorted(records, key=lambda r: r["score"] or -1, reverse=True)
print([r["name"] for r in tempting])
```

```text
['al', 'bo', 'ed', 'ab', 'cy'] []
['bo', 'al', 'cy', 'ab', 'ed']
```

→ repo: `chapters/ch07_python_gotchas/solutions/ex16_sort_with_none.py`

*Edge cases:* empty, all `None`, a 0 score, top ties. All variants O(n log n). *Follow-ups:* `None`
first (flip the first component); descending by name (two passes); why the comparator is slowest.

## 7.20 Heaps: min-only (negate for max); tuple tie-breaks compare next field

```python
import heapq
import itertools

heap = [-x for x in [5, 1, 9, 3]]
heapq.heapify(heap)                  # a list is not a heap until heapified
print(-heapq.heappop(heap), hasattr(heapq, "heappush_max"))
jobs = [(2, {"n": "b"}), (1, {"n": "a"}), (2, {"n": "c"})]
try:
    h = list(jobs)
    heapq.heapify(h)
    print([heapq.heappop(h)[1]["n"] for _ in jobs])
except TypeError as e:
    print("TypeError:", e)
seq = itertools.count()
h = [(p, next(seq), job) for p, job in jobs]
heapq.heapify(h)
print([heapq.heappop(h)[2]["n"] for _ in jobs])
```

```text
9 False
TypeError: '<' not supported between instances of 'dict' and 'dict'
['a', 'b', 'c']
```

`heapq` is a min-heap: negate numbers for max (strings need a wrapper with reversed `__lt__`).
Tuples compare field by field, so equal priorities reach the payload; a unique counter as second
field stops there and makes ties FIFO (ex14, → §6.8). Public max-heap functions
(`heappush_max`, …) arrive in **3.14** — absent in 3.13, as printed.

## 7.21 Recursion: ~1000 default limit, no tail-call optimisation, `sys.setrecursionlimit`

```python
import sys

def depth_tail(n, acc=0):
    return acc if n == 0 else depth_tail(n - 1, acc + 1)   # a tail call, still a frame

print(sys.getrecursionlimit())
try:
    depth_tail(5_000)
except RecursionError as e:
    print("RecursionError:", e)
sys.setrecursionlimit(10_000)
print(depth_tail(5_000))
```

```text
1000
RecursionError: maximum recursion depth exceeded
5000
```

CPython's default is 1,000 frames (including those already on the stack) and it never eliminates
tail calls. Raising the limit is a patch: deeper input fails again, every frame costs memory, and
recursion through C code can still overflow the C stack (before 3.11 pure-Python recursion could
too and crash the process). Use a loop or explicit stack (→ §14.2; ex15).

## 7.22 Caching: `lru_cache` needs hashable args; unbounded `cache` memory growth

```python
import gc
import weakref
from functools import cache

@cache
def total(xs):
    return sum(xs)

try:
    total([1, 2])
except TypeError as e:
    print("TypeError:", e)
print(total((1, 2)), total.cache_info())

class Model:
    @cache                     # one cache on the class; keys hold self
    def score(self, x):
        return x * 2

m = Model()
m.score(3)
ref = weakref.ref(m)
del m
gc.collect()
print("instance freed:", ref() is None)
```

```text
TypeError: unhashable type: 'list'
3 CacheInfo(hits=0, misses=1, maxsize=None, currsize=1)
instance freed: False
```

Arguments form the key, so they must be hashable (pass tuples). `cache` (3.9+) is
`lru_cache(maxsize=None)`: it never evicts, so a long-running process grows without bound;
`lru_cache()` defaults to 128 entries. Cached methods keep every `self` alive, and cached mutable
results are shared by all callers. Fixes: bound `maxsize`, `cache_clear()`, or a cached helper
defined inside the function (→ §6.11, §19.2, Ch. 25).

## 7.23 Strings: `split()` vs `split(' ')`; immutability; Unicode vs bytes

```python
import unicodedata

print(" a  b ".split(), " a  b ".split(" "), "".split(","))
try:
    "cat"[0] = "b"
except TypeError as e:
    print("TypeError:", e)
one, two = "café", "café"           # é vs e + combining accent
print(one == two, len(one), len(two), len(one.encode()), b"abc"[0])
print(unicodedata.normalize("NFC", two) == one)
user = {"name": "ana"}
print(f"{user["name"]}")                       # 3.12+ only (PEP 701)
```

```text
['a', 'b'] ['', 'a', '', 'b', ''] ['']
TypeError: 'str' object does not support item assignment
False 4 5 5 97
True
ana
```

`split()` splits on whitespace runs and drops empties; `split(" ")` keeps one empty string per
extra space. Strings are immutable: build new ones. `len` counts code points, not bytes or visible
characters — normalise before comparing user text; indexing `bytes` gives an `int`. **Version
trap:** reusing the outer quote inside an f-string is legal only from **3.12** (PEP 701, which also
allows backslashes and comments there); 3.10/3.11 raise `SyntaxError`. Write `f"{user['name']}"`.

## 7.24 Concurrency: GIL and optional free-threaded build; threads vs processes vs asyncio

```python
import sys
import sysconfig

print(sysconfig.get_config_var("Py_GIL_DISABLED"), sys._is_gil_enabled())   # 3.13+
```

```text
0 True
```

| Workload | Tool |
|---|---|
| CPU-bound pure Python (threads don't run bytecode in parallel under the GIL) | processes, NumPy |
| Blocking I/O, tens of tasks (GIL released while waiting) | threads |
| Thousands of concurrent I/O waits | `asyncio` |

The GIL does **not** make `count += 1` atomic; shared state needs a lock. The free-threaded build
is experimental in 3.13 and supported but opt-in in 3.14; the default build, used here, keeps the
GIL (→ §27.5–§27.7, Ch. 28).

## 7.25 Concurrency: forgetting `await`, blocking calls in async, unbounded `gather`

```python
import asyncio
import time

async def work(blocking):
    time.sleep(0.05) if blocking else await asyncio.sleep(0.05)

async def main():
    c = work(False)                     # forgot await: nothing ran
    print(type(c).__name__)
    c.close()
    for blocking in (True, False):
        t = time.perf_counter()
        await asyncio.gather(*(work(blocking) for _ in range(4)))
        print("blocking" if blocking else "async", time.perf_counter() - t > 0.15)
    sem, live, peak = asyncio.Semaphore(3), 0, 0
    async def limited():
        nonlocal live, peak
        async with sem:
            live += 1
            peak = max(peak, live)
            await work(False)
            live -= 1
    await asyncio.gather(*(limited() for _ in range(20)))
    print("peak:", peak)

asyncio.run(main())
```

```text
coroutine
blocking True
async False
peak: 3
```

Calling a coroutine function only builds a coroutine; unawaited, it never runs (Python warns
`never awaited`). A blocking call freezes every task — the four `time.sleep`s took over 0.15 s,
the async ones overlapped; use `await asyncio.to_thread(f)` (3.9+). Bound a huge `gather` with a
`Semaphore`. `TaskGroup` (3.11+) cancels siblings on failure and raises `ExceptionGroup`, caught
with `except*`; `exc.add_note()` (3.11+) adds context (→ §28.6–§28.9).

## 7.26 Typing: hints are not enforced at runtime

```python
def double(x: int) -> int:
    return x * 2

print(double("ab"), double.__annotations__)
```

```text
abab {'x': <class 'int'>, 'return': <class 'int'>}
```

Annotations are stored, never checked. mypy/pyright catch `double("ab")` statically; at run time you
need `isinstance` or a validator (→ repo:
`chapters/ch05_syntax_types_functions/solutions/ex12_check_annotations.py`).

## 7.27 Serialisation: `pickle` is unsafe on untrusted data

```python
import pickle

class Payload:
    def __reduce__(self):                 # "rebuild me by calling print(...)"
        return (print, ("code ran during pickle.loads!",))

pickle.loads(pickle.dumps(Payload()))
```

```text
code ran during pickle.loads!
```

Unpickling may call any importable callable — `os.system` as easily as `print`. Never unpickle
data you do not control; exchange JSON, sign trusted pickles (HMAC), and load checkpoints with
`torch.load(..., weights_only=True)` (→ §37.7).

## 7.28 Gotchas cumulative quiz

```python
from collections import Counter

def f(x, acc=[]):
    acc.append(x)
    return len(acc)
print(f(1), f(2))
fs = [lambda: i for i in range(3)]
print(fs[0]())
print(-7 // 2, round(3.5), round(4.5))
g = (ch for ch in "abc")
print("b" in g, list(g))
print({True: "t", 1: "one"})
a = [1, 2]; b = a; a += [3]; a = a + [4]
print(b)
print(Counter("aab") - Counter("abc"))
print(0.1 * 3 == 0.3, sorted([3, 1, 2]).reverse())
```

<details>
<summary>Answers</summary>

```text
@@
```

(1) Shared default, §7.1. (2) Late binding, §7.5. (3) Floor; halves to even, §7.9. (4) `in`
consumed `a`, `b`, §7.12. (5) One key, §7.6. (6) `+=` mutates, `+` rebinds, §7.2. (7) ≤ 0 dropped,
§7.14. (8) §7.8; `reverse()` returns `None`, §7.19.

</details>

## Version watch

| Since | Behaviour (§) |
|---|---|
| 3.8 | `is` with a literal → `SyntaxWarning` (7.6) |
| 3.9 | `functools.cache`, `asyncio.to_thread` (7.22, 7.25) |
| 3.10 | `zip(strict=True)` (7.12) |
| 3.11 | 4,300-digit `int`↔`str` limit, also 3.10.7 (7.10); `TaskGroup`, `except*`, `add_note` (7.25); pure-Python calls off the C stack (7.21) |
| 3.12 | compensated float `sum` (7.8); PEP 701 f-strings (7.23) |
| 3.13 | experimental free-threaded build; 3.14 supported opt-in (7.24) |
| 3.14 | public max-heap functions in `heapq` (7.20) |

Implementation details, never guarantees: the small-int cache, constant merging, in-place `+=`.

## Interviewer's view

- **Rewarded:** naming the mechanism in one sentence; fixing the cause; separating language rules
  from CPython details.
- **Penalised:** `is` for values, `==` on floats, `pop(0)` or `x in list` in loops,
  `setrecursionlimit` as the fix, mutable defaults in your own code.
- **Strong signal:** predicting buggy code's output before running it, then proving the fix with an
  edge case.

## Exercises

All in `chapters/ch07_python_gotchas/`; each has a `buggy_*` version, the fix, and edge-case tests.

| ID | Title | Tier | § |
|---|---|---|---|
| ex01 | Mutable default argument | ★ | 7.1 |
| ex02 | Shallow copy of a nested config | ★ | 7.2 |
| ex03 | Grid rows that move together | ★ | 7.3 |
| ex04 | Shopping carts that share items | ★ | 7.4 |
| ex05 | Late-binding lambdas, broken counter | ★ | 7.5 |
| ex06 | Equal points that cannot go in a set | ★ | 7.7 |
| ex07 | Bills that never settle | ★ | 7.8 |
| ex08 | Rounding and negative division | ★ | 7.9 |
| ex09 | Removing items while looping | ★ | 7.11 |
| ex10 | Statistics from an exhausted iterator | ★ | 7.12 |
| ex11 | A primality test that gives up early | ★ | 7.13 |
| ex12 | `defaultdict` phantom keys, `Counter` drops | ◆ | 7.14 |
| ex13 | Deduplication that gets slow | ◆ | 7.16 |
| ex14 | Max-heap and tie-breaking bugs | ★ | 7.20 |
| ex15 | Recursion that hits the limit | ★ | 7.21 |
| ex16 | A leaderboard that crashes on `None` | ◆ | 7.19 |

## Checkpoint quiz

1. Why does `@dataclass` reject `items: list = []`?
2. May equal objects have different hashes? May unequal ones share a hash?
3. Give exact C-style division for 30-digit ints.
4. A BFS over 10⁵ nodes uses `queue.pop(0)`. Cost and fix?
5. Why is `sys.setrecursionlimit(10**6)` weak for a 10⁶-deep DFS?

<details>
<summary>Answers</summary>

1. The list would be shared by every instance (§7.4); it demands `default_factory`.
2. No: `a == b` must imply equal hashes. Yes: collisions are legal.
3. `q = abs(a) // abs(b)`, negated if the signs differ; `int(a / b)` goes through a float.
4. O(n²), each pop shifts the rest; `deque.popleft()` gives O(n).
5. Frames cost memory, deeper input fails again, C-level recursion can still crash; an explicit
   stack has no limit (§14.2).

</details>

## Summary card

- Defaults evaluate once → `None`. Class-body lists are shared → `__init__`.
- `=` aliases; `copy()`/`[:]` are shallow; `deepcopy` nested data; `[[0]*n for _ in …]`.
- Closures read late → `i=i`; assignment makes a name local → `nonlocal`.
- `is` only for `None`/sentinels; `True == 1` as a key. `__eq__` kills `__hash__` → `frozen=True`.
- Floats: `isclose` + `abs_tol`; money `Decimal("…")`. `//` floors; `round` halves to even.
- No resizing while iterating; iterators are one-pass; `for … else` = no `break`.
- `defaultdict[k]` inserts; `Counter -` drops ≤ 0; `pop(0)`, `x in list`, slices, `deque[i]` are O(n).
- Stable sorts; tuple keys; `None` vs int raises. Heaps: negate, `(prio, seq, item)`.
- 1,000 frames, no TCO → explicit stack. `cache`: hashable args, unbounded, pins `self`.
- GIL ≠ atomic; await everything; bound `gather`; hints don't run; never unpickle untrusted data.
