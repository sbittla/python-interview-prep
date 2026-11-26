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

Approach ladder
---------------
1. Brute force — check that the answer contains some ``[n]``: catches nothing about content.
2. Improved   — per-claim citation validity: catches made-up or shifted citations. O(answer).
3. Optimal (here) — per-claim lexical support against the cited text: O(claim terms + cited
   terms) per claim. Catches added facts with new words.
   Beyond: an NLI (entailment) model or an LLM judge (ex10) per claim catches paraphrase
   and negation, at one model call per claim.
   Why move up: groundedness/faithfulness = "every claim follows from the cited context",
   which is a per-claim property.

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
    out = []
    for sent in split_sentences(answer):
        cites = list(dict.fromkeys(int(n) for n in CITE_RE.findall(sent)))
        text = " ".join(CITE_RE.sub("", sent).split())
        text = re.sub(r"\s+([.!?,;:])", r"\1", text)          # "days ." -> "days."
        out.append((text, cites))
    return out


def support(claim: str, texts: list[str]) -> float:
    terms = set(content_terms(claim))
    if not terms:
        return 1.0
    evidence = set().union(*(content_terms(t) for t in texts)) if texts else set()
    return len(terms & evidence) / len(terms)


def check_answer(answer: str, sources: dict[int, str], threshold: float = 0.6) -> dict:
    if answer.strip() == ABSTAIN:
        return {"abstained": True, "claims": [], "grounded": 1.0, "citations_valid": 1.0}
    rows = []
    for text, cites in split_claims(answer):
        if not cites:
            status, sup = "uncited", 0.0
        elif any(n not in sources for n in cites):
            status, sup = "bad-citation", 0.0
        else:
            sup = support(text, [sources[n] for n in cites])
            status = "supported" if sup >= threshold else "unsupported"
        rows.append((text, cites, status, round(sup, 4)))
    n = len(rows)
    return {"abstained": False, "claims": rows,
            "grounded": round(sum(r[2] == "supported" for r in rows) / n, 4) if n else 0.0,
            "citations_valid": round(sum(r[2] not in {"bad-citation", "uncited"} for r in rows) / n, 4)
            if n else 0.0}


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
