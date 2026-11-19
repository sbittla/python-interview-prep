# Chapter 2. Interview Playbook (Short Form)

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 2–3 hours · **Prerequisites:** Chapter 1

Knowing algorithms is half of a coding round; the other half is a routine that turns a vague
prompt into tested code while someone watches. This chapter gives you that routine plus six small
repo tools for practising it on every later chapter.

**Learning objectives**

- Run the 6-step method end to end, with an exit test for each step.
- Ask the clarifying questions that change the algorithm, and state assumptions for the rest.
- State a complexity target *before* coding and verify it *after* coding.
- Test your own code with a dry run, an edge-case sweep and a brute-force cross-check.
- Keep a 45- or 60-minute round on schedule and recover cleanly from mistakes.

> **Recognise the moment**
>
> | Signal in the room | Go to |
> |---|---|
> | Prompt is one or two sentences, no constraints given | §2.2 clarify |
> | You have been silent for more than ~30 seconds | §2.3 think aloud |
> | You have an idea but have not said its cost | §2.4 |
> | No idea after 3–4 minutes | §2.5 |
> | "I think it's done" | §2.6 test before you say so |
> | Clock past a checkpoint | §2.7 |
> | Interviewer: "Are you sure about that line?" | §2.8 |

## 2.1 The 6-step method: clarify → examples → brute force → optimise → code → test

Each step has a goal and an **exit test**: a concrete thing you can point to before moving on.

| Step | Goal | Exit test |
|---|---|---|
| 1. Clarify | Pin down inputs, outputs, limits | You restate the problem in one sentence; the interviewer agrees |
| 2. Examples | Make it concrete | One normal and one edge example with expected answers |
| 3. Brute force | Prove you can solve it at all | Correct idea + its complexity said aloud |
| 4. Optimise | Meet the size limit from step 1 | Better idea + complexity; interviewer agrees to code it |
| 5. Code | Clean, readable implementation | Finished, named helpers, no dead branches |
| 6. Test | Find your own bugs first | Dry run on an example + edge cases walked through |

Never skip step 3 to look fast: it is both your fallback answer and your test oracle.

### Worked example: counting pairs, end to end

*Prompt:* "Given a list of integers and a target, count the pairs that add up to the target."

**1. Clarify.** "Pairs of positions or pairs of values? If `nums = [2, 2, 2]` and the target is 4,
is the answer 1 or 3?" Interviewer: positions `i < j`, so 3. "How long can the list be?" Up to
10^5. "Negatives?" Yes. "Can I modify the list?" Prefer not. Restate: *count index pairs
i < j with nums[i] + nums[j] == target; n ≤ 10^5; values may repeat or be negative.*

**2. Examples.** `[1, 3, 2, 2], 4 → 2` (1+3 and 2+2). `[], 0 → 0`. `[2, 2, 2], 4 → 3`.

**3. Brute force.** Check every pair with two nested loops: O(n²) time, O(1) extra space. At
n = 10^5 that is about 5 × 10^9 pair checks, far over budget (§2.4), so move up a rung.

**4. Optimise.** The brute force asks, for each `j`, "how many earlier values equal
`target - nums[j]`?" A dict of counts answers that in O(1) average time. One pass: O(n) time,
O(n) space. Say it aloud before coding.

**5. Code.**

```python
def count_pairs_fast(nums: list[int], target: int) -> int:
    seen: dict[int, int] = {}
    pairs = 0
    for x in nums:
        pairs += seen.get(target - x, 0)   # partners seen so far: j > i automatically
        seen[x] = seen.get(x, 0) + 1
    return pairs
```

Look up *before* inserting `x`: otherwise `x` pairs with itself when `2 * x == target`.

**6. Test.** Dry-run `[1, 3, 2, 2]` (shown in §2.6), then walk the edge cases: empty list,
one element, all equal, negatives. When practising, also *stress-test*: run the fast version and
the brute force on 500 seeded random small inputs and report the first disagreement.

