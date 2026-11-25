# Chapter 32. Take-Home and Pair-Programming Workflow

◆ Extended · Tracks S M L · Study time ≈ 3 h · Prerequisites: Chapter 2, Chapter 31

**Learning objectives**

- Scope a take-home to its time box; record scope and assumptions in the README.
- Lay out a small typed, tested project a reviewer can run in one command.
- Read unfamiliar code aloud, refactor behind characterization tests, absorb spec changes.

> **Recognise it.** "Take about 3 hours"; "we'll extend it in the follow-up"; "here's our
> repo, add a feature"; "requirements will change".

## 32.1 Take-home: scoping, time-boxing, README, assumptions

Plan first: list tasks, estimate each, tag it must/should/could, and reserve about a quarter
of the time for tests, README and a clean run. For the §32.7 brief:

```text
must   (115 min): parse + validate CSV 40, per-category totals 20, CLI with argparse 25, unit tests for core 30
should ( 30 min): JSON output 15, month filter 15
could  ( 70 min): multi-currency 60, --strict flag 10
budget 170: reserve 42, build 128, musts 115, slack 3
  added beyond musts: ['--strict flag']
  deferred: ['JSON output', 'month filter', 'multi-currency']
```

With 13 minutes left, the 15-minute "should" misses; the 10-minute "could" fits. At 120
minutes the musts overflow: ask what matters most.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex06_scope_planner.py`.
Write assumptions down (hidden ones look like bugs):

```markdown
# expense-report
## How to run      pip install -e . · expense_report data.csv · pytest
## Assumptions     one currency; negatives are refunds
## Trade-offs      whole file in memory; Decimal, not float
## Scope           done: musts, --strict · next: JSON 15, month filter 15, multi-currency 60
## Time spent      about 3 h
```

## 32.2 Project structure, typing, linting, tests

```text
expense_report/
├── README.md
├── pyproject.toml       # deps, entry point, lint/type config
├── src/expense_report/  # model.py · parse.py · report.py · cli.py
└── tests/               # unit tests + CLI end-to-end
```

| Layer | Rule | Why it helps |
|---|---|---|
| Model | frozen dataclasses (→ §24.8), `Decimal` money (→ §7.8) | no float drift |
| Core | pure functions, no I/O | unit tests need no files |
| CLI | `cli(argv, out, err) -> int`; argparse redirected to them | all text testable via `io.StringIO` |
| Errors | "line N: reason" per bad row; unreadable file → exit 1 | no crash, no traceback |

Annotate public functions; run formatter, linter, type checker if allowed. Tests: §31.1–§31.3.

## 32.3 What reviewers grade in take-homes

| Area | Strong | Weak |
|---|---|---|
| Correctness | spec met, edge rows tested | happy path only |
| Structure | layers, small functions | one long `main()` |
| Tests | edge and error cases, one command | none |
| Communication | README: run, assumptions, trade-offs | missing or vague |
| Hygiene | no `breakpoint()`, bare `except:`, TODOs | debris left in |

Exercise 02 checks the mechanical rows with `ast` and `tokenize`, without running the code.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex02_submission_checker.py`.
§31.8 lists what to look for as a reviewer.

## 32.4 Pair programming: collaboration signals, navigating an unfamiliar codebase

Pairing scores *how* you work: restate, plan before typing, think aloud (→ §2.3), treat
hints as information. Read the entry point, then tests, then the path you change, asking
aloud where X is defined and who calls it:

```text
entry_points = ['legacy_rate']
callers_of('unit_price') = ['Invoice.subtotal', 'legacy_rate']
```

Resolution is by name only, so say "probably dead, can I check?" rather than deleting
`legacy_rate`.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex03_code_navigator.py`.

## 32.5 Incremental delivery and refactoring live

Ship a thin slice end to end, keep it green, add one requirement at a time. Refactor in two
steps: structure first (behaviour frozen), then behaviour.

**Worked problem: tidy a legacy fee function.** *Ladder:* (1) rewrite from reading: quirks
get lost; (2) hand-picked tests cover only what you understood; (3) a **golden master**:
record outcomes on a boundary grid (each literal, ±1); compare after every step.

```python
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


