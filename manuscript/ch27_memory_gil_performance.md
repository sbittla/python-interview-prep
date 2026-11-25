# Chapter 27. Memory Model, GIL, Free-Threading and Performance

◆ Extended · Tracks S L (M optional) · Study time ≈ 4 h · Prerequisites: Chapters 7, 22, 24

**Learning objectives**

- Explain identity, reference counting and when the cycle collector is needed.
- Measure memory comparatively and justify `__slots__`.
- State what the GIL does and does not protect, and what free-threading changes.
- Pick processes, threads or asyncio, and profile before optimising.

> **Recognise it.** "Why didn't threads help?", "is `x += 1` thread-safe?", "a million small
> objects", "explain the GIL", "make this faster" → this chapter. Gotchas: → §7.6, §7.24; APIs: Ch. 28.

## 27.1 Everything is an object: identity, type, value

Every object has an **identity** (fixed for its lifetime; `id()`), a **type** and a **value**. `==`
compares values, `is` identity. Use `is` only for `None`, `True`/`False` and your own sentinels:

```python
import sys

print(int("256") is int("256"), int("257") is int("257"))   # built at run time
joined = "".join(["hello", "_", "world"])
print(joined is "hello_world", sys.intern(joined) is sys.intern("hello_world"))
```

```text
True False
False True
```

CPython caches the ints −5…256 and interns identifier-like string constants; neither is guaranteed
(→ §7.6). Build values at run time: the compiler folds equal literals, so `257 is 257` can print
`True`. The `is` with a literal draws a `SyntaxWarning`, itself the lesson. → repo:
`chapters/ch27_memory_gil_performance/solutions/ex01_identity_type_value.py`.

## 27.2 Reference counting and garbage collection

CPython frees an object the instant its **reference count** reaches zero. Cycles never reach zero,
so a **generational cycle collector** (`gc`) periodically scans containers (ints and strs are never
tracked). 3.10–3.13 use three generations; thresholds vary (`gc.get_threshold()` is `(700, 10, 10)`
in 3.12, `(2000, 10, 10)` in 3.13). 3.14.0–3.14.4 shipped an incremental collector with two
generations (young, old); 3.14.5 reverted to the 3.13 design. Since 3.12, `None`, `True` and small
ints are **immortal** (PEP 683): their refcount is a fixed sentinel.

**Worked problem 1 — "When is this object freed?"** With the collector off, link nodes, drop the
names, log deaths. *Ladder.* (1) `sys.getrefcount`: the call adds a reference. (2) Print in
`__del__`: adds a finaliser to the class under study. (3) `weakref.finalize(obj, callback)` fires
when the object dies, by either mechanism, without keeping it alive: O(1) per object;
`gc.collect()` is O(tracked objects), hence generations.

```python
import gc
import weakref


class Node:
    def __init__(self, name):
        self.name, self.other = name, None


def lifetime(cycle):
    events = []
    gc.disable()
    try:
        a, b = Node("a"), Node("b")
        a.other = b
        if cycle:
            b.other = a
        for node in (a, b):
            weakref.finalize(node, events.append, f"freed:{node.name}")
        del a, b, node
        events.append("collect")
        start = len(events)
        gc.collect()
        events[start:] = sorted(events[start:])   # order within one collection is unspecified
    finally:
        gc.enable()
    return events


print("chain", lifetime(False))
print("pair ", lifetime(True))
```

```text
chain ['freed:a', 'freed:b', 'collect']
pair  ['collect', 'freed:a', 'freed:b']
```

The chain dies at `del` (a's count hits zero, which drops b's); the pair waits for `gc.collect()`.
Edge cases: self-loop; `weakref.ref` back-link (no strong cycle); restoring the caller's `gc` state;
same-collection order. Wrong-but-tempting: "`del` frees the object"; it removes a *name*. Follow-ups: why only containers are tracked; how `WeakValueDictionary` caches avoid leaks.
→ repo: `chapters/ch27_memory_gil_performance/solutions/ex02_refcount_gc.py`.

## 27.3 Mutability and the memory model

Names bind to objects; containers hold references; assignment never copies. `[[0] * 3] * 3` holds
one row three times; a tuple's references are fixed, a list inside it is not. Copies: → §7.2. Ex03
finds aliased mutables with one DFS keyed by `id()` (O(m); a repeat id also stops cycles) and
reports `[('root[0]', 'root[1]'), ('root[0]', 'root[2]')]` for that grid.

## 27.4 `__slots__` and memory savings

