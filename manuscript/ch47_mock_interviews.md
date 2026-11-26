# Chapter 47. Mock Interviews with Rubrics

★ Core · Tracks S M L · Study time ≈ 4 h plus the mocks · Prerequisites: Chapter 2, Chapter 46, and the chapters each mock draws on

A mock turns practice into a measurement: timed, watched and scored by criterion, so it shows
*what* to fix. Here are ten mocks, two rubrics, and repo tools to schedule, log, score and track them.

**Learning objectives**

- Run a mock solo, with a peer, or recorded, with real timing and an event log.
- Pick from ten mocks across the SWE, Data/ML and GenAI/LLM tracks, and know what strong looks like in each.
- Score a round on the weighted §47.3 or §47.4 rubric with anchored 0–4 ratings.
- Turn a series of scores into a trend, your weakest criteria and next week's drills.

> **Recognise the moment**
>
> | Situation | Go to |
> |---|---|
> | Problems solve fine at home but rounds go badly | §47.1: add a clock and a watcher |
> | "Which mock next?" | §47.2 and the seeded rotation |
> | Score the round you just ran | §47.3 (AI-free) or §47.4 (AI allowed) |
> | Five mocks in and stuck at the same score | §47.5 |

## 47.1 Running a mock: solo, peer, recorded

| Mode | What it misses | Compensate by |
|---|---|---|
| Solo | nobody hears your silences; you go easy on yourself | think aloud anyway; log events as you go |
| Peer | peers hint too early or forget to probe | the generated script fixes cue times and hint order |
| Recorded | live pressure | review within 24 h; log and score from the recording |

**Protocol.** Pick from the rotation, not by mood. See the problem only when the clock starts,
keep the time split, never pause, and use only what the round allows. Score within ten minutes,
then debrief for five.

**Log events, not impressions.** Write one line per event, `MM:SS EVENT [detail]`. The events are
`ASK`, `SAY`, `PLAN`, `COMPLEXITY`, `CODE_START`, `RUN p/t`, `HINT`, `TEST_ADDED` and `BUG_FOUND`,
between `START` and `END`. The analyser validates the log (line-numbered
errors, no time going backwards) and emits flags tagged with the rubric criterion they support.
Two scripted logs of the same problem:

```text
s2_candidate_a: 20:45 total, first question 01:05, code 06:40, first green 16:10
  runs=2 hints=0 own tests=2 longest gap=02:10
  no flags
s2_candidate_b: 21:30 total, first question -, code 00:50, first green 17:20
  runs=3 hints=2 own tests=0 longest gap=05:40
  flag [clarifying] coded before asking any question
  flag [approach] no approach stated before coding
  flag [approach] 2 hints used
  flag [complexity] complexity not stated before coding
  flag [testing] no tests of your own added
  flag [communication] silent 05:40 from 00:50
```

Both passed at about minute 17; only the log shows B coded blind with two hints. Flags are evidence,
not a score.
→ repo: `chapters/ch47_mock_interviews/solutions/ex03_session_log_analyser.py`

