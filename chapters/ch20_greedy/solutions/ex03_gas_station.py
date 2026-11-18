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

Approach ladder
---------------
1. Brute force — simulate a lap from every start. O(n^2) time, O(1) space.
2. Optimal — one pass. Keep a running tank from the current candidate start; when it goes
   negative at station i, no station in [start, i] can be the answer (each would arrive at i
   with even less fuel), so restart at i+1. If total gas >= total cost the final candidate
   works. O(n) time, O(1) space.

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
    n = len(gas)
    for s in range(n):
        tank = 0
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                break
        else:
            return s
    return -1


def start_station(gas: list[int], cost: list[int], trace: bool = False) -> int:
    total = tank = start = 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        diff = g - c
        total += diff
        tank += diff
        if trace:
            print(f"  i={i} net={diff:+d} tank={tank:+d} start={start}")
        if tank < 0:            # cannot get past i from any start in [start, i]
            start, tank = i + 1, 0
            if trace:
                print(f"    tank negative -> restart at {start}")
    return start if total >= 0 else -1


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
