# Chapter 3. Diagnostic Test and Track Selection

**Tier:** ★ Core · **Tracks:** S M L · **Time:** 60-minute test + 45 minutes to grade and plan ·
**Prerequisites:** Chapter 1 (tracks S/M/L, §1.7), Chapter 2 (the 6-step method)

**Learning objectives**

- Take a timed 30-question diagnostic: Python behaviour, complexity, two coding problems.
- Score it with a fixed rubric and place yourself: fast track, full path or foundations.
- Turn area scores plus your Chapter 1 track into a weekly plan with repair blocks.
- Start a spaced-repetition log that revisits every miss at 1, 3, 7 and 21 days.

> **Recognise it — what your result is telling you**
>
> | Symptom | Meaning | Go to |
> |---|---|---|
> | Misses on Q1–8 (numbers, slicing, `Counter`) | shaky Python core | Ch. 5–6, §7.8–7.9 |
> | Misses on Q9–16 (aliasing, defaults, scope) | bugs you cannot see | Ch. 7, 23 |
> | Misses on Q17–28 | cannot state cost up front | Ch. 8 |
> | Q29/Q30 fail only on `[]` or touching input | method, not knowledge | Ch. 2 |
> | Every area ≥ 75 % | fast track | §3.2 |

## 3.1 30-question diagnostic: Python behaviour, complexity reasoning, two coding problems

**Rules.** One sitting, 60 minutes, paper or a text file, **no interpreter, no AI assistant**.
A blank scores zero. Do not open `chapters/ch03_diagnostic_test/` first: it contains this test.

| Part | Questions | Suggested time | Points |
|---|---|---|---|
| A. Predict the output | Q1–16 | 16 min | 16 |
| B. Complexity | Q17–28 | 12 min | 12 |
| C. Coding | Q29–30 | 2 × 15 min | 8 (4 each) |

**Part A — what does each snippet print?** Each snippet runs on its own (CPython 3.10+); write
the exact printed line.

```python
# Q1
print(7 // -2, -7 % 3)
# Q2
print(round(2.5), round(3.5))
# Q3
x = [1, 2, 3]
print(x[::-1][1:], x[-5:2])
# Q4
print(0.1 + 0.2 == 0.3, abs(0.1 + 0.2 - 0.3) < 1e-9)
# Q5
d = {"a": 1}
d.setdefault("a", 5)
d.setdefault("b", 7)
print(d)
# Q6
from collections import Counter
print(Counter("banana").most_common(2))
# Q7
print(sorted(["bb", "a", "ccc", "dd"], key=len))
# Q8
a, *b, c = range(5)
print(a, b, c)
# Q9
def f(x, acc=[]):
    acc.append(x)
    return acc
f(1)
print(f(2))
# Q10
grid = [[0] * 2] * 2
grid[0][0] = 1
print(grid)
# Q11
fs = [lambda: i for i in range(3)]
print([f() for f in fs])
# Q12
print(True + True, bool("False"), bool(""))
# Q13
g = (x * x for x in range(3))
print(sum(g), sum(g))
# Q14
t = (1, [2])
try:
    t[1] += [3]
except TypeError:
    print('TypeError', t)
# Q15
x = 1
def f():
    print(x)
    x = 2
try:
    f()
except Exception as e:
    print(type(e).__name__)
# Q16
a = [1, 2, 3]
b = a
a += [4]
c = a
a = a + [5]
print(b, c is b, a)
```

**Part B — pick the tightest bound listed.** Options: **A** O(1) · **B** O(log n) · **C** O(n) ·
**D** O(n log n) · **E** O(n²) · **F** O(2ⁿ). Worst-case time unless stated; `n` is the size of the collection.

| Q | Operation | Q | Operation |
|---|---|---|---|
| 17 | `x in lst` (list) | 23 | `for i in range(n): for j in range(i): total += 1` |
| 18 | `x in st` (set, average case) | 24 | `heapq.heappush(h, x)` |
| 19 | `lst.pop(0)` | 25 | naive recursive `fib(n) = fib(n-1) + fib(n-2)` |
| 20 | `dq.popleft()` (`collections.deque`) | 26 | `i = 1; while i < n: i *= 2` |
| 21 | `sorted(lst)` | 27 | `for i in range(n): total += sum(lst[i:])` |
| 22 | `bisect.bisect_left(lst, x)`, `lst` sorted | 28 | extra **space** of recursive DFS on a path-shaped tree |

**Part C — coding.** Use the 6-step method from Chapter 2; state complexity before you code.