**Peer script.** For a peer who has never interviewed, the generator prints one page per mock:
the files only the interviewer opens, a prompt to read aloud, cue times with a checkpoint at 40 %
of each problem (minute 13 for S2's first problem), hints to give one at a time after about three
minutes stuck, the follow-ups, and a scoring sheet for the right rubric.
→ repo: `chapters/ch47_mock_interviews/solutions/ex05_peer_script.py`

## 47.2 Ten mock interviews (SWE ×4, Data/ML ×3, GenAI/LLM ×3)

Each mock opens and closes with 5 minutes; statements, tests and solutions sit behind each
cross-reference. Roles are generic formats, not any company's loop.

| Id | Role | Min | Split (min) | Problems |
|---|---|---|---|---|
| S1 | SWE coding screen | 45 | 5 · 13 · 22 · 5 | Ch. 45 #050 merge sorted lists; §10.5 longest substring without repeats |
| S2 | SWE onsite coding | 60 | 5 · 22 · 28 · 5 | §15.4 top-k frequent words; §16.8 course schedule |
| S3 | SWE design-style | 60 | 5 · 8 API · 22 · 20 · 5 | §29.2 LRU cache; §29.5 rate limiter |
| S4 | SWE algorithms | 45 | 5 · 25 · 10 · 5 | §19.9 word break; §19.6 coin change |
| M1 | Data scientist / analytics | 60 | 5 · 22 · 28 · 5 | §30.9 top-N per group (SQL); §34.9 cohort retention |
| M2 | ML fundamentals | 45 | 5 · 20 · 15 · 5 | §35.7 ROC-AUC with ties; §35.11 leakage-free CV |
| M3 | ML engineer | 60 | 5 · 25 · 25 · 5 | §36.2 logistic regression; §37.9 broken training loop |
| L1 | LLM model internals | 60 | 5 · 20 · 10 · 20 · 5 | §39.1 attention; §39.3 masks; §39.7 KV cache |
| L2 | LLM retrieval | 60 | 5 · 25 · 15 · 10 · 5 | §40.3 BM25; §40.5 RRF; §40.11 eval harness |
| L3 | LLM app, AI allowed | 75 | 5 · 10 plan · 25 · 20 · 10 walk · 5 | §41.1 function-calling loop; §41.3 tool errors |

Strong signals and follow-ups (the complete lists, prompts and hints are in the catalogue and
the peer script):

| Id | Strong looks like | Follow-ups |
|---|---|---|
| S1 | dummy head, stable ties, O(n + m); last-seen index window, O(n); traces `"abba"` and `""` | merge k lists (→ §15.6); ≤ k distinct (→ §10.6) |
| S2 | compares sort O(n log n) with a size-k heap O(n log k); alphabetical tie-break right *inside a min-heap*; Kahn, a cycle = order shorter than n | word stream (→ §15.3); return one cycle |
| S3 | API and O(1) targets first (→ §29.1); dict + linked list or `OrderedDict`, trade-off stated; injected clock | TTL; thread safety (→ §28.2); token bucket vs sliding log |
| S4 | states state/transition/base (→ §19.3); memo → bottom-up; loop order separates combinations from orderings | all splits (exponential); one-row memory (→ §19.15) |
| M1 | asks how ties rank, picks `ROW_NUMBER`/`RANK`/`DENSE_RANK` deliberately; defines *active* first; hand-checks 3 users | weekly cohorts; cohort table in SQL |
| M2 | AUC = P(pos > neg), ties half; O(P·N) pairs → O(n log n) ranks, cross-checked; feature selection inside folds | PR-AUC at 1 % positives (→ §35.7); calibration |
| M3 | overflow-safe sigmoid + gradient check (→ §35.2); O(n·d) per epoch; symptom → probe → one-line fix | L2 (→ §36.10); NaN at step 40 |
| L1 | shapes aloud; why √d_k; no NaN on a fully masked row; cache tested against full recompute | KV-cache memory (→ §39.7); grouped-query attention |
| L2 | names the IDF variant; scores only query-term postings, ties by id; Recall@K and MRR before tuning | chunk size (→ §40.2); reranker (→ §40.6); ANN (→ §40.7) |
| L3 | plan and stop conditions before prompting; tests with the mock model first; retries only transient errors; explains each line (→ §46.2–46.6) | schema output (→ §41.4); fallback model (→ §43.3) |

**Scheduling.** Each track has its own seeded shuffle; sessions cycle through the listed tracks;
an exhausted queue reshuffles without back-to-back repeats:

```text
SWE-track loop, 8 sessions, 2 per week (seed 7):
  week 1: ['S4', 'S2']  (105 min)
  week 2: ['M2', 'S1']  (90 min)
  week 3: ['S3', 'M1']  (120 min)
  week 4: ['S2', 'S4']  (105 min)
```

The loader checks that segments sum to each mock's length and that every referenced problem
file exists.
→ repo: `chapters/ch47_mock_interviews/solutions/ex02_mock_planner.py`, data in
`chapters/ch47_mock_interviews/data/mocks.json`

## 47.3 Standard coding-round rubric

| Criterion | Weight | 4 = strong | 1 = weak |
|---|---|---|---|
| Clarifying requirements and constraints | 10 | asks what changes the algorithm; restates | codes from the first sentence |
| Approach and trade-off reasoning | 20 | brute force + cost, a better idea, a reason | one idea, no costs |
| Correctness on tests and edge cases | 25 | passes, edge cases included | fails examples or empty input |
| Code quality and Pythonic style | 15 | clear names, small helpers, defensible idioms | one long block, magic indices |
| Complexity analysis | 10 | time and space right, before and after | wrong or missing |
| Testing and debugging | 10 | dry run, own edge cases, finds own bug | "I think it works" |
| Communication | 10 | narrates decisions, uses hints well | long silences |
| **Total** | **100** | | |

Rate each criterion 0–4: 0 missing, 1 weak, 2 mixed, 3 solid, 4 strong. A criterion earns
weight × rating / 4 points, so totals are exact multiples of ¼. These are this book's practice
bands, not any company's bar: **ready** ≥ 85 with no rating below 2; **close** ≥ 70; **not yet**
otherwise. The floor rule exists because one collapsed criterion sinks a round: 92.5 with testing
rated 1 reports `close (floor: Testing and debugging)`.

**Worked scoring (S2).** Clarified well (4), talked throughout (4), proposed only the heap with no
comparison (approach 3), tie-break failed a hidden test until traced (correctness 3), called the
counter O(1) space (complexity 2), wrote edge cases only after a hint (testing 2):

```python
from ex01_rubric_scorer import CODING_RUBRIC, report, score

ratings = {"clarifying": 4, "approach": 3, "correctness": 3, "code_quality": 3,
           "complexity": 2, "testing": 2, "communication": 4}
print(report(score(CODING_RUBRIC, ratings)))
```

```text
criterion                                 wt rating     points
Clarifying requirements and constraints   10 4 strong    10.00
Approach and trade-off reasoning          20 3 solid     15.00
Correctness on tests and edge cases       25 3 solid     18.75
Code quality and Pythonic style           15 3 solid     11.25
Complexity analysis                       10 2 mixed      5.00
Testing and debugging                     10 2 mixed      5.00
Communication                             10 4 strong    10.00
total                                    100             75.00  -> close
feedback:
  1. Correctness on tests and edge cases: -6.25 -> stress-test against brute force on seeded small inputs (see §2.1)
  2. Approach and trade-off reasoning: -5.00 -> say brute force and its cost, then one better idea with its trade-off (see §2.1)
  3. Complexity analysis: -5.00 -> state time and space before coding and re-derive them after (see §2.4)
```

Feedback is ranked by **points lost**: a 3 on correctness (−6.25) outranks a 2 on complexity
(−5.00); ties keep rubric order. The scorer uses `Fraction`, checks the weights sum to 100, and
rejects missing or unknown keys (a typo like `complexty` cannot score 0 silently) and `True`
(`isinstance(True, int)` holds).
→ repo: `chapters/ch47_mock_interviews/solutions/ex01_rubric_scorer.py`

## 47.4 AI-assisted round rubric

| Criterion | Weight | 4 = strong | 1 = weak |
|---|---|---|---|
| Problem decomposition and planning | 20 | testable steps and stop conditions first | one giant prompt |
| Prompting and context management | 15 | spec, signature, constraints, what not to change | "write an agent" |
| Verifying and critiquing AI output | 30 | own tests first, probes edges, finds the bug | "the examples pass" |
| Integration and code quality | 20 | reviews the diff like a PR | pastes unread code |
| Explaining and owning the final code | 15 | defends each line: cost, alternative, evidence | "the AI chose that" |
| **Total** | **100** | | |

Verification carries 30 points because it is what an AI-allowed round exists to test (→ §46.1).
L3 rated 3 · 3 · 2 · 3 · 2 gives `total=63.75 verdict=not yet`, and the top fix is
`Verifying and critiquing AI output: -15.00`. That one rating of 2 costs twice what any other
criterion does. The same bands and floor rule apply.

## 47.5 Self-review and turning scores into a study plan

**Within 24 hours,** re-rate each criterion from the log or recording; discuss first any criterion
where you and your peer differ by two or more. Write one concrete fix per criterion that lost five
or more points ("state the counter's space", not "get better at complexity").

**Across mocks,** the tracker scores each row of `data/scores.csv` with the ex01 scorer. It reports
the least-squares trend, and the weakest criteria by **mean points lost over the last three mocks**:
fixed problems drop out, and heavier criteria count more. Excerpt:

```text
  trend: +7.43 points per mock
  weak: correctness   avg lost 4.17 (last 3)
  weak: testing       avg lost 4.17 (last 3)
...
Study plan (coding):
  correctness (avg -4.17 pts): stress-test against brute force on seeded small inputs (see §2.1); retake S4
  testing (avg -4.17 pts): dry-run one example and add a failing case before you say done (see §2.6); retake S4
```

The slope uses every mock, so one good day is not a trend. The retake is the mock in the window
with the lowest rating on that criterion; on a tie, the most recent one.
→ repo: `chapters/ch47_mock_interviews/solutions/ex04_progress_tracker.py`

**Rules for the plan.**

1. Next week's drills target the two weakest criteria and nothing else.
2. Retake a mock after a week at the earliest, so you aren't replaying a memorised answer.
3. A track is done after **ready** on two *different* mocks in a row.
4. Flat for three mocks? Change the drill, not the mock count: the gap is usually a habit.
5. Carry the weakest criteria into the final repair plan (→ §48.1).

## Interviewer's view

- Rewarded: clarifying first, a costed comparison, own tests, a found bug, narrated decisions, hints used at once.
- Penalised: fast silent code, defending a bug, "I think it works", and, with AI allowed, code you cannot explain.

## Exercises

Index: `chapters/ch47_mock_interviews/README.md`.

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Weighted rubric scorer with feedback | ★ | rubric as data + validation |
| 02 | Mock catalogue, time boxes, seeded rotation | ◆ | round-robin over shuffled queues |
| 03 | Mock session log analyser | ★ | parse, validate, single-pass metrics |
| 04 | Progress tracker and study plan | ◆ | least squares + ranked deficits |
| 05 | Peer-interviewer script generator | ○ | template from validated data |

## Checkpoint quiz

1. Why rank feedback by points lost rather than by rating?
2. A round totals 92.5 with testing rated 1. What is the verdict?
3. Why are weak criteria taken from a recent window, but the trend from all mocks?
4. When does the S2 script first offer a hint for problem A?
5. Why does verification carry 30 of 100 points in §47.4?

<details><summary>Answers</summary>

1. Weights differ: a 3 on correctness (−6.25) costs more than a 2 on complexity (−5.00).
2. Close (floor: testing). One collapsed criterion is a risk however high the sum is.
3. Weakness should reflect current habits; a trend needs every point so one outlier cannot dominate.
4. At the 40 % checkpoint (minute 13), and only after about three minutes stuck.
5. Directing and checking generated code is what the round is designed to test (→ §46.1).
</details>

## Summary card

- A mock is a clock, a watcher, a log and a rubric. Run it solo, with a peer or recorded, and score within 10 minutes.
- Log `MM:SS EVENT` lines. Flags are evidence: questions before code, a plan, complexity, own tests, silences.
- Ten mocks (S1–S4, M1–M3, L1–L3) reuse chapter and Ch. 45 problems. Rotate them with a seed.
- Weights: coding rubric 10/20/25/15/10/10/10; AI rubric 20/15/30/20/15. Rate 0–4; points = w × r / 4.
- Bands: ready ≥ 85 with no rating below 2; close ≥ 70; otherwise not yet.
- Plan: two weakest criteria by mean points lost over the last 3, targeted drills, retake after a week.
