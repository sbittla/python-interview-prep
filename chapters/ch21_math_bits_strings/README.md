# Chapter 21 — Math, Bits and String Algorithms

Manuscript: `manuscript/ch21_math_bits_strings.md`. Standard library only.

| # | Exercise | Tier | Pattern | Rungs implemented | Section |
|---|---|---|---|---|---|
| 01 | [GCD / LCM of a list, fraction reduction](solutions/ex01_gcd_lcm_fractions.py) | ★ | Euclid's algorithm | divisor scan → Euclid → `math.gcd`/`lcm`, `Fraction` | 21.1 |
| 02 | [Sieve, SPF table, segmented sieve](solutions/ex02_sieve_factorise.py) | ★ | sieve of Eratosthenes | trial division → sieve → SPF factorise → segmented ◆ | 21.2 |
| 03 | [Fast modular power and modular inverse](solutions/ex03_mod_pow_inverse.py) | ★ | binary exponentiation, extended Euclid | O(b) loop → recursive → iterative; ext-Euclid vs Fermat | 21.3 |
| 04 | [nCr mod p and Pascal's triangle](solutions/ex04_ncr_mod_p.py) | ★ | factorial tables, Lucas | Pascal row/table → fact + inverse fact → Lucas ◆ | 21.4 |
| 05 | [Single number I and II](solutions/ex05_single_number.py) | ★ | XOR cancellation, bit counting mod 3 | Counter → XOR; Counter → per-bit count → ones/twos masks | 21.5–21.6 |
| 06 | [Counting bits, popcount, power of two](solutions/ex06_count_bits_power_two.py) | ★ | bit tricks + DP | shift → Kernighan → built-in; per-number → `bits[i>>1]` DP | 21.6 |
| 07 | [Subsets via bitmask, submasks, Gosper](solutions/ex07_subsets_bitmask.py) | ★ | integer as a set | sum per mask → lowest-bit DP; submask walk; Gosper's hack ◆ | 21.6 |
| 08 | [KMP prefix function, repeating unit, Z-function](solutions/ex08_kmp_z_function.py) | ★ (Z ○) | border arrays | brute → `str.find` loop → KMP; Z-function search | 21.7, 21.9 |
| 09 | [Rabin–Karp and longest duplicate substring](solutions/ex09_rabin_karp.py) | ★ (LDS ◆) | rolling hash + verification | brute → rolling hash; LDS: all lengths → binary search + slices → binary search + hash | 21.8 |
| 10 | [Reservoir sampling and Fisher–Yates](solutions/ex10_reservoir_shuffle.py) | ◆ | randomised algorithms | store-all → Algorithm R; pick-and-pop → Fisher–Yates; exact uniformity check | 21.10 |

Every solution cross-checks its optimal rung against the slower rungs (or the standard library)
in `main()`, and every test file compares them on seeded random inputs. Randomised code takes a
`randbelow` callable, so `ex10` proves uniformity *exactly* by enumerating every random-choice
sequence instead of relying on sampling noise.

## How to run

```bash
.venv/Scripts/python chapters/ch21_math_bits_strings/solutions/ex08_kmp_z_function.py
.venv/Scripts/python -m pytest chapters/ch21_math_bits_strings            # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch21_math_bits_strings  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 21                         # regenerate outputs/
```

Work in `exercises/` (stubs raise `NotImplementedError` and carry hints and wrong-but-tempting
answers instead of the full approach ladder); compare with `solutions/`; expected program output
is in `outputs/`.