**Wrong but tempting.** "Sort, then two pointers, one pair per match" fails when values repeat:
moving both pointers after a match skips duplicate partners. The stress tester finds it, and a
greedy *shrinker* (delete elements, move values toward 0 while it still fails) reduces it to a
case you can trace by hand:

```text
fast vs brute, 500 random cases: counterexample = None
two-pointer vs brute: counterexample = ([2, 2, 3, -1, -5, 3, -5, -4], 5)
shrunk to ([2, 2, 3], 5): buggy -> 1, brute -> 2
```

Counting runs of equal values repairs it, but the dict version is simpler. Follow-up to expect:
return the pairs themselves (output can be Θ(n²)).

→ repo: `chapters/ch02_interview_playbook/solutions/ex05_stress_tester.py` (with the shrinker)

## 2.2 Clarifying questions checklist (input size, types, duplicates, empties, sortedness)

Ask questions whose answers **change the algorithm or the edge cases**; for the rest, state an
assumption ("I'll assume ASCII; tell me if not"). The repo tool turns a signature into an ordered
checklist and audits which categories you skipped:

```text
Signature: count_pairs(nums: list[int], target: int)
1. [size] How large can the input get? (sets the target complexity)
2. [output] What should I return when there is no valid answer?
3. [mutation] May I modify the input in place, or must it stay unchanged?
4. [empty] Can nums be empty or have one element?
5. [duplicates] Can nums contain duplicates? Do they count separately?
6. [range] Can values in nums be negative or zero?
7. [sortedness] Is nums sorted? Does output order matter?
8. [range] Can target be zero or negative? What is its maximum?
```

| Answer | How it changes the solution |
|---|---|
| n ≤ 20 vs n ≤ 10^5 | Exponential search is fine vs need O(n log n) or better |
| Input is sorted | Binary search or two pointers become available |
| Duplicates allowed | Counting logic, dedup in output, `<` vs `≤` in comparisons |
| Negatives allowed | Sliding-window "shrink when sum too big" breaks (→ §10.5) |
| May mutate input | Sort in place: avoids an O(n) copy (Timsort may still use ~n/2 scratch) |

Pitfall: a long interrogation. Three to six questions, then restate the problem.

## 2.3 Thinking aloud: communication scripts and phrases

The interviewer can only score reasoning they hear. Narrate *decisions*, not keystrokes.

| Moment | Example phrase |
|---|---|
| Restating | "So the input is…, I return…, and the tricky part seems to be…" |
| Choosing | "Sorting is O(n log n); a hash map is O(n) with extra memory. I'll take the map." |
| Before coding | "Plan: one pass, a dict of counts, look up before insert. Shall I code that?" |
| Pausing to think | "Let me take ten seconds to check the loop bounds." |
| Inviting input | "Does that assumption match what you had in mind?" |

Announced silence is fine. Narrating syntax ("now a colon") fills air without showing judgement.

## 2.4 Stating complexity before and after coding

**Before:** turn the size limit into a budget. A rough CPython rule is ~10^7 simple operations
per second (an order of magnitude, not a benchmark). The repo tool finds the costliest class that
fits in about one second:

```text
Largest class that fits in ~1 s at 10^7 simple ops/s:
  n =            10: O(n!)
  n =            20: O(2^n)
  n =           500: O(n^2)
  n =         3,000: O(n^2)
  n =       100,000: O(n log n)
  n =     1,000,000: O(n)
  n = 1,000,000,000: O(log n)
```

**After:** re-derive the cost from the code you wrote. Hidden loops count: `x in list`, slicing,
`list.pop(0)`; string `+=` in a loop may be O(n) per step (CPython often, not always, extends in
place). The *doubling test* checks it: measure at n and 2n; log₂ of the ratio approximates the
exponent. In practice you time both runs with `time.perf_counter`; the repo counts operations
so its output is deterministic:

