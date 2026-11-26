"""
Exercise 09 — Groundedness and Citation Checks                     [Tier: ★ Core]
Chapter 40 · Pattern: claim splitting + evidence matching · Target time: 30 min

Problem
-------
The model was told to cite every sentence as ``[n]``. Check an answer against the numbered
sources that were in its prompt.

1. ``split_claims(answer)``: sentences (``ragkit.split_sentences``) -> ``(claim_text, cites)``,
   where ``cites`` are the ``[n]`` numbers in order of first appearance and ``claim_text`` is the
   sentence with the citation markers removed.
2. ``support(claim, texts)``: fraction of the claim's ``content_terms`` (distinct) that occur in
   the union of ``texts``' terms; a claim with no content terms -> 1.0.
3. ``check_answer(answer, sources, threshold=0.6)`` with ``sources = {n: text}``. Each claim gets
   a status:
   - ``"uncited"``: no citation;
   - ``"bad-citation"``: cites a number that is not a source;
   - ``"supported"`` / ``"unsupported"``: support from the *cited* sources >= / < threshold.
   Return ``{"abstained", "claims": [(text, cites, status, support)], "grounded",
   "citations_valid"}``: ``grounded`` = supported / claims, ``citations_valid`` = claims whose
   citations exist / claims (both rounded to 4). An answer equal to ``ragkit.ABSTAIN`` is
   ``abstained=True`` with no claims and both rates 1.0.

Examples
--------
>>> split_claims("Keys rotate every 90 days [2]. Use two keys [1][2].")
[('Keys rotate every 90 days.', [2]), ('Use two keys.', [1, 2])]

Constraints
-----------
- Support is computed against the cited sources only: a claim that is true according to an
  *uncited* source is still a citation error.

Hints
-----
- ``CITE_RE.findall(sentence)`` finds the citation numbers; ``dict.fromkeys`` keeps their order.
- Support uses only the texts of the *cited* sources.
- Check citation validity before computing support.

Wrong-but-tempting
------------------
- Checking support against all sources: hides wrong citations.
- Counting an abstention as ungrounded, or reporting groundedness without the abstention rate.
- Believing lexical support catches negation.

Follow-ups
----------
- Lexical overlap is fooled by negation: "requests are NOT rejected" shares almost every term
  with "requests are rejected" (see ``main``). Say so before the interviewer does.
- Faithfulness (supported by context) differs from correctness (true in the world) and from
  answer relevance (answers the question). A grounded answer to the wrong question still fails.
- Track abstention rate separately: a system that always says "I don't know" is 100% grounded.
"""
from __future__ import annotations

import re

from ragkit import (ABSTAIN, MockLLM, content_terms, dense_ranking, format_prompt, load_chunks,
                    load_queries, split_sentences)

CITE_RE = re.compile(r"\[(\d+)\]")


def split_claims(answer: str) -> list[tuple[str, list[int]]]:
    raise NotImplementedError("TODO")


def support(claim: str, texts: list[str]) -> float:
    raise NotImplementedError("TODO")


def check_answer(answer: str, sources: dict[int, str], threshold: float = 0.6) -> dict:
    raise NotImplementedError("TODO")


def main() -> None:
    print(split_claims("Keys rotate every 90 days [2]. Use two keys [1][2]."))
    srcs = {1: "Plain HTTP requests are rejected with error E403.",
            2: "Rotate access keys every 90 days."}
    for ans in ["Rotate access keys every 90 days [2].", "Rotate access keys every 90 days [1].",
                "Rotate access keys every 90 days.", "Rotate access keys every 90 days [3].",
                "Plain HTTP requests are not rejected [1].", ABSTAIN]:
        res = check_answer(ans, srcs)
        print(f"{ans!r:47} -> {[(r[2], r[3]) for r in res['claims']] or 'abstained'}")

    chunks = load_chunks()
    items = [(c["id"], c["text"]) for c in chunks]
    text_of = dict(items)
    print(f"\n{'mode':<12}{'grounded':>9}{'cites ok':>9}{'abstain':>8}  (mean over 12 queries, top-3 chunks)")
    for mode in ("extractive", "hallucinate", "miscite"):
        llm = MockLLM(mode)
        g = c = a = 0.0
        for q in load_queries():
            top = [cid for cid, _ in dense_ranking(q["query"], items)[:3]]
            prompt = format_prompt(q["query"], [(cid, text_of[cid]) for cid in top])
            res = check_answer(llm.complete(prompt), {n: text_of[cid] for n, cid in enumerate(top, 1)})
            g, c, a = g + res["grounded"], c + res["citations_valid"], a + res["abstained"]
        print(f"{mode:<12}{g / 12:>9.4f}{c / 12:>9.4f}{int(a):>8}")


if __name__ == "__main__":
    main()
