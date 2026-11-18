"""
Exercise 01 — FizzBuzz With Pluggable Rules                  [Tier: ★ Core]
Chapter 05 · Pattern: loops + conditionals · Target time: 10 min

Problem
-------
Return a list of strings for the integers 1..n (inclusive). For each number, concatenate the
word of every rule ``(divisor, word)`` whose divisor divides the number, in rule order. If no
rule matches, the entry is the number itself as a string. The default rules are
``((3, "Fizz"), (5, "Buzz"))``, which gives classic FizzBuzz.

Examples
--------
>>> solve(5)
['1', '2', 'Fizz', '4', 'Buzz']
>>> solve(15)[-1]
'FizzBuzz'
>>> solve(7, rules=((7, "Bazz"),))[-1]
'Bazz'

Constraints
-----------
- 0 <= n <= 10**5 (n == 0 returns an empty list)
- every divisor is a positive int

Approach ladder
---------------
1. Brute force — an if/elif chain that tests 15 first, then 3, then 5. O(n) time, but the
   number of branches grows as 2**rules, and forgetting to test 15 first is the classic bug.
2. Optimal    — build each entry by concatenating matching words, falling back to str(i) with
   ``word or str(i)``. Still O(n * r) time (r = number of rules), O(n) output space, and adding
   a rule is a data change rather than a code change. That extensibility is why we move up.

Follow-ups
----------
- Make it a generator so huge n does not build a list (yield instead of append).
- Rules that depend on something other than divisibility? Pass predicates instead of divisors.
"""
from __future__ import annotations

DEFAULT_RULES: tuple[tuple[int, str], ...] = ((3, "Fizz"), (5, "Buzz"))  # immutable default


def brute_force(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:          # must come first, or 15 prints "Fizz"
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out


def solve(n: int, rules: tuple[tuple[int, str], ...] = DEFAULT_RULES) -> list[str]:
    out = []
    for i in range(1, n + 1):
        word = "".join(text for divisor, text in rules if i % divisor == 0)
        out.append(word or str(i))   # "" is falsy, so fall back to the number
    return out


def main() -> None:
    print("classic 1..15:", " ".join(solve(15)))
    print("brute == solve for n=100:", brute_force(100) == solve(100))
    print("custom rules :", solve(21, rules=((3, "Fizz"), (5, "Buzz"), (7, "Bazz")))[-1])
    print("n = 0        :", solve(0))


if __name__ == "__main__":
    main()
