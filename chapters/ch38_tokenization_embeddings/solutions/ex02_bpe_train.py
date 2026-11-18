"""
Exercise 02 — Train a Byte-Level BPE Tokenizer from Scratch       [Tier: ★ Core]
Chapter 38 · Pattern: greedy pair merging / counting · Target time: 35 min

Problem
-------
Train a byte-level byte-pair-encoding (BPE) tokenizer on ``data/corpus.txt``.

- The base vocabulary is the 256 byte values (ids 0..255), so *any* string can be encoded.
- Pre-tokenize the text into "words" with the regex ``PRETOKEN`` (a leading space stays
  attached to the word, as in GPT-2) and count each distinct word once with its frequency.
- Repeat ``num_merges`` times: count all adjacent id pairs (weighted by word frequency),
  pick the most frequent pair (ties: the smallest pair tuple), give it the next new id
  (256, 257, ...), and replace every occurrence in every word.
- Return the ordered list of merges and the vocabulary ``id -> bytes``.

Examples
--------
>>> merges, vocab = train_bpe("aaab aaab", 2)
>>> [vocab[256 + i] for i in range(2)]
[b'aa', b'aaa']

Constraints
-----------
- Deterministic: same corpus and ``num_merges`` -> same merges.
- Stop early if no pair occurs at least twice.

Hints
-----
- Work on a ``dict[tuple[int, ...], int]`` of word -> frequency, not on the raw text.
- ``merge_ids`` walks the list once: if ``ids[i:i+2] == pair`` emit ``new_id`` and skip 2.
- ``max(counts.items(), key=lambda kv: (kv[1], -kv[0][0], -kv[0][1]))`` = highest count,
  smallest pair on ties.

Approach ladder
---------------
1. Brute force — recount pairs over the whole raw byte stream after every merge:
   O(M · N) for M merges over N bytes.
2. Improved   — count over *distinct pre-tokenized words* weighted by frequency:
   O(M · U) where U = total bytes of unique words (much smaller than N). This is what
   we implement and what most teaching implementations do.
3. Optimal    — keep a pair->count index and a pair->words inverted index and update only
   the words that contain the merged pair (plus a heap for the max): near O(N log V)
   overall. Production trainers (e.g. Rust implementations) do this.

Follow-ups
----------
- Why byte-level instead of character-level? (No OOV ever; 256-symbol base alphabet.)
- Why pre-tokenize? (Merges never cross word boundaries, so "dog." and "dog" share tokens.)
- How does vocabulary size trade off against sequence length and embedding-table size?
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "corpus.txt"
# A leading space stays attached to the following word: " cat", " sleeps", "."
PRETOKEN = re.compile(r" ?[A-Za-z]+| ?[0-9]+| ?[^\sA-Za-z0-9]+|\s+")


def pretokenize(text: str) -> list[str]:
    return PRETOKEN.findall(text)


def word_freqs(text: str) -> dict[tuple[int, ...], int]:
    """Distinct pre-tokens as byte-id tuples, with their counts."""
    counts = Counter(pretokenize(text))
    return {tuple(w.encode("utf-8")): c for w, c in counts.items()}


def get_pair_counts(words: dict[tuple[int, ...], int]) -> Counter:
    counts: Counter = Counter()
    for ids, freq in words.items():
        for a, b in zip(ids, ids[1:]):
            counts[(a, b)] += freq
    return counts


def merge_ids(ids: tuple[int, ...], pair: tuple[int, int], new_id: int) -> tuple[int, ...]:
    out, i = [], 0
    while i < len(ids):
        if i + 1 < len(ids) and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return tuple(out)


def train_bpe(text: str, num_merges: int):
    """Return (merges, vocab): merges is a list of pairs; vocab maps id -> bytes."""
    words = word_freqs(text)
    vocab = {i: bytes([i]) for i in range(256)}
    merges: list[tuple[int, int]] = []
    for step in range(num_merges):
        counts = get_pair_counts(words)
        if not counts:
            break
        pair, cnt = max(counts.items(), key=lambda kv: (kv[1], -kv[0][0], -kv[0][1]))
        if cnt < 2:
            break
        new_id = 256 + step
        merges.append(pair)
        vocab[new_id] = vocab[pair[0]] + vocab[pair[1]]
        words = {merge_ids(w, pair, new_id): f for w, f in words.items()}
    return merges, vocab


def main() -> None:
    text = DATA.read_text(encoding="utf-8")
    print(f"corpus bytes: {len(text.encode('utf-8'))}  distinct pre-tokens: {len(word_freqs(text))}")
    print(f"pretokenize sample: {pretokenize('The cat sleeps, quietly.')}")

    merges, vocab = train_bpe(text, 120)
    print(f"\nlearned merges: {len(merges)}  vocab size: {len(vocab)}")
    print("first 20 merges (id: left + right -> token):")
    for k, (a, b) in enumerate(merges[:20]):
        nid = 256 + k
        print(f"  {nid}: {vocab[a]!r:>10} + {vocab[b]!r:<10} -> {vocab[nid]!r}")
    longest = sorted(vocab.values(), key=lambda t: (-len(t), t))[:8]
    print(f"longest tokens: {longest}")

    # Compression: total tokens over all pre-tokens after merging
    words = word_freqs(text)
    before = sum(len(w) * f for w, f in words.items())
    after_words = words
    for k, pair in enumerate(merges):
        after_words = {merge_ids(w, pair, 256 + k): f for w, f in after_words.items()}
    after = sum(len(w) * f for w, f in after_words.items())
    print(f"\ntokens before: {before}  after: {after}  bytes/token: {before / after:.2f}")

    toy_merges, toy_vocab = train_bpe("aaab aaab", 5)
    print(f"toy 'aaab aaab' merges: {[toy_vocab[256 + i] for i in range(len(toy_merges))]}")


if __name__ == "__main__":
    main()