- **Q29.** Given a list of user ids in arrival order, return the first id that occurs exactly once
  in the whole list, or `None`. Example: `["ann", "bob", "ann", "cy", "bob"]` → `"cy"`.
- **Q30.** Given closed booking intervals `[start, end]` in any order, return the merged busy
  periods sorted by start; overlapping *or touching* intervals merge. Example:
  `[[8, 10], [1, 3], [2, 6]]` → `[[1, 6], [8, 10]]`; `[[1, 3], [3, 5]]` → `[[1, 5]]`.

<details>
<summary>Answer key (Q1–28) — open only after the 60 minutes</summary>

Part A answers were produced by **executing** each snippet (§3.2), not typed by hand.

| Q | Prints | Why | Q | Prints | Why |
|---|---|---|---|---|---|
| 1 | `-4 2` | `//` floors; `%` takes the divisor's sign | 9 | `[1, 2]` | default list created once, shared |
| 2 | `2 4` | round-half-to-even | 10 | `[[1, 0], [1, 0]]` | `* 2` copies the reference to one row |
| 3 | `[2, 1] [1, 2]` | slices clamp out-of-range bounds | 11 | `[2, 2, 2]` | closures read `i` at call time |
| 4 | `False True` | binary floats; compare with a tolerance | 12 | `2 True False` | `bool` subclasses `int`; non-empty str is truthy |
| 5 | `{'a': 1, 'b': 7}` | `setdefault` never overwrites | 13 | `5 0` | a generator is exhausted after one pass |
| 6 | `[('a', 3), ('n', 2)]` | counts, highest first | 14 | `TypeError (1, [2, 3])` | `+=` mutates the list, then the tuple store fails |
| 7 | `['a', 'bb', 'dd', 'ccc']` | sort is stable | 15 | `UnboundLocalError` | assignment makes `x` local to the whole function |
| 8 | `0 [1, 2, 3] 4` | starred target always gets a list | 16 | `[1, 2, 3, 4] True [1, 2, 3, 4, 5]` | `+=` mutates in place; `a + [5]` builds a new list |

Part B: 17 C · 18 A · 19 C · 20 A · 21 D · 22 B · 23 E · 24 B · 25 F · 26 B · 27 E · 28 C.
Q25 is Θ(φⁿ) ≈ Θ(1.618ⁿ); O(2ⁿ) is the tightest bound *listed*. Q27 is quadratic because each
slice copies n − i items before `sum` reads them. Q28: the recursion stack holds all n frames.

Part C: graded by the hidden tests in §3.2; worked solutions follow there.
</details>

## 3.2 Scoring and placement: fast track vs full path

**Rubric.** One point per question in Parts A and B. Each coding problem runs against 8 hidden
tests and earns `4 * passed // 8`: 8 passed → 4, 6–7 → 3, 4–5 → 2, 2–3 → 1; a test that raises
fails. On paper, trace your code through the 8 `CASES` in the solution files honestly.

| Area | Questions | Max | Pass (75 %) | Repair if below |
|---|---|---|---|---|
| core | Q1–8 | 8 | 6 | Ch. 5–6; §7.8–7.9 |
| gotchas | Q9–16 | 8 | 6 | Ch. 7, 23 |
| complexity | Q17–28 | 12 | 9 | Ch. 8 |
| coding | Q29–30 | 8 | 6 | Ch. 2, 9 |
| **total** | 30 | **36** | | |

**Placement rule** (applied in this order):

1. Overall below 40 % (14/36 or less) → **foundations** — Python and basic DSA come first.
2. Every area at or above 75 % → **fast track** — skim Part I, start Part II in week 1.
3. Otherwise → **full path**, with a repair block for each weak area.

One weak area blocks the fast track: four missed gotchas lose screens that Big-O skill won't save.

**The auto-grader.** Where does the Part A key come from? *Brute force:* type it by hand — one
typo marks every reader wrong. *Improved:* run each snippet in a subprocess — correct, but 16
interpreter start-ups. *Optimal:* `exec` each snippet in a fresh namespace and capture stdout
in-process; the interpreter itself writes the key, and a test fails on any `SyntaxWarning`.

```python
def run_snippet(code: str) -> str:
    """Execute ``code`` in a fresh namespace and return what it printed (stripped)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<diagnostic>", "exec"), {"__name__": "__diagnostic__"})
    return buf.getvalue().strip()


def answer_key() -> dict[int, str]:
    key = {qid: run_snippet(code) for qid, code in PREDICT.items()}
    key.update({qid: letter for qid, (_, letter) in CHOICE.items()})
    return key
```

`grade(sheet, coding_points)` normalises whitespace and letter case and returns per-area points
plus missed ids. A sample candidate who knows the basics but not the traps:

