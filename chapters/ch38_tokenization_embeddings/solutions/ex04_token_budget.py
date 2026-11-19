"""
Exercise 04 — Token Budgeting and Truncation Strategies           [Tier: ★ Core]
Chapter 38 · Pattern: budget allocation / greedy packing · Target time: 25 min

Problem
-------
An LLM call has a fixed context window. You must fit the prompt *and* leave room for the
answer. Using a simple deterministic token counter (``count_tokens``: words and
punctuation marks — a stand-in for a real tokenizer), implement:

- ``truncate(tokens, budget, strategy)`` with strategies
  ``"head"`` (keep the first ``budget`` tokens), ``"tail"`` (keep the last ``budget``) and
  ``"middle"`` (middle-out: keep the start and the end, replace the middle with a single
  ``"…"`` marker token; the marker counts toward the budget).
- ``fit_messages(messages, context_window, reserve_for_output)``: messages are
  ``(role, text)`` pairs. Always keep the first message if its role is ``"system"``; then
  keep the most recent messages that still fit, dropping the oldest turns first. Each
  message costs ``count_tokens(text) + 4`` (per-message formatting overhead). Return the
  kept messages in original order. Raise ``ValueError`` if even the system message plus
  the latest message cannot fit.

Examples
--------
>>> truncate(list("abcdefgh"), 5, "middle")
['a', 'b', '…', 'g', 'h']
>>> truncate(list("abcdefgh"), 3, "tail")
['f', 'g', 'h']

Constraints
-----------
- ``budget >= 0``; when ``len(tokens) <= budget`` return the tokens unchanged.
- Middle-out with ``budget == 1`` returns just the marker.

Hints
-----
- Middle-out: after the marker you have ``budget - 1`` slots; give the head the extra one
  when it is odd: ``head = (budget - 1 + 1) // 2``.
- Walk the conversation backwards, accumulating cost, and stop at the first message that
  does not fit (do not skip over it — that would create a hole in the dialogue).

Approach ladder
---------------
1. Brute force — try every subset of messages and keep the best that fits: O(2^n).
2. Optimal    — recency-greedy: system prompt + newest-first until full: O(n). Recency is
   what matters in chat, and contiguity keeps the dialogue coherent, so greedy is both
   simpler and *better* than an optimal knapsack here.

Follow-ups
----------
- Which strategy for a long log file? (Tail — errors are at the end.) For a contract?
  (Head + retrieval.) For a stack trace? (Middle-out — the top and the root cause matter.)
- Summarise dropped turns instead of discarding them ("conversation memory").
"""
from __future__ import annotations

import re

MARKER = "…"
PER_MESSAGE_OVERHEAD = 4


def count_tokens(text: str) -> int:
    return len(re.findall(r"\w+|[^\w\s]", text))


def truncate(tokens: list[str], budget: int, strategy: str = "head") -> list[str]:
    if budget < 0:
        raise ValueError("budget must be >= 0")
    if len(tokens) <= budget:
        return list(tokens)
    if strategy == "head":
        return tokens[:budget]
    if strategy == "tail":
        return tokens[len(tokens) - budget:] if budget else []
    if strategy == "middle":
        if budget == 0:
            return []
        keep = budget - 1
        head = (keep + 1) // 2
        tail = keep - head
        return tokens[:head] + [MARKER] + (tokens[len(tokens) - tail:] if tail else [])
    raise ValueError(f"unknown strategy {strategy!r}")


def message_cost(text: str) -> int:
    return count_tokens(text) + PER_MESSAGE_OVERHEAD


def fit_messages(messages: list[tuple[str, str]], context_window: int,
                 reserve_for_output: int) -> list[tuple[str, str]]:
    budget = context_window - reserve_for_output
    if not messages:
        return []
    has_system = messages[0][0] == "system"
    kept_head = [messages[0]] if has_system else []
    rest = messages[1:] if has_system else messages
    used = sum(message_cost(t) for _, t in kept_head)
    tail: list[tuple[str, str]] = []
    for role, text in reversed(rest):
        cost = message_cost(text)
        if used + cost > budget:
            break
        tail.append((role, text))
        used += cost
    if rest and not tail:
        raise ValueError("system prompt + latest message exceed the budget")
    return kept_head + tail[::-1]


def main() -> None:
    tokens = re.findall(r"\w+|[^\w\s]", "Traceback: file a.py line 1 in main ; file b.py line 9 in helper ; ValueError: bad input")
    print(f"tokens ({len(tokens)}): {' '.join(tokens)}")
    for strategy in ["head", "tail", "middle"]:
        print(f"  {strategy:6s} budget=9: {' '.join(truncate(tokens, 9, strategy))}")
    print(f"  middle budget=1: {truncate(tokens, 1, 'middle')}  budget=0: {truncate(tokens, 0, 'middle')}")

    chat = [
        ("system", "You are a concise assistant for a bike shop."),
        ("user", "Do you sell helmets?"),
        ("assistant", "Yes, we stock road and mountain helmets in three sizes."),
        ("user", "What sizes exactly, and what do they cost?"),
        ("assistant", "Small, medium and large; all cost 59 euros."),
        ("user", "Can I return one if it does not fit?"),
    ]
    print("\nmessage costs:", [message_cost(t) for _, t in chat])
    for window in [120, 60, 45]:
        kept = fit_messages(chat, window, reserve_for_output=16)
        used = sum(message_cost(t) for _, t in kept)
        print(f"window={window:3d} reserve=16 -> kept {len(kept)} msgs, {used} tokens: "
              f"{[r[0] + ':' + str(i) for i, r in enumerate(chat) if r in kept]}")
    try:
        fit_messages(chat, 20, reserve_for_output=16)
    except ValueError as e:
        print(f"window=20 -> ValueError: {e}")


if __name__ == "__main__":
    main()
