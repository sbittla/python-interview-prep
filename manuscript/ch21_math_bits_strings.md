# Chapter 21. Math, Bits and String Algorithms

◆ Extended · Tracks S, M, L · Study time ≈ 5 h · Prerequisites: Ch. 8 (Big-O), Ch. 9 (strings, hashing)

**Learning objectives**

- Write Euclid, a sieve and fast power; name the built-ins that replace them.
- Use bit operators on unbounded and negative ints.
- Match strings in O(n + m) with KMP; use a rolling hash with verification.
- Prove reservoir sampling and Fisher–Yates uniform; spot the biased shuffle.

> **Recognise it**
>
> | Signal | Reach for |
> |---|---|
> | "modulo 10⁹ + 7", huge exponent | `pow(a, b, m)`, factorial tables |
> | "appears twice/thrice except one", O(1) space | XOR, bit counting |
> | n ≤ 20, "all subsets" | bitmasks |
> | "all occurrences", "period" | KMP |
> | "duplicate substring" | rolling hash |
> | unknown-length stream, "shuffle" | reservoir, Fisher–Yates |

## 21.1 GCD/LCM (`math.gcd`, `math.lcm`)

Euclid, `while b: a, b = b, a % b`, then `abs(a)`, takes O(log min(a, b)) iterations; trying
every divisor is O(min(a, b)). lcm(a, b) = `abs(a // gcd(a, b) * b)`, or 0 if either is
0. Both built-ins are variadic (3.9+):

```python
import math
print(math.gcd(12, 18, 30), math.gcd(-4, 6), math.lcm(4, 6, 10), math.lcm(0, 5))
```

```text
6 2 60 0
```

→ repo: `chapters/ch21_math_bits_strings/solutions/ex01_gcd_lcm_fractions.py`

## 21.2 Primes: sieve of Eratosthenes, `math.isqrt`

Trial division of every k ≤ n is O(n√n); the sieve is O(n log log n) time, O(n) space.

```python
from math import isqrt

def sieve(n: int) -> list[int]:
    if n < 2:
        return []
    flags = bytearray([1]) * (n + 1)
    flags[0] = flags[1] = 0
    for p in range(2, isqrt(n) + 1):
        if flags[p]:                       # p is prime: cross off p*p, p*p+p, ...
            flags[p * p::p] = bytes(len(range(p * p, n + 1, p)))
    return [k for k in range(n + 1) if flags[k]]

print(sieve(30), len(sieve(10**6)))
print(isqrt(10**30 - 1), int((10**30 - 1) ** 0.5))
```

```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29] 78498
999999999999999 1000000000000000
```

Start at p·p: smaller multiples k·p (k < p) were crossed off by a smaller prime. Line two shows
why to use `math.isqrt` (3.8+): the float root overshoots. Repo extras: SPF
table, segmented sieve. → repo: `chapters/ch21_math_bits_strings/solutions/ex02_sieve_factorise.py`

## 21.3 Modular arithmetic and fast exponentiation (`pow(a, b, m)`)

You may reduce mod m before or after each +, −, ×; division needs a modular inverse.
Python's `x % m` lies in [0, m) for m > 0 even when x < 0 (unlike C/Java).

**Worked problem 1 — a^b mod m, b up to 10¹⁸.** Rung 1, `a ** b % m`, first builds a
b·log₂a-bit number. Rung 2 multiplies b times: O(b), 10¹⁸ steps. Rung 3 recurses on a^b = (a^⌊b/2⌋)² ·
a^(b mod 2): O(log b) time and stack. Rung 4 walks the bits of b: O(log b), O(1) space.

```python
def mod_pow(a: int, b: int, m: int) -> int:     # b >= 0, m >= 1
    result, a = 1 % m, a % m           # 1 % m handles m == 1
    while b:
        if b & 1:                      # this bit of b is set: multiply it in
            result = result * a % m
        a = a * a % m                  # a, a^2, a^4, a^8, ...
        b >>= 1
    return result

P = 10**9 + 7
print(mod_pow(7, 10**18, P), pow(7, 10**18, P), mod_pow(-2, 3, 5), mod_pow(5, 0, 1))
print(pow(3, -1, 11), pow(3, P - 2, P) == pow(3, -1, P))
```

```text
259616729 259616729 2 0
4 True
```