grid = [(g, m) for g in (0, 1000, 1001, 5000) for m in (False, True)]
for case, old, new in compare(fee_legacy, fee_tidied, grid):
    print(case, "legacy:", old, "new:", new)
```

```text
(0, False) legacy: 0 new: raises ValueError
(0, True) legacy: 0 new: raises ValueError
(1000, True) legacy: 2000 new: 1500
```

**Wrong-but-tempting:** "fixing" weight 0 or `>` → `>=` mid-refactor: a behaviour change
needs its own commit and your pair's agreement. **Edge cases:** zero/negative inputs, exact
thresholds, unknown zones (priced as international), exceptions; integer cents.
**Follow-up:** a grid without 1-kg weights misses the `>=` bug (a repo test pins this).
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex04_refactor_characterization.py`.

## 32.6 Follow-up discussion: extensions and trade-offs

**Worked problem: checkout kata.** v1 sums unit prices; v2 adds "3 A for 130"; v3 adds
"10% off baskets of 200+" after multi-buys, rounded down. *Ladder:* (1) an `if` per
requirement: by v3 offers and coupon interleave; (2) `Counter` (→ §6.7) + `divmod` makes
offers arithmetic, O(n + distinct SKUs); (3) **rules as objects** behind one interface
(Strategy, → §24.11; a `Protocol` in the repo, → §24.9; API first, → §29.1), ordered by
stage: a new kind of offer is a new class; v1/v2 tests pass unchanged.

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


A3, B2, P = MultiBuy("A", 3, 130), MultiBuy("B", 2, 45), {"A": 50, "B": 30, "C": 20}
print(total("ABA", P), total("AAAA", P, [A3]), total("BAACABA", P, [PercentOff(10, 200), A3, B2]))
```

```text
130 180 221
```

The coupon runs last: 280 − 20 − 15 = 245, minus 24. **Wrong-but-tempting:** 10% of the
gross (28) over-discounts; `round()` can round up (24.7 → 25) and rounds halves to even
(24.5 → 24, 25.5 → 26); `//` always rounds down. **Edge cases:** empty basket, unknown SKU, exact threshold, scan order, invalid rules
(rejected at construction). **Follow-ups:** two offers on one
SKU make the cheapest mix a knapsack (→ §19.6); coupon order is a business rule: ask.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex05_checkout_kata.py`.
Debrief: bring costed extensions and a decision to reverse.

## 32.7 Sample take-home with model solution

Brief: "CLI that totals a messy transactions CSV per category, largest first; optional month
filter; JSON mode." Model solution: §32.2's layers; exit 0 ok, 1 unreadable file or `--strict`
errors, 2 bad arguments.

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

Tests cover quoted newlines, `NaN`, 30 February, non-UTF-8 input and `20240301`, which
`date.fromisoformat` accepts from 3.11, so the code checks the shape first.
→ repo: `chapters/ch32_take_home_pair_programming/solutions/ex01_expense_report_cli.py`.

## Interviewer's view

- Rewarded: stated scope, written assumptions, edge-case tests, small green steps.
- Penalised: silent guesses, overruns, refactors that change behaviour.

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
4. Mid-refactor, your pair says "`> 2000` looks like a bug". Now what?
5. Where does "buy 2 get 1 free" go in the kata?

<details><summary>Answers</summary>

1. Ask what matters most; keep the reserve; list the cuts in the README.
2. Tests pass a list and `io.StringIO` (argparse's usage text lands there too); no subprocess.
3. Raising instead of returning 0 is a behaviour change; compare must see it.
4. Note it; finish the refactor; then change it in a separate, agreed step.
5. Nowhere new: `MultiBuy(sku, 3, 2 * unit)`. Only a new kind of offer needs a class.
</details>

## Summary card

- Plan first: ~25% reserve; must → should → could; README states assumptions.
- Typed model, pure core, thin `cli(argv, out, err) -> int`, `Decimal` money.
- Pairing: restate, plan, narrate; entry point → tests → touched path.
- Refactor behind a golden master; change behaviour separately.
- Changing specs: rules behind one interface; old tests stay green.
