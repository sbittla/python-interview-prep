"""
Exercise 04 — Flatten Arbitrarily Nested Lists                [Tier: ★ Core]
Chapter 23 · Pattern: recursion + yield from / explicit stack · Target time: 15 min

Problem
-------
Given a value that may contain lists and tuples nested to any depth, yield the non-container
items left to right. Strings and bytes are atoms (do not split them into characters).

Examples
--------
>>> list(flatten([1, [2, [3, (4, 5)]], "ab"]))
[1, 2, 3, 4, 5, 'ab']
>>> list(flatten([]))
[]

Constraints
-----------
- Nesting depth may exceed 1,000 (``flatten_iterative`` must not hit the recursion limit).
- Must be lazy: ``next(flatten(huge))`` returns the first item without walking everything.

Hints
-----
- ``yield from flatten(child)`` delegates to a recursive generator.
- For the iterative version, keep a stack of *iterators*, not of lists — that keeps it lazy.
- Test for containers with ``isinstance(x, (list, tuple))``.

Approach ladder
---------------
1. Recursive function that builds and concatenates lists — O(n * depth) copying, eager.
2. Recursive generator with ``yield from`` — O(n) items, lazy, but Python recursion depth ~1000.
3. Iterative generator with a stack of iterators — O(n), lazy, depth limited only by memory.

Follow-ups
----------
- How would you flatten only one level? (``itertools.chain.from_iterable``)
- How would you support dicts (flatten values) or arbitrary iterables, still treating str as atom?
"""
from __future__ import annotations

from typing import Any, Iterator

CONTAINERS = (list, tuple)


def flatten_eager(value: Any) -> list:
    """Rung 1: builds intermediate lists at every level."""
    if not isinstance(value, CONTAINERS):
        return [value]
    out: list = []
    for item in value:
        out = out + flatten_eager(item)  # copying on purpose: this is the slow rung
    return out


def flatten(value: Any) -> Iterator:
    """Rung 2: recursive generator."""
    if isinstance(value, CONTAINERS):
        for item in value:
            yield from flatten(item)
    else:
        yield value


def flatten_iterative(value: Any) -> Iterator:
    """Rung 3: explicit stack of iterators; no recursion."""
    if not isinstance(value, CONTAINERS):
        yield value
        return
    stack = [iter(value)]
    while stack:
        for item in stack[-1]:
            if isinstance(item, CONTAINERS):
                stack.append(iter(item))
                break
            yield item
        else:  # inner iterator exhausted without break
            stack.pop()


def deeply_nested(depth: int) -> list:  # provided
    """Helper for the demo: [[[...[42]...]]] with the given depth."""
    v: Any = [42]
    for _ in range(depth):
        v = [v]
    return v


def main() -> None:
    data = [1, [2, [3, (4, 5)]], "ab", [], [[[]]], 6]
    print("eager    :", flatten_eager(data))
    print("recursive:", list(flatten(data)))
    print("iterative:", list(flatten_iterative(data)))
    print("atom input:", list(flatten("hello")), list(flatten_iterative(7)))

    deep = deeply_nested(5000)
    try:
        list(flatten(deep))
    except RecursionError:
        print("recursive on depth 5000: RecursionError")
    print("iterative on depth 5000:", list(flatten_iterative(deep)))

    # Laziness: the first item is produced without touching the rest.
    huge = [[i, [i + 1]] for i in range(0, 2_000_000, 2)]
    print("first item of huge:", next(flatten_iterative(huge)))


if __name__ == "__main__":
    main()