**Inverse:** exists iff gcd(a, m) = 1; extended Euclid finds it in O(log m), Fermat gives
a^(p−2) for p prime and p ∤ a (it silently returns 0 if a ≡ 0); `pow(a, -1, m)` (3.8+) raises
`ValueError` if none exists. **Wrong but
tempting:** Fermat with a composite modulus; `result = 1` instead of `1 % m`. Edge cases: b = 0,
m = 1, a < 0, a ≡ 0. Follow-up: Fibonacci in O(log n) is this loop on 2×2 matrices.
→ repo: `chapters/ch21_math_bits_strings/solutions/ex03_mod_pow_inverse.py`

## 21.4 Combinatorics (`math.comb`, `math.perm`), Pascal's triangle

`math.comb`/`math.perm` (3.8+) are exact, but C(10⁵, 5·10⁴) has about 10⁵ bits. Pascal's rule C(n, k) = C(n−1, k−1) +
C(n−1, k) builds an O(n²) table using only additions, so any modulus works. For many queries mod
a prime p > N, precompute `fact[i] = fact[i-1] * i % p` up to N, **one** inverse
`inv[N] = pow(fact[N], p - 2, p)`, then `inv[i-1] = inv[i] * i % p` downwards; each query is
`fact[n] * inv[k] * inv[n-k] % p`: O(N + log p) setup, O(1) per query. For n ≥ p, the repo
uses Lucas' theorem.
→ repo: `chapters/ch21_math_bits_strings/solutions/ex04_ncr_mod_p.py`

## 21.5 Bit basics: AND, OR, XOR, shifts, masks

Test bit i with `x >> i & 1`; set, clear, toggle with `x | (1 << i)`, `x & ~(1 << i)`,
`x ^ (1 << i)`. `x & -x` isolates the lowest set bit; `x & (x - 1)` drops it.
Python ints are unbounded; a negative int acts as two's complement with *infinitely many* leading
1s: `~x == -x - 1` and `>>` floors. Emulate 32-bit code by masking with
`0xFFFFFFFF`.

```python
x = 0b101100                                   # 44
print(f"{x & -x:#b} {x & (x - 1):#b} {x.bit_length()}", bin(-5), ~5, -5 >> 1)
u = -5 & 0xFFFFFFFF                            # 32-bit two's-complement view
print(u, u - (1 << 32) if u >> 31 else u)      # convert back to signed
```

```text
0b100 0b101000 6 -0b101 -6 -3
4294967291 -5
```

`1 << 3 - 1` is 4: parenthesise shifts. `while x: x >>= 1` never ends for negative x.

## 21.6 Bit tricks: single number (XOR), count bits, power of two, subsets via bitmask

**Worked problem 2 — Single number.** x ^ x = 0 and XOR is commutative, so XOR-ing all values
cancels the pairs: O(n), O(1) space. Harder: the others appear **three** times. Rung 1, a
`Counter`: O(n) time and space. Rung 2 counts each of 32 bit positions mod 3: O(32n) time, O(1)
space, plus a sign fix when bit 31 is set. Rung 3 keeps a mod-3 counter for all bits in two
masks: one pass, no sign fix.

```python
from functools import reduce
from operator import xor

def single_three(nums: list[int]) -> int:      # others appear three times
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos              # bits seen 1 time (mod 3)
        twos = (twos ^ x) & ~ones              # bits seen 2 times (mod 3)
    return ones

print(reduce(xor, [4, 1, 2, 1, 2]), single_three([2, 2, 3, 2]),
      single_three([-2, -2, 1, 1, -3, 1, -3, -3, -4, -2]))
```

```text
4 3 -4
```

Each bit cycles 00 → `ones` → `twos` → 00. **Wrong but tempting:** XOR for triples (three
copies XOR to x); rung 2 without the sign fix returns -4 as 4294967292. Edge cases: negatives,
−2³¹, a single element. Follow-up: two singles — XOR all, split by the lowest set bit.

**Counting bits 0..n:** `bits[i] = bits[i >> 1] + (i & 1)`, O(n) vs O(n log n) for a
popcount each; one popcount is `x.bit_count()` (3.10+) or Kernighan's `x &= x - 1` loop.
**Power of two:** `x > 0 and x & (x - 1) == 0`. **Subsets:** mask m in `range(1 << n)` holds
item i iff `m >> i & 1`; O(n·2ⁿ) (backtracking §18.2, bitmask DP §19.13). Submasks: step
`sub = (sub - 1) & mask`. → repo: `chapters/ch21_math_bits_strings/solutions/ex05_single_number.py`,
`chapters/ch21_math_bits_strings/solutions/ex06_count_bits_power_two.py`,
`chapters/ch21_math_bits_strings/solutions/ex07_subsets_bitmask.py`

