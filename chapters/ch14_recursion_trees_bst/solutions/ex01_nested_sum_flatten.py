"""
Exercise 01 — Depth-Weighted Sum and Flatten of Nested Lists      [Tier: ★ Core]
Chapter 14 · Pattern: recursion -> explicit stack · Target time: 15 min

Problem
-------
A nested list holds ints and other nested lists, to any depth.
(a) depth_sum: return the sum of every int multiplied by its depth; ints in the
    outer list have depth 1.
(b) flatten: return all ints in left-to-right order.
Write each one recursively and then iteratively with an explicit stack, so the
iterative version survives nesting far deeper than Python's recursion limit.

Examples
--------
>>> depth_sum_recursive([1, [4, [6]]])        # 1*1 + 4*2 + 6*3
27
>>> flatten_iterative([1, [2, [3, 4]], [], 5])
[1, 2, 3, 4, 5]

Constraints
-----------
- Up to 10**5 ints in total; nesting depth up to 10**5 (iterative versions).

Approach ladder
---------------
1. Recursive — the base case is "an int"; the recursive case is "a list: recurse
   into each item with depth + 1". O(N) time, O(D) call stack (D = depth).
2. Explicit stack — push (sublist, depth) pairs yourself. Same O(N) time, O(D)
   heap memory, and no RecursionError at depth 5,000 (default limit ~1,000, →
   §7.21). For flatten, keep a stack of *iterators*: each iterator is a paused
   "frame" that remembers where it stopped, which preserves left-to-right order.

Hints
-----
- Recursive flatten: `out.extend(flatten(item))` for lists, `out.append(item)` else.
- Iterative sum: order doesn't matter, so a plain stack of (list, depth) is enough.
- Iterative flatten: when you meet a sublist, push iter(sublist) and `break` out
  of the current for-loop; the old iterator resumes later at the next item.

Edge cases
----------
- [] -> 0 / []; [[[]]] -> 0 / []; negative ints; a single int at depth 10,000.

Wrong-but-tempting
------------------
- Pushing sublists on a stack and popping them for flatten: reverses the order.
- `sys.setrecursionlimit(10**6)` as the "fix": it can crash the interpreter with a
  C-stack overflow instead of raising RecursionError (→ §7.21).

Follow-ups
----------
- Inverse depth sum (leaves weighted 1, the outermost ints weighted max depth):
  BFS by level, keep a running level sum and add it once per level.
- Make flatten lazy: a generator with the same iterator stack (or `yield from`).
"""
from __future__ import annotations

Nested = list  # list[int | Nested]


def depth_sum_recursive(nested: Nested, depth: int = 1) -> int:
    total = 0
    for item in nested:
        if isinstance(item, list):
            total += depth_sum_recursive(item, depth + 1)   # recursive case
        else:
            total += item * depth                            # base case: an int
    return total


def depth_sum_iterative(nested: Nested) -> int:
    total = 0
    stack = [(nested, 1)]                 # what each call frame would have held
    while stack:
        items, depth = stack.pop()
        for item in items:
            if isinstance(item, list):
                stack.append((item, depth + 1))
            else:
                total += item * depth
    return total


def flatten_recursive(nested: Nested) -> list[int]:
    out: list[int] = []
    for item in nested:
        if isinstance(item, list):
            out.extend(flatten_recursive(item))
        else:
            out.append(item)
    return out


def flatten_iterative(nested: Nested) -> list[int]:
    out: list[int] = []
    stack = [iter(nested)]                # each iterator = one paused frame
    while stack:
        for item in stack[-1]:
            if isinstance(item, list):
                stack.append(iter(item))  # "call": descend, resume parent later
                break
            out.append(item)
        else:                             # iterator exhausted: "return"
            stack.pop()
    return out


def trace_depth_sum(nested: Nested, depth: int = 1) -> int:
    """depth_sum_recursive, printing each call and return indented by depth."""
    pad = "  " * (depth - 1)
    print(f"{pad}call depth={depth} {nested}")
    total = 0
    for item in nested:
        total += trace_depth_sum(item, depth + 1) if isinstance(item, list) else item * depth
    print(f"{pad}return {total}")
    return total


def deep(depth: int) -> Nested:
    """[1, [1, [1, ...]]] nested `depth` levels, built without recursion."""
    root: Nested = [1]
    cur = root
    for _ in range(depth - 1):
        nxt: Nested = [1]
        cur.append(nxt)
        cur = nxt
    return root


def main() -> None:
    trace_depth_sum([1, [4, [6]]])
    cases = [[1, [4, [6]]], [[1, 1], 2, [1, 1]], [1, [2, [3, 4]], [], 5], [], [[[]]], [-3, [-2]]]
    for c in cases:
        print(f"{c!s:<24} sum rec={depth_sum_recursive(c):<3} it={depth_sum_iterative(c):<3}"
              f" flat={flatten_iterative(c)}")
    big = deep(5000)
    try:
        depth_sum_recursive(big)
    except RecursionError:
        print("recursive, depth 5000 -> RecursionError")
    print("iterative, depth 5000 ->", depth_sum_iterative(big), "| flatten length",
          len(flatten_iterative(big)))


if __name__ == "__main__":
    main()
