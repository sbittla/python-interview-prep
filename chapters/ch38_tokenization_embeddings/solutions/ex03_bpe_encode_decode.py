"""
Exercise 03 — BPE Encode and Decode (Round Trip)                  [Tier: ★ Core]
Chapter 38 · Pattern: rank-ordered greedy merging · Target time: 25 min

Problem
-------
Given the ordered merge list produced by ``train_bpe`` (Exercise 02), implement

- ``encode(text, merges) -> list[int]``: pre-tokenize, turn each piece into UTF-8 byte ids,
  then repeatedly apply the *earliest-learned* merge that is present in the piece until no
  learned merge applies.
- ``decode(ids, vocab) -> str``: concatenate the byte strings and decode as UTF-8
  (``errors="replace"`` so a cut in the middle of a multi-byte character shows ``\\ufffd``).

The round trip ``decode(encode(s)) == s`` must hold for *every* string, including text
with accents, CJK characters and emoji that never appeared in training.

Examples
--------
>>> merges, vocab = train_bpe("low lower lowest", 10)
>>> decode(encode("lowest slow", merges), vocab)
'lowest slow'

Constraints
-----------
- ``encode`` must give the same result as applying the merges one by one in training
  order over the whole piece (``encode_naive``).

Hints
-----
- Build ``rank = {pair: index}`` once. In each piece, find the adjacent pair with the
  smallest rank; merge all its occurrences; repeat.
- New ids are ``256 + rank``.

Approach ladder
---------------
1. Brute force — ``encode_naive``: for every merge in order, scan the piece: O(M · n)
   per piece even when most merges are irrelevant.
2. Optimal    — ``encode``: look only at pairs present in the piece and pick the lowest
   rank: O(n^2) per piece worst case, but n (piece length) is tiny, and we never touch
   the thousands of irrelevant merges. A cache of piece -> ids makes repeated words free.

Follow-ups
----------
- Why must encoding apply merges in training order? (A later merge may assume an earlier
  one already happened; other orders give token sequences the model never saw.)
- Streaming decode: why must you buffer incomplete UTF-8 sequences between tokens?
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from ex02_bpe_train import merge_ids, pretokenize, train_bpe

DATA = Path(__file__).resolve().parent.parent / "data" / "corpus.txt"


def encode_naive(text: str, merges: list[tuple[int, int]]) -> list[int]:
    out: list[int] = []
    for piece in pretokenize(text):
        ids = tuple(piece.encode("utf-8"))
        for k, pair in enumerate(merges):
            ids = merge_ids(ids, pair, 256 + k)
        out.extend(ids)
    return out


def encode_piece(ids: tuple[int, ...], rank: dict[tuple[int, int], int]) -> tuple[int, ...]:
    while len(ids) >= 2:
        candidates = [(rank[p], p) for p in zip(ids, ids[1:]) if p in rank]
        if not candidates:
            break
        r, pair = min(candidates)
        ids = merge_ids(ids, pair, 256 + r)
    return ids


def encode(text: str, merges: list[tuple[int, int]]) -> list[int]:
    rank = {pair: k for k, pair in enumerate(merges)}

    @lru_cache(maxsize=None)
    def cached(piece: str) -> tuple[int, ...]:
        return encode_piece(tuple(piece.encode("utf-8")), rank)

    out: list[int] = []
    for piece in pretokenize(text):
        out.extend(cached(piece))
    return out


def decode(ids: list[int], vocab: dict[int, bytes]) -> str:
    return b"".join(vocab[i] for i in ids).decode("utf-8", errors="replace")


def main() -> None:
    text = DATA.read_text(encoding="utf-8")
    merges, vocab = train_bpe(text, 120)

    for s in ["the farmer feeds the goat every morning.",
              "The engineer repairs the spaceship!",
              "café naïve 東京 🙂"]:
        ids = encode(s, merges)
        pieces = [vocab[i].decode("utf-8", errors="replace") for i in ids]
        print(f"text: {s!r}")
        print(f"  bytes={len(s.encode('utf-8'))} tokens={len(ids)} pieces={pieces}")
        print(f"  round trip ok: {decode(ids, vocab) == s}  matches naive: {ids == encode_naive(s, merges)}")

    emoji_ids = encode("🙂", merges)
    print(f"\nemoji ids: {emoji_ids}  (4 raw bytes, no merges learned)")
    print(f"decode first 2 bytes only: {decode(emoji_ids[:2], vocab)!r}")

    lines = text.splitlines()
    all_ok = all(decode(encode(l, merges), vocab) == l for l in lines)
    n_tok = sum(len(encode(l, merges)) for l in lines)
    n_bytes = sum(len(l.encode("utf-8")) for l in lines)
    print(f"corpus round trip ok: {all_ok}  bytes/token: {n_bytes / n_tok:.2f}")


if __name__ == "__main__":
    main()
