"""
Exercise 07 — Prompt Assembly under a Context Budget                [Tier: ★ Core]
Chapter 40 · Pattern: greedy knapsack-style packing + citation map · Target time: 30 min

Problem
-------
``assemble(question, chunks, budget, reserve=50, order="score")`` builds the prompt sent to the
model from retrieved ``chunks = [{"id", "text", "score"}, ...]``. Tokens are counted with
``ragkit.count_tokens`` and the layout is ``ragkit.format_prompt``.

1. The prompt *plus* ``reserve`` tokens kept free for the answer must fit in ``budget``. If the
   instructions and question alone do not fit -> ``ValueError``.
2. Drop duplicates: chunks whose text is equal after lowercasing and collapsing whitespace;
   keep the higher-scoring one (ties -> smaller id).
3. Take chunks by score desc (ties -> id). Add a chunk only if its whole source line fits; if
   it does not, skip it and keep trying smaller ones (never cut a chunk in half).
4. ``order="score"`` numbers the kept chunks best-first; ``order="edges"`` puts the best chunks
   at the two ends and the weakest in the middle (``edge_order``).
5. Return ``{"prompt", "sources": {n: chunk_id}, "dropped": [(chunk_id, reason)], "tokens"}``
   with reason ``"duplicate"`` or ``"budget"``; ``tokens`` = prompt tokens.

Examples
--------
>>> edge_order(["r1", "r2", "r3", "r4", "r5"])
['r1', 'r3', 'r5', 'r4', 'r2']

Constraints
-----------
- Deterministic: identical input -> identical prompt (prompt caching and tests depend on it).

Approach ladder
---------------
1. Brute force — concatenate everything. O(total) but overflows the window; the API errors or
   something gets cut, possibly the question at the end.
2. Improved   — concatenate, then cut at ``budget`` tokens: always fits, but cuts a chunk
   mid-sentence and wastes budget on duplicates.
3. Optimal    — dedupe, sort by score, add whole chunks while they fit, skipping ones that do
   not: O(n log n + total tokens). Citation numbers map back to chunk ids for checking (ex09).
   Why move up: the budget goes to distinct, relevant, complete evidence. (Exact best-subset
   packing is a 0/1 knapsack, → §19.6; greedy by score is the standard practical choice.)

Follow-ups
----------
- "Lost in the middle" (Liu et al., 2023): long-context models used evidence at the start and
  end of the context better than evidence in the middle -> ``order="edges"``.
- Put the question after the sources and repeat key instructions near the end for long prompts.
- Retrieved text is untrusted input: it can contain instructions (prompt injection, → §42.11).
- Token counts must come from the target model's tokenizer in production (→ §38.3).
"""
from __future__ import annotations

from ragkit import MockLLM, count_tokens, embed, format_prompt, load_chunks


def edge_order(items: list) -> list:
    """Best-first list -> best at both ends: ranks 1, 3, 5, ... then ..., 4, 2."""
    return items[0::2] + items[1::2][::-1]


def assemble(question: str, chunks: list[dict], budget: int, reserve: int = 50,
             order: str = "score") -> dict:
    if order not in {"score", "edges"}:
        raise ValueError(f"unknown order {order!r}")
    used = count_tokens(format_prompt(question, [])) + reserve
    if used > budget:
        raise ValueError(f"instructions + question + reserve need {used} tokens > budget {budget}")
    dropped: list[tuple[str, str]] = []
    seen: set[str] = set()
    kept: list[dict] = []
    for c in sorted(chunks, key=lambda c: (-c["score"], c["id"])):
        key = " ".join(c["text"].lower().split())
        if key in seen:
            dropped.append((c["id"], "duplicate"))
            continue
        seen.add(key)
        cost = count_tokens(f"[{len(kept) + 1}] ({c['id']}) {c['text']}")   # its whole source line
        if used + cost > budget:
            dropped.append((c["id"], "budget"))                            # skip, try smaller ones
            continue
        kept.append(c)
        used += cost
    if order == "edges":
        kept = edge_order(kept)
    prompt = format_prompt(question, [(c["id"], c["text"]) for c in kept])
    return {"prompt": prompt, "sources": {n: c["id"] for n, c in enumerate(kept, 1)},
            "dropped": dropped, "tokens": count_tokens(prompt)}


def naive_truncate(question: str, chunks: list[dict], budget: int) -> str:
    """Rung 2: concatenate, then cut at the budget (shown only to demonstrate the damage)."""
    words = format_prompt(question, [(c["id"], c["text"]) for c in chunks]).split()
    return " ".join(words[:budget])


def main() -> None:
    print("edge_order:", edge_order(["r1", "r2", "r3", "r4", "r5"]))
    chunks = load_chunks()
    question = "why does deleting my bucket fail with E409"
    q = embed(question)
    scored = sorted(({"id": c["id"], "text": c["text"], "score": round(float(embed(c["text"]) @ q), 4)}
                     for c in chunks), key=lambda c: (-c["score"], c["id"]))[:5]
    top = scored[0]                                  # a re-ingested copy with different case/spacing
    scored.append({"id": top["id"] + "-dup", "text": "  " + top["text"].upper(), "score": top["score"]})
    print("candidates:", [(c["id"], c["score"], count_tokens(c["text"])) for c in scored])

    res = assemble(question, scored, budget=190, reserve=40)
    print(f"\nbudget=190 reserve=40 -> prompt tokens={res['tokens']} (+40 reserved)")
    print("sources:", res["sources"])
    print("dropped:", res["dropped"])
    print(res["prompt"])
    llm = MockLLM()
    answer = llm.complete(res["prompt"])
    print("\nmock answer:", answer)

    print("\nedges order:", assemble(question, scored, 400, 40, order="edges")["sources"])
    cut = naive_truncate(question, scored, 120)
    print("naive cut keeps the question:", "Question:" in cut, "| ends with:", repr(cut[-30:]))
    try:
        assemble(question, scored, budget=60, reserve=40)
    except ValueError as e:
        print("ValueError:", e)


if __name__ == "__main__":
    main()
