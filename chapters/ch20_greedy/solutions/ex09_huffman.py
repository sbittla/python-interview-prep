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

Approach ladder
---------------
1. Fixed-length code — ceil(log2(k)) bits per symbol. Simple, not optimal for skewed data.
2. Huffman — repeatedly merge the two least frequent trees (min-heap); the merged weight is
   their sum. O(k log k). Exchange argument: in some optimal tree the two rarest symbols are
   deepest siblings; merging them reduces the problem to k-1 symbols.
3. Cost only — the total encoded length equals the sum of all merge weights, so you can
   compute it with just a heap of numbers (the "connect ropes" problem).

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
    if len(freqs) == 1:
        return {next(iter(freqs)): "0"}
    tie = count()
    # A tree is either a symbol (str) or a pair (left, right).
    heap = [(f, next(tie), sym) for sym, f in sorted(freqs.items())]
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, next(tie), (left, right)))
    codes: dict[str, str] = {}

    def walk(tree, prefix: str) -> None:
        if isinstance(tree, str):
            codes[tree] = prefix
            return
        walk(tree[0], prefix + "0")
        walk(tree[1], prefix + "1")

    walk(heap[0][2], "")
    return codes


def cost(freqs: dict[str, int]) -> int:
    heap = list(freqs.values())
    if len(heap) == 1:
        return heap[0]                       # one symbol, one bit each
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        merged = heapq.heappop(heap) + heapq.heappop(heap)
        total += merged
        heapq.heappush(heap, merged)
    return total


def encode(text: str, codes: dict[str, str]) -> str:
    return "".join(codes[ch] for ch in text)


def decode(bits: str, codes: dict[str, str]) -> str:
    reverse = {v: k for k, v in codes.items()}
    out, cur = [], ""
    for b in bits:
        cur += b
        if cur in reverse:                   # prefix-free: first match is the symbol
            out.append(reverse[cur])
            cur = ""
    return "".join(out)


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