```text
Sample sheet:
  core        7/8
  gotchas     4/8
  complexity  9/12
  coding      6/8
  total      26/36
  missed: [2, 9, 11, 13, 14, 19, 27, 28, 30]
```

→ repo: `chapters/ch03_diagnostic_test/solutions/ex01_diagnostic_bank.py`

### Worked solution: Q29 first unique value

*Brute force:* `ids.count(x) == 1` for each id — O(n²); ~10¹⁰ steps at 10⁵ ids, so move up a
rung. *Optimal:* count once with a hash map, then rescan the **original list** to keep arrival
order — O(n) time, O(k) space for k distinct ids.

```python
def first_unique(ids: Sequence[Hashable]) -> Hashable | None:
    counts = Counter(ids)
    for x in ids:
        if counts[x] == 1:
            return x
    return None
```

Wrong-but-tempting: `min(counts, key=counts.get)` returns the least frequent id, which may occur
twice. Edge cases: empty list, all repeated, falsy id `0`. Scorer output:

```text
score first_unique             4/4
score brute_force              4/4
score tempting_least_frequent  3/4
```

### Worked solution: Q30 merge booked intervals

*Brute force:* repeatedly find any overlapping pair, fuse it and rescan — O(n³) worst case.
*Optimal:* sort by start (O(n log n)); after sorting, only the **last** merged interval can
overlap the next one, so one sweep finishes the job. (Full treatment: → §17.6.)

```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])                  # new list: input never aliased
    return merged
```

Wrong-but-tempting: dropping `max` (nested `[[1, 10], [2, 3]]` breaks; scores 3/4) or using `<`
(touching intervals stay apart).

→ repo: `chapters/ch03_diagnostic_test/solutions/ex03_first_unique.py`,
`chapters/ch03_diagnostic_test/solutions/ex04_merge_intervals.py`

## 3.3 Mapping results to tracks and weekly plans

Your target role picks the **track** (S software engineering, M data/ML, L GenAI/LLM, → §1.7);
the diagnostic picks the **path** and where repair time goes. Path plus weeks available picks the
plan, refining Chapter 1's time-only rule with evidence:

| Path | < 8 weeks | 8–11 weeks | ≥ 12 weeks |
|---|---|---|---|
| fast | crash-4 | standard-8 (Part I skimmed) | standard-8 (Part I skimmed) |
| full | crash-4 + warning | standard-8 | standard-8 |
| foundations | standard-8 + warning | standard-8 + warning | foundations-12 |

Weeks 6–7 of the standard plan become your track's chapters (S: 28–32, M: 33–37, L: 38–43);
week 1 gets a repair block per weak area, weakest first, and ends with a **diagnostic retake**.
In foundations-12 the four foundation weeks *are* the repair, so the retake moves to week 4.

Output for two candidates (excerpt; ex02 also plans a 12-week foundations case):

```text
strong SWE: core=100% gotchas=88% complexity=92% coding=100% overall=94%
  path=fast weak=[] track=S weeks=4 -> plan=crash-4 warning=False
    Week 1: Patterns and hashing (Ch. 2, 8-11); skim Part I via the diagnostic + diagnostic retake
    Week 3: DP, backtracking (Ch. 18-19) + track S highlights
    (4 weeks in total)
sample sheet: core=88% gotchas=50% complexity=75% coding=75% overall=72%
  path=full weak=['gotchas'] track=L weeks=8 -> plan=standard-8 warning=False
    Week 1: Playbook, Big-O, Python essentials, gotchas, arrays/strings/hashing (Ch. 1-9) + Repair: gotchas (Ch. 7, 23) + diagnostic retake
    Week 6: Track part 1: Ch. 38-40
    Week 7: Track part 2: Ch. 41-43
    (8 weeks in total)
```

Pitfalls: treating a warning as permission; retaking until answers are memorised — a retake
counts only if you can explain each answer aloud.

→ repo: `chapters/ch03_diagnostic_test/solutions/ex02_placement.py`

## 3.4 Setting up a spaced-repetition log (revisit at 1, 3, 7, 21 days)

Every miss — diagnostic questions now, practice problems later — becomes a row in an append-only
CSV: `date,problem,pattern,result,minutes`, with `result` one of `solved`, `struggled`, `failed`.
Store **attempts, not due dates**: due dates are derived, so a failed review restarts the ladder
automatically and nothing goes stale when you skip a day.

| Last attempt | Trailing `solved` streak | Next review |
|---|---|---|
| `failed` / `struggled` | 0 | +1 day (ladder restarts) |
| `solved` | 1 / 2 / 3 / 4 | +1 / +3 / +7 / +21 days |
| `solved` | 5 or more | retired |

