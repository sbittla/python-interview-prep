"""
Exercise 01 — Chunking: Fixed Windows, Sentences, Headings          [Tier: ★ Core]
Chapter 40 · Pattern: sliding window + greedy packing · Target time: 30 min

Problem
-------
Split documents into retrievable chunks. Sizes are in tokens, counted with
``ragkit.count_tokens`` (whitespace words; a real system uses the model's tokenizer, → §38.3).

1. ``fixed_chunks(text, size, overlap=0)``: windows of ``size`` words; consecutive windows
   share ``overlap`` words (step = size - overlap). The last window ends at the last word, and no
   window is emitted that is already contained in the previous one. Empty text -> [].
   ``size <= 0`` or ``not 0 <= overlap < size`` -> ``ValueError``.
2. ``sentence_chunks(text, max_tokens)``: greedily pack whole sentences
   (``ragkit.split_sentences``) while the chunk stays within ``max_tokens``. A single sentence
   longer than ``max_tokens`` is hard-split with ``fixed_chunks(sentence, max_tokens)``.
3. ``heading_chunks(markdown, max_tokens)``: split on Markdown headings (``#`` to ``######``),
   keep the heading *path* (``"Access keys > Rotation"``) as metadata, and pack each section's
   body with ``sentence_chunks``. Body text before the first heading gets path ``""``;
   headings with no body produce no chunk. Returns ``[{"heading": path, "text": chunk}, ...]``.

Examples
--------
>>> fixed_chunks("a b c d e f g", size=4, overlap=2)
['a b c d', 'c d e f', 'e f g']
>>> sentence_chunks("One two. Three four five. Six.", max_tokens=3)
['One two.', 'Three four five.', 'Six.']

Constraints
-----------
- Words are never split; only a sentence longer than the budget is split mid-sentence.
- Output is a pure function of the input (no randomness).

Approach ladder
---------------
1. Brute force — ``char_chunks``: slice every ``size`` characters. O(n), but it cuts words and
   sentences in half, so a fact can be split across two chunks and match neither.
2. Improved   — fixed word windows with overlap. O(n · size / step) output words; overlap gives
   a fact near a boundary a second chance, at the cost of size/step times more index text.
3. Optimal    — structure-aware (the "recursive" strategy): headings -> sentences -> words, only
   falling to a finer separator when a piece is too big. O(n); chunks are coherent and carry a
   heading path that can be shown to the model or used as a filter.
   Why move up: retrieval quality depends on a chunk being about one thing.

Follow-ups
----------
- Semantic chunking: embed each sentence and start a new chunk where the cosine similarity of
  neighbours drops below a threshold. Costs one embedding per sentence at index time.
- Small-to-big: index small chunks for precise matching but return the parent section.
- Tables and code blocks should never be split; treat them as atomic pieces.
- Chunk ids must be stable (doc id + position) so citations and caches survive re-indexing.
"""
from __future__ import annotations

import re

from ragkit import count_tokens, load_corpus, split_sentences


def char_chunks(text: str, size: int) -> list[str]:
    """Rung 1: fixed character slices (cuts words)."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [text[i:i + size] for i in range(0, len(text), size)]


def fixed_chunks(text: str, size: int, overlap: int = 0) -> list[str]:
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    words = text.split()
    chunks: list[str] = []
    step = size - overlap
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):          # this window reached the end: stop
            break
    return chunks


def sentence_chunks(text: str, max_tokens: int) -> list[str]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for sent in split_sentences(text):
        n = count_tokens(sent)
        if n > max_tokens:                      # one sentence alone is too big: hard split
            if cur:
                chunks.append(" ".join(cur))
                cur, cur_len = [], 0
            chunks.extend(fixed_chunks(sent, max_tokens))
            continue
        if cur_len + n > max_tokens:
            chunks.append(" ".join(cur))
            cur, cur_len = [], 0
        cur.append(sent)
        cur_len += n
    if cur:
        chunks.append(" ".join(cur))
    return chunks


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def heading_chunks(markdown: str, max_tokens: int) -> list[dict]:
    out: list[dict] = []
    path: list[tuple[int, str]] = []            # (level, title) stack
    body: list[str] = []

    def flush() -> None:
        text = " ".join(body)
        heading = " > ".join(title for _, title in path)
        out.extend({"heading": heading, "text": c} for c in sentence_chunks(text, max_tokens))
        body.clear()

    for line in markdown.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            flush()
            level = len(m[1])
            while path and path[-1][0] >= level:  # pop siblings and deeper levels
                path.pop()
            path.append((level, m[2]))
        elif line.strip():
            body.append(line.strip())
    flush()
    return out


def main() -> None:
    print("fixed size=4 overlap=2:", fixed_chunks("a b c d e f g", 4, 2))
    print("fixed size=4 overlap=0:", fixed_chunks("a b c d e f g h", 4))
    print("short text:", fixed_chunks("a b", 4, 1), " empty:", fixed_chunks("", 4, 1))
    try:
        fixed_chunks("a b c", 3, 3)
    except ValueError as e:
        print("overlap == size ->", e)
    print("sentences max=3:", sentence_chunks("One two. Three four five. Six.", 3))
    print("long sentence max=3:", sentence_chunks("Short. This sentence has seven words in it.", 3))

    doc = next(d for d in load_corpus() if d["id"] == "d06")
    print("\nchar_chunks(d06, 60)[:2]:", char_chunks(doc["text"], 60)[:2])
    md = "# Access keys\n" + doc["text"].replace("## ", "### ")
    for c in heading_chunks(md, max_tokens=20):
        print(f"  [{c['heading']}] ({len(c['text'].split())} words) {c['text']}")
    print("preamble + empty heading:",
          heading_chunks("Intro text.\n# A\n# B\nBody of B.", 10))


if __name__ == "__main__":
    main()
