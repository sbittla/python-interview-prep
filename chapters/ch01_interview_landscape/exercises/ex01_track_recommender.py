"""
Exercise 01 — Track Recommender                                   [Tier: ★ Core]
Chapter 01 · Pattern: rule table / dictionary dispatch · Target time: 20 min

Problem
-------
The course has three tracks: S (Software Engineering), M (Data / ML) and L (GenAI / LLM).
Write `recommend_track(profile)` that takes a candidate profile (a dict) and returns a dict:

    {"track": "S" | "M" | "L", "parts": [...], "reasons": [...]}

Profile keys (all optional except "target_role"):
- "target_role": free text such as "backend engineer", "data scientist", "LLM engineer".
- "interests":   list of strings, e.g. ["rag", "pytorch"].
- "skip_python_basics": bool — True when the diagnostic test placed the reader on the fast track.

Rules:
1. Score each track: +3 for every role keyword found in target_role, +1 for every interest
   keyword. Keywords live in ROLE_KEYWORDS / INTEREST_KEYWORDS.
2. The highest score wins; ties are broken in the order S, M, L (S is the safest default because
   every loop contains general coding rounds). A profile with no matches gets S.
3. "parts" is the track's part list from TRACK_PARTS. When skip_python_basics is True, Part "I"
   is removed (the reader skims it instead).
4. "reasons" lists, in sorted order, the keywords that matched the winning track.

Examples
--------
>>> recommend_track({"target_role": "Backend Engineer"})["track"]
'S'
>>> recommend_track({"target_role": "ML engineer", "interests": ["pandas"]})["track"]
'M'

Constraints
-----------
- Matching is case-insensitive and on whole words (split on non-letters).
- Never mutate the input profile.


Hints
-----
- Tokenise with re.findall(r"[a-z]+", text.lower()).
- max() over ("S", "M", "L") with key=score keeps the first track on ties.

Follow-ups
----------
- How would you support a "hybrid" recommendation when two tracks are within 1 point?
- How would you add a new track without editing the scoring function?
"""
from __future__ import annotations

import re

TRACK_PARTS = {
    "S": ["0", "I", "II", "III", "IV", "V", "VIII"],
    "M": ["0", "I", "II", "III", "V", "VI", "VIII"],
    "L": ["0", "I", "II", "III", "IV", "V", "VII", "VIII"],
}

ROLE_KEYWORDS = {
    "S": {"backend", "frontend", "software", "swe", "fullstack", "platform", "sre", "infrastructure"},
    "M": {"data", "scientist", "analyst", "ml", "machine", "learning", "analytics"},
    "L": {"llm", "genai", "ai", "nlp", "agent", "agents", "rag", "applied"},
}

INTEREST_KEYWORDS = {
    "S": {"systems", "apis", "concurrency", "databases", "design"},
    "M": {"pandas", "numpy", "statistics", "pytorch", "sql", "experiments"},
    "L": {"rag", "transformers", "prompting", "embeddings", "agents", "tokenization"},
}


def tokens(text: str) -> set[str]:
    """Lower-case word tokens of `text`."""
    raise NotImplementedError("TODO")


def score_tracks(profile: dict) -> dict[str, int]:
    """Return {"S": n, "M": n, "L": n} using the keyword rules."""
    raise NotImplementedError("TODO")


def recommend_track(profile: dict) -> dict:
    """Return {"track", "parts", "reasons"} for the profile."""
    raise NotImplementedError("TODO")


def main() -> None:
    profiles = [
        {"target_role": "Backend Engineer", "interests": ["APIs", "databases"]},
        {"target_role": "Data Scientist", "interests": ["pandas", "statistics"]},
        {"target_role": "LLM Engineer", "interests": ["RAG", "embeddings"], "skip_python_basics": True},
        {"target_role": "ML engineer", "interests": ["transformers", "agents", "prompting"]},
        {"target_role": "Engineer"},  # no matches -> default S
    ]
    for p in profiles:
        rec = recommend_track(p)
        print(f"{p['target_role']:<18} scores={score_tracks(p)} -> track {rec['track']}")
        print(f"    parts:   {' '.join(rec['parts'])}")
        print(f"    reasons: {rec['reasons']}")


if __name__ == "__main__":
    main()
