# Chapter 25. Decorators, Closures and functools

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 4–5 hours · **Prerequisites:** Chapters 5, 7

Home for *writing* decorators and context managers. Taught elsewhere: late binding (§7.5),
`lru_cache` (§6.11, §7.22), memoised DP (§19.2), LRU cache (§29.2), backoff jitter (§42.3).

**Learning objectives**

- Explain closures as captured variables and use `nonlocal` correctly.
- Write decorators, factories and decorator classes; make retry/timing/memoise testable.
- Use `partial`, `cache`, `singledispatch`, `total_ordering`; write context managers.

> **Recognise it**
>
> | You hear / see | Reach for |
> |---|---|
> | "add logging / timing / retries to many functions" | decorator |
> | "configurable: retry 3 times, cache 100 entries" | decorator factory `@d(...)` |
> | "remember state between calls, no class" | closure + `nonlocal` |
> | "cache an expensive pure function" | `@cache`, `@lru_cache`, memoise |
> | "always clean up / roll back, even on error" | context manager |

## 25.1 Functions as objects; higher-order functions

A function is an object (`__name__`, `__doc__`, `__code__`) that can sit in a dict, be passed in
and be returned. *Higher-order* functions take or return functions: `sorted(key=)`, `map`, every
decorator. A dispatch dict replaces an if/elif chain: O(1) average instead of O(k).

```python
import operator

TABLE = {"add": operator.add, "neg": operator.neg, "abs": abs}

def run(line):
    op, *args = line.split()
    fn = TABLE.get(op)
    return fn(*map(int, args)) if fn else f"unknown op {op!r}"

print([run(s) for s in ["add 2 3", "neg 4", "pow 2 3"]])
```

```text
[5, -4, "unknown op 'pow'"]
```

## 25.2 Closures and captured variables

An inner function that reads an enclosing variable keeps it alive in a *cell* after the outer
call returns. Assigning to the name makes it local unless you declare
`nonlocal`; mutating a captured list needs no declaration.

```python
def make_averager():
    total, count = 0.0, 0
    def add(x):
        nonlocal total, count            # without this: UnboundLocalError
        total += x
        count += 1
        return total / count
    return add

avg = make_averager()
print([avg(x) for x in (10, 20, 60)])
print(avg.__code__.co_freevars, [c.cell_contents for c in avg.__closure__])
```

```text
[10.0, 15.0, 30.0]
('count', 'total') [3, 90.0]
```

O(1) per call; the brute-force rung sums a stored list, O(n). Closures made in one call share
cells; loop lambdas see the final value (→ §7.5).

## 25.3 Writing decorators; `functools.wraps`

`@d` above `def f` means `f = d(f)`, run **once, at definition time**. The wrapper forwards
`*args, **kwargs` and returns the result. Stacks apply bottom-up: below, `greet` is
`bold(count_calls(greet))`.

```python
from functools import wraps

def count_calls(func):
    @wraps(func)                       # copy __name__, __doc__, ...; set __wrapped__
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

@bold
@count_calls
def greet(name):
    """Say hello."""
    return f"hi {name}"

print(greet("ann"), greet("bo"), greet.__name__, greet.__doc__)
print(greet.calls, greet.__wrapped__.calls)
```

```text
<b>hi ann</b> <b>hi bo</b> greet Say hello.
0 2
```

Without `wraps`, logs show `wrapper` and `inspect.signature` shows `(*args, **kwargs)`. `wraps`
copies `__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotations__` (and
`__type_params__` on 3.12+), sets `__wrapped__`, and *merges* `__dict__`. That merge is the second
line's trap: `bold` copied `calls = 0` once; the live counter is on `greet.__wrapped__`.

## 25.4 Decorators with arguments

`@repeat(3)` first *calls* `repeat(3)`, which returns the real decorator: three levels.

```python
from functools import wraps

def repeat(times):                       # 1. factory: the configuration
    if times < 0:
        raise ValueError("times must be >= 0")   # fails at decoration time
    def decorator(func):                 # 2. decorator: the function
        @wraps(func)
        def wrapper(*args, **kwargs):    # 3. wrapper: each call's arguments
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(3)
def roll():
    return 6

print(roll(), roll.__name__)
```

```text
[6, 6, 6] roll
```

