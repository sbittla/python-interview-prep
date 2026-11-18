"""
Exercise 07 — Job-Description Classifier                          [Tier: ◆ Extended]
Chapter 01 · Pattern: Counter-based keyword scoring · Target time: 25 min

Problem
-------
SWE, Data/ML and GenAI/LLM loops test different things. A quick way to decide what to prepare is
to read the job description. Write `classify(jd_text)` that returns a dict:

- "counts": {"S": n, "M": n, "L": n} — how many keyword *occurrences* of each track's SIGNALS
  appear in the text (case-insensitive, whole words; multi-word phrases such as
  "system design" count as one occurrence);
- "track": the track with the highest count (ties: S, then M, then L);
- "likely_rounds": sorted union of LIKELY_ROUNDS for every track whose count is at least half of
  the winner's count (and > 0) — mixed roles get mixed loops;
- "top_terms": the three most frequent matched terms as (term, count), most frequent first,
  ties alphabetical.

Examples
--------
>>> classify("We build REST APIs and distributed systems in Python.")["track"]
'S'

Constraints
-----------
- Text up to 10_000 characters. Return plain dicts/lists (no Counter objects).

Approach ladder
---------------
1. Brute force — text.count(term) for every term: matches substrings ("ai" inside "maintain").
2. Optimal    — tokenise once, count unigrams and bigrams with Counter, look terms up: O(n).

Hints
-----
- words = re.findall(r"[a-z0-9+#]+", text.lower()); bigrams = zip(words, words[1:]).
- Counter.most_common does not break ties alphabetically — sort explicitly.

Follow-ups
----------
- How would you weight terms in the "requirements" section more than in "nice to have"?
"""
from __future__ import annotations

import re
from collections import Counter

SIGNALS = {
    "S": ["apis", "rest", "distributed", "microservices", "concurrency", "system design",
          "databases", "backend", "scalability"],
    "M": ["pandas", "numpy", "statistics", "sql", "experimentation", "feature engineering",
          "scikit-learn", "pytorch", "a/b testing", "models"],
    "L": ["llm", "llms", "rag", "retrieval", "embeddings", "prompt", "agents", "fine-tuning",
          "transformers", "evaluation"],
}

LIKELY_ROUNDS = {
    "S": ["coding", "system_design", "practical", "behavioural"],
    "M": ["coding", "ml_coding", "sql_or_pandas", "ml_concepts", "behavioural"],
    "L": ["coding", "llm_coding", "llm_system_design", "behavioural"],
}


def term_counts(text: str) -> Counter:
    """Counter of unigrams and bigrams ("a b") in the lower-cased text."""
    words = re.findall(r"[a-z0-9+#/\-]+", text.lower())
    counts = Counter(words)
    counts.update(f"{a} {b}" for a, b in zip(words, words[1:]))
    return counts


def classify(jd_text: str) -> dict:
    """Track, keyword counts, likely rounds and top terms for a job description."""
    counts = term_counts(jd_text)
    track_counts = {t: sum(counts[term] for term in terms) for t, terms in SIGNALS.items()}
    track = max(("S", "M", "L"), key=lambda t: track_counts[t])
    best = track_counts[track]
    rounds: set[str] = set()
    for t in ("S", "M", "L"):
        if track_counts[t] > 0 and 2 * track_counts[t] >= best:
            rounds |= set(LIKELY_ROUNDS[t])
    matched = [(term, counts[term]) for terms in SIGNALS.values() for term in terms if counts[term]]
    top = sorted(matched, key=lambda kv: (-kv[1], kv[0]))[:3]
    return {"counts": track_counts, "track": track, "likely_rounds": sorted(rounds),
            "top_terms": top}


def main() -> None:
    jds = {
        "Backend": "Design REST APIs and microservices. Experience with databases, concurrency "
                   "and system design for scalability. Backend on-call rotation.",
        "Data scientist": "Use pandas, SQL and statistics to run A/B testing and experimentation. "
                          "Build models with scikit-learn; pandas expertise required.",
        "LLM engineer": "Build RAG pipelines: retrieval, embeddings, prompt design and evaluation "
                        "of LLM agents. Some PyTorch and REST APIs.",
        "Vague": "Join our fast-paced team and maintain great products.",
    }
    for name, text in jds.items():
        r = classify(text)
        print(f"{name}: track={r['track']} counts={r['counts']}")
        print(f"    rounds: {r['likely_rounds']}")
        print(f"    top terms: {r['top_terms']}")


if __name__ == "__main__":
    main()
