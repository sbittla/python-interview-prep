"""
Exercise 06 — Uptime and Budget Reports with itertools           [Tier: ◆ Extended]
Chapter 06 · Pattern: groupby runs, accumulate, combinations, product · Target time: 20 min

Problem
-------
1. `longest_outage(statuses)` — `statuses` is a list like ["up", "down", ...]
   sampled once a minute. Return (start_index, length) of the longest run of
   consecutive "down" samples; the earliest one on ties; (-1, 0) if none.
2. `lowest_balance(start, deltas)` — an account starts at `start` and applies
   `deltas` in order. Return the lowest balance ever held (including `start`).
3. `affordable_pairs(prices, budget)` — `prices` maps item -> price. Return
   every unordered pair of DIFFERENT items whose total is <= budget, as sorted
   (a, b) name tuples with a < b, in sorted order.
4. `count_codes(digits, length, repeat)` — how many PIN codes of `length` can
   be formed from the distinct characters in `digits`, with or without reusing
   a digit. Build them with itertools, not a formula.

Examples
--------
>>> longest_outage(["up", "down", "down", "up", "down"])
(1, 2)
>>> lowest_balance(100, [-30, 50, -90, 10])
30
>>> affordable_pairs({"tea": 3, "cake": 5, "pie": 9}, 9)
[('cake', 'tea')]
>>> count_codes("123", 2, repeat=True), count_codes("123", 2, repeat=False)
(9, 6)

Constraints
-----------
- len(statuses), len(deltas) <= 10**6; len(prices) <= 200; codes enumerated
  only for small inputs.

Hints
-----
- groupby only groups ADJACENT equal keys — that is exactly a run.
- `accumulate(..., initial=x)` (3.8+) prepends x to the output.
- d**L codes with reuse; d!/(d-L)! without — use these to check your counts.

Follow-ups
----------
- Longest outage across a midnight wrap-around (circular list).
- Pairs within budget for n = 10**5: sort prices + two pointers (→ Ch 10).
"""
from __future__ import annotations

from itertools import accumulate, combinations, groupby, permutations, product
from operator import itemgetter


def brute_force_outage(statuses: list[str]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def longest_outage(statuses: list[str]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def brute_force_balance(start: int, deltas: list[int]) -> int:
    raise NotImplementedError("TODO")


def lowest_balance(start: int, deltas: list[int]) -> int:
    raise NotImplementedError("TODO")


def affordable_pairs(prices: dict[str, int], budget: int) -> list[tuple[str, str]]:
    raise NotImplementedError("TODO")


def count_codes(digits: str, length: int, repeat: bool) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    log = ["up", "down", "down", "up", "down", "down", "down", "up", "down"]
    print("longest_outage:", longest_outage(log), "| brute:", brute_force_outage(log))
    print("no outage:", longest_outage(["up", "up"]), "| empty:", longest_outage([]))
    deltas = [-30, 50, -90, 10]
    print("running balances:", list(accumulate(deltas, initial=100)))
    print("lowest_balance:", lowest_balance(100, deltas), "| brute:", brute_force_balance(100, deltas))
    menu = {"tea": 3, "cake": 5, "pie": 9, "bun": 2}
    print("pairs <= 8:", affordable_pairs(menu, 8))
    print("codes '1234' len 3: reuse =", count_codes("1234", 3, True),
          "| no reuse =", count_codes("1234", 3, False))
    print("runs of 'aaabccdd':", [(k, len(list(g))) for k, g in groupby("aaabccdd")])


if __name__ == "__main__":
    main()