Bare `@repeat` passes the function as `times` (`TypeError`). To allow `@tag` and `@tag(name="em")`,
use `def tag(func=None, *, name="span")`; return the decorator when `func is None`.

## 25.5 Practical decorators: timing, retry, logging, memoise

**Worked problem (ex05): retry with exponential backoff.** Retry up to `times` attempts on chosen
exceptions, waiting `base_delay * factor**(k-1)` before retry k (capped at `max_delay`); re-raise
the last error.

- *Rung 1:* a try/except loop at every call site: O(times) calls, but duplicated.
- *Rung 2:* a fixed `@retry` calling `time.sleep`: same cost, but tests wait real seconds.
- *Rung 3:* a factory with an exception filter and an **injected `sleep`**: O(times) calls, O(1)
  extra memory. Why move up: one tested policy; tests pass `waits.append` as `sleep`.

```python
import time
from functools import wraps

def retry(times=3, *, exceptions=(Exception,), base_delay=0.1, factor=2.0,
          max_delay=None, sleep=time.sleep):
    if times < 1:
        raise ValueError("times must be >= 1")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise                    # last failure, unchanged
                    delay = base_delay * factor ** (attempt - 1)
                    sleep(delay if max_delay is None else min(delay, max_delay))
        return wrapper
    return decorator

attempts, waits = [], []

@retry(4, exceptions=(ConnectionError,), sleep=waits.append)
def fetch():
    attempts.append(1)
    if len(attempts) < 3:
        raise ConnectionError("down")
    return "ok"

print(fetch(), len(attempts), waits)
```

```text
ok 3 [0.1, 0.2]
```

→ repo: `chapters/ch25_decorators_closures_functools/solutions/ex05_retry_backoff.py`

*Edge-case checklist:* `times=1`; first-try success (no sleep); no sleep after the final attempt;
non-retryable errors pass straight through; subclasses match.
*Wrong-but-tempting:* `except Exception: pass` (returns `None`); catching `BaseException`
(retries Ctrl-C); patching `time.sleep` in a test — the default was bound
when `retry` was defined, so the patch never reaches it.
*Follow-ups:* jitter and idempotency (→ §42.3); async with `asyncio.sleep` (Chapter 28).

**Timing and logging (ex06):** inject the clock and the sink. `timed(clock=time.perf_counter,
report=print)` reads the clock in `try/finally`, so failing calls are timed; `log_calls(log)` logs
the call and result (or exception) and re-raises. Use `perf_counter`, not `time.time` (wall clock,
can jump).

**Worked problem (ex07): memoise from scratch.**

- *Rung 1:* plain recursive Fibonacci makes 2·fib(n+1) − 1 calls, O(φⁿ).
- *Wrong-but-tempting:* `if cache.get(key):` treats a cached `0`, `""` or `None` as missing.
- *Rung 2:* `if key in cache`: O(n) calls, O(n) memory, O(1) average per lookup. Why move up:
  exponential → linear with a three-line decorator; the `in` test keeps falsy results.

```python
from functools import lru_cache, wraps

_KW = object()                           # separates positional from keyword parts

def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = args if not kwargs else (*args, _KW, *sorted(kwargs.items()))
        if key in cache:                 # not cache.get(key): 0 is a valid result
            wrapper.hits += 1
            return cache[key]
        wrapper.misses += 1
        cache[key] = result = func(*args, **kwargs)
        return result
    wrapper.hits = wrapper.misses = 0
    return wrapper

def make_fib(decorate):
    @decorate
    def fib(n):                          # recursion goes through the rebound name
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    return fib

ours, std = make_fib(memoize), make_fib(lru_cache(maxsize=None))
print(ours(25), ours.misses, ours.hits, std(25), std.cache_info())
```

```text
75025 26 23 75025 CacheInfo(hits=23, misses=26, maxsize=None, currsize=26)
```

→ repo: `chapters/ch25_decorators_closures_functools/solutions/ex07_memoize.py`

*Edge cases:* falsy results; unhashable arguments (`TypeError`, as in `lru_cache`); keyword order
(one entry here, `lru_cache` may store two); recursion depth (→ §7.21). *Follow-ups:* LRU eviction
(→ §29.2); methods keep every `self` alive (→ §7.22); never memoise impure functions.

## 25.6 Class decorators ◆