## 21.7 String matching: KMP

**Worked problem 3 — All occurrences, overlaps included.** Rung 1 compares at every start: O(nm)
on `"aaa…a"`/`"aa…ab"`. Rung 2 loops `text.find(pattern, i + 1)`: no documented O(n + m)
bound. Rung 3, KMP, never re-reads matched text: O(n + m) time, O(m)
space. pi[i] is the longest proper prefix of `s[:i+1]` that is also its suffix (a *border*).
After a mismatch with k characters matched, border pi[k−1] is still matched: continue there.

```python
def prefix_function(s: str) -> list[int]:
    pi = [0] * len(s)                  # pi[i]: longest proper border of s[:i+1]
    k = 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]              # fall back to the next shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi

def kmp_search(text: str, pattern: str) -> list[int]:
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    pi, k, hits = prefix_function(pattern), 0, []
    for i, ch in enumerate(text):      # i never moves backwards
        while k and ch != pattern[k]:
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:                     # match ends at i
            hits.append(i - m + 1)
            k = pi[k - 1]              # keep going: overlaps allowed
    return hits

print(prefix_function("aabaaab"), kmp_search("abababa", "aba"), kmp_search("aaaaa", "aa"))
```

```text
[0, 1, 0, 1, 2, 2, 3] [0, 2, 4] [0, 1, 2, 3]
```

**Why O(n + m):** k rises at most once per character and each fallback lowers it, so fallbacks ≤
n (as in §12.4). The shortest period is p = n − pi[n−1] (`"abcab"` → 3); s is a
whole repetition of it iff p divides n. **Wrong but tempting:** resetting k to 0 on a mismatch
or after a match (misses overlaps). Edge cases: empty pattern, m > n, overlaps, m = 1.
Follow-up: shortest palindrome by prepending, from `prefix_function(s + "#" + s[::-1])`.
→ repo: `chapters/ch21_math_bits_strings/solutions/ex08_kmp_z_function.py`

## 21.8 Rabin-Karp rolling hash (and deduplication use)

**Worked problem 4.** Read a window as a base-B number mod M. Rung 1 re-hashes each window, O(m)
each; rolling (drop the leaving term, append one) is O(1) per window. Equal hashes do not prove
equal strings, so verify every hit: O(n + m + occ·m) expected for occ matches, O(nm) worst
case. KMP stays O(n + m) even on `"a" * n` with pattern `"a" * (n // 2)`.

```python
def rk_search(text: str, pattern: str, mod: int = (1 << 61) - 1, base: int = 911_382_323):
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return list(range(n + 1)) if m == 0 else []
    high = pow(base, m - 1, mod)               # weight of the leaving character
    hp = hw = 0
    for i in range(m):
        hp = (hp * base + ord(pattern[i])) % mod
        hw = (hw * base + ord(text[i])) % mod
    hits = []
    for i in range(n - m + 1):
        if hw == hp and text[i:i + m] == pattern:   # verify every hash hit
            hits.append(i)
        if i + m < n:                               # roll the window by one
            hw = ((hw - ord(text[i]) * high) * base + ord(text[i + m])) % mod
    return hits

print(rk_search("abracadabra", "abra"), rk_search("abracadabra", "abra", mod=5, base=2))
```

```text
[0, 7] [0, 7]
```

With modulus 5, three of the six non-matching windows collide; verification keeps the answer
right. Edge cases: m = 0, m > n, all-equal text, tiny modulus. With a random base, two fixed different windows
collide with probability ≤ (m − 1)/M: use a large prime M and a random base per run.

**Follow-up: deduplication.** Map each length-L window's hash to its starts and slice-compare
only on a hit, like `dict` (§6.5). Longest duplicate substring: binary search on L with this
check, O(n log n) expected (O(n² log n) with sliced substrings).
→ repo: `chapters/ch21_math_bits_strings/solutions/ex09_rabin_karp.py`

## 21.9 Z-function ○

z[i] = longest common prefix of s and `s[i:]`, O(n) via the rightmost match window. In z of
`pattern + text`, each i ≥ m with z[i] ≥ m is a match at i − m: O(n + m).

## 21.10 Randomised algorithms: reservoir sampling, shuffle ◆

**Reservoir sampling.** Rung 1 stores the stream for `random.sample`: O(n) memory. Algorithm R
keeps the first k; item i (0-based) replaces a random slot with probability k/(i+1): O(k)
memory. It survives each later step t with probability 1 − 1/(t+1); the product telescopes to k/n.

