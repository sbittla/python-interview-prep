"""
Exercise 03 — Round-Format Checklist Generator                    [Tier: ★ Core]
Chapter 01 · Pattern: set union + stable de-duplication · Target time: 20 min

Problem
-------
Different round formats need different preparation. COMMON lists items that apply to every
round; FORMAT_ITEMS lists extra items for each format ("whiteboard", "shared_editor",
"online_judge", "take_home", "pair_programming", "notebook").

Write `build_checklist(formats, ai_policy)`:
- `formats` is a list of format names (may contain duplicates, any case);
- `ai_policy` is "ai_free", "ai_allowed" or "unknown";
- return a list of checklist strings: COMMON first, then each format's items in the order the
  formats first appear, then the policy items. Duplicate items appear once (first occurrence wins).
- Unknown format names raise ValueError listing the valid names.

`render(checklist)` returns the checklist as "[ ] item" lines, numbered from 1.

Examples
--------
>>> build_checklist(["online_judge"], "ai_free")[:1]
['Confirm the language and Python version you will use']

Constraints
-----------
- Order matters: the result must be deterministic.

Approach ladder
---------------
1. Brute force — concatenate lists, then remove duplicates with `x not in result`: O(n^2).
2. Optimal    — walk the items once, track a `seen` set: O(n). (dict.fromkeys also works.)

Hints
-----
- dict.fromkeys(iterable) keeps first-seen order and drops duplicates.
- Normalise format names with .strip().lower().

Follow-ups
----------
- How would you attach an estimated preparation time to each item?
"""
from __future__ import annotations

COMMON = [
    "Confirm the language and Python version you will use",
    "Ask how long the round is and whether it has one or several problems",
    "Prepare two clarifying questions you always ask",
    "Plan to state time and space complexity out loud",
]

FORMAT_ITEMS = {
    "whiteboard": [
        "Practise writing code by hand without autocomplete",
        "Leave space between lines for corrections",
        "Dry-run on a small example by tracing variables in a table",
    ],
    "shared_editor": [
        "Practise in a plain editor without autocomplete or linting",
        "Ask whether code will be executed or only read",
        "Dry-run on a small example by tracing variables in a table",
    ],
    "online_judge": [
        "Practise reading input from stdin and printing exact output",
        "Check the judge's Python version and time limit",
        "Test the largest input size for timeouts",
    ],
    "take_home": [
        "Clarify the deadline, scope and how the submission is graded",
        "Include a README, tests and run instructions",
        "Keep commits small with clear messages",
    ],
    "pair_programming": [
        "Ask whether you may look up documentation",
        "Narrate decisions and invite the interviewer's input",
        "Write a failing test before fixing a bug",
    ],
    "notebook": [
        "Restart the kernel and run all cells before you finish",
        "Fix random seeds and print shapes after each transform",
    ],
}

POLICY_ITEMS = {
    "ai_free": [
        "Practise the last two weeks without AI assistants",
        "Memorise stdlib signatures you rely on (heapq, bisect, collections)",
    ],
    "ai_allowed": [
        "Ask which tools are allowed and whether prompts are visible to the interviewer",
        "Practise reviewing and testing AI-generated code out loud",
    ],
    "unknown": [
        "Ask the recruiter in writing whether AI tools are allowed in this round",
    ],
}


def build_checklist(formats: list[str], ai_policy: str) -> list[str]:
    """Ordered, de-duplicated checklist for the given formats and AI policy."""
    names = [f.strip().lower() for f in formats]
    bad = sorted(set(n for n in names if n not in FORMAT_ITEMS))
    if bad:
        raise ValueError(f"unknown formats {bad}; valid: {sorted(FORMAT_ITEMS)}")
    if ai_policy not in POLICY_ITEMS:
        raise ValueError(f"unknown ai_policy {ai_policy!r}; valid: {sorted(POLICY_ITEMS)}")
    items = list(COMMON)
    for name in dict.fromkeys(names):
        items.extend(FORMAT_ITEMS[name])
    items.extend(POLICY_ITEMS[ai_policy])
    return list(dict.fromkeys(items))


def render(checklist: list[str]) -> str:
    """Numbered '[ ]' lines."""
    return "\n".join(f"{i:>2}. [ ] {item}" for i, item in enumerate(checklist, start=1))


def main() -> None:
    print("== Shared editor + whiteboard, AI-free round ==")
    print(render(build_checklist(["Shared_Editor", "whiteboard", "shared_editor"], "ai_free")))
    print("\n== Take-home, policy unknown ==")
    print(render(build_checklist(["take_home"], "unknown")))
    try:
        build_checklist(["hackathon"], "ai_free")
    except ValueError as exc:
        print("\nError:", exc)


if __name__ == "__main__":
    main()
