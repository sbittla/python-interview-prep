# Chapter 46. AI-Assisted Round Practice

◆ Extended · Tracks S M L · Study time ≈ 3 h · Prerequisites: Chapter 2, Chapter 31, Chapter 32

**Learning objectives**

- Run a repeatable workflow when an assistant writes code: decompose, prompt, test first, review, probe, explain.
- Expose plausible-but-wrong generated code with an oracle and seeded random inputs.
- Measure a hidden complexity bug deterministically, then fix it and state the new bound.
- Explain the trade-offs of every line you keep, and switch back to AI-free mode cleanly.

> **Recognise it.** "You may use any assistant"; "here is a repo, add a feature"; "walk me
> through what it generated".

## 46.1 How AI-allowed rounds differ

Policies differ by company and change; confirm the current one with your recruiter (→ §1.4).
Where assistants are allowed, the round often changes shape:

| | AI-free round | AI-allowed round |
|---|---|---|
| Task size | one function | a feature, several files, often in an existing codebase (→ §32.4) |
| Main signal | correct, tested solution | how you direct, verify and own the AI's output |

The §47.4 rubric gives 30 of 100 points to verifying and critiquing AI output.

## 46.2 Workflow

1. **Decompose** into small, testable steps; prompt per step.
2. **Prompt with context:** spec, signature, constraints, edge cases, surrounding style, and
   what *not* to change. Vague prompts get plausible code for a different problem.
3. **Tests first:** write the oracle and edge cases before reading the code, so it cannot
   anchor what you test (→ §31.2).
4. **Review the diff line by line** as a colleague's pull request (→ §31.8): what does each
   line assume, and what does it cost?
5. **Run and probe edges:** empty, one element, boundaries, duplicates, ties, negatives,
   repeated calls; a seeded property check against a brute-force oracle.
6. **Explain** each kept line aloud (→ §2.3); delete what you cannot explain.

## 46.3 Failure modes

| Failure mode | Looks like | Catch it with | Repo |
|---|---|---|---|
| Wrong boundary | binary search with `hi = len(a) - 1` | oracle + "x above all" | ex01 |
| Hidden O(n²) | `if x not in seen` on a list (→ §7.16) | count `__eq__` calls | ex02 |
| Leaked state | `def f(items, seen=[])` (→ §7.1) | call twice on fresh input | ex02 |
| Wrong tie-break | `Counter.most_common` keeps first-seen order | random text with ties | ex03 |
| Float/rounding | `round(float(p), 2)`; halves to even (→ §7.8, §7.9) | exact `Fraction` oracle | ex04 |
| Unhandled empty | `sum(x) / len(x)` on `[]` | edge-case table | ex04 |
| Off-by-one | `range(len(nums) - k)` misses the last window | k == len(nums) | ex05 |
| Over-reliance | "the examples pass" | tests written before reading | all |
| Can't explain | "the AI chose a heap" | the §46.6 checklist | ex06 |

## 46.4 Exercises: fix subtly wrong AI-generated solutions

**Worked problem: first index ≥ x.** Prompt: "index of the first element ≥ x in a sorted
list, `len(a)` if none". *Ladder:* (1) try a few examples: it passes; (2) hand-picked edge
cases: they find the bug *if* you think of "x above everything"; (3) a **property check**:
hundreds of seeded small cases against a linear-scan oracle, checked smallest first. That
finds the bug whether or not you thought of the case, and keeps guarding the fix.

```python
import random


def generated_first_ge(a, x):          # given: "first index with a[i] >= x, else len(a)"
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def oracle(a, x):                       # slow but obviously right
    return next((i for i, v in enumerate(a) if v >= x), len(a))


def find_counterexample(candidate, trials=300, seed=0):
    rng = random.Random(seed)
    cases = []
    for _ in range(trials):
        a = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 6)))
        cases.append((a, rng.randint(-1, 6)))      # x below, inside, above
    for a, x in sorted(cases, key=lambda c: len(c[0])):   # smallest first
        if candidate(a, x) != oracle(a, x):
            return a, x
    return None


print([generated_first_ge([1, 3, 5], x) for x in (0, 3, 4)])
bad = find_counterexample(generated_first_ge)
print(bad, generated_first_ge(*bad), oracle(*bad))
```

```text
[0, 1, 2]
([0], 3) 0 1
```

**Fix and explain.** `len(a)` is a legal answer, so it must lie in the search range:
`lo, hi = 0, len(a)`. Invariant: the answer is in `[lo, hi]`; each step halves the range, so
O(log n) time, O(1) space. With that one change `find_counterexample(first_ge)` returns `None`.
The empty list was right *by accident* (`hi = -1`, loop skipped, returns 0).
**Wrong-but-tempting:** `if x > a[-1]: return len(a)` (crashes on `[]`); a linear scan (O(n)). **Edge cases:** `[]`, x below all, x above all, x equal to
the last element, all duplicates. **Follow-ups:** ship `bisect.bisect_left` (→ §11.2) unless
asked to hand-roll; an unsorted input gives a meaningless answer silently, so state the
precondition.
→ repo: `chapters/ch46_ai_assisted_practice/solutions/ex01_lower_bound_boundary.py`.