```text
Doubling check (operation counts, n = 1000 -> 2000):
  brute pair count exponent ~ 2.0
  hash  pair count exponent ~ 1.0
```

Always give time *and* space, and say "average" for hash-based structures (→ §8.7 for
constraint reading, §22.7 for hidden costs).

## 2.5 When stuck: hints, simplifying the problem, working small cases

1. **Solve tiny cases by hand** (n = 0, 1, 2, 3) and look for the pattern in your own steps.
2. **Simplify:** drop one constraint (sortedness, duplicates, a dimension), solve that, then
   ask what the constraint breaks.
3. **Name the brute force and find repeated work.** "For each j I rescan everything before it"
   points straight at a hash map or prefix sum.
4. **Scan the toolbox:** sort? hash map? two pointers? heap? BFS? DP over prefixes?
5. **Ask for a hint, precisely:** "I have O(n²) by checking all pairs; is there a property of the
   input I should exploit?"

Restate a hint in your own words and act on it at once; ignoring it costs more than needing it.

## 2.6 Testing your own code: dry runs and edge-case walkthroughs

A **dry run** executes the code by hand on a small input, writing each variable change. The repo
tracer (`sys.settrace`) prints exactly that table so you can check your hand-trace:

```text
Dry run of count_pairs([1, 3, 2, 2], 4):
 0  L0  (call)                                 nums=[1, 3, 2, 2], target=4
 1  L1  seen: dict[int, int] = {}              seen={}
 2  L2  pairs = 0                              pairs=0
 3  L3  for x in nums:                         x=1
 4  L4  pairs += seen.get(target - x, 0)       -
 5  L5  seen[x] = seen.get(x, 0) + 1           seen={1: 1}
 6  L3  for x in nums:                         x=3
 7  L4  pairs += seen.get(target - x, 0)       pairs=1
 8  L5  seen[x] = seen.get(x, 0) + 1           seen={1: 1, 3: 1}
 9  L3  for x in nums:                         x=2
10  L4  pairs += seen.get(target - x, 0)       -
11  L5  seen[x] = seen.get(x, 0) + 1           seen={1: 1, 3: 1, 2: 1}
12  L3  for x in nums:                         -
13  L4  pairs += seen.get(target - x, 0)       pairs=2
14  L5  seen[x] = seen.get(x, 0) + 1           seen={1: 1, 3: 1, 2: 2}
15  L3  for x in nums:                         -
16  L6  return pairs                           -
result = 2
```

At step 10 the first `2` finds no partner because the dict holds only earlier values. (Step 12
shows `-` because `x` is rebound to an equal value.)

Then an **edge-case walkthrough**, varying one input at a time so a failure has one cause: empty,
single, two equal, all equal, negatives, ascending, descending, zero, and a large value. The
repo generator builds these 12 cases for a `(list[int], int)` signature and catches a tempting
"running minimum" bug in a windowed max-gap function:

```text
max_gap_buggy fails on: ['nums=empty', 'nums=ascending', 'k=zero', 'k=negative']
```

In the room: dry-run one normal example, then list edge cases aloud and trace the riskiest.

## 2.7 Time management in 45- and 60-minute rounds

Keep about five minutes at each end for introductions and your questions, and split the rest
roughly 15 / 25 / 40 / 20 % across clarify+examples, brute+optimise, code and test. The planner
rounds to whole minutes without losing any:

```text
45-minute round:
   0-5  intro             (5 min)
   5-10 clarify+examples  (5 min)
  10-19 brute+optimise    (9 min)
  19-33 code              (14 min)
  33-40 test              (7 min)
  40-45 closing           (5 min)
```

For 60 minutes the same shares give 8 / 12 / 20 / 10. The checkpoints matter more than the exact
numbers. If the optimisation has not arrived by the end of its slot, code the best idea you have
and *say* the better one: working O(n log n) code beats an unfinished O(n) sketch. If coding runs
long, stub helpers and finish the main path. Never skip testing; trace one example even with three
minutes left. For two problems in one round, plan each with half the working time.

