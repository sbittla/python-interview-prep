"""
Exercise 03 — Bayes' Rule: Screening Tests and Updates           [Tier: ★ Core]
Chapter 35 · Pattern: Bayes' rule, base rates · Target time: 15 min

Problem
-------
A condition has prevalence ``prior``. A test has sensitivity P(+ | sick) and specificity
P(- | healthy).

1. ``posterior(prior, sensitivity, specificity, positive=True)``: P(sick | result), exact
   when given ``Fraction`` inputs. Raise ``ValueError`` if P(result) == 0.
2. ``sequential(prior, sensitivity, specificity, results)``: apply ``posterior`` once per
   result, assuming results are independent given the true state.
3. ``count_posterior(...)``: brute force by counting an explicit population of N people.
4. ``simulate_posterior(..., trials, seed)``: Monte Carlo estimate with numpy.

Examples
--------
>>> posterior(Fraction(1, 100), Fraction(9, 10), Fraction(91, 100))
Fraction(10, 109)

Constraints
-----------
- 0 <= prior, sensitivity, specificity <= 1.

Hints
-----
- P(result) = P(result | sick) P(sick) + P(result | healthy) P(healthy).
- For a negative result use 1 - sensitivity and specificity in place of the positive rates.
- Sequential tests: feed each posterior in as the next prior.
- Counting: build the four cells of a 2x2 table for N people.

Wrong-but-tempting
------------------
- Answering "90 %" (the sensitivity): confuses P(+ | sick) with P(sick | +).
- Forgetting the healthy people's false positives in the denominator.
- Treating repeated tests as independent when the same error source repeats.

Follow-ups
----------
- Odds form: posterior odds = prior odds * LR, with LR+ = sens / (1 - spec).
- Why does a 90 %-sensitive, 91 %-specific test give only 10/109 ~ 9 % at 1 % prevalence?
  (Per 10,000 tested: 891 false positives vs 90 true positives.)
- Independence of repeated tests is an assumption; the same lab error repeats.
- Edge cases: prior 0 or 1 (no update possible), P(result) = 0, negative results.
"""
from __future__ import annotations

from fractions import Fraction

import numpy as np


def posterior(prior, sensitivity, specificity, positive: bool = True):
    raise NotImplementedError("TODO")


def sequential(prior, sensitivity, specificity, results: list[bool]):
    raise NotImplementedError("TODO")


def count_posterior(n: int, prior, sensitivity, specificity, positive: bool = True) -> Fraction:
    raise NotImplementedError("TODO")


def simulate_posterior(prior: float, sensitivity: float, specificity: float,
                       trials: int = 1_000_000, seed: int = 0) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    prior, sens, spec = Fraction(1, 100), Fraction(9, 10), Fraction(91, 100)
    p = posterior(prior, sens, spec)
    print("P(sick | +)        =", p, "=", round(float(p), 4))
    print("count in 10,000    =", count_posterior(10_000, prior, sens, spec))
    print("simulate (seed 35) =", round(simulate_posterior(0.01, 0.9, 0.91, seed=35), 3))
    print("P(sick | -)        =", posterior(prior, sens, spec, positive=False),
          "  counted:", count_posterior(10_000, prior, sens, spec, positive=False))
    two = sequential(prior, sens, spec, [True, True])
    lr = sens / (1 - spec)
    odds = prior / (1 - prior) * lr ** 2
    print("two positives      =", two, "=", round(float(two), 4), "  odds*LR^2 agrees:", odds / (1 + odds) == two)
    print("+ then -           =", round(float(sequential(prior, sens, spec, [True, False])), 4))
    print("prior 0 stays 0    =", posterior(Fraction(0), sens, spec))
    try:
        posterior(Fraction(0), Fraction(0), Fraction(1))
    except ValueError as e:
        print("impossible result  -> ValueError:", e)


if __name__ == "__main__":
    main()
