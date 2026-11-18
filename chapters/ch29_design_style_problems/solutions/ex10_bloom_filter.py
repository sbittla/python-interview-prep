"""
Exercise 10 — Bloom Filter                         [Tier: ◆ Extended]
Chapter 29 · Pattern: bit array + k hash functions · Target time: 30 min

Problem
-------
Implement a Bloom filter: a set-membership structure that may return false positives
but never false negatives, using a fixed number of bits.

    bf = BloomFilter(m_bits, k_hashes)
    bf.add(item)                -> None
    item in bf                  -> bool   ("possibly present" / "definitely absent")
    BloomFilter.for_capacity(n, fp_rate) -> filter sized for n items at target error rate

Use deterministic hashing (`hashlib`, not the built-in `hash`, which is salted per
process for str) and derive the k indexes with double hashing: idx_i = (h1 + i*h2) mod m.

Examples
--------
>>> bf = BloomFilter.for_capacity(1000, 0.01)
>>> bf.m, bf.k
(9586, 7)
>>> bf.add("alice"); "alice" in bf, "bob" in bf
(True, False)

Constraints
-----------
- Items are strings (encode as UTF-8). m up to 10**8 bits.

Approach ladder
---------------
1. Exact set — `set()` of items: no false positives, but memory grows with item size
   (tens of bytes per entry plus the items themselves).
2. Single hash into a bit array — 1 bit-ish per item but high collision rate.
3. k hashes into m bits — with m = -n ln p / (ln 2)^2 and k = (m/n) ln 2 the false
   positive rate is about p. For p = 1% that is ~9.6 bits per item regardless of item size.

Hints
-----
- Store bits in a `bytearray(ceil(m / 8))`; bit i lives in byte i >> 3, mask 1 << (i & 7).
- Two 64-bit halves of one SHA-256 digest give h1 and h2 (force h2 odd so it is never 0).
- Theoretical FP rate after n inserts: (1 - e^(-k n / m)) ** k.

Follow-ups
----------
- Deletion: a counting Bloom filter (small counters instead of bits).
- Union of two filters with the same m, k = bitwise OR.
- Where used: LSM-tree databases skip disk reads for absent keys; CDN "one-hit wonder"
  filtering; checking leaked-password lists without storing them.
"""
from __future__ import annotations

import hashlib
import math


def _hashes(item: str) -> tuple[int, int]:
    digest = hashlib.sha256(item.encode("utf-8")).digest()
    h1 = int.from_bytes(digest[:8], "big")
    h2 = int.from_bytes(digest[8:16], "big") | 1
    return h1, h2


class BloomFilter:
    def __init__(self, m: int, k: int) -> None:
        if m <= 0 or k <= 0:
            raise ValueError("m and k must be positive")
        self.m, self.k = m, k
        self.bits = bytearray((m + 7) // 8)
        self.n = 0                                   # items added (for stats)

    @classmethod
    def for_capacity(cls, n: int, fp_rate: float) -> "BloomFilter":
        m = math.ceil(-n * math.log(fp_rate) / (math.log(2) ** 2))
        k = max(1, round(m / n * math.log(2)))
        return cls(m, k)

    def _indexes(self, item: str):
        h1, h2 = _hashes(item)
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str) -> None:
        for idx in self._indexes(item):
            self.bits[idx >> 3] |= 1 << (idx & 7)
        self.n += 1

    def __contains__(self, item: str) -> bool:
        return all(self.bits[idx >> 3] & (1 << (idx & 7)) for idx in self._indexes(item))

    def expected_fp_rate(self) -> float:
        return (1 - math.exp(-self.k * self.n / self.m)) ** self.k

    def fill_ratio(self) -> float:
        return sum(bin(b).count("1") for b in self.bits) / self.m


def main() -> None:
    bf = BloomFilter.for_capacity(1000, 0.01)
    print(f"sized for n=1000, p=1%: m={bf.m} bits ({bf.m / 8 / 1024:.2f} KiB), k={bf.k}")
    members = [f"user-{i}" for i in range(1000)]
    for item in members:
        bf.add(item)
    print("false negatives:", sum(item not in bf for item in members))
    probes = [f"other-{i}" for i in range(20_000)]
    fp = sum(item in bf for item in probes)
    print(f"false positives: {fp} / {len(probes)} = {fp / len(probes):.4f}")
    print(f"theoretical rate: {bf.expected_fp_rate():.4f}   bits set: {bf.fill_ratio():.3f}")

    print("\nover-filling the same filter to 3000 items:")
    for i in range(1000, 3000):
        bf.add(f"user-{i}")
    fp = sum(item in bf for item in probes)
    print(f"false positives: {fp / len(probes):.4f}   theoretical: {bf.expected_fp_rate():.4f}")

    print("\nk trade-off at m=9586, n=1000 (theory):")
    for k in (1, 3, 5, 7, 10, 15):
        rate = (1 - math.exp(-k * 1000 / 9586)) ** k
        print(f"  k={k:<2} -> {rate:.4f}")


if __name__ == "__main__":
    main()
