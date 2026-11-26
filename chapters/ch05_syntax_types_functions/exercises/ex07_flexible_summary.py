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

Hints
-----
1. ``brute_force`` takes a list and an options dict; it may simply delegate to ``solve``.
2. Where in a signature must a parameter appear to become keyword-only?
3. Decide the order of checks: the None policy, then "no values", then label clashes.
4. How do you pass an existing list as separate positional arguments?

Follow-ups
----------
- How would you call it with an existing list?
- What does ``def f(a, /, b, *, c)`` mean?
"""
from __future__ import annotations

from typing import Any


def brute_force(values: list, options: dict | None = None) -> dict[str, Any]:
    raise NotImplementedError("TODO")


def solve(*values: float | None, precision: int = 2, skip_none: bool = True,
          **labels: Any) -> dict[str, Any]:
    raise NotImplementedError("TODO")


def main() -> None:
    print(solve(3, 1, 2))
    print(solve(1, None, 2, precision=1, unit="ms", source="probe-7"))
    data = [2.5, 3.25, 4.125]
    print("unpacked list:", solve(*data, precision=3))
    print("brute agrees :", brute_force(data, {"precision": 3}) == solve(*data, precision=3))
    for call in (lambda: solve(), lambda: solve(1, None, skip_none=False),
                 lambda: solve(1, count=5)):
        try:
            print("result:", call())
        except (TypeError, ValueError) as exc:
            print(f"{type(exc).__name__}: {exc}")
    print("four positionals are all data:", solve(1, 2, 3, 2)["count"])
    try:
        eval("solve(1, 2, precision=1, 3)")      # positional after keyword
    except SyntaxError as exc:
        print("SyntaxError:", exc.msg)


if __name__ == "__main__":
    main()