## 2.8 Recovering from mistakes gracefully

Everyone writes bugs; the signal is how you handle them: **notice → name → fix → re-test.** "I see a problem: when `2 * x == target`, `x` pairs with itself
because I insert before I look up. Swapping these two lines fixes it; let me re-run the `[2]`
case."

| Mistake | Graceful recovery |
|---|---|
| Interviewer hints at a bug | Thank them, trace the line on the smallest failing input, fix |
| Approach fails mid-coding | Say why, reuse what you can, re-plan aloud |
| Forgot an edge case | Add the guard, then add that case to your test list |
| Wrong complexity claim | Correct it explicitly; do not hope it goes unnoticed |
| Blanked on an API | Say what it should do and write a tiny helper |

Avoid defensiveness and silent fixes.

## Interviewer's view

| Rubric area | Strong signal | Weak signal |
|---|---|---|
| Problem solving | Clarifies, compares two approaches with costs, picks with a reason | Jumps to code; one idea, no trade-off |
| Coding | Readable names, small helpers, idiomatic Python | Long single block, magic indices |
| Verification | Dry runs before claiming done, finds own bug | Says "I think it works" without tracing |
| Communication | Narrates decisions, invites input, uses hints well | Long silences or narrates syntax |

Silent, untested optimal code can score below a slower solution that was reasoned aloud and verified.

## Exercises

In `chapters/ch02_interview_playbook/` (index: `chapters/ch02_interview_playbook/README.md`).

| ID | Title | Tier | Pattern / step |
|---|---|---|---|
| ex01 | Clarifying-question checklist builder | ◆ | clarify |
| ex02 | Edge-case generator for a signature | ★ | examples, testing |
| ex03 | Complexity budget and doubling check | ★ | state complexity |
| ex04 | Dry-run tracer with `sys.settrace` | ◆ | dry runs |
| ex05 | Brute vs optimised stress tester with shrinking | ★ | optimise, test |
| ex06 | Timebox planner for 45/60-minute rounds | ○ | time management |

## Checkpoint quiz

1. Why write the brute force (step 3) even when you already see the optimal idea?
2. n ≤ 2,000. Is an O(n²) algorithm in Python acceptable? Is O(n³)?
3. In `count_pairs_fast`, what goes wrong if you insert `x` into `seen` before the lookup?
4. Why should an edge-case generator vary one parameter at a time?
5. You are 25 minutes into a 45-minute round with no optimal idea. What do you do?

<details>
<summary>Answers</summary>

1. It proves you can solve it, gives a fallback answer, and is the reference for stress tests.
2. O(n²) ≈ 4 × 10^6 steps: fine. O(n³) ≈ 8 × 10^9: far too slow.
3. `x` pairs with itself when `2 * x == target`: `[2]`, target 4 returns 1 instead of 0.
4. Each failure has a single cause, and the case count is a sum, not a product.
5. Code your best approach cleanly, test it, and say what a faster one would need; working code
   beats an unfinished sketch.

</details>

## Summary card

- **Method:** clarify → examples → brute force → optimise → code → test; move on only when the
  step's exit test is met.
- **Clarify** size, types, duplicates, empties, sortedness, output on "no answer", mutation;
  assume the rest aloud.
- **Budget:** ~10^7 simple Python ops/s; n ≤ 20 → 2^n, ≤ ~3,000 → n², ≤ 10^5 → n log n,
  10^6 → n. Re-derive the actual cost after coding.
- **Stuck:** tiny cases, drop a constraint, find repeated work, ask a precise hint.
- **Test:** dry-run a normal example, then edges one at a time; when practising, stress against
  the brute force and shrink failures.
- **Time (45 min):** 5 intro · 5 clarify · 9 design · 14 code · 7 test · 5 close.
- **Mistakes:** notice → name → fix → re-test, out loud.
