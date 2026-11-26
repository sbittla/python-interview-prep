# Chapter 1. The Interview Landscape

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 1–2 hours · **Prerequisites:** none

Processes differ by company, team and year: this chapter gives general patterns and a way to
verify *your* loop.

**Learning objectives**

- Name the stages of a typical loop and what each filters for.
- Prepare for whiteboard, shared-editor, online-judge, take-home and pairing formats.
- Verify a round's AI policy from first-party, written, recent evidence.
- Contrast SWE, Data/ML and GenAI/LLM loops; pick a track and plan.

> **Recognise the round**
>
> | The recruiter says… | Probably | Prepare |
> |---|---|---|
> | "Complete this link within a week" | Online assessment | stdin/stdout, time limits (§1.3) |
> | "Live coding with an engineer" | Coding round | Talk while you type |
> | "Work in our codebase together" | Pairing / practical | Read code fast, write tests |

## 1.1 Interview loop anatomy: screen, online assessment, coding, practical, design, behavioural

Most loops are a funnel: cheap, standardised filters first, expensive human rounds later.

| Stage | What it filters for |
|---|---|
| Recruiter screen | Role fit, level, logistics; *your chance to ask about the loop* |
| Online assessment (OA) | Correct, fast-enough code written alone against hidden tests |
| Technical phone screen | One or two problems with a live interviewer |
| Coding rounds | Problem solving, clean code, testing, communication |
| Practical | Realistic tasks: parse logs, fix a bug, extend code (→ §30.1, §31.4) |
| Design | System or low-level design (→ §29.1, §43.1) |
| Behavioural | Ownership, collaboration, handling conflict and failure |

Feedback from all rounds is usually combined afterwards, so one weak round is not automatically
fatal. Loops vary (some swap the OA for a take-home): ask the recruiter for the list of rounds
and budget prep time in proportion (§1.7).

## 1.2 Round formats: whiteboard, shared editor, online judge, take-home, pair programming

| Format | Code runs? | What changes | Practise by |
|---|---|---|---|
| Whiteboard | No | No autocomplete or undo | Paper; tracing variables in a table (→ §2.6) |
| Shared editor | Sometimes | Every keystroke watched | A plain editor, linting off |
| Online judge | Yes, hidden tests | Exact I/O, time limits, no credit for ideas | Timed sets with stdin parsing (→ §4.3) |
| Take-home | Yes, your machine | Graded on structure, tests, README | One small project end to end (→ §32.1) |
| Pair programming | Yes | Collaboration scored; unfamiliar code | Extending other people's code (→ §32.4) |

Pitfall: practising only on a judge trains guess-and-resubmit; a whiteboard gives no red/green
signal, so build Chapter 2's dry-run habit.

## 1.3 Platforms and environments (online judges, CoderPad-style editors, notebooks)

- **Online judges** take either a full program (stdin → stdout) or a function with a fixed
  signature. Check the Python version (→ §4.2) and the time limit first. Hidden tests often
  include large inputs, so an O(n²) solution that passes the examples can still time out (→ §8.7).
- **Collaborative editors (CoderPad-style)** share one buffer, sometimes with a Run button. Ask
  whether you may run code.
- **Notebooks** appear mostly in Data/ML rounds. Hidden state is the trap: a cell may depend on
  a variable you have since deleted. Restart and run all before "done"; fix seeds; print shapes.

## 1.4 AI-free vs AI-allowed rounds — how to verify a company's current policy

Some rounds forbid AI assistants; others allow them and grade how you direct and check the tool
(→ §46.1, rubric §47.4). Policies differ by company, team and round, and change, so hearsay is a
lead, not a fact.

**Verification rule:** *verified* means first-party, written and recent: a recruiter email or
written interview instructions (the exercise uses 30 days). A recruiter's phone answer is
*likely*; forum and blog posts stay *unverified* however new. Ask per round, since one loop can
mix AI-free coding with an AI-allowed practical; until verified, assume AI-free. The repo
checker encodes the rule, grouping by round once (O(N), not a rescan per round):

