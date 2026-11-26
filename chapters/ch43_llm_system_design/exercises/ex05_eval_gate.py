"""
Exercise 05 — Offline Eval Pipeline with a Regression Gate         [Tier: ◆ Extended]
Chapter 43 · Pattern: golden set → per-item checks → per-slice report → gate · Target time: 40 min

Problem
-------
Before a new prompt or model ships, an offline evaluation compares it with the current
baseline on a fixed golden set and decides PASS or BLOCK. The "models" here are deterministic
mocks: dictionaries of canned answers (no network).

``check(item, answer) -> bool`` (deterministic, rule-based):
- unanswerable item: pass iff the answer is a refusal (contains one of REFUSALS after
  ``normalise``) — a confident answer to an unanswerable question is a hallucination.
- answerable item: pass iff it is not a refusal, every fact in ``item.facts`` appears as a
  whole-word phrase in the normalised answer, and the citation ``[<item.source>]`` is present.
``normalise`` lowercases, drops commas inside numbers ("1,000" -> "1000") and collapses spaces.

``evaluate(golden, answers) -> dict[qid, bool]``; a missing answer counts as a fail.
``report(golden, results) -> dict[slice, (passed, total)]`` plus key "ALL".

``gate(golden, base, cand, critical=("unanswerable",), overall_tol=0.02, slice_tol=0.25)``
-> (decision, reasons):
- BLOCK if any item in a critical slice flips pass -> fail ("critical regression: q10").
- BLOCK if the overall pass rate drops by more than overall_tol.
- BLOCK if a non-critical slice drops by more than slice_tol.
- otherwise PASS. ``reasons`` lists every triggered rule, in that order; empty on PASS.
``flips(base, cand)`` -> (newly failing qids, newly passing qids), each sorted.

Examples
--------
>>> base = evaluate(GOLDEN, BASELINE); report(GOLDEN, base)["ALL"]
(9, 12)
>>> gate(GOLDEN, base, evaluate(GOLDEN, CANDIDATE_A))[0]
'BLOCK'

Constraints
-----------
- qids unique; every item's slice non-empty. Deterministic: no LLM judge, no sampling.

Hints
-----
- Whole-word phrase match: regex lookarounds that forbid a word character just
  before and just after re.escape(fact), so '150' does not match inside '1500'.
- report: a defaultdict of [passed, total], updated for the item's slice and for 'ALL'.
- flips: sort qids by (len, text) so q2 comes before q10.
- gate: append reasons in rule order; the decision is BLOCK iff any reason exists.

Follow-ups
----------
- With 4 items per slice one flip moves the slice by 25 points: grow slices, or report a
  bootstrap interval (→ §35.5); paired flips suit McNemar's test better than two rates.
- Rule-based checks miss paraphrases; an LLM judge (→ §40.10) needs its own calibration set.
- Offline pass is necessary, not sufficient: confirm online with an A/B test (→ §35.6).
- Edge cases: missing answer, refusal phrased in capitals, "10" must not match "100".
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

REFUSALS = ("i don't know", "not in the provided documents", "cannot find")


@dataclass(frozen=True)
class Item:
    qid: str
    slice: str
    question: str
    facts: tuple[str, ...] = ()
    source: str = ""
    answerable: bool = True


GOLDEN = [
    Item("q1", "policy", "Vacation days for new staff?", ("20 days",), "doc1"),
    Item("q2", "policy", "Can unused vacation roll over?", ("5 days",), "doc1"),
    Item("q3", "policy", "Who approves remote work?", ("manager",), "doc2"),
    Item("q4", "policy", "Is there a learning budget?", ("1000",), "doc3"),
    Item("q5", "numeric", "Laptop refresh cycle in years?", ("3 years",), "doc4"),
    Item("q6", "numeric", "Days allowed to file expenses?", ("30",), "doc5"),
    Item("q7", "numeric", "Maximum hotel rate per night?", ("150",), "doc5"),
    Item("q8", "numeric", "Weeks of parental leave?", ("16 weeks",), "doc6"),
    Item("q9", "unanswerable", "What is the CEO's salary?", answerable=False),
    Item("q10", "unanswerable", "What will next year's bonus be?", answerable=False),
    Item("q11", "unanswerable", "What is the office wifi password?", answerable=False),
    Item("q12", "unanswerable", "Will the share price rise tomorrow?", answerable=False),
]

_COMMON = {
    "q1": "New staff get 20 days of vacation [doc1].",
    "q3": "Your manager approves remote work [doc2].",
    "q5": "Laptops are replaced every 3 years [doc4].",
    "q6": "File expenses within 30 days [doc5].",
    "q8": "Parental leave is 16 weeks [doc6].",
    "q9": "That is not in the provided documents.",
    "q11": "I don't know; it is not in the provided documents.",
    "q12": "I cannot find that in the documents.",
}
BASELINE = {**_COMMON,
            "q2": "Unused vacation expires at year end [doc1].",       # wrong
            "q4": "Yes, up to $1,000 per year.",                       # no citation
            "q7": "Hotels up to $1500 per night [doc5].",              # 1500 is not 150
            "q10": "I don't know."}
CANDIDATE_A = {**_COMMON,
               "q2": "Up to 5 days roll over [doc1].",
               "q4": "Yes, up to $1,000 per year [doc3].",
               "q7": "Hotels up to $150 per night [doc5].",
               "q10": "Next year's bonus will be 10% [doc3]."}      # hallucination
CANDIDATE_B = {**BASELINE, "q2": "Up to 5 days roll over [doc1]."}


def normalise(text: str) -> str:
    raise NotImplementedError("TODO")


def _is_refusal(answer: str) -> bool:
    a = normalise(answer)
    return any(r in a for r in REFUSALS)


def check(item: Item, answer: str | None) -> bool:
    raise NotImplementedError("TODO")


def evaluate(golden: list[Item], answers: dict[str, str]) -> dict[str, bool]:
    raise NotImplementedError("TODO")


def report(golden: list[Item], results: dict[str, bool]) -> dict[str, tuple[int, int]]:
    raise NotImplementedError("TODO")


def flips(base: dict[str, bool], cand: dict[str, bool]) -> tuple[list[str], list[str]]:
    raise NotImplementedError("TODO")


def gate(golden: list[Item], base: dict[str, bool], cand: dict[str, bool],
         critical: tuple[str, ...] = ("unanswerable",), overall_tol: float = 0.02,
         slice_tol: float = 0.25) -> tuple[str, list[str]]:
    raise NotImplementedError("TODO")


def main() -> None:
    base = evaluate(GOLDEN, BASELINE)
    print("baseline:", report(GOLDEN, base))
    for name, answers in [("candidate A", CANDIDATE_A), ("candidate B", CANDIDATE_B)]:
        cand = evaluate(GOLDEN, answers)
        broke, fixed = flips(base, cand)
        print(f"{name}: {report(GOLDEN, cand)}")
        print(f"  newly failing {broke}, newly passing {fixed} -> {gate(GOLDEN, base, cand)}")
    worse = evaluate(GOLDEN, {**BASELINE, "q1": "Vacation is generous [doc1].",
                              "q3": "HR decides [doc2]."})
    print("policy slice regresses:", gate(GOLDEN, base, worse))
    print("missing answer:", check(GOLDEN[0], None),
          "| capital refusal:", check(GOLDEN[8], "I DON'T KNOW."),
          "| '150' in '$1500':", check(GOLDEN[6], "$1500 [doc5]"))


if __name__ == "__main__":
    main()
