"""
Exercise 02 — Custom Iterators: Countdown and a Re-iterable Range   [Tier: ★ Core]
Chapter 23 · Pattern: iterator protocol · Target time: 20 min

Problem
-------
1. ``Countdown(n)`` is an *iterator*: iterating it yields n, n-1, ..., 1 and it is exhausted
   afterwards (a second loop yields nothing). ``iter(c) is c`` must be True.
2. ``StepRange(start, stop, step)`` is an *iterable*: every ``for`` loop over it starts afresh,
   like the built-in ``range``. It also supports ``len()``. ``step`` may be negative; ``step == 0``
   raises ``ValueError``.

Examples
--------
>>> list(Countdown(3))
[3, 2, 1]
>>> r = StepRange(0, 10, 3)
>>> list(r), list(r), len(r)
([0, 3, 6, 9], [0, 3, 6, 9], 4)

Constraints
-----------
- Do not use generators for ``Countdown`` (implement ``__next__`` by hand).
- ``StepRange`` must not store all values.

Hints
-----
- An iterator's ``__iter__`` returns ``self``; ``__next__`` raises ``StopIteration`` when done.
- An iterable's ``__iter__`` returns a *new* iterator each time. A generator method is the
  shortest way to write that.
- ``len`` of a range: ``max(0, ceil((stop - start) / step))`` — do it with integer arithmetic.

Approach ladder
---------------
1. Store a list and return ``iter(list)`` — works but O(n) memory.
2. Hand-written iterator class holding only the current position — O(1) memory.
3. Split iterable vs iterator so the object is re-iterable — the design ``range`` uses.

Follow-ups
----------
- What does ``for`` do under the hood? (``it = iter(x)``; loop ``next(it)`` until StopIteration)
- Why is a generator object single-use but a list is not?
"""
from __future__ import annotations


class Countdown:
    """An iterator: it *is* its own iterator and can be consumed only once."""

    def __init__(self, n: int) -> None:
        self.current = n

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class StepRange:
    """An iterable: each call to iter() produces a fresh generator."""

    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        if step == 0:
            raise ValueError("step must not be zero")
        self.start, self.stop, self.step = start, stop, step

    def __iter__(self):
        value = self.start
        if self.step > 0:
            while value < self.stop:
                yield value
                value += self.step
        else:
            while value > self.stop:
                yield value
                value += self.step

    def __len__(self) -> int:
        if self.step > 0:
            span, step = self.stop - self.start, self.step
        else:
            span, step = self.start - self.stop, -self.step
        return max(0, (span + step - 1) // step)

    def __repr__(self) -> str:
        return f"StepRange({self.start}, {self.stop}, {self.step})"


def manual_for(iterable) -> list:
    """What a for-loop does, spelled out with iter() and next()."""
    result = []
    it = iter(iterable)
    while True:
        try:
            item = next(it)
        except StopIteration:
            break
        result.append(item)
    return result


def main() -> None:
    c = Countdown(3)
    print("iter(c) is c:", iter(c) is c)
    print("first pass :", list(c))
    print("second pass:", list(c), "(exhausted)")

    r = StepRange(0, 10, 3)
    print(repr(r), "->", list(r), "again:", list(r), "len:", len(r))
    down = StepRange(10, 0, -4)
    print(repr(down), "->", list(down), "len:", len(down))
    empty = StepRange(5, 5)
    print(repr(empty), "->", list(empty), "len:", len(empty))
    print("len matches range:", all(
        len(StepRange(a, b, s)) == len(range(a, b, s))
        for a in range(-3, 4) for b in range(-3, 4) for s in (-3, -2, -1, 1, 2, 3)))
    print("manual_for:", manual_for(StepRange(1, 4)))
    try:
        StepRange(0, 5, 0)
    except ValueError as exc:
        print("ValueError:", exc)


if __name__ == "__main__":
    main()