```python
def next_due(last_day: str, streak: int) -> str | None:
    if streak < 0:
        raise ValueError("streak must be >= 0")
    if streak == 0:
        return _shift(last_day, LADDER[0])
    if streak > len(LADDER):
        return None
    return _shift(last_day, LADDER[streak - 1])
```

`due(rows, today)` groups rows by problem, stable-sorts by date (same-day rows keep file order),
computes the trailing streak and returns every `(due_date, problem)` up to today, overdue included. The sample sheet's
nine misses, reviewed on two days:

```text
Seeded 9 rows; due on 2026-11-19: 9 items
Reviewed on 11-19 (Q11, Q30 still wrong) and 11-20 (all right). Next due:
  2026-11-21: ['diag-Q11', 'diag-Q30']
  2026-11-23: ['diag-Q02', 'diag-Q09', 'diag-Q13', 'diag-Q14', 'diag-Q19', 'diag-Q27', 'diag-Q28']
```

Log `solved` only if you answered *and explained* it without notes in the target time; otherwise
`struggled`. Chapter 48 reads the same file and adds a daily cap, a 7-day
agenda and a weakest-pattern ranking (→ §48.1,
`chapters/ch48_final_roadmap/solutions/ex02_spaced_repetition.py`).

→ repo: `chapters/ch03_diagnostic_test/solutions/ex05_review_log.py`

## Interviewer's view

The three parts mirror three signals interviewers score (→ §1.6): **Python fluency** (screens
ask "what does this print?" because a candidate who misreads aliasing ships that bug), **stating
complexity** before coding, and **working, tested code**. Q29 and Q30 are easy on purpose: points
are lost on `[]`, touching intervals and mutated inputs — exactly where interviewers probe.

## Exercises

All in `chapters/ch03_diagnostic_test/` (stubs in `exercises/`, run tests with `TARGET=exercises`).

| Id | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | 30-question diagnostic and auto-grader (key produced by executing snippets) | ★ | data-driven grading, `exec` + `redirect_stdout` |
| ex02 | Placement: scores → path → weekly plan for track S/M/L | ★ | decision table + templating |
| ex03 | Q29 first unique value + 0–4 scorer | ★ | hash-map frequency count |
| ex04 | Q30 merge booked intervals + 0–4 scorer | ★ | sort + linear sweep |
| ex05 | Spaced-repetition log (1, 3, 7, 21 days), CSV round trip | ★ | append-only log + date arithmetic |

## Checkpoint quiz

1. Why does the grader execute the Part A snippets instead of storing their answers?
2. Scores: core 8, gotchas 8, complexity 12, coding 3. Path and repair block?
3. Scores total 14/36 and you have 10 weeks. Which plan, and is there a warning?
4. You failed a problem on 18 Nov and solved it on 19 and 20 Nov. When is it next due?
5. In `merge`, why is comparing only with the last merged interval enough, and what does
   `merged[-1][1] = end` break?

<details>
<summary>Answers</summary>

1. The key is then produced by the interpreter itself, so it cannot contain a typo or a
   version-specific mistake; a test also fails if any snippet emits a warning.
2. Full path (coding 3/8 = 38 % < 75 %; overall 31/36 = 86 %, so not foundations); repair:
   playbook + hashing drills (Ch. 2, 9) in week 1.
3. 14/36 = 39 % < 40 % → foundations; with fewer than 12 weeks it becomes standard-8 **with** a warning.
4. Trailing streak 2 → +3 days → 23 Nov.
5. After sorting by start, every earlier interval ends at or before the last merged end, so only the
   last one can reach the next start. Plain assignment shrinks the end on nested input:
   `[[1, 10], [2, 3]]` would give `[[1, 3]]`.
</details>

## Summary card

- **Test:** 60 min, no interpreter; 16 predict-output, 12 Big-O, 2 coding (`4 * passed // 8`); max 36.
- **Placement:** < 40 % overall → foundations; every area ≥ 75 % → fast track; else full path.
- **Plan:** track from your role (Ch. 1), plan from path + weeks, week-1 repair per weak area,
  retake at the end of week 1 (week 4 on foundations-12).
- **Grader:** answer keys come from running the code, never from typing.
- **Q29:** `Counter`, rescan in order, O(n). **Q30:** sort, sweep, `max`, `<=`, O(n log n).
- **Log:** store attempts; miss → +1 day; streak 1/2/3/4 → +1/+3/+7/+21; 5 → retired (feeds Ch. 48).
