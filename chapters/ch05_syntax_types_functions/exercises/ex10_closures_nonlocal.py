"""
Exercise 10 — Counters and Running Averages With Closures     [Tier: ★ Core]
Chapter 05 · Pattern: LEGB scope, nonlocal · Target time: 15 min

Problem
-------
Implement two closure factories:

- ``solve(start=0, step=1)`` returns a pair of functions ``(increment, current)``.
  ``increment()`` advances the counter by ``step`` and returns the new value; ``current()``
  returns the value without changing it. Counters created by separate calls are independent.
- ``make_averager()`` returns a function ``add(x)`` that records x and returns the running
  mean of every value seen so far, storing only a total and a count (O(1) memory).

Examples
--------
>>> inc, cur = solve(10, 5)
>>> inc(), inc(), cur()
(15, 20, 20)
>>> avg = make_averager(); avg(10), avg(20), avg(60)
(10.0, 15.0, 30.0)

Constraints
-----------
- no global variables and no classes: state must live in the enclosing function's scope

Hints
-----
1. ``brute_force_increment`` uses a module-level variable. Why do two counters built that way
   interfere?
2. Put the state in a local variable of the factory and define the inner functions there.
3. Reading an enclosing variable works out of the box; *assigning* to it does not. Run it and
   read the error, then find the keyword that changes the rule.
4. The averager needs only two numbers of state, not a list of every value.

Follow-ups
----------
- Mutating a container (``state["n"] += 1``) works without ``nonlocal``. Why?
- When would you switch to a class?
"""
from __future__ import annotations

from collections.abc import Callable

_global_count = 0


def brute_force_increment() -> int:
    raise NotImplementedError("TODO")


def solve(start: int = 0, step: int = 1) -> tuple[Callable[[], int], Callable[[], int]]:
    raise NotImplementedError("TODO")


def make_averager() -> Callable[[float], float]:
    raise NotImplementedError("TODO")


def main() -> None:
    inc_a, cur_a = solve()
    inc_b, cur_b = solve(100, 10)
    print("a:", inc_a(), inc_a(), inc_a(), "| b:", inc_b(), inc_b(), "| a now", cur_a(), "b now", cur_b())
    avg = make_averager()
    print("running means:", [avg(x) for x in (10, 20, 60, 10)])
    print("closure cells:", [c.cell_contents for c in inc_b.__closure__])

    def broken():
        count = 0

        def bump():
            count += 1          # assignment makes `count` local to bump
            return count
        return bump

    try:
        broken()()
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
    print("global version:", brute_force_increment(), brute_force_increment())


if __name__ == "__main__":
    main()
