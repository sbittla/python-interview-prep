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

Hints
-----
1. Start with the classic if/elif chain for 3 and 5 as ``brute_force``. Which test must come
   first, and why does that ordering problem get worse with every extra rule?
2. For ``solve``, build each entry from the rules instead of branching on them. What is the
   entry when no rule matched, and how can an empty string help you detect that?
3. State the time cost in terms of n and the number of rules.

Follow-ups
----------
- Make it a generator so huge n does not build a list (yield instead of append).
- Rules that depend on something other than divisibility? Pass predicates instead of divisors.
"""
from __future__ import annotations

DEFAULT_RULES: tuple[tuple[int, str], ...] = ((3, "Fizz"), (5, "Buzz"))  # immutable default


def brute_force(n: int) -> list[str]:
    raise NotImplementedError("TODO")


def solve(n: int, rules: tuple[tuple[int, str], ...] = DEFAULT_RULES) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    print("classic 1..15:", " ".join(solve(15)))
    print("brute == solve for n=100:", brute_force(100) == solve(100))
    print("custom rules :", solve(21, rules=((3, "Fizz"), (5, "Buzz"), (7, "Bazz")))[-1])
    print("n = 0        :", solve(0))


if __name__ == "__main__":
    main()