**Hidden quadratic, measured without a clock.** Probes with distinct hashes and a counting
`__eq__`: a set compares hashes first and never reaches `__eq__`; a list scan calls it
n(n−1)/2 times:

```text
n=100: __eq__ calls generated=4950 fixed=0
n=200: __eq__ calls generated=19900 fixed=0
n=400: __eq__ calls generated=79800 fixed=0
```

The fix, a local `set` (no mutable default), is O(n) expected time and O(n) space, and now
requires hashable items: a trade-off to state.
→ repo: `chapters/ch46_ai_assisted_practice/solutions/ex02_dedupe_hidden_state.py`.
Exercises 03–04 hunt tie order, `split(" ")` and float rounding the same way.

## 46.5 Exercises: review and optimise a generated solution

Generated `max_window_sum(nums, k)` loops `for i in range(len(nums) - k)` with `best = 0` and
`sum(nums[i:i + k])`. A review note names the line, the problem and the change:

| Category | Note |
|---|---|
| correctness | `range(len(nums) - k)` skips the last window; use `+ 1` |
| correctness | `best = 0` is wrong when every window is negative |
| complexity | re-summing each slice is O((n−k+1)·k); keep a running sum |
| edge case | `k == 0` or `k > len(nums)` silently returns 0, and negative k returns a meaningless slice sum; raise `ValueError` |

Counting element reads gives evidence, not a timing: n = 2000, k = 1000 prints
`reads generated=1000000 fixed=3000`. The running sum (→ §10.4) adds `nums[i]`,
subtracts `nums[i - k]`: O(n) time, O(1) space, checked against brute force on seeded cases.
→ repo: `chapters/ch46_ai_assisted_practice/solutions/ex05_review_optimise_window.py`.

## 46.6 Exercises: explain trade-offs aloud

A 30–60 second answer to "why this version?" covers complexity, space, an alternative, edge
cases, assumptions and evidence. Exercise 06 makes the checklist data and
scores an answer with word-boundary regexes (so "contest" is not "test"), under a 90-word
budget (excerpt of the run):

```text
vague           ok=False words=  6 missing=['complexity', 'space', 'alternative', 'edge cases', 'assumptions', 'evidence']
rambling        ok=False words=150 missing=['complexity', 'space', 'alternative', 'edge cases', 'assumptions']
keyword soup    ok=True  words=  8 missing=[]
mine            ok=True  words= 83 missing=[]
```

The passing answer explains the dedupe fix: O(n²) and stateful before, O(n) expected and
O(n) space after; `dict.fromkeys` as the alternative; hashable items required; empty and
repeated calls; the `__eq__` probe as evidence. The keyword-soup row shows the limit: the
scorer checks *mentions*, not truth or sentences.
→ repo: `chapters/ch46_ai_assisted_practice/solutions/ex06_tradeoff_checklist.py`.

## 46.7 Switching back to AI-free mode

Many loops still include AI-free rounds; keep both modes in practice:

- Alternate days: solve a bank problem (→ §45.1) cold, then redo an exercise here with an
  assistant, writing the tests yourself.
- Before an AI-free round, warm up timed with completion tools turned off.
- Keep the habits that transfer: oracle first, edge-case list, complexity before and after
  coding (→ §2.4), dry runs (→ §2.6).
- Recall drills: write `bisect_left`, a running window and a `Counter` top-k from memory.

## Interviewer's view

- Rewarded: a plan before prompting, own tests, bugs found and explained, checked
  complexity, every line defended.
- Penalised: pasting output unread, "it passed the examples", re-prompting until green.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Fix a generated binary search | ★ | oracle + seeded random cases |
| 02 | Fix a generated dedupe | ★ | probe objects count work |
| 03 | Fix a generated top-k words | ◆ | failures classified by kind |
| 04 | Fix a generated average | ◆ | exact `Fraction` oracle |
| 05 | Review and optimise a sliding-window sum | ◆ | review notes + read counting |
| 06 | Trade-off checklist scorer | ◆ | rubric as data |

Index: `chapters/ch46_ai_assisted_practice/README.md`.

## Checkpoint quiz

1. Why write the oracle before reading the generated code?
2. Why sort random cases by size before checking them?
3. How can you show a hidden O(n²) without timing anything?
4. The generated binary search passes on `[]`. Is that evidence it is correct?
5. What can the trade-off scorer not check?

<details><summary>Answers</summary>

1. The code would anchor your tests to its own assumptions, so you would miss its bugs.
2. The first failure reported is small, so it is easy to explain and becomes a regression test.
3. Count the work: `__eq__` calls with a probe class, or element reads through a wrapper.
4. No. It is right by accident (`hi = -1`); "x above all" still fails.
5. Whether the stated points are true. It only checks that they are mentioned.
</details>

## Summary card

- AI-allowed rounds grade direction and verification; confirm the policy first (→ §1.4).
- Workflow: decompose → prompt with context → tests first → review diff → probe edges → explain.
- Oracle + seeded small cases, smallest first; keep the counterexample.
- Suspects: boundaries, `in list`, mutable defaults, ties, float rounding, empty input.
- Explain the six checklist points (§46.6); keep AI-free practice going.