**Shuffle.** Pick-and-pop is uniform but O(n²). Fisher–Yates is O(n): for i from n−1 down, swap
a[i] with a[j], j uniform in [0, i]: n! equally likely choice sequences, one per permutation.
CPython's `random.shuffle` uses this loop.

```python
import random

def reservoir_sample(stream, k: int, randbelow) -> list:
    res = []
    for i, item in enumerate(stream):
        if i < k:
            res.append(item)
        else:
            j = randbelow(i + 1)               # uniform in [0, i]
            if j < k:                          # probability k / (i + 1)
                res[j] = item
    return res

def fisher_yates(items: list, randbelow) -> list:
    a = list(items)
    for i in range(len(a) - 1, 0, -1):
        j = randbelow(i + 1)                   # j in [0, i]: i itself included
        a[i], a[j] = a[j], a[i]
    return a

rng = random.Random(21)
print(reservoir_sample(range(10), 3, rng.randrange), fisher_yates("abcde", rng.randrange))
```

```text
[0, 3, 2] ['e', 'a', 'c', 'b', 'd']
```

**Wrong but tempting:** j uniform in [0, n) for every i: nⁿ equal paths cannot split evenly over
n! permutations for n ≥ 3. Exact counts over every choice sequence (repo):

```text
exact fisher_yates n=3: [1, 1, 1, 1, 1, 1]
exact pick_pop     n=3: [1, 1, 1, 1, 1, 1]
exact naive        n=3: [4, 5, 5, 5, 4, 4]  <- biased
```

`randbelow(i)` gives only cyclic permutations (Sattolo).
→ repo: `chapters/ch21_math_bits_strings/solutions/ex10_reservoir_shuffle.py`

## 21.11 Practice set

Ten exercises below. More: Chapter 45, problems
128–132.

## Interviewer's view

- **Name the built-in** (`pow`, `math.gcd`, `str.find`); implement if asked.
- **Overflow:** say where C/Java would overflow; mask to emulate 32 bits.
- **Prove, don't assert:** KMP's bound, Fisher–Yates' n! paths, reservoir's k/n; raise hash
  collisions before you are asked.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | GCD/LCM, fractions | ★ | Euclid |
| ex02 | Sieve, SPF, segmented sieve | ★ | sieve |
| ex03 | Modular power and inverse | ★ | fast power |
| ex04 | nCr mod p, Pascal, Lucas | ★ | factorial tables |
| ex05 | Single number I and II | ★ | XOR, bits mod 3 |
| ex06 | Counting bits, power of two | ★ | bit tricks + DP |
| ex07 | Subsets, submasks, Gosper | ★ | bitmask |
| ex08 | KMP, repeating unit, Z-function | ★ | border arrays |
| ex09 | Rabin–Karp, longest duplicate | ★ | rolling hash |
| ex10 | Reservoir, Fisher–Yates | ◆ | randomised |

Index: `chapters/ch21_math_bits_strings/README.md`.

## Checkpoint quiz

1. Why does the sieve start at p·p?
2. How many multiplications does fast power need for b = 10¹⁸?
3. Why does `single_three` need no sign fix?
4. Why do KMP's fallbacks total at most n?
5. Why is swapping a[i] with any index in [0, n) biased for n = 3?

<details>
<summary>Answers</summary>

1. Smaller multiples k·p (k < p) already fell to a smaller prime.
2. At most ≈ 2·log₂ b ≈ 120 (square per bit, multiply per set bit).
3. Negatives act as infinite two's complement.
4. k rises at most once per character; each fallback lowers it.
5. 27 equal paths over 6 permutations; 6 does not divide 27.

</details>

## Summary card

- **GCD** `a, b = b, a % b`, O(log); lcm `a // g * b`. **Sieve** from p·p to `isqrt(n)`.
- **Mod:** reduce every step; inverse by `pow(a, -1, m)`, ext-Euclid, Fermat (p prime, p ∤ a).
- **Fast power:** O(log b), start at `1 % m`. **nCr:** fact + inv_fact, O(1) per query.
- **Bits:** `x & -x`, `x & (x - 1)`; negatives = infinite 1s; mask `0xFFFFFFFF`.
- **Single number:** XOR pairs; `ones`/`twos` triples. **Subsets:** masks `0..2ⁿ−1`.
- **KMP:** `k = pi[k-1]`, O(n + m). **Rabin–Karp:** roll, always verify.
- **Random:** reservoir k/(i+1); Fisher–Yates j ∈ [0, i].
