"""
Exercise 07 — A Flexible Summary Function                     [Tier: ★ Core]
Chapter 05 · Pattern: *args, keyword-only args, **kwargs · Target time: 15 min

Problem
-------
Write ``solve(*values, precision=2, skip_none=True, **labels)`` that summarises any number of
numeric positional arguments and returns a dict with keys ``count``, ``mean``, ``min``,
``max`` (mean rounded to ``precision`` places) plus every extra keyword argument copied in.

- ``precision`` and ``skip_none`` are keyword-only (they come after ``*values``).
- When ``skip_none`` is true, ``None`` values are ignored; otherwise a ``None`` raises
  ``TypeError("None in values")``.
- With no usable values raise ``ValueError("no values")``.
- A label must not overwrite a computed key: raise ``ValueError("label clashes: <key>")``.

Examples
--------
>>> solve(3, 1, 2)
{'count': 3, 'mean': 2.0, 'min': 1, 'max': 3}
>>> solve(1, None, 2, precision=1, unit="ms")
{'count': 2, 'mean': 1.5, 'min': 1, 'max': 2, 'unit': 'ms'}

Constraints
-----------
- up to 10**5 values; values are ints or floats (or None)

Approach ladder
---------------
1. Brute force — accept a single list argument and a dict of options. Works, but every caller
   has to build a list and remember option names inside a dict, which the signature cannot
   document or validate.
2. Optimal    — use the signature itself: ``*values`` collects positionals into a tuple,
   parameters after it are keyword-only, ``**labels`` collects the rest into a dict. One pass
   over the values: O(n) time, O(n) space for the filtered list.

Follow-ups
----------
- How would you call it with an existing list? ``solve(*my_list)`` unpacks it.
- What does ``def f(a, /, b, *, c)`` mean? ``a`` positional-only, ``b`` either, ``c`` keyword-only.
"""
from __future__ import annotations

from typing import Any


def brute_force(values: list, options: dict | None = None) -> dict[str, Any]:
    options = options or {}
    return solve(*values, **options)


def solve(*values: float | None, precision: int = 2, skip_none: bool = True,
          **labels: Any) -> dict[str, Any]:
    if not skip_none and any(v is None for v in values):
        raise TypeError("None in values")
    nums = [v for v in values if v is not None]
    if not nums:
        raise ValueError("no values")
    result: dict[str, Any] = {
        "count": len(nums),
        "mean": round(sum(nums) / len(nums), precision),
        "min": min(nums),
        "max": max(nums),
    }
    for key, value in labels.items():
        if key in result:
            raise ValueError(f"label clashes: {key}")
        result[key] = value
    return result


def main() -> None:
    print(solve(3, 1, 2))
    print(solve(1, None, 2, precision=1, unit="ms", source="probe-7"))
    data = [2.5, 3.25, 4.125]
    print("unpacked list:", solve(*data, precision=3))
    print("brute agrees :", brute_force(data, {"precision": 3}) == solve(*data, precision=3))
    for call in (lambda: solve(), lambda: solve(1, None, skip_none=False),
                 lambda: solve(1, count=5), lambda: solve(1, 2, 3)):
        try:
            print("result:", call())
        except (TypeError, ValueError) as exc:
            print(f"{type(exc).__name__}: {exc}")
    try:
        solve(1, 2, 3, 2)   # fine: four positional values
        eval("solve(1, 2, precision=1, 3)")
    except SyntaxError as exc:
        print("SyntaxError:", exc.msg)


if __name__ == "__main__":
    main()
