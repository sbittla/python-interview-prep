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

Hints
-----
- Start ``used`` at the tokens of ``format_prompt(question, [])`` plus ``reserve``.
- The cost of a chunk is the token count of its whole source line ``[n] (id) text``.
- edge_order: the odd ranks go left to right, the even ranks come back right to left (slicing).

Wrong-but-tempting
------------------
- Stopping at the first chunk that does not fit (a smaller, later chunk may still fit).
- Forgetting the answer reserve: the model has no room to reply.
- Truncating the concatenated prompt: cuts a chunk in half and may cut off the question.

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
    raise NotImplementedError("TODO")


def assemble(question: str, chunks: list[dict], budget: int, reserve: int = 50,
             order: str = "score") -> dict:
    raise NotImplementedError("TODO")


def naive_truncate(question: str, chunks: list[dict], budget: int) -> str:
    """Rung 2: concatenate, then cut at the budget (shown only to demonstrate the damage)."""
    raise NotImplementedError("TODO")


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
