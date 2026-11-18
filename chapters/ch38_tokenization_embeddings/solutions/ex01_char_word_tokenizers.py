"""
Exercise 01 — Character and Word Tokenizers                       [Tier: ★ Core]
Chapter 38 · Pattern: vocabulary building / encode-decode · Target time: 20 min

Problem
-------
Build two tiny tokenizers and compare them.

1. A character tokenizer: the vocabulary is every distinct character in the training
   texts (sorted), preceded by the special tokens ``<pad>`` (id 0) and ``<unk>`` (id 1).
2. A word tokenizer: split text into lowercase words and punctuation marks with a regular
   expression, keep words seen at least ``min_freq`` times, and map everything else to
   ``<unk>``. Ids are assigned by descending frequency, ties broken alphabetically.

Both must provide ``encode`` (text -> list[int]) and ``decode`` (list[int] -> text).
Also write ``oov_rate`` — the fraction of word tokens in a text that map to ``<unk>``.

Examples
--------
>>> vocab = build_char_vocab(["abc", "cab"])
>>> char_encode("cabz", vocab)
[4, 2, 3, 1]
>>> char_decode([4, 2, 3], vocab)
'cab'
>>> word_split("Hello, world!")
['hello', ',', 'world', '!']

Constraints
-----------
- Deterministic ids: never depend on set or dict iteration order.
- ``decode`` skips ``<pad>``; unknown ids decode as ``<unk>``.

Hints
-----
- ``sorted(set("".join(texts)))`` gives a deterministic character list.
- ``re.findall(r"\\w+|[^\\w\\s]", text.lower())`` splits words from punctuation.
- ``Counter.most_common`` does not tie-break alphabetically; sort by ``(-count, word)``.

Approach ladder
---------------
1. Brute force — linear search in a list for each token: O(V) per lookup.
2. Optimal    — dict token->id and list id->token: O(1) per lookup, O(n) encode.
   The interesting decision is not speed but *granularity*: characters never go OOV but
   produce long sequences; words give short sequences but an unbounded vocabulary and OOVs.

Follow-ups
----------
- Why do production LLMs use neither? (Subwords: bounded vocab, no OOV, short sequences.)
- How would you make decode reversible for whitespace? (Store spaces as tokens, or bytes.)
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

PAD, UNK = "<pad>", "<unk>"
DATA = Path(__file__).resolve().parent.parent / "data" / "corpus.txt"


def build_char_vocab(texts: list[str]) -> dict[str, int]:
    """Map special tokens then every distinct character (sorted) to an id."""
    chars = sorted(set("".join(texts)))
    tokens = [PAD, UNK] + chars
    return {tok: i for i, tok in enumerate(tokens)}


def char_encode(text: str, vocab: dict[str, int]) -> list[int]:
    unk = vocab[UNK]
    return [vocab.get(ch, unk) for ch in text]


def char_decode(ids: list[int], vocab: dict[str, int]) -> str:
    inv = {i: t for t, i in vocab.items()}
    out = []
    for i in ids:
        tok = inv.get(i, UNK)
        if tok == PAD:
            continue
        out.append(tok)
    return "".join(out)


def word_split(text: str) -> list[str]:
    """Lowercase, then split into runs of word characters and single punctuation marks."""
    return re.findall(r"\w+|[^\w\s]", text.lower())


def build_word_vocab(texts: list[str], min_freq: int = 1) -> dict[str, int]:
    counts = Counter(w for t in texts for w in word_split(t))
    kept = sorted((w for w, c in counts.items() if c >= min_freq), key=lambda w: (-counts[w], w))
    tokens = [PAD, UNK] + kept
    return {tok: i for i, tok in enumerate(tokens)}


def word_encode(text: str, vocab: dict[str, int]) -> list[int]:
    unk = vocab[UNK]
    return [vocab.get(w, unk) for w in word_split(text)]


def word_decode(ids: list[int], vocab: dict[str, int]) -> str:
    """Join with spaces; punctuation is attached to the previous word (lossy!)."""
    inv = {i: t for t, i in vocab.items()}
    out: list[str] = []
    for i in ids:
        tok = inv.get(i, UNK)
        if tok == PAD:
            continue
        if out and re.fullmatch(r"[^\w\s]", tok):
            out[-1] += tok
        else:
            out.append(tok)
    return " ".join(out)


def oov_rate(text: str, vocab: dict[str, int]) -> float:
    ids = word_encode(text, vocab)
    if not ids:
        return 0.0
    return sum(i == vocab[UNK] for i in ids) / len(ids)


def main() -> None:
    lines = DATA.read_text(encoding="utf-8").splitlines()
    cv = build_char_vocab(lines)
    wv = build_word_vocab(lines, min_freq=2)
    print(f"corpus lines: {len(lines)}")
    print(f"char vocab size: {len(cv)}  first 12: {list(cv)[:12]}")
    print(f"word vocab size (min_freq=2): {len(wv)}  top 8: {list(wv)[2:10]}")

    sample = "The engineer repairs the laptop."
    ce, we = char_encode(sample, cv), word_encode(sample, wv)
    print(f"\nsample: {sample!r}")
    print(f"char ids ({len(ce)}): {ce[:16]} ...")
    print(f"word ids ({len(we)}): {we}")
    print(f"char round trip exact: {char_decode(ce, cv) == sample}")
    print(f"word round trip: {word_decode(we, wv)!r}  (case lost)")

    unseen = "The astronaut repairs the spaceship in orbit!"
    print(f"\nunseen: {unseen!r}")
    print(f"word ids: {word_encode(unseen, wv)}")
    print(f"word decode: {word_decode(word_encode(unseen, wv), wv)!r}")
    print(f"word OOV rate: {oov_rate(unseen, wv):.3f}")
    print(f"char OOV count: {sum(i == cv[UNK] for i in char_encode(unseen, cv))}")
    print(f"char unk for emoji: {char_encode('hi 🙂', cv)}")

    print("\nlength comparison (tokens per sentence):")
    for s in lines[:3]:
        print(f"  chars={len(char_encode(s, cv)):3d} words={len(word_encode(s, wv)):2d}  {s}")


if __name__ == "__main__":
    main()
