"""Shared helpers for Chapter 40 (a helper module, not an exercise; identical in exercises/).

Everything is local and deterministic: no network, no API keys, no model downloads.

- ``load_corpus()``  16 short help-centre documents about a *fictional* object store
                     (data/corpus.jsonl: id, title, area, access, year, text with ``## `` headings).
- ``load_chunks()``  one chunk per ``## `` section: id ``"d06#1"``, text ``"<title> / <heading>: <body>"``.
- ``load_queries()`` 12 queries with relevant document ids (data/queries.json).
- ``tokenize`` / ``content_terms``  lowercase ``[a-z0-9]+`` tokens; the second drops stop words.
- ``count_tokens``   whitespace word count: the chapter's stand-in for a real tokenizer (→ §38.3).
- ``embed``          signed feature-hashing embedder (words + character trigrams, → §38.4):
                     NOT a learned model; it captures surface overlap only, but it has the same
                     interface as a real encoder (text -> unit vector) and is bit-identical everywhere.
- ``keyword_ranking`` / ``dense_ranking``  deliberately simple baseline retrievers used by the
                     demos of later exercises (ex03 and ex02 build the real versions).
- ``format_prompt``  the one prompt layout the MockLLM understands.
- ``MockLLM``        a deterministic, *extractive* stand-in for a model: it copies the source
                     sentences that share the most terms with the question and cites them.
"""
from __future__ import annotations

import json
import re
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"

STOPWORDS = frozenset(
    "a an and are as at be by can do does for from how i in is it its my of on or so that the "
    "this to was what when which who why will with you your".split()
)


def load_corpus() -> list[dict]:
    with open(DATA / "corpus.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_queries() -> list[dict]:
    return json.loads((DATA / "queries.json").read_text(encoding="utf-8"))


def load_chunks() -> list[dict]:
    chunks = []
    for doc in load_corpus():
        for i, section in enumerate(re.split(r"^## ", doc["text"], flags=re.M)[1:]):
            heading, _, body = section.partition("\n")
            chunks.append({
                "id": f"{doc['id']}#{i}", "doc": doc["id"], "area": doc["area"],
                "access": doc["access"], "year": doc["year"],
                "text": f"{doc['title']} / {heading.strip()}: {' '.join(body.split())}",
            })
    return chunks


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def content_terms(text: str) -> list[str]:
    return [t for t in tokenize(text) if t not in STOPWORDS]


def count_tokens(text: str) -> int:
    return len(text.split())


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def _features(text: str) -> list[str]:
    feats = []
    for w in content_terms(text):
        feats.append("w:" + w)
        padded = f"#{w}#"
        feats.extend("c:" + padded[i:i + 3] for i in range(len(padded) - 2))
    return feats


def embed(text: str, dim: int = 256) -> np.ndarray:
    """Unit vector (or all zeros for text with no content terms)."""
    v = np.zeros(dim)
    for f in _features(text):
        h = zlib.crc32(f.encode("utf-8"))           # stable across runs (hash() is salted)
        v[h % dim] += 1.0 if (h >> 31) & 1 == 0 else -1.0
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def keyword_ranking(query: str, items: list[tuple[str, str]]) -> list[str]:
    """Ids ranked by how many distinct query terms they contain (ties by id); zero-overlap dropped."""
    q = set(content_terms(query))
    scored = [(len(q & set(content_terms(text))), item_id) for item_id, text in items]
    return [i for s, i in sorted(scored, key=lambda p: (-p[0], p[1])) if s > 0]


def dense_ranking(query: str, items: list[tuple[str, str]], dim: int = 256) -> list[tuple[str, float]]:
    """Every id with its cosine score, best first (ties by id). Full sort: O(N d + N log N)."""
    q = embed(query, dim)
    scored = [(item_id, round(float(embed(text, dim) @ q), 4)) for item_id, text in items]
    return sorted(scored, key=lambda p: (-p[1], p[0]))


INSTRUCTIONS = ("Answer the question using only the numbered sources. Cite every sentence with "
                "[n]. If the sources do not contain the answer, reply: I don't know.")
ABSTAIN = "I don't know."
_SOURCE_RE = re.compile(r"^\[(\d+)\] \((.+?)\) (.*)$")


def format_prompt(question: str, sources: list[tuple[str, str]]) -> str:
    """sources: (chunk_id, text) pairs, numbered [1], [2], ... in the given order."""
    lines = [INSTRUCTIONS, "", "Sources:"]
    lines += [f"[{n}] ({cid}) {' '.join(text.split())}" for n, (cid, text) in enumerate(sources, 1)]
    lines += ["", f"Question: {' '.join(question.split())}", "Answer:"]
    return "\n".join(lines)


def parse_prompt(prompt: str) -> tuple[str, dict[int, tuple[str, str]]]:
    question, sources = "", {}
    for line in prompt.splitlines():
        m = _SOURCE_RE.match(line)
        if m:
            sources[int(m[1])] = (m[2], m[3])
        elif line.startswith("Question: "):
            question = line[len("Question: "):]
    return question, sources


class MockLLM:
    """Deterministic extractive 'model'.

    A sentence's weight is the sum over shared question terms of 1 / (number of source sentences
    containing that term), so a rare term such as "e409" outweighs a common one such as
    "bucket"; ties go to the lower source number, then the earlier sentence.

    mode="extractive"  copy the (up to) two source sentences that share at least 2 question
                       terms (1 for a one-term question), best first, each ending in its
                       citation, e.g. ``"Rotate access keys every 90 days [2]."``;
                       abstain with ``ABSTAIN`` when no sentence shares enough terms.
    mode="hallucinate" the same answer plus one unsupported sentence citing [1].
    mode="miscite"     the same sentences but every citation number shifted by +1.
    """

    def __init__(self, mode: str = "extractive") -> None:
        if mode not in {"extractive", "hallucinate", "miscite"}:
            raise ValueError(f"unknown mode {mode!r}")
        self.mode = mode
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        question, sources = parse_prompt(prompt)
        q = set(content_terms(question))
        need = 2 if len(q) >= 2 else 1
        sents = [(n, idx, sent, set(content_terms(sent)))
                 for n, (_, text) in sorted(sources.items())
                 for idx, sent in enumerate(split_sentences(text))]
        df = Counter(t for *_, terms in sents for t in terms & q)   # rarer shared terms weigh more
        cands = []
        for n, idx, sent, terms in sents:
            shared = q & terms
            if len(shared) >= need:
                weight = round(sum(1 / df[t] for t in shared), 6)
                cands.append((-weight, n, idx, sent))
        if not cands:
            return ABSTAIN
        shift = 1 if self.mode == "miscite" else 0
        parts = [f"{sent.rstrip('.!?')} [{n + shift}]." for _, n, _, sent in sorted(cands)[:2]]
        if self.mode == "hallucinate":
            parts.append("Egress is always free for every customer [1].")
        return " ".join(parts)