**Worked problem 2 — "We hold a million `Point(x, y)` records; cut memory."** *Ladder.* (1)
`sys.getsizeof`: shallow; both classes below report 48 bytes on 64-bit 3.12/3.13. (2) Add
`getsizeof(obj.__dict__)`: on 3.12/3.13 touching `__dict__` allocates a new dict, so you measure your
probe. (3) Compare `tracemalloc` peaks over n instances: O(n) time and memory.

```python
import tracemalloc


class Plain:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Slotted:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


def peak_bytes(cls, n):
    tracemalloc.start()
    items = [cls(i, i) for i in range(n)]
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak


plain, slotted = peak_bytes(Plain, 50_000), peak_bytes(Slotted, 50_000)
print("slots smaller:", slotted < plain)
print("saves at least 25%:", slotted <= 0.75 * plain)
```

```text
slots smaller: True
saves at least 25%: True
```

Slots replace the per-instance dict with fixed slots described on the class. Costs: no new
attributes (`AttributeError`), no `vars(obj)`, no weak references unless `"__weakref__"` is listed;
two bases with non-empty slots conflict. `@dataclass(slots=True)` (3.10+) does it for you (→ §24.8).
Edge cases: a slot-less base brings `__dict__` back; n = 0. Wrong-but-tempting: trusting
`getsizeof`. Follow-up: for millions of numbers, `array` or NumPy.
→ repo: `chapters/ch27_memory_gil_performance/solutions/ex04_slots_memory.py`.

## 27.5 The GIL in the default build: what it limits

The **global interpreter lock** lets one thread at a time execute Python bytecode, which keeps
refcounting cheap and C extensions simple. A blocking thread (I/O, `time.sleep`) releases it; when
another thread is waiting, the running thread is asked to drop it after each switch interval
(`sys.getswitchinterval()`, 0.005 s by default); long C work (hashlib, zlib, NumPy) can release it.
Ex05 (excerpt):

```text
gil enabled: True
threads overlap sleep-bound work: True
threads speed up CPU-bound work: False
```

**Worked problem 3 — "Threads each run `counter += 1`. Is the total always right?"** Not guaranteed:
it is load–add–store (`LOAD_GLOBAL`, `LOAD_CONST`, `BINARY_OP`, `STORE_GLOBAL` in 3.11+; `INPLACE_ADD`
instead of `BINARY_OP` in 3.10), and the language promises no atomicity. Older CPythons, other
implementations and the free-threaded build lose updates; current GIL builds switch only at certain
instructions and rarely show it. *Ladder.* (1) Run unlocked threads: zero losses prove nothing.
(2) `dis.dis` shows several instructions. (3) Model interleavings deterministically,
O(len(schedule)), then fix with a `Lock`:

```python
def run_schedule(schedule):
    """Each letter runs that thread's next step of one `+= 1`: load, add, store."""
    counter, step, reg = 0, {}, {}
    for t in schedule:
        k = step.get(t, 0)
        if k == 0:
            reg[t] = counter          # load
        elif k == 1:
            reg[t] += 1               # add
        elif k == 2:
            counter = reg[t]          # store (may overwrite another thread's update)
        else:
            raise ValueError(f"thread {t!r} ran more than 3 steps")
        step[t] = k + 1
    if any(k != 3 for k in step.values()):
        raise ValueError("unfinished thread")
    return counter


for s in ["AAABBB", "ABABAB", "ABBBAA"]:
    print(s, run_schedule(s))
```

```text
AAABBB 2
ABABAB 1
ABBBAA 1
```

Edge cases: empty schedule (0), three threads, too many steps, unfinished threads; a locked run
gives exactly threads × per_thread. Wrong-but-tempting: "the GIL makes my code thread-safe".
Follow-ups: is `list.append` atomic (a CPython detail; prefer `queue.Queue`); free-threading.
→ repo: `chapters/ch27_memory_gil_performance/solutions/ex10_gil_not_thread_safety.py`.

## 27.6 Free-threaded Python (3.14, PEP 779): supported but opt-in, compatibility caveats

| Version | Status |
|---|---|
| 3.13 | Experimental free-threaded build (PEP 703), separate binary `python3.13t` |
| 3.14 | Officially supported (PEP 779), still a separate opt-in build; the default keeps the GIL |

Caveats: single-threaded code is slower (roughly 5–10 % per the 3.14 release notes); importing a C
extension that does not declare support re-enables the GIL with a warning (override: `PYTHON_GIL=0`
or `-X gil=0`); code that relied on the GIL races more. Check: `sys._is_gil_enabled()` (3.13+).

## 27.7 CPU-bound vs I/O-bound: choosing processes, threads or asyncio

