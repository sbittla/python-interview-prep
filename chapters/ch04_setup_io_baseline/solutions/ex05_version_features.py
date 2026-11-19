"""
Exercise 05 — Version Baseline and Feature Checker           [Tier: ◆ Extended]
Chapter 04 · Pattern: feature detection, graceful fallback · Target time: 12 min

Problem
-------
An online judge may run an older Python than your laptop. Build a small
toolkit that answers "can I use this feature here?":

- ``supports(feature, version)`` -> bool, from the table ``FEATURES``
  (feature name -> minimum (major, minor)). Unknown feature -> KeyError.
- ``feature_report(version)`` -> dict feature -> bool for every feature.
- ``probe_runtime()`` -> the same dict, but measured by actually trying each
  feature in *this* interpreter (compile a snippet, look up a name).
- ``check_baseline(version, minimum=(3, 10))`` -> "ok" or a message listing
  the baseline features you must avoid.
- ``batched(iterable, n)`` -> tuples of up to n items: use
  ``itertools.batched`` when present (3.12+), else a pure-Python fallback.

Never print the running interpreter's version: output must be identical on
every machine, so ``main()`` prints booleans and a table for fixed versions.

Examples
--------
>>> supports("match statement (PEP 634)", (3, 9))
False
>>> supports("ExceptionGroup / except* (PEP 654)", (3, 11))
True
>>> check_baseline((3, 12))
'ok'
>>> list(batched("abcde", 2))
[('a', 'b'), ('c', 'd'), ('e',)]

Constraints
-----------
- Versions are (major, minor) tuples; compare tuples, never strings
  ("3.9" > "3.10" is True as strings).

Approach ladder
---------------
1. Brute force — parse ``sys.version`` (a free-form string) and compare text.
   Breaks on "3.10" vs "3.9" and on vendor suffixes.
2. Improved   — compare ``sys.version_info[:2]`` with tuples: correct, O(1),
   but trusts a hand-written table.
3. Optimal    — *feature detection*: try the feature itself (``compile`` the
   syntax, ``hasattr`` the name) and fall back when it is missing. Syntax
   probes must go through ``compile()`` on a string; writing new syntax
   directly in the file is a SyntaxError on old versions before any check runs.

Follow-ups
----------
- How do you learn a judge's version? Submit ``import sys; print(sys.version)``
  on a scratch problem, or read the judge's language page.
- Why does ``from __future__ import annotations`` let ``int | None`` appear in
  annotations on 3.7-3.9? Annotations become unevaluated strings.
- Wrong-but-tempting: ``if sys.version_info >= (3, 10): match ...`` in the
  same file — the parser rejects the whole file on 3.9 anyway.
"""
from __future__ import annotations

import builtins
import importlib.util
import itertools
from collections.abc import Iterable, Iterator
from typing import Any

FEATURES: dict[str, tuple[int, int]] = {
    "match statement (PEP 634)": (3, 10),
    "X | Y unions at runtime (PEP 604)": (3, 10),
    "zip(strict=True) (PEP 618)": (3, 10),
    "ExceptionGroup / except* (PEP 654)": (3, 11),
    "tomllib module (PEP 680)": (3, 11),
    "type-parameter syntax (PEP 695)": (3, 12),
    "itertools.batched": (3, 12),
    "template strings t'' (PEP 750)": (3, 14),
}
BASELINE = (3, 10)


def supports(feature: str, version: tuple[int, int]) -> bool:
    return tuple(version[:2]) >= FEATURES[feature]


def feature_report(version: tuple[int, int]) -> dict[str, bool]:
    return {name: supports(name, version) for name in FEATURES}


def _compiles(source: str) -> bool:
    try:
        compile(source, "<probe>", "exec")
    except SyntaxError:
        return False
    return True


def _zip_strict() -> bool:
    try:
        list(zip([1], [2], strict=True))
    except TypeError:
        return False
    return True


def _runtime_union() -> bool:
    try:
        int | str
    except TypeError:
        return False
    return True


def probe_runtime() -> dict[str, bool]:
    return {
        "match statement (PEP 634)": _compiles("match x:\n    case 1:\n        pass\n"),
        "X | Y unions at runtime (PEP 604)": _runtime_union(),
        "zip(strict=True) (PEP 618)": _zip_strict(),
        "ExceptionGroup / except* (PEP 654)": hasattr(builtins, "ExceptionGroup"),
        "tomllib module (PEP 680)": importlib.util.find_spec("tomllib") is not None,
        "type-parameter syntax (PEP 695)": _compiles("type Pair[T] = tuple[T, T]\n"),
        "itertools.batched": hasattr(itertools, "batched"),
        "template strings t'' (PEP 750)": _compiles("t'hi'\n"),
    }


def check_baseline(version: tuple[int, int], minimum: tuple[int, int] = BASELINE) -> str:
    version = tuple(version[:2])
    if version >= minimum:
        return "ok"
    missing = [name for name, need in FEATURES.items() if version < need <= minimum]
    return f"below {minimum[0]}.{minimum[1]}: avoid " + ", ".join(missing)


def _batched_fallback(iterable: Iterable[Any], n: int) -> Iterator[tuple[Any, ...]]:
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while chunk := tuple(itertools.islice(it, n)):
        yield chunk


def batched(iterable: Iterable[Any], n: int) -> Iterator[tuple[Any, ...]]:
    impl = getattr(itertools, "batched", None)    # 3.12+; graceful fallback below
    if impl is None:
        return _batched_fallback(iterable, n)
    return impl(iterable, n)


def main() -> None:
    import sys
    versions = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14)]
    print((f"{'feature':38}" + "".join(f"{v[0]}.{v[1]:<4}" for v in versions)).rstrip())
    for name in FEATURES:
        row = "".join(f"{'yes' if supports(name, v) else '-':<6}" for v in versions)
        print(f"{name:38}{row}".rstrip())
    print()
    print("3.9 baseline check:", check_baseline((3, 9)))
    print("3.12 baseline check:", check_baseline((3, 12)))
    here = sys.version_info[:2]
    print(f"this interpreter meets the 3.10 baseline: {check_baseline(here) == 'ok'}")
    print(f"runtime probes agree with the table: {probe_runtime() == feature_report(here)}")
    print("batched('abcde', 2):", list(batched("abcde", 2)))
    print("fallback agrees with batched:",
          list(_batched_fallback(range(7), 3)) == list(batched(range(7), 3)))


if __name__ == "__main__":
    main()
