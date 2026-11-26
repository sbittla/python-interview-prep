"""
Exercise 01 — Weighted Rubric Scorer with Feedback        [Tier: ★ Core]
Chapter 47 · Pattern: rubric as data + validation · Target time: 25 min

Problem
-------
A mock is scored on a rubric: a list of (key, label, weight) criteria whose weights
sum to 100. The interviewer rates each criterion on an anchored 0-4 scale:

    0 missing · 1 weak · 2 mixed · 3 solid · 4 strong

A criterion earns weight * rating / 4 points. Implement

- ``validate_rubric(rubric)``: keys unique, weights positive ints, total exactly 100.
- ``score(rubric, ratings) -> Scorecard``: ``ratings`` maps every key to an int 0-4
  (bool is not an int here). Missing or unknown keys, or a bad rating, raise
  ValueError naming the offending keys. The scorecard holds exact totals (Fraction),
  one row per criterion, a verdict and feedback.
- Verdict: total >= 85 and every rating >= 2 -> "ready"; total >= 70 -> "close";
  otherwise "not yet". A total >= 85 with a criterion rated 0 or 1 is "close", and the
  verdict names the floor criteria: one collapsed criterion is a real risk even when the
  sum looks high. (These bands are this book's practice thresholds, not any company's.)
- Feedback: up to three criteria that lost the most points (ties: rubric order),
  skipping criteria that lost nothing, each with a concrete next step.

Both rubrics from §47.3 and §47.4 are defined below with the outline's exact weights.

Examples
--------
>>> card = score(CODING_RUBRIC, {"clarifying": 4, "approach": 3, "correctness": 3,
...     "code_quality": 3, "complexity": 2, "testing": 2, "communication": 4})
>>> card.total, card.verdict
(Fraction(75, 1), 'close')

Constraints
-----------
- Exact arithmetic: points are multiples of 1/4, so print them with two decimals.
- Rubric order is the display order.

Approach ladder
---------------
1. Brute force — average the ratings: ignores weights, so 4/4 on communication
   offsets 0/4 on correctness. Wrong by design.
2. Improved   — weighted float sum: right numbers, but no validation (a typo key
   silently scores 0) and no actionable output.
3. Optimal    — validated weighted sum with Fraction, a floor rule and ranked
   feedback. O(C log C) for C criteria (the feedback sort).

Follow-ups
----------
- Calibrate two interviewers: score the same recording, compare per-criterion gaps.
- Half-point ratings: allow Fraction ratings in steps of 1/2.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

CODING_RUBRIC = (
    ("clarifying", "Clarifying requirements and constraints", 10),
    ("approach", "Approach and trade-off reasoning", 20),
    ("correctness", "Correctness on tests and edge cases", 25),
    ("code_quality", "Code quality and Pythonic style", 15),
    ("complexity", "Complexity analysis", 10),
    ("testing", "Testing and debugging", 10),
    ("communication", "Communication", 10),
)
AI_RUBRIC = (
    ("decomposition", "Problem decomposition and planning", 20),
    ("prompting", "Prompting and context management", 15),
    ("verifying", "Verifying and critiquing AI output", 30),
    ("integration", "Integration and code quality", 20),
    ("ownership", "Explaining and owning the final code", 15),
)
SCALE = {0: "missing", 1: "weak", 2: "mixed", 3: "solid", 4: "strong"}
NEXT_STEP = {
    "clarifying": "ask size, duplicates, empties and output-on-failure before coding (see §2.2)",
    "approach": "say brute force and its cost, then one better idea with its trade-off (see §2.1)",
    "correctness": "stress-test against brute force on seeded small inputs (see §2.1)",
    "code_quality": "name helpers, drop dead branches, use idioms you can defend (see §31.8)",
    "complexity": "state time and space before coding and re-derive them after (see §2.4)",
    "testing": "dry-run one example and add a failing case before you say done (see §2.6)",
    "communication": "narrate decisions, not keystrokes; invite input at checkpoints (see §2.3)",
    "decomposition": "split the task into testable steps before the first prompt (see §46.2)",
    "prompting": "give spec, signature, constraints and what not to change (see §46.2)",
    "verifying": "write the oracle first and probe edges on every generated diff (see §46.4)",
    "integration": "review the diff like a PR: names, complexity, error paths (see §46.5)",
    "ownership": "explain complexity, alternative and evidence for each kept line (see §46.6)",
}


@dataclass(frozen=True)
class Row:
    key: str
    label: str
    weight: int
    rating: int
    points: Fraction
    lost: Fraction


@dataclass(frozen=True)
class Scorecard:
    total: Fraction
    rows: tuple[Row, ...]
    verdict: str
    feedback: tuple[str, ...]


def validate_rubric(rubric) -> None:
    keys = [k for k, _, _ in rubric]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate criterion keys")
    for key, _, w in rubric:
        if isinstance(w, bool) or not isinstance(w, int) or w <= 0:
            raise ValueError(f"weight for {key!r} must be a positive int")
    total = sum(w for _, _, w in rubric)
    if total != 100:
        raise ValueError(f"weights sum to {total}, expected 100")


def score(rubric, ratings: dict[str, int]) -> Scorecard:
    validate_rubric(rubric)
    keys = [k for k, _, _ in rubric]
    missing = [k for k in keys if k not in ratings]
    unknown = sorted(set(ratings) - set(keys))
    if missing or unknown:
        raise ValueError(f"missing={missing} unknown={unknown}")
    bad = [k for k in keys if isinstance(ratings[k], bool)
           or not isinstance(ratings[k], int) or ratings[k] not in SCALE]
    if bad:
        raise ValueError(f"ratings must be ints 0-4: {bad}")

    rows = tuple(Row(k, label, w, ratings[k], Fraction(w * ratings[k], 4),
                     Fraction(w * (4 - ratings[k]), 4)) for k, label, w in rubric)
    total = sum((r.points for r in rows), Fraction(0))
    floors = [r.label for r in rows if r.rating <= 1]
    if total >= 85 and not floors:
        verdict = "ready"
    elif total >= 85:
        verdict = "close (floor: " + "; ".join(floors) + ")"
    elif total >= 70:
        verdict = "close"
    else:
        verdict = "not yet"
    order = sorted((i for i, r in enumerate(rows) if r.lost > 0),
                   key=lambda i: (-rows[i].lost, i))[:3]
    feedback = tuple(f"{rows[i].label}: -{float(rows[i].lost):.2f} -> {NEXT_STEP[rows[i].key]}"
                     for i in order)
    return Scorecard(total, rows, verdict, feedback)


def report(card: Scorecard) -> str:
    lines = [f"{'criterion':<40} {'wt':>3} {'rating':<10} {'points':>6}"]
    for r in card.rows:
        lines.append(f"{r.label:<40} {r.weight:>3} {r.rating} {SCALE[r.rating]:<8} "
                     f"{float(r.points):>6.2f}")
    lines.append(f"{'total':<40} {100:>3} {'':<10} {float(card.total):>6.2f}  -> {card.verdict}")
    lines += ["feedback:"] + [f"  {i}. {f}" for i, f in enumerate(card.feedback, 1)]
    return "\n".join(lines)


def main() -> None:
    print("Mock S2, coding rubric (worked example):")
    s2 = {"clarifying": 4, "approach": 3, "correctness": 3, "code_quality": 3,
          "complexity": 2, "testing": 2, "communication": 4}
    print(report(score(CODING_RUBRIC, s2)))

    print("\nHigh total, one collapsed criterion:")
    floor = {"clarifying": 4, "approach": 4, "correctness": 4, "code_quality": 4,
             "complexity": 4, "testing": 1, "communication": 4}
    card = score(CODING_RUBRIC, floor)
    print(f"total={float(card.total):.2f} verdict={card.verdict}")

    print("\nMock L3, AI-assisted rubric:")
    l3 = {"decomposition": 3, "prompting": 3, "verifying": 2, "integration": 3, "ownership": 2}
    card = score(AI_RUBRIC, l3)
    print(f"total={float(card.total):.2f} verdict={card.verdict}")
    print("top fix:", card.feedback[0])

    print("\nValidation:")
    for bad in ({**s2, "complexty": 3}, {**s2, "testing": 5}, {**s2, "testing": True}):
        try:
            score(CODING_RUBRIC, bad)
        except ValueError as exc:
            print("  ValueError:", exc)


if __name__ == "__main__":
    main()
