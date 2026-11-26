"""
Exercise 06 — Design-Doc Rubric Scorer                             [Tier: ○ Reference]
Chapter 43 · Pattern: checklist as data + partial credit · Target time: 20 min

Problem
-------
Turn the §43.1 interview framework into a self-check. Given the text of your design notes,
score it against RUBRIC: each criterion has a weight, a list of signal regexes and the number
of *distinct* signals needed for full marks (``need``). Numbers matter in design rounds, so the
"estimates" criterion counts numbers with units (NUMBER_WITH_UNIT) instead of words.

``score(text, rubric=RUBRIC) -> list[Line]``: for each criterion, ``hits`` = distinct signals
found (case-insensitive, each signal must start at a word boundary); ``points`` =
``weight * min(hits, need) / need`` rounded to 1 decimal.
``total(lines)`` = sum of points (rounded to 1 decimal).
``gaps(lines, k=3)`` = up to k criterion names with the most lost points (weight - points),
largest first, ties by rubric order; criteria with nothing lost are never listed.

Examples
--------
>>> total(score(""))
0.0
>>> score("p95 latency under 2 s at 50 qps")[0].points
15.0

Constraints
-----------
- Weights sum to 100. Keyword matching is a coarse proxy: it rewards *mentioning* a
  concern, not handling it well. Use it to find gaps, never as a grade.

Hints
-----
- Estimates: count DISTINCT lowercased NUMBER_WITH_UNIT matches.
- Signals: one re.search per signal, anchored at a word boundary, ignoring case.
- gaps: sort (lost points descending, rubric index ascending), skip zero losses.

Follow-ups
----------
- Add a criterion for "trade-offs" that needs both sides named ("X vs Y because ...").
- Score the same notes at minute 10 and minute 35 of a mock interview (→ Ch. 47).
- Edge cases: empty text (0), a signal repeated many times (counts once), text with numbers
  but no units (estimates stay 0).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

NUMBER_WITH_UNIT = re.compile(
    r"\b\d[\d,.]*\s?(?:k|m|gb|tb|ms|s|qps|rps|tokens?|gpus?|replicas?|%)(?![a-z])", re.I)


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: int
    signals: tuple[str, ...]
    need: int


@dataclass(frozen=True)
class Line:
    name: str
    hits: int
    need: int
    points: float
    weight: int


RUBRIC = (
    Criterion("requirements", 15, ("qps", "p9[59]", "ttft", "latency", "slo", "users?",
                                   "freshness", "budget"), 3),
    Criterion("estimates", 15, (), 3),          # counted with NUMBER_WITH_UNIT
    Criterion("architecture", 15, ("gateway", "retriev", "index", "cache", "queue",
                                   "rerank", "vector"), 3),
    Criterion("data", 10, ("ingest", "chunk", "embed", "acl", "permission", "re-?index"), 2),
    Criterion("evaluation", 15, ("golden", "eval", "regression", r"recall@", "faithful",
                                 "a/b"), 2),
    Criterion("failure_modes", 10, ("fallback", "timeout", "outage", "degrad", "retr(y|ies)",
                                    "circuit"), 2),
    Criterion("safety", 10, ("pii", "injection", "guardrail", "acl", "redact"), 2),
    Criterion("observability", 10, ("trace", "dashboard", "metric", "cost", "alert",
                                    "feedback"), 3),
)


def _hits(text: str, c: Criterion) -> int:
    raise NotImplementedError("TODO")


def score(text: str, rubric: tuple[Criterion, ...] = RUBRIC) -> list[Line]:
    raise NotImplementedError("TODO")


def total(lines: list[Line]) -> float:
    raise NotImplementedError("TODO")


def gaps(lines: list[Line], k: int = 3) -> list[str]:
    raise NotImplementedError("TODO")


WEAK = """We put a vector store in front of a large model. Users ask questions and the
model answers from retrieved documents. We will make it fast and cheap."""

STRONG = """Requirements: 50 qps peak, p95 TTFT under 1 s, answers cite sources, docs fresh
within 1 h, cost budget fixed. Estimates: 3000 tokens prompt, 300 tokens output, 26 GPUs at
batch 64, KV cache 0.4 GB per request. Architecture: gateway -> retriever (hybrid index)
-> reranker -> generator; exact cache in front. Data: ingest, chunk, embed, re-index on
change; ACL filter at query time. Evaluation: golden set per slice, regression gate,
recall@10, faithfulness. Failure modes: retriever timeout -> keyword-only fallback; model
outage -> degraded answer. Safety: PII redaction, prompt-injection filter on documents.
Observability: traces per stage, cost per team, alerts on p95, thumbs feedback."""


def show(label: str, text: str) -> None:
    lines = score(text)
    detail = ", ".join(f"{l.name} {l.points:g}/{l.weight}" for l in lines)
    print(f"{label}: {total(lines)}/100  gaps={gaps(lines)}")
    print(f"  {detail}")


def main() -> None:
    show("weak notes", WEAK)
    show("strong notes", STRONG)
    show("empty", "")
    print("numbers without units:", score("we need 3 and 50 and 7")[1])
    print("repeated signal counts once:", score("cache cache cache")[2].hits)


if __name__ == "__main__":
    main()
