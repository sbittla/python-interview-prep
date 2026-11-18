"""
Exercise 03 — Gas Station (circular route)                         [Tier: ★ Core]
Chapter 20 · Pattern: greedy restart on negative prefix · Target time: 20 min

Problem
-------
Stations 0..n-1 sit on a circular road. At station i you may fill up `gas[i]` units; driving
from i to i+1 (mod n) burns `cost[i]`. The tank is unlimited and starts empty. Return the
smallest index from which you can drive one full lap, or -1 if no start works. (When a
solution exists it is unique for the classic problem's inputs, but we return the smallest.)

Examples
--------
>>> start_station([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])
3
>>> start_station([2, 3, 4], [3, 4, 3])
-1

Constraints
-----------
- 1 <= n <= 10^5, 0 <= gas[i], cost[i] <= 10^4.

Hints
-----
- If the total gas is less than the total cost, the answer is -1 immediately.
- If you start at s and first run dry after station i, what about starting at s+1?

Follow-ups
----------
- Return all valid starts (with zero-net segments there can be several): brute force or
  check prefix minima.
- Limited tank capacity: greedy breaks; becomes a simulation / DP problem.
"""
from __future__ import annotations


def brute_force(gas: list[int], cost: list[int]) -> int:
    raise NotImplementedError("TODO")


def start_station(gas: list[int], cost: list[int], trace: bool = False) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    gas, cost = [1, 2, 3, 4, 5], [3, 4, 5, 1, 2]
    print("trace:")
    ans = start_station(gas, cost, trace=True)
    print("answer:", ans, "| brute force:", brute_force(gas, cost))
    print()
    for g, c in (([2, 3, 4], [3, 4, 3]), ([5], [4]), ([4], [5]), ([3, 1, 1], [1, 2, 2]),
                 ([0, 0, 0], [0, 0, 0])):
        print(f"gas={g} cost={c} -> {start_station(g, c)} (brute {brute_force(g, c)})")


if __name__ == "__main__":
    main()