```python
from collections import defaultdict, namedtuple
from datetime import date

Evidence = namedtuple("Evidence", "round stance source on")
TRUST = {"recruiter_email": 3, "interviewer_guide": 3, "recruiter_call": 2,
         "candidate_forum": 1, "old_blog_post": 1}

def assess(evidence, today, max_age_days=30):
    by_round = defaultdict(list)
    for ev in evidence:
        by_round[ev.round].append(ev)
    result = {}
    for rnd in sorted(by_round):
        fresh = [e for e in by_round[rnd] if 0 <= (today - e.on).days <= max_age_days]
        written = [e for e in fresh if TRUST[e.source] == 3]
        verbal = [e for e in fresh if TRUST[e.source] == 2]
        if written:
            stances = {e.stance for e in written}
            result[rnd] = ("verified", stances.pop()) if len(stances) == 1 else ("conflicting", None)
        elif verbal:
            result[rnd] = ("likely", max(verbal, key=lambda e: e.on).stance)
        else:
            result[rnd] = ("unverified", None)   # forum posts never verify anything
    return result

evidence = [
    Evidence("coding", "forbidden", "recruiter_email", date(2026, 11, 10)),
    Evidence("coding", "allowed", "candidate_forum", date(2026, 11, 15)),
    Evidence("practical", "partial", "recruiter_call", date(2026, 11, 16)),
    Evidence("take_home", "allowed", "recruiter_email", date(2026, 6, 1)),   # stale
]
for rnd, (status, stance) in assess(evidence, date(2026, 11, 18)).items():
    print(f"{rnd:<10} {status:<11} {stance}")
```

```text
coding     verified    forbidden
practical  likely      partial
take_home  unverified  None
```

The newer forum post does not override the email; the June email is stale.
The repo version also drafts a question for each round that is not verified.

→ repo: `chapters/ch01_interview_landscape/solutions/ex04_ai_policy_checker.py`

## 1.5 What SWE, Data/ML and GenAI/LLM loops test differently

All three usually keep a general coding round; the rest follows the job.

| | SWE (S) | Data / ML (M) | GenAI / LLM (L) |
|---|---|---|---|
| Practical | Logs, bug fixing, LLD (→ §29.2, §30.1) | pandas / SQL analysis (→ §34.4, §34.9) | RAG, tool calling, retries (→ §40.1, §41.1, §42.3) |
| From scratch | LRU cache, rate limiter | Metrics, k-means (→ §35.7, §36.4) | Attention, decoding, BPE (→ §39.1, §39.8, §38.2) |
| Design | System / low-level design | Experiment design (→ §35.6) | LLM system design (→ §43.2) |
| Concepts | Python internals, concurrency | Statistics, leakage (→ §35.11) | Embeddings, evaluation (→ §40.9) |

Mixed roles get mixed loops. ex07 counts a job description's track keywords (words and phrases
like "system design") and lists rounds for each track scoring at least half the winner. An LLM
role that also mentions PyTorch and REST APIs:

```text
LLM engineer: track=L counts={'S': 2, 'M': 1, 'L': 7}
    rounds: ['behavioural', 'coding', 'llm_coding', 'llm_system_design']
```

Wrong but tempting: `text.count("ai")`, which also counts the "ai" in "maintain". Tokenise first.

→ repo: `chapters/ch01_interview_landscape/solutions/ex07_job_description_classifier.py`

## 1.6 How you are scored: signals interviewers look for

Interviewers rate *signals* and back each with evidence from the session. Names vary; the
signals recur:

| Signal | Evidence written down |
|---|---|
| Problem solving | Clarified, compared approaches, few hints needed |
| Coding | Correct, readable, idiomatic |
| Verification | Traced an example, found own bugs, covered edge cases |
| Complexity | Stated time and space, before and after coding |
| Communication | Explained decisions, used hints well |

This book's coding rubric (§47.3) weights these out of 100. Silent optimal code leaves rows
without evidence, and many rubrics let one very low rating on a heavy signal outweigh a good
average. The repo scorer models that veto (weights illustrative):

```text
coding     {'problem_solving': 4, 'coding': 1, 'communication': 4, 'testing': 4} -> {'score': 3.1, 'decision': 'no hire', 'weakest': 'coding'}
```

A 3.1 average is otherwise a "hire". `weakest` is your next practice target.

→ repo: `chapters/ch01_interview_landscape/solutions/ex05_signal_scorer.py`

