"""
Exercise 07 — Build memoize from Scratch (and match lru_cache)          [Tier: ★ Core]
Chapter 25 · Pattern: decorator with state (cache dict) · Target time: 20 min

Problem
-------
Write `memoize(func)`, a decorator that caches results of a pure function.

- Key: the positional args plus the keyword args; keyword order must not
  matter (f(a=1, b=2) and f(b=2, a=1) share an entry).
- Falsy results (0, "", None) must be cached too.
- Unhashable arguments raise TypeError, as with functools.lru_cache.
- Expose `wrapper.cache` (the dict), `wrapper.hits`, `wrapper.misses` and
  `wrapper.cache_clear()`.
- `make_fib(decorate)` builds a recursive Fibonacci whose recursive calls go
  through the decorated name, so the cache is hit inside the recursion.

Examples
--------
>>> fib = make_fib(memoize); fib(30), fib.misses, fib.hits
(832040, 31, 28)

Constraints
-----------
- 0 <= n <= 300 for fib (recursion depth stays well under the default ~1000 limit).

Approach ladder
---------------
1. No cache — plain recursion makes 2*fib(n+1) - 1 calls: O(phi^n) time,
   phi ~ 1.618; O(n) stack.
2. Wrong-but-tempting — `if cache.get(key): return cache[key]` treats a cached 0
   as a miss, so every later fib(0) lookup recomputes (shown in main()).
3. Optimal — `if key in cache`: each n computed once, O(n) calls, O(n) memory,
   O(1) average per lookup. Same counts as @functools.lru_cache(maxsize=None).
   Why move up: exponential -> linear with three lines of decorator.

Hints
-----
- key = args, plus (a marker, *sorted(kwargs.items())) when there are kwargs.
- `hash(key)` raises TypeError for a list inside the tuple: let it propagate.
- Inside make_fib, `fib` refers to the enclosing name, which `@decorate` rebinds
  to the wrapper — that is why recursion hits the cache.

Follow-ups
----------
- Bound the cache (LRU eviction): OrderedDict + move_to_end, built in §29.2.
- Memoising a method: `self` becomes part of the key and keeps every instance
  alive; prefer functools.cached_property or a per-instance dict (§7.22).
- When is memoisation WRONG? Impure functions (time, random, I/O, mutation).
"""
from __future__ import annotations

from functools import lru_cache, wraps
from typing import Callable

_KW = object()        # separates positional from keyword parts of the key


def memoize(func: Callable) -> Callable:
    cache: dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = args if not kwargs else (*args, _KW, *sorted(kwargs.items()))
        if key in cache:                       # not cache.get(key): 0 is a result
            wrapper.hits += 1
            return cache[key]
        wrapper.misses += 1
        result = cache[key] = func(*args, **kwargs)
        return result

    def cache_clear() -> None:
        cache.clear()
        wrapper.hits = wrapper.misses = 0

    wrapper.cache, wrapper.cache_clear = cache, cache_clear
    wrapper.hits = wrapper.misses = 0
    return wrapper


def memoize_buggy(func: Callable) -> Callable:
    cache: dict = {}

    @wraps(func)
    def wrapper(*args):
        if cache.get(args):                    # BUG: falsy cached values look missing
            wrapper.hits += 1
            return cache[args]
        wrapper.misses += 1
        cache[args] = func(*args)
        return cache[args]
    wrapper.hits = wrapper.misses = 0
    return wrapper


def make_fib(decorate: Callable[[Callable], Callable]) -> Callable[[int], int]:
    @decorate
    def fib(n: int) -> int:
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    return fib


def count_plain_calls(n: int) -> int:
    calls = 0

    def fib(k: int) -> int:
        nonlocal calls
        calls += 1
        return k if k < 2 else fib(k - 1) + fib(k - 2)
    fib(n)
    return calls


def main() -> None:
    n = 25
    fib, buggy, std = make_fib(memoize), make_fib(memoize_buggy), make_fib(lru_cache(maxsize=None))
    print(f"fib({n}) = {fib(n)} | buggy = {buggy(n)} | lru_cache = {std(n)}")
    print("plain recursion calls:", count_plain_calls(n))
    print(f"memoize     misses={fib.misses} hits={fib.hits}")
    print(f"buggy       misses={buggy.misses} hits={buggy.hits}")
    info = std.cache_info()
    print(f"lru_cache   misses={info.misses} hits={info.hits}")
    for label, f in (("memoize", fib), ("buggy", buggy)):
        before = f.misses
        for _ in range(3):
            f(0)                                      # fib(0) == 0 is falsy
        print(f"{label:7} fib(0) three more times -> new misses = {f.misses - before}")

    @memoize
    def area(w: int, h: int = 1) -> int:
        return w * h

    print("kw order ignored:", area(w=2, h=3), area(h=3, w=2), "entries =", len(area.cache))
    try:
        area([2], 3)
    except TypeError as exc:
        print("unhashable arg:", exc)
    fib.cache_clear()
    print("after cache_clear:", len(fib.cache), fib.hits, fib.misses)


if __name__ == "__main__":
    main()
