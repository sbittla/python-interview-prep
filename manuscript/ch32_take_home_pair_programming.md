# Chapter 32. Take-Home and Pair-Programming Workflow

◆ Extended · Tracks S M L · Study time ≈ 3 h · Prerequisites: Chapter 2, Chapter 31

**Learning objectives**

- Scope a take-home to its time box and record the scope and assumptions in the README.
- Lay out a small typed, tested project that a reviewer can run in one command.
- Work out a stranger's code aloud, and refactor it behind characterization tests.
- Absorb spec changes (v1 → v2 → v3) without breaking earlier behaviour.

> **Recognise it.** "Take about 3 hours"; "we'll extend it in the follow-up"; "here's our
> repo, add a feature"; "the requirements will change as we go".

## 32.1 Take-home: scoping, time-boxing, README, assumptions

Plan first: list tasks, estimate each, tag it must/should/could, and reserve about a quarter
of the time for tests, README and a clean run. If the musts overflow, ask what matters most:

```text
budget 170: in ['--strict flag'], deferred ['JSON output', 'month filter', 'multi-currency']
budget 120: must tasks need 115 min, build budget is 90 min
```

Above, a 15-minute "should" does not fit the 13 minutes left, but a 10-minute "could" does.
The deferred list becomes the README's *next steps*.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex06_scope_planner.py`.
Write each ambiguity down as an **assumption** ("negative amounts are refunds"): a written
assumption can be disagreed with; a hidden one looks like a bug. Report your real time spent.

## 32.2 Project structure, typing, linting, tests

```text
expense_report/
├── README.md            # how to run, assumptions, trade-offs, next steps
├── pyproject.toml       # deps, entry point, lint/type config
├── src/expense_report/  # model.py · parse.py · report.py · cli.py
└── tests/               # per-module unit tests + CLI end-to-end
```

| Layer | Rule | Why it helps |
|---|---|---|
| Model | frozen dataclasses, `Decimal` money | no float drift; types document data |
| Core | pure functions, no I/O | unit tests need no files |
| CLI | `cli(argv, out, err) -> int` | test with `io.StringIO`; real exit codes |
| Errors | collect "line N: reason" per bad row | one typo does not kill the run |

Annotate public functions; run a formatter, linter and type checker if allowed. Test design
and fixtures: §31.1–§31.2; injecting clocks and randomness: §31.3.

## 32.3 What reviewers grade in take-homes

| Area | Strong | Weak |
|---|---|---|
| Correctness | spec met, edge rows handled, tests prove it | happy path only |
| Structure | layers, small functions, clear names | one long `main()` |
| Tests | edge and error cases, one command | none, or "it runs" |
| Communication | README: run, assumptions, trade-offs | missing or vague |
| Hygiene | no `breakpoint()`, bare `except:`, TODOs | debris left in |

Exercise 02 checks the mechanical rows with `ast`, without running the code.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex02_submission_checker.py`.
§31.8 lists what to look for as a reviewer.

## 32.4 Pair programming: collaboration signals, navigating an unfamiliar codebase

Pairing scores *how* you work: restate, plan before typing, think aloud (→ §2.3), treat
hints as information, hand back the keyboard. Read the entry point, then tests (intended
use), then the path you change, asking aloud where X is defined and who calls it:

```text
callers_of('unit_price') = ['Invoice.subtotal', 'legacy_rate']
entry_points = ['legacy_rate']
```

Resolution is by name only, so say "probably dead, can I check?" rather than deleting
`legacy_rate`.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex03_code_navigator.py`.

## 32.5 Incremental delivery and refactoring live

Run a thin slice end to end, keep it green, add one requirement at a time. Refactor in two
steps: structure with behaviour frozen, then behaviour on purpose.

**Worked problem: tidy a legacy fee function.** *Ladder:* (1) rewrite from reading: quirks
get lost unproven; (2) hand-picked tests: they cover only what you understood; (3) a **golden
master**: record today's outcomes on a boundary grid (each literal, ±1) and compare after
every step: one call per case per version.

```python
import itertools


def record(fn, cases):            # golden master, exceptions included
    out = {}
    for case in cases:
        try:
            out[case] = fn(*case)
        except Exception as exc:
            out[case] = f"raises {type(exc).__name__}"
    return out


def compare(old, new, cases):
    before, after = record(old, cases), record(new, cases)
    return [(c, before[c], after[c]) for c in cases if before[c] != after[c]]


def fee_legacy(g, m):                      # given: nobody dares touch it
    if g <= 0:
        return 0
    c = 1500 + ((g + 999) // 1000) * 500
    if m:
        if c > 2000:
            c = c - 500
    return c


def fee_tidied(grams, member):             # "obviously the same, but cleaner"
    if grams <= 0:
        raise ValueError("weight must be positive")
    cost = 2000 + (-(-grams // 1000) - 1) * 500
    return cost - 500 if member and cost >= 2000 else cost


grid = list(itertools.product((0, 1000, 1001, 5000), (False, True)))
for case, old, new in compare(fee_legacy, fee_tidied, grid):
    print(case, "legacy:", old, "new:", new)
```

```text
(0, False) legacy: 0 new: raises ValueError
(0, True) legacy: 0 new: raises ValueError
(1000, True) legacy: 2000 new: 1500
```

