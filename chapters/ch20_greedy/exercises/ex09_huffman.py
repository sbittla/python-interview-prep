"""
Exercise 09 — Huffman Coding                                       [Tier: ○ Reference]
Chapter 20 · Pattern: greedy merge of two smallest (min-heap) · Target time: 35 min

Problem
-------
Given symbol frequencies, build an optimal prefix-free binary code: no codeword is a prefix
of another, and the total encoded length sum(freq[s] * len(code[s])) is minimal.
Implement `huffman_codes(freqs)` (deterministic tie-breaking), `encode`, `decode`, and
`cost(freqs)` which returns the minimal total bit length (the sum of all merge weights).

Examples
--------
>>> cost({"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45})
224
>>> cost({"x": 7})
7

Constraints
-----------
- 1 <= number of symbols <= 256, frequencies are positive integers.

Hints
-----
- Put (weight, tie_breaker, tree) in the heap so trees are never compared directly.
- A single distinct symbol needs a 1-bit code by convention ("0").

Follow-ups
----------
- Connect n ropes with minimum total cost: identical to `cost`.
- Canonical Huffman codes (sorted by length, then symbol) make the code table compact.
"""
from __future__ import annotations

import heapq
from itertools import count


def huffman_codes(freqs: dict[str, int]) -> dict[str, str]:
    raise NotImplementedError("TODO")


def cost(freqs: dict[str, int]) -> int:
    raise NotImplementedError("TODO")


def encode(text: str, codes: dict[str, str]) -> str:
    raise NotImplementedError("TODO")


def decode(bits: str, codes: dict[str, str]) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    freqs = {"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45}
    codes = huffman_codes(freqs)
    print("symbol freq code")
    for sym in sorted(codes):
        print(f"  {sym}    {freqs[sym]:>3}  {codes[sym]}")
    weighted = sum(freqs[s] * len(codes[s]) for s in freqs)
    print("weighted length:", weighted, "| cost():", cost(freqs), "| fixed 3-bit:", 3 * sum(freqs.values()))
    text = "abacabadf"
    bits = encode(text, codes)
    print("encode", repr(text), "->", bits)
    print("decode back ->", repr(decode(bits, codes)))
    print("single symbol:", huffman_codes({"z": 4}), "cost", cost({"z": 4}))


if __name__ == "__main__":
    main()