## 1.7 Choosing your track and study plan

Choose the track for the job you are interviewing for:

| Track | Target roles | Parts |
|---|---|---|
| **S** Software Engineering | Backend, platform, general SWE | 0, I–V, VIII |
| **M** Data / ML | Data scientist, ML engineer | 0, I–III, V, VI, VIII (IV optional) |
| **L** GenAI / LLM | AI / LLM engineer | 0, I–V, VII, VIII (VI optional) |

DSA (Parts II–III) is in every track; Chapter 3's diagnostic decides whether you skim Part I.

| Plan | For | Shape |
|---|---|---|
| Standard, 8 wk × 10–12 h | Most readers | DSA weeks 1–5, track 6–7, mocks 8 |
| Crash, 4 wk × ~15 h | Experienced, interview soon | Patterns; trees/graphs; DP + track; mocks |
| Foundations, 12 wk × 6–8 h | Beginners, career changers | 4 weeks Python, then the 8-week plan |
| Role add-on, 6 wk | Strong DSA, moving to ML/LLM | Parts VI–VII, Part V, two mocks |

Inside a plan, split hours by preparation weight × number of rounds. Rounding each share
separately drifts (three equal shares of 10 hours round to 3 + 3 + 3 = 9). The
*largest-remainder* method floors every share, then gives leftover hours to the largest
fractional parts, so the total is exact; O(T log T) for T round types. ex02, for a phone screen,
two coding rounds, design and behavioural:

```text
SWE loop, 40 h: {'behavioural': 2, 'coding': 24, 'phone_screen': 5, 'system_design': 9}
```

→ repo: `chapters/ch01_interview_landscape/solutions/ex02_loop_planner.py`,
`chapters/ch01_interview_landscape/solutions/ex06_study_plan_builder.py`

## Interviewer's view

| Area | Strong | Weak |
|---|---|---|
| Preparation | Knew the rounds and formats in advance | Surprised by the format |
| AI policy | Confirmed in writing per round | Assumed from a forum post |
| Signals | Evidence for every rubric row | Only "got the answer" |
| Fit | Prepared the role's SQL / ML / LLM rounds | Generic DSA only |

## Exercises

In `chapters/ch01_interview_landscape/` (index: `chapters/ch01_interview_landscape/README.md`).

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Track recommender | ★ | rule table, set intersection |
| ex02 | Interview-loop prep-hours planner | ★ | largest-remainder allocation |
| ex03 | Round-format checklist generator | ★ | ordered de-duplication |
| ex04 | AI-policy evidence checker | ★ | group-by + rules on dated records |
| ex05 | Interview signal scorer | ★ | weighted average + veto |
| ex06 | Study-plan builder | ★ | decision table |
| ex07 | Job-description classifier | ◆ | Counter over unigrams and bigrams |

## Checkpoint quiz

1. Why does judge-only practice underprepare you for a whiteboard round?
2. A recruiter's call last week: AI allowed in the practical. A forum post yesterday: banned.
   Status, and next step?
3. How can one round's coding rating sink a good average?
4. A backend job description mentions pandas and SQL twice. What do you add to your prep?
5. Why can rounding each share of a study budget separately lose an hour?

<details>
<summary>Answers</summary>

1. No execution feedback or autocomplete, and communication is scored.
2. "Likely allowed"; the forum post does not count. Ask for written confirmation; practise both ways.
3. A very low rating on a heavily weighted signal can veto the decision.
4. A SQL / pandas analysis round.
5. Each `round()` errs independently and the errors need not cancel; largest remainder fixes it.

</details>

## Summary card

- **Loop:** screen → OA or phone screen → coding, practical, design, behavioural → combined
  decision. Ask for the exact list.
- **Formats:** whiteboard (no execution), shared editor (watched), judge (hidden tests, exact
  I/O), take-home (structure, README), pairing (collaboration).
- **AI policy:** verified = first-party, written, recent, per round; else assume AI-free and ask.
- **Tracks:** S, M, L share Parts 0–III; the job description adds rounds.
- **Scoring:** evidence for every signal; one low, heavy signal can veto.
- **Plan:** pick by weeks × hours; split hours with largest remainder.