**Wrong-but-tempting:** "fixing" weight 0 or `>` → `>=` mid-refactor. Maybe right, but a
behaviour change: separate commit, pair's agreement. **Edge cases:** zero/negative inputs,
exact thresholds, unknown enum values (the exercise prices unknown zones as international),
exceptions; integer cents so float order cannot matter. **Follow-up:** a grid without 1-kg
weights misses the `>=` bug (a repo test pins this), so take boundaries from every literal.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex04_refactor_characterization.py`.

## 32.6 Follow-up discussion: extensions and trade-offs

**Worked problem: checkout kata.** v1 sums unit prices; v2 adds "3 A for 130"; v3 adds
"10% off baskets of 200+" after multi-buys, rounded down. *Ladder:* (1) an `if` per
requirement: by v3 offers and coupon interleave; (2) `Counter` + `divmod` makes offers
arithmetic, O(n + distinct SKUs); (3) **rules as objects** with one interface, ordered by
stage: a new requirement is a new class, and v1/v2 tests pass unchanged.

```python
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class MultiBuy:                    # v2: "3 A for 130"
    sku: str
    qty: int
    price: int
    stage = 0                      # item rules run first

    def discount(self, counts, prices, subtotal):
        return counts[self.sku] // self.qty * (self.qty * prices[self.sku] - self.price)


@dataclass(frozen=True)
class PercentOff:                  # v3: "10% off baskets of 200+"
    percent: int
    min_subtotal: int
    stage = 1                      # basket rules see the post-offer subtotal

    def discount(self, counts, prices, subtotal):
        return subtotal * self.percent // 100 if subtotal >= self.min_subtotal else 0


def total(skus, prices, rules=()):  # v1 is total(skus, prices)
    counts = Counter(skus)
    subtotal = sum(prices[s] * n for s, n in counts.items())
    for rule in sorted(rules, key=lambda r: r.stage):
        subtotal -= rule.discount(counts, prices, subtotal)
    return subtotal


PRICES = {"A": 50, "B": 30, "C": 20}
RULES = [PercentOff(10, 200), MultiBuy("A", 3, 130), MultiBuy("B", 2, 45)]
print(total("ABA", PRICES), total("AAAA", PRICES, RULES[1:]), total("BAACABA", PRICES, RULES))
```

```text
130 180 221
```

Listed first, the coupon still runs last: 280 − 20 − 15 = 245, minus 24 (10%, rounded
down). **Edge cases:** empty basket, unknown SKU (the repo raises `ValueError`), subtotal on
the threshold, rounding, scan order (a seeded shuffle test). **Follow-ups:** two offers on
one SKU make the cheapest mix a small knapsack (→ §19.6): ask if in scope. Coupon before or
after offers is a business rule: ask.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex05_checkout_kata.py`.
For a take-home debrief, prepare three costed extensions and one decision you would reverse.

## 32.7 Sample take-home with model solution

Brief: "CLI that totals a messy transactions CSV per category, largest first; optional month
filter; JSON mode." The model solution uses §32.2's layers (`parse_rows` → rows + errors,
`summarize`, `render_*`, thin `cli`); exit 0 ok, 1 missing file or `--strict` errors, 2 bad
arguments.

```text
$ expense_report transactions.csv --month 2024-03   -> exit 0
rent           1200.00
groceries        67.95
eating out       31.40
books            12.00
transport         5.80
TOTAL          1317.15
  [stderr] warning: line 7: bad amount 'abc'
  [stderr] warning: line 10: missing category
  [stderr] warning: line 11: bad date '2024-13-01'
```

"Transport" merged with "transport", and a refund was netted. The tests cover quoted commas,
`NaN`, 30 February and a wrong header.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex01_expense_report_cli.py`.

## Interviewer's view

- Rewarded: stated scope, written assumptions, edge-case tests, small green steps.
- Penalised: silent guesses, overrunning the time box, refactor mixed with behaviour change.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Sample take-home: expense summary CLI | ★ | layered CLI |
| 02 | Pre-submission checker | ◆ | `ast` static checks |
| 03 | Definitions and call-site navigator | ◆ | `ast.NodeVisitor` |
| 04 | Refactor behind characterization tests | ★ | golden master |
| 05 | Checkout kata v1 → v3 | ★ | rules as data |
| 06 | Take-home scope planner | ○ | must/should/could |

Index: `chapters/ch32_take_home_pair_programming/README.md`.

## Checkpoint quiz

1. The musts alone exceed your build time. What now?
2. Why does `cli` take `argv`, `out` and `err`?
3. Why record exceptions in a golden master?
4. Mid-refactor, your pair says "`> 2000` looks like a bug". What do you do?
5. Where does "buy 2 get 1 free" go in the kata?

<details><summary>Answers</summary>

1. Ask what matters most; keep the reserve; list the cuts in the README.
2. Tests pass a list and `io.StringIO` and check the exit code; no subprocess.
3. Raising instead of returning 0 is a behaviour change; compare must see it.
4. Note it, finish the frozen-behaviour refactor, then change it in an agreed separate step.
5. A new item-stage rule class; `total` and the existing tests stay as they are.
</details>

## Summary card

- Plan first; ~25% reserve; must → should → could; README: run, assumptions, trade-offs.
- Typed model, pure core, thin `cli(argv, out, err) -> int`, `Decimal` money.
- Pairing: restate, plan, narrate; entry point → tests → touched path.
- Refactor: golden master on boundaries, small steps, behaviour changes separately.
- Changing specs: rules behind one interface; old tests stay green.
