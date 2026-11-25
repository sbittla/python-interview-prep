"""
Exercise 01 — Climbing Stairs Variants and Decode Ways              [Tier: ★ Core]
Chapter 19 · Pattern: 1D DP, counting ways · Target time: 25 min

Problem
-------
1. `count_ways(n, steps)` — a staircase has n steps and each move climbs one of the
   sizes in `steps` (default (1, 2)). Count the distinct move sequences that land
   exactly on step n. Order matters: 1+2 and 2+1 are different sequences.
2. `min_cost_climb(cost)` — landing on step i costs cost[i]. You may start on step 0
   or step 1 and each move climbs 1 or 2 steps. Return the cheapest total cost to get
   past the last step.
3. `decode_ways(s)` — letters A..Z were encoded as "1".."26" and concatenated
   ("AB" -> "12"). Count the ways to decode the digit string s. A code never has a
   leading zero: "06" is not F, and a lone "0" decodes to nothing. The empty string
   has exactly one decoding (the empty message).

Examples
--------
>>> count_ways(5), count_ways(4, (1, 3, 5))
(8, 3)
>>> min_cost_climb([10, 15, 20])
15
>>> decode_ways("226"), decode_ways("06"), decode_ways("11106")
(3, 0, 2)

Constraints
-----------
- 0 <= n <= 10^4; steps are distinct positive integers.
- 0 <= len(cost) <= 10^4, 0 <= cost[i] <= 999.
- 0 <= len(s) <= 10^4, s contains digits only. Answers are exact Python ints.

Hints
-----
- The memoised rung recurses ~n deep and hits the ~1000 limit (section 7.21) well inside
  the constraints; this is why the final answer is a table.
- Write the recursion first; the table is the recursion with the calls replaced by
  array reads.
- Decode ways is climbing stairs with steps 1 and 2 where a step is only legal if the
  digits it consumes form a valid code.
- "0" can only be the second digit of "10" or "20".

Follow-ups
----------
- Steps that may not repeat consecutively: add "last step" to the state.
- Decode ways with "*" wildcards (any of 1-9): same DP, multiply by the choices; take
  the answer mod 10^9 + 7.
"""
from __future__ import annotations

from collections import deque
from functools import cache


# ---------------------------------------------------------------- climbing stairs
def count_ways_brute(n: int, steps: tuple[int, ...] = (1, 2)) -> int:
    raise NotImplementedError("TODO")


def count_ways_memo(n: int, steps: tuple[int, ...] = (1, 2)) -> int:
    raise NotImplementedError("TODO")


def count_ways_table(n: int, steps: tuple[int, ...] = (1, 2)) -> int:
    raise NotImplementedError("TODO")


def count_ways(n: int, steps: tuple[int, ...] = (1, 2)) -> int:
    raise NotImplementedError("TODO")


def min_cost_climb_brute(cost: list[int]) -> int:
    raise NotImplementedError("TODO")


def min_cost_climb(cost: list[int]) -> int:
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------- decode ways
def _two_digit_ok(s: str, i: int) -> bool:
    return i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26


def decode_ways_brute(s: str) -> int:
    raise NotImplementedError("TODO")


def decode_ways_memo(s: str) -> int:
    raise NotImplementedError("TODO")


def decode_ways_table(s: str) -> int:
    raise NotImplementedError("TODO")


def decode_ways(s: str) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    print("count_ways (steps 1,2) n=0..10:", [count_ways(n) for n in range(11)])
    print("count_ways(4, (1, 3, 5)):", count_ways(4, (1, 3, 5)))
    print("count_ways(100):", count_ways(100))
    print("rungs agree n=20, steps (1,2,3):",
          count_ways_brute(20, (1, 2, 3)) == count_ways_memo(20, (1, 2, 3))
          == count_ways_table(20, (1, 2, 3)) == count_ways(20, (1, 2, 3)))
    for cost in ([10, 15, 20], [1, 100, 1, 1, 1, 100, 1, 1, 100, 1], [5], []):
        print(f"min_cost_climb({cost}) = {min_cost_climb(cost)}")
    for s in ["12", "226", "06", "10", "11106", "2101", "100", "", "1111111111"]:
        rungs = (decode_ways_brute(s), decode_ways_memo(s), decode_ways_table(s), decode_ways(s))
        print(f"decode_ways({s!r:<12}) = {rungs[-1]:<3} all rungs agree: {len(set(rungs)) == 1}")


if __name__ == "__main__":
    main()
