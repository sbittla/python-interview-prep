"""
Exercise 01 — Identity, Type, Value                         [Tier: ★ Core]
Chapter 27 · Pattern: `is` vs `==`, caching and interning · Target time: 15 min

Problem
-------
Every Python object has an identity (fixed for its lifetime; `id()` in
CPython is its address), a type (`type(obj)`) and a value (what `==` compares).

1. `describe(x, y)` returns a dict with three booleans:
   {"same_object": x is y, "equal": x == y, "same_type": type(x) is type(y)}.
2. `runtime_ints_identical(n)` builds n twice at run time (`int(str(n))`) and
   reports whether both calls return the very same object. In CPython this is
   True exactly for the cached small ints -5..256 — an implementation
   detail, not a language guarantee.
3. `cached_int_range(lo, hi)` returns the (first, last) n in [lo, hi] for
   which `runtime_ints_identical(n)` is True, or None when none are.
4. `interned_equal(parts)` joins the string parts at run time and returns
   (runtime_is_literal, interned_is_literal): whether the joined string is
   the same object as the identical literal "".join(parts) computed via
   `sys.intern`, before and after interning.

Examples
--------
>>> describe([1, 2], [1, 2])
{'same_object': False, 'equal': True, 'same_type': True}
>>> describe(1, 1.0)
{'same_object': False, 'equal': True, 'same_type': False}
>>> cached_int_range(-10, 300)          # CPython 3.10-3.13
(-5, 256)

Constraints
-----------
- Never print id() values: they change from run to run.

Approach ladder
---------------
1. Brute force — compare with `==` everywhere. Correct for values, but cannot
   tell aliasing (two names, one list) from equal copies.
2. Improved   — use `is` for identity questions (None, sentinels, aliasing).
3. Optimal    — know which `is` results are *guaranteed* (None, True, False,
   your own sentinels) and which are CPython accidents (small ints, interned
   strings). Probe the accident at run time instead of trusting a literal,
   because the compiler folds equal constants in one code object into one
   object, which makes `257 is 257` misleadingly True. O(1) per probe;
   `cached_int_range` is O(hi - lo).

Hints
-----
- Build values at run time (`int("257")`) to defeat constant folding.
- `sys.intern(s)` returns the canonical copy of an equal string.

Follow-ups
----------
- Why is `x == None` wrong-but-tempting? (A class can override `__eq__`;
  `is None` cannot be fooled and is faster.)
- `1 == 1.0 == True` yet the types differ: what does `{1: "a", True: "b"}`
  contain? (One key: equal values with equal hashes collide.)
"""
from __future__ import annotations

import sys


def describe(x: object, y: object) -> dict[str, bool]:
    return {"same_object": x is y, "equal": x == y, "same_type": type(x) is type(y)}


def runtime_ints_identical(n: int) -> bool:
    return int(str(n)) is int(str(n))


def cached_int_range(lo: int, hi: int) -> tuple[int, int] | None:
    hits = [n for n in range(lo, hi + 1) if runtime_ints_identical(n)]
    return (hits[0], hits[-1]) if hits else None


def interned_equal(parts: list[str]) -> tuple[bool, bool]:
    literal = sys.intern("".join(parts))          # the canonical (interned) copy
    runtime = "".join(parts)                      # a fresh object with the same value
    return runtime is literal, sys.intern(runtime) is literal


def main() -> None:
    a = [1, 2]
    b = a                                         # alias: two names, one object
    pairs = [("alias", a, b), ("copy", a, list(a)), ("int vs float", 1, 1.0),
             ("None vs None", None, None), ("True vs 1", True, 1)]
    for label, x, y in pairs:
        print(f"{label:13} {describe(x, y)}")
    print("runtime 256 identical:", runtime_ints_identical(256))
    print("runtime 257 identical:", runtime_ints_identical(257))
    print("cached range in [-10, 300]:", cached_int_range(-10, 300))
    print("cached range in [1000, 1010]:", cached_int_range(1000, 1010))
    print("joined 'hello_world' is interned copy (before, after sys.intern):",
          interned_equal(["hello", "_", "world"]))
    print("dict with keys 1 and True:", {1: "a", True: "b"})


if __name__ == "__main__":
    main()