A decorator *applied to a class* receives the finished class and returns a class, usually the
same object modified in place (a plugin `@register`, ex08's `auto_repr`, plain `@dataclass`);
`@dataclass(slots=True)` (3.10+) is an exception: it returns a new class. A decorator *written as a
class* keeps state on an instance; it needs `update_wrapper(self, func)` and `__get__`, because a
plain instance is not a descriptor and on a method would never receive `self`:

```python
import types
from functools import update_wrapper

class CountCalls:
    def __init__(self, func):
        update_wrapper(self, func)
        self.func, self.calls = func, 0
    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)
    def __get__(self, obj, objtype=None):    # bind like a function does
        if obj is None:
            return self
        return types.MethodType(self, obj)

class Cart:
    @CountCalls
    def add(self, item):
        return f"added {item}"

cart = Cart()
print(cart.add("tea"), cart.add("milk"), Cart.add.calls)
```

```text
added tea added milk 2
```

Without `__get__`, `cart.add("tea")` raises `TypeError` (missing argument). A singleton decorator
returning a function breaks `isinstance` (→ §24.11).

→ repo: `chapters/ch25_decorators_closures_functools/solutions/ex08_class_decorators.py`

## 25.7 `functools`: `partial`, `lru_cache`, `cache`, `singledispatch`, `total_ordering`

| Tool | Notes |
|---|---|
| `partial(f, *args, **kw)` | pre-fills arguments; exposes `.func`, `.args`, `.keywords` |
| `lru_cache(maxsize=128)` | LRU memoise; bare `@lru_cache` since 3.8; `cache_info()` |
| `cache` (3.9+) | `lru_cache(maxsize=None)`: unbounded memory (→ §7.22) |
| `singledispatch` | dispatch on the first argument's type via the MRO; unions in `register` need 3.11+ |
| `total_ordering` | `__eq__` + one of `<`, `<=`, `>`, `>=` → the rest (slower) |

```python
from functools import partial, singledispatch, total_ordering

parse_hex = partial(int, base=16)

@singledispatch
def describe(obj):
    return f"object of type {type(obj).__name__}"

@describe.register
def _(obj: int):
    return f"int {obj}"

@describe.register
def _(obj: bool):                       # without this, True would dispatch to int
    return f"bool {obj}"

@describe.register
def _(obj: list):
    return "list [" + ", ".join(map(describe, obj)) + "]"

@total_ordering
class Version:
    def __init__(self, text):
        self.parts = tuple(map(int, text.split(".")))
    def __eq__(self, other):
        return self.parts == other.parts if isinstance(other, Version) else NotImplemented
    def __lt__(self, other):
        return self.parts < other.parts if isinstance(other, Version) else NotImplemented
    def __hash__(self):
        return hash(self.parts)

print(parse_hex("ff"), parse_hex.keywords)
print(describe([1, True, 2.5]))
print(Version("1.10") >= Version("1.9.9"), "1.10" >= "1.9.9")
```

```text
255 {'base': 16}
list [int 1, bool True, object of type float]
True False
```

Dispatch is cached per type. Return `NotImplemented`, not `False`, for foreign types: Python tries
the reflected operation, then `<` raises `TypeError` (`==` falls back to identity).

## 25.8 Context managers: `with`, `__enter__`/`__exit__`, `contextlib.contextmanager`

`with cm as x:` calls `x = cm.__enter__()`, runs the block, then always calls
`cm.__exit__(exc_type, exc, tb)` (all `None` on a clean exit). A truthy return **suppresses** the
exception (`contextlib.suppress` works this way). With `@contextmanager`, code before `yield` is
the enter step, code after it the exit step, and an exception in the block is raised *at the yield*.

**Worked problem (ex10): a dict transaction.** Edits stay on success; on any exception the dict
returns to its state at entry and the error propagates.

- *Rung 1:* snapshot / try / except / restore pasted around every edit: O(n), duplicated.
- *Rung 2:* a class: O(n) time and memory for the snapshot on enter; restore on error. Why: one
  tested rollback policy instead of pasted copies.
- *Rung 3:* the generator form: same cost. Why: less boilerplate, but `try` must wrap the `yield`.

```python
from contextlib import contextmanager

class Transaction:
    def __init__(self, store):
        self.store = store
    def __enter__(self):
        self.snapshot = dict(self.store)         # shallow copy, O(n)
        return self.store
    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:                 # the block raised: roll back in place
            self.store.clear()
            self.store.update(self.snapshot)
        return False                             # never swallow the error

@contextmanager
def transaction(store):
    snapshot = dict(store)
    try:
        yield store                              # the with-block runs here
    except BaseException:
        store.clear()
        store.update(snapshot)
        raise

def transfer(store, manager, amount):
    try:
        with manager(store) as s:
            s["alice"] -= amount
            s["bob"] += amount
            if s["alice"] < 0:
                raise ValueError("overdraft")
        return "committed"
    except ValueError as exc:
        return f"rolled back ({exc})"

for manager in (Transaction, transaction):
    store = {"alice": 50, "bob": 0}
    print(manager.__name__, transfer(store, manager, 30), transfer(store, manager, 30), store)
```

```text
Transaction committed rolled back (overdraft) {'alice': 20, 'bob': 30}
transaction committed rolled back (overdraft) {'alice': 20, 'bob': 30}
```

→ repo: `chapters/ch25_decorators_closures_functools/solutions/ex10_context_managers.py`

*Edge-case checklist:* added and deleted keys undone; `KeyboardInterrupt` rolls back
(`BaseException`); restore in place so other references see it; nested values are shared by the
shallow snapshot (→ §7.2).
*Wrong-but-tempting:* cleanup after a bare `yield` — skipped on error (ex10's `temp_attr_buggy`
leaks its temporary value; the fix is `try/finally`); `return True` from `__exit__` "to be safe",
which swallows every error.
*Follow-ups:* savepoints; `ExitStack`; `ContextDecorator`.

## Interviewer's view

- **Rewarded:** `wraps` unprompted; config validated at decoration time; injected `sleep`/`clock`;
  `try/finally` around `yield`.
- **Penalised:** wrappers that drop the return value or `**kwargs`; retrying every exception;
  real `time.sleep` in tests.

## Exercises

All in `chapters/ch25_decorators_closures_functools/`.

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Compose, apply_n, dispatch table | ★ | higher-order functions |
| ex02 | Running average, shared cells | ★ | `nonlocal`, `__closure__` |
| ex03 | count_calls and `wraps` | ★ | wrapper, stacking |
| ex04 | repeat, validate, optional parens | ★ | decorator factory |
| ex05 | Retry with backoff | ★ | injected sleep |
| ex06 | Timing and logging | ★ | injected clock |
| ex07 | Memoize from scratch | ★ | stateful decorator |
| ex08 | Class decorators, decorator classes | ◆ | registry, `__get__` |
| ex09 | functools toolkit | ★ | `partial`, `singledispatch`, `total_ordering` |
| ex10 | Transaction, temp_attr, Suppress | ★ | context managers |

## Checkpoint quiz

1. When does a decorator's body run, and when does its wrapper run?
2. Why does bare `@repeat` fail when `repeat` is a factory?
3. In §25.3, why does `greet.calls` stay 0?
4. A decorator class works on functions but not methods. What is missing?
5. Your `@contextmanager` cleanup never runs when the block raises. Why?

<details>
<summary>Answers</summary>

1. The body runs once, when the `def` executes; the wrapper runs on every call.
2. The function arrives as `times`, so `times < 0` raises `TypeError`.
3. `wraps` merged the inner wrapper's `__dict__` once, copying `calls = 0`; the live counter is
   `greet.__wrapped__.calls`.
4. `__get__`, returning `types.MethodType(self, obj)` so `self` is bound.
5. The exception is raised at the `yield`, skipping later code. Use `try/finally`.

</details>

## Summary card

- Closures capture variables (cells); `nonlocal` to rebind; loop late binding is §7.5.
- `@d` ≡ `f = d(f)` at definition time; stacks apply bottom-up; always `@wraps(func)`.
- Factory: `factory(config) → decorator(func) → wrapper(*args, **kwargs)`.
- Retry/timing/logging: inject `sleep`, `clock`, `log`; re-raise the last error.
- Memoise: key = args + sorted kwargs; test with `in`.
- Decorator classes need `update_wrapper` and `__get__`.
- `singledispatch` follows the MRO (register `bool`); `total_ordering` needs `__eq__` + one order.
- `__exit__` truthy = suppress; `@contextmanager` needs `try` around `yield`.