| Workload | Default build | Why |
|---|---|---|
| Tiny job | sequential | pool start-up and pickling cost more |
| CPU-bound pure Python | processes | one GIL per process |
| CPU-bound, GIL released (NumPy) or free-threaded | threads | shared memory |
| I/O, tens of waits, blocking libraries | threads | GIL released while blocked |
| I/O, thousands of sockets, async libraries | asyncio | one thread, cheap coroutines |

Ex06 encodes this table; APIs: → §28.4–§28.6.

## 27.8 Performance tactics: built-ins, local variables, avoiding hidden copies

Measure first (§27.9), then push loops into C (`sum`, `sorted`, set algebra; ex08), pick the right
container (→ §6.14), and avoid hidden copies: a list where a generator would do, bytes slices where a
`memoryview` shares, `xs = xs[1:]` in a loop (O(n²)). Locals beat globals, but 3.11's specialising
interpreter (PEP 659; about 1.25× faster than 3.10 on average per its release notes) narrowed such
micro-gains. `append` over-allocates, so resizes are rare (→ §22.3). Ex07 (excerpt):

```text
generator vs list          same result: True  lean peak lower: True
memoryview vs bytes slice  same result: True  lean peak lower: True
index vs slice loop        same result: True  lean peak lower: True
```

## 27.9 Profiling: `cProfile`, `timeit`, `tracemalloc`

`timeit` says how long (compare the minimum of repeats) and `cProfile` where time goes (→ §22.8);
`tracemalloc` gives peak memory and, from a snapshot taken while the data is alive, the allocating
line. Call counts and allocation sites are deterministic, so they make reliable tests (ex09, excerpt):

```text
fib(20) calls: {'fib': 21891}
fib_memo(20) calls: {'fib_memo': 21}
top allocation line: return [f"{v:>40}" for v in values]
```

## 27.10 Interview-ready answer: "Explain the GIL in 2026"

> "In default CPython, the GIL lets one thread run bytecode at a time; it protects interpreter state
> such as refcounts. Threads still help for I/O, since blocking calls and many C extensions release
> it; CPU-bound pure Python needs processes. It does not make my code thread-safe: `x += 1` is
> several bytecodes, so I use locks or queues. A free-threaded build is experimental in 3.13 and
> supported but opt-in in 3.14, with single-thread overhead and extensions that must declare
> support. I'd measure before choosing."

## Interviewer's view

- Rewarded: version-qualified claims; comparative measurement; the GIL is not a lock for *your* data.
- Penalised: "Python can't do parallelism"; `is` for values; one raw timing.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Identity, type, value | ★ | `is` vs `==`, caching, interning |
| 02 | When is an object freed? (worked above) | ★ | `weakref.finalize` lifetimes |
| 03 | Find hidden aliasing in a nested structure | ◆ | identity-aware DFS |
| 04 | `__slots__`: measure the saving (worked above) | ★ | comparative tracemalloc |
| 05 | See the GIL: CPU-bound vs I/O-bound threads | ★ | boolean benchmark |
| 06 | Processes, threads or asyncio? | ★ | workload classification |
| 07 | Hidden copies with tracemalloc | ★ | peak-memory comparison |
| 08 | Built-ins vs hand-written loops | ◆ | rewrite + race |
| 09 | Profile without timings | ◆ | `ncalls`, allocation sites |
| 10 | The GIL is not thread safety (worked above) | ★ | interleaving model + `Lock` |

Index: `chapters/ch27_memory_gil_performance/README.md`.

## Checkpoint quiz

1. Why can `a is b` be `True` for `256` but `False` for `257`?
2. Two objects reference each other; you `del` both names. When are they freed?
3. Does `__slots__` always reduce `sys.getsizeof(obj)`?
4. Four threads run a pure-Python loop (default build). Speed-up?
5. Is `count += 1` safe in threads because of the GIL?

<details><summary>Answers</summary>

1. CPython caches −5…256, an implementation detail. Compare ints with `==`.
2. At the next cycle collection, not at `del`.
3. No: `getsizeof` is shallow; measure with tracemalloc.
4. About none. Use processes, or a free-threaded build.
5. No: it is not atomic (load, add, store). Use a `Lock`.
</details>

## Summary card

- `is` only for `None`, booleans and sentinels; int caching and interning are CPython details.
- Refcount frees at zero; the generational `gc` handles cycles; immortal objects since 3.12.
- `__slots__`: no per-instance dict, less memory, fewer features; verify with tracemalloc.
- GIL: one thread runs bytecode; released on blocking I/O and by many C extensions; not a data lock.
- Free-threaded: experimental in 3.13 (PEP 703), supported opt-in in 3.14 (PEP 779), not default.
- CPU → processes; blocking I/O → threads; many sockets → asyncio; tiny → sequential.
