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

Approach ladder
---------------
1. Brute force — index loops: compare statuses[i] with statuses[i-1] and track
   run starts by hand; recompute sum(deltas[:i]) for every prefix (O(n^2));
   nested `for i ... for j > i` loops for pairs.
2. Optimal    — `groupby(enumerate(statuses), key=status)` yields each run with
   its indices; `accumulate(deltas, initial=start)` gives all running balances
   in O(n); `combinations(sorted(prices), 2)` yields each unordered pair once;
   `product(d, repeat=L)` vs `permutations(d, L)` enumerate codes with and
   without reuse. Same big-O as careful loops, far fewer off-by-one chances.

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
    best = (-1, 0)
    for i in range(len(statuses)):
        if statuses[i] == "down" and (i == 0 or statuses[i - 1] != "down"):
            j = i
            while j < len(statuses) and statuses[j] == "down":
                j += 1
            if j - i > best[1]:
                best = (i, j - i)
    return best


def longest_outage(statuses: list[str]) -> tuple[int, int]:
    best = (-1, 0)
    for status, run in groupby(enumerate(statuses), key=itemgetter(1)):
        if status == "down":
            idx = [i for i, _ in run]
            if len(idx) > best[1]:
                best = (idx[0], len(idx))
    return best


def brute_force_balance(start: int, deltas: list[int]) -> int:
    return min(start + sum(deltas[:i]) for i in range(len(deltas) + 1))   # O(n^2)


def lowest_balance(start: int, deltas: list[int]) -> int:
    return min(accumulate(deltas, initial=start))


def affordable_pairs(prices: dict[str, int], budget: int) -> list[tuple[str, str]]:
    return [(a, b) for a, b in combinations(sorted(prices), 2)
            if prices[a] + prices[b] <= budget]


def count_codes(digits: str, length: int, repeat: bool) -> int:
    pool = sorted(set(digits))
    codes = product(pool, repeat=length) if repeat else permutations(pool, length)
    return sum(1 for _ in codes)


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
