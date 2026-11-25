"""
Exercise 02 — Closures: Running Average and Shared Cells                [Tier: ★ Core]
Chapter 25 · Pattern: closure state with nonlocal · Target time: 15 min

Problem
-------
1. `make_averager()` returns `add(x)`, which records x and returns the mean of
   every value seen so far. Use O(1) memory: keep a running total and count in
   the enclosing scope, not a list.
2. `make_account(balance)` returns three closures `(deposit, withdraw, balance_of)`
   that share ONE balance. `withdraw` raises ValueError("insufficient funds") if
   the amount exceeds the balance; both deposit and withdraw return the new balance.
3. `free_vars(f)` returns {name: current value} for every variable f captured,
   read from `f.__code__.co_freevars` and `f.__closure__`, sorted by name.

Examples
--------
>>> avg = make_averager(); avg(10), avg(20), avg(60)
(10.0, 15.0, 30.0)
>>> dep, wd, bal = make_account(100); dep(50), wd(30), bal()
(150, 120, 120)

Constraints
-----------
- Values are ints or floats; amounts are >= 0.

Hints
-----
- Assigning to a captured name (`total += x`) makes it local unless you declare
  `nonlocal total`; mutating a captured list (`lst.append`) does not need it.
- Closures capture VARIABLES (cells), not values: two closures made in the same
  call see each other's updates. Late binding in loops is §7.5.

Follow-ups
----------
- Rewrite make_averager as a class with `__call__`. When is each clearer?
- Why does `make_account(0)` called twice give independent accounts?
- What does `f.__closure__` return for a function that captures nothing?
"""
from __future__ import annotations

from typing import Callable


def make_averager_list() -> Callable[[float], float]:
    raise NotImplementedError("TODO")


def make_averager() -> Callable[[float], float]:
    raise NotImplementedError("TODO")


def make_account(balance: int):
    raise NotImplementedError("TODO")


def free_vars(f: Callable) -> dict[str, object]:
    raise NotImplementedError("TODO")


def main() -> None:
    avg, avg_list = make_averager(), make_averager_list()
    print("running mean:", [avg(x) for x in (10, 20, 60, 10)])
    print("list version agrees:", [avg_list(x) for x in (10, 20, 60, 10)])
    print("captured state:", free_vars(avg))

    deposit, withdraw, balance_of = make_account(100)
    print("deposit(50) ->", deposit(50), "| withdraw(30) ->", withdraw(30),
          "| balance_of() ->", balance_of())
    try:
        withdraw(500)
    except ValueError as exc:
        print("withdraw(500) ->", exc)
    print("withdraw sees the shared cell:", free_vars(withdraw))
    other = make_account(0)
    print("independent account:", other[2](), "| first still", balance_of())
    print("no captures -> __closure__ is", (lambda x: x).__closure__)


if __name__ == "__main__":
    main()
