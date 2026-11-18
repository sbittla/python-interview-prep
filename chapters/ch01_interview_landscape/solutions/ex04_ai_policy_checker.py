"""
Exercise 04 — AI-Policy Evidence Checker                          [Tier: ★ Core]
Chapter 01 · Pattern: group-by + rule evaluation over dated records · Target time: 30 min

Problem
-------
Whether AI assistants are allowed in a round varies by company, by team and even by round, and
policies change. Before an interview you collect evidence about the policy for each round:

    Evidence(round="coding", stance="forbidden", source="recruiter_email", on=date(2026, 11, 2))

`stance` is "allowed", "forbidden" or "partial" (e.g. docs only). `source` is one of SOURCE_TRUST:
"interviewer_guide" and "recruiter_email" are written, first-party statements (trust 3);
"recruiter_call" is first-party but verbal (trust 2); "candidate_forum" and "old_blog_post"
are second-hand (trust 1).

Write `assess(evidence, today, max_age_days=30)` returning {round: (status, stance_or_None)}:
- Only evidence no older than max_age_days counts as *fresh*.
- If any fresh trust-3 evidence exists: status "verified" when all fresh trust-3 stances agree
  (stance = that stance), otherwise "conflicting" (stance None).
- Else if any fresh trust-2 evidence exists: "likely" with the most recent trust-2 stance.
- Else: "unverified" (stance None) — even if a forum post says something.
Rounds are returned in sorted order.

`questions_to_ask(assessment)` returns a sorted list of follow-up questions, one per round that
is not "verified".

Examples
--------
See main(); the demo uses today = 2026-11-18.

Constraints
-----------
- Never treat second-hand evidence as verified, however recent.
- Dates are datetime.date objects; no wall-clock reads (deterministic).

Approach ladder
---------------
1. Brute force — for each round, rescan the whole evidence list per rule: O(R * N).
2. Optimal    — group evidence by round once (dict of lists), then apply the rules: O(N).

Hints
-----
- collections.defaultdict(list) to group by round.
- (today - ev.on).days gives the age in days.

Follow-ups
----------
- How would you represent "allowed for documentation lookup only"?
- What would you change if the evidence came from several recruiters who disagree?
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

SOURCE_TRUST = {
    "interviewer_guide": 3,
    "recruiter_email": 3,
    "recruiter_call": 2,
    "candidate_forum": 1,
    "old_blog_post": 1,
}


@dataclass(frozen=True)
class Evidence:
    round: str
    stance: str
    source: str
    on: date


def assess(evidence: list[Evidence], today: date, max_age_days: int = 30) -> dict:
    """{round: (status, stance)} following the rules in the docstring."""
    by_round: dict[str, list[Evidence]] = defaultdict(list)
    for ev in evidence:
        by_round[ev.round].append(ev)
    result = {}
    for rnd in sorted(by_round):
        fresh = [e for e in by_round[rnd] if 0 <= (today - e.on).days <= max_age_days]
        written = [e for e in fresh if SOURCE_TRUST[e.source] == 3]
        verbal = [e for e in fresh if SOURCE_TRUST[e.source] == 2]
        if written:
            stances = {e.stance for e in written}
            result[rnd] = ("verified", stances.pop()) if len(stances) == 1 else ("conflicting", None)
        elif verbal:
            latest = max(verbal, key=lambda e: e.on)
            result[rnd] = ("likely", latest.stance)
        else:
            result[rnd] = ("unverified", None)
    return result


def questions_to_ask(assessment: dict) -> list[str]:
    """One follow-up question per round that is not verified."""
    templates = {
        "conflicting": "I have received different answers about AI tools in the {r} round. "
                       "Could you confirm the current policy in writing?",
        "likely": "Could you confirm by email that the {r} round policy is still '{s}'?",
        "unverified": "Are AI assistants (chat or autocomplete) allowed in the {r} round?",
    }
    out = []
    for rnd, (status, stance) in assessment.items():
        if status != "verified":
            out.append(templates[status].format(r=rnd, s=stance))
    return sorted(out)


def main() -> None:
    today = date(2026, 11, 18)
    evidence = [
        Evidence("coding", "forbidden", "recruiter_email", date(2026, 11, 10)),
        Evidence("coding", "allowed", "candidate_forum", date(2026, 11, 15)),
        Evidence("practical", "allowed", "recruiter_call", date(2026, 11, 12)),
        Evidence("practical", "partial", "recruiter_call", date(2026, 11, 16)),
        Evidence("take_home", "allowed", "old_blog_post", date(2025, 3, 1)),
        Evidence("take_home", "allowed", "recruiter_email", date(2026, 6, 1)),  # stale
        Evidence("system_design", "forbidden", "interviewer_guide", date(2026, 11, 1)),
        Evidence("system_design", "allowed", "recruiter_email", date(2026, 11, 3)),
    ]
    result = assess(evidence, today)
    for rnd, (status, stance) in result.items():
        print(f"{rnd:<14} {status:<12} {stance}")
    print("\nQuestions to send the recruiter:")
    for q in questions_to_ask(result):
        print(" -", q)


if __name__ == "__main__":
    main()
