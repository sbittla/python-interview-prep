"""
Exercise 03 — Property-Style Tests with a Seeded Generator [Tier: ◆ Extended]
Chapter 31 · Pattern: properties + random generation + shrinking · Target time: 30 min

Problem
-------
Run-length encoding turns "aaabcc" into "a3b1c2". Implement ``rle_encode`` and
``rle_decode`` for strings of lowercase letters, then test them with *properties* instead of
hand-picked examples:

1. round trip:      decode(encode(s)) == s
2. canonical form:  no two adjacent groups in the encoding share a letter
3. size bound:      the counts in the encoding sum to len(s)

Write ``find_counterexample(prop, seed, trials)`` that generates random inputs with
``random.Random(seed)`` (no third-party library), and ``shrink(prop, s)`` that reduces a failing
input to a minimal one. Show that the property suite catches ``rle_decode_buggy``, which reads
only one digit of each count, and shrinks the failure to the smallest string that exposes it.

Examples
--------
>>> rle_encode("aaabcc")
'a3b1c2'
>>> rle_decode("a12b1")
'aaaaaaaaaaaab'

Constraints
-----------
- Input strings use letters a-z only (digits would make the format ambiguous).

Approach ladder
---------------
1. Brute force — hand-written examples; "aaabcc" passes for the buggy decoder too, because
   no run is 10 or longer.
2. Improved   — uniformly random strings: runs of 10+ are rare, so the bug hides.
3. Optimal    — a generator biased toward long runs, a fixed seed for reproducibility, and a
   greedy shrinker that deletes/simplifies characters while the property still fails.
   Cost: O(trials x n) to search, O(n^2) property calls to shrink.

Follow-ups
----------
- Why fix the seed? A failing CI run must be reproducible; print the seed with the failure.
- The ``hypothesis`` library does generation + shrinking for you; know the idea even when you
  cannot install it.
"""
from __future__ import annotations

import random
import re
from collections.abc import Callable
from itertools import groupby

import pytest


def rle_encode(s: str) -> str:
    return "".join(f"{ch}{len(list(group))}" for ch, group in groupby(s))


def rle_decode(code: str) -> str:
    return "".join(ch * int(count) for ch, count in re.findall(r"([a-z])(\d+)", code))


def rle_decode_buggy(code: str) -> str:
    """The version under review: reads exactly one digit per count."""
    out = []
    for i in range(0, len(code), 2):
        out.append(code[i] * int(code[i + 1]))
    return "".join(out)


def solve(s: str) -> str:
    return rle_encode(s)


# ------------------------------------------------------------------ generator + properties
def random_run_string(rng: random.Random, max_runs: int = 6, max_run: int = 14) -> str:
    """Biased generator: build the string from runs so long runs are common."""
    parts = []
    for _ in range(rng.randint(0, max_runs)):
        parts.append(rng.choice("abc") * rng.randint(1, max_run))
    return "".join(parts)


def roundtrip(decoder: Callable[[str], str]) -> Callable[[str], bool]:
    def prop(s: str) -> bool:
        try:
            return decoder(rle_encode(s)) == s
        except Exception:  # noqa: BLE001 - a crash is also a property failure
            return False

    return prop


def canonical(s: str) -> bool:
    letters = re.findall(r"[a-z]", rle_encode(s))
    return all(a != b for a, b in zip(letters, letters[1:]))


def size_bound(s: str) -> bool:
    return sum(int(n) for n in re.findall(r"\d+", rle_encode(s))) == len(s)


def find_counterexample(prop: Callable[[str], bool], seed: int, trials: int = 300) -> str | None:
    rng = random.Random(seed)
    for _ in range(trials):
        s = random_run_string(rng)
        if not prop(s):
            return s
    return None


def shrink(prop: Callable[[str], bool], s: str) -> str:
    """Greedy shrinking: keep any smaller/simpler variant that still fails."""
    improved = True
    while improved:
        improved = False
        candidates = [s[:i] + s[i + 1:] for i in range(len(s))]          # delete one char
        candidates += [s.replace(ch, "a") for ch in sorted(set(s)) if ch != "a"]  # simplify
        candidates += [s[:i] + "a" + s[i + 1:] for i in range(len(s)) if s[i] != "a"]
        for cand in candidates:
            if not prop(cand):
                s, improved = cand, True
                break
    return s


# ------------------------------------------------------------------ embedded pytest suite
SEEDS = [0, 1, 2, 3, 4]


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("prop", [roundtrip(rle_decode), canonical, size_bound],
                         ids=["roundtrip", "canonical", "size_bound"])
def test_properties_hold(prop, seed):
    assert find_counterexample(prop, seed) is None


def test_examples_still_matter():
    assert rle_encode("") == ""
    assert rle_encode("aaabcc") == "a3b1c2"
    assert rle_decode("a12b1") == "a" * 12 + "b"


def test_buggy_decoder_is_caught_and_shrunk():
    prop = roundtrip(rle_decode_buggy)
    failing = find_counterexample(prop, seed=0)
    assert failing is not None
    assert shrink(prop, failing) == "a" * 10


def main() -> None:
    print("rle_encode('aaabcc') =", rle_encode("aaabcc"))
    print("rle_decode('a12b1')  =", rle_decode("a12b1"))
    rng = random.Random(3)
    print("sample generated inputs (seed 3):", [random_run_string(rng, 3, 4) for _ in range(4)])
    print()
    for name, prop in [("roundtrip", roundtrip(rle_decode)), ("canonical", canonical),
                       ("size_bound", size_bound)]:
        found = [find_counterexample(prop, seed) for seed in SEEDS]
        failures = sum(f is not None for f in found)
        print(f"property {name:<10} seeds {SEEDS}: {failures} counterexamples")
    print()
    prop = roundtrip(rle_decode_buggy)
    print("hand-picked example 'aaabcc' passes the buggy decoder:", prop("aaabcc"))
    for seed in SEEDS:
        failing = find_counterexample(prop, seed)
        if failing is not None:
            print(f"seed {seed}: counterexample of length {len(failing)}: {failing!r}")
            minimal = shrink(prop, failing)
            print(f"shrunk to {minimal!r} (length {len(minimal)})")
            code = rle_encode(minimal)
            try:
                outcome = repr(rle_decode_buggy(code))
            except Exception as exc:  # noqa: BLE001
                outcome = f"{type(exc).__name__}: {exc}"
            print(f"  encode -> {code!r}; buggy decode -> {outcome}")
            break
    print()
    from ch31_testkit import print_results, run_embedded_tests

    print_results(run_embedded_tests(__file__))


if __name__ == "__main__":
    main()
