"""
Exercise 10 — Lab: Beam Search with Length Normalisation          [Tier: ◆ Extended]
Chapter 39 · Pattern: keep the k best partial hypotheses per step · Target time: 35 min

Problem
-------
``step_logprobs(prefix)`` returns a 1-D array of next-token log-probabilities over a vocabulary
of size V (token ``eos`` ends a hypothesis). Implement
``beam_search(step_logprobs, V, eos, k, max_len, alpha=0.0)`` returning the best hypotheses
as ``[(tokens, score), ...]`` sorted by score descending (ties: lexicographically smaller
tokens first), where

    score(seq) = (sum of log-probs of its tokens) / len(seq) ** alpha

and len counts generated tokens including EOS. Rules:

- A hypothesis that emits EOS is *finished* and moves to the finished pool (every EOS
  expansion is kept there). The k best *unfinished* expansions survive each step.
- After ``max_len`` steps the surviving unfinished hypotheses are candidates too (truncated).
- With k = 1 the alive beam follows the greedy path; unlike ``greedy`` it also remembers the
  EOS expansions along that path, so it can return a shorter, better-scoring prefix. Also implement ``exhaustive(...)`` that scores every possible
  sequence with the same rule (V ** max_len of them) and ``greedy(...)``.

Examples
--------
On the hand-made model in ``toy_model`` greedy picks "a" (0.55) and then wanders through a
flat distribution ("a a a a", probability 0.015 at max_len = 4); beam search with k = 2 keeps
"b" alive and finds "b <eos>" with probability 0.405.

Constraints
-----------
- Small V and max_len for ``exhaustive``. alpha >= 0.

Approach ladder
---------------
1. Brute force — enumerate all sequences: O(V^max_len) model calls. Exact, hopeless for real V.
2. Greedy      — argmax each step: O(max_len) model calls, but a high-probability first token can lead
   into a low-probability continuation (the toy model shows it).
3. Beam search — O(max_len · k) model calls and O(max_len · k·V log(k·V)) to rank expansions
   (O(k·V) with argpartition). Still approximate: beam width k = V^max_len would be exhaustive.

Follow-ups
----------
- Why length normalisation? Each token adds a log-prob <= 0, so raw sums favour short
  outputs (early EOS). Dividing by len**alpha (alpha ≈ 0.6–1.0 in practice; GNMT uses a
  ((5 + len) / 6) ** alpha variant) removes that bias; alpha = 1 can over-correct and prefer
  long, even truncated, outputs. Both shown in ``main``.
- Alive hypotheses at one step all have the same length, so ranking them by raw sum is the
  same as ranking by normalised score; normalisation matters only when comparing finished ones.
- Beam search is for "one best answer" tasks (translation, constrained outputs); open-ended
  chat usually samples (ex09) because beams are repetitive and bland.
- Batch the k beams as one forward pass and reorder each beam's KV cache (→ ex08) by the
  parent index of the surviving hypotheses.
- Beam search is not guaranteed to beat greedy: pruning can drop the prefix greedy keeps.
- Edge cases: k = 1, k > number of possible hypotheses, EOS as the very first token, max_len = 1.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

EPS = 1e-12


def toy_model():
    """Vocabulary 0=<eos>, 1='a', 2='b', 3='c'. Next-token probabilities depend on the last token."""
    table = {
        None: [0.00, 0.55, 0.45, 0.00],       # first token
        1: [0.10, 0.30, 0.30, 0.30],          # after 'a': flat, nothing likely
        2: [0.90, 0.05, 0.05, 0.00],          # after 'b': almost surely stop
        3: [0.60, 0.20, 0.20, 0.00],
    }

    def step(prefix):
        p = np.array(table[prefix[-1] if prefix else None], dtype=float)
        return np.log(np.maximum(p, EPS))
    return step


def random_bigram_model(V: int, seed: int):
    rng = np.random.default_rng(seed)
    logits = rng.standard_normal((V + 1, V)) * 2.0     # row V = start state
    logits[V, 0] = -np.inf                             # no empty output: EOS cannot come first

    def step(prefix):
        z = logits[prefix[-1] if prefix else V]
        return z - (z.max() + np.log(np.exp(z - z.max()).sum()))
    return step


def _score(total: float, length: int, alpha: float) -> float:
    return total / (length ** alpha)


def _ranked(cands, alpha):
    return sorted(((tuple(s), _score(t, len(s), alpha)) for s, t in cands), key=lambda c: (-c[1], c[0]))


def beam_search(step_logprobs, V: int, eos: int, k: int, max_len: int, alpha: float = 0.0):
    alive = [((), 0.0)]
    finished = []
    for _ in range(max_len):
        expansions = []
        for seq, total in alive:
            lp = step_logprobs(list(seq))
            for tok in range(V):
                cand = (seq + (tok,), total + float(lp[tok]))
                (finished if tok == eos else expansions).append(cand)
        expansions.sort(key=lambda c: (-c[1], c[0]))  # same length: raw sum ranks them
        alive = expansions[:k]
        if not alive:
            break
    return _ranked(finished + alive, alpha)


def greedy(step_logprobs, V: int, eos: int, max_len: int):
    seq, total = [], 0.0
    for _ in range(max_len):
        lp = step_logprobs(seq)
        tok = int(np.argmax(lp))
        seq.append(tok)
        total += float(lp[tok])
        if tok == eos:
            break
    return tuple(seq), total


def exhaustive(step_logprobs, V: int, eos: int, max_len: int, alpha: float = 0.0):
    cands = []
    for n in range(1, max_len + 1):
        for seq in itertools.product(range(V), repeat=n):
            if eos in seq[:-1] or (n < max_len and seq[-1] != eos):
                continue                               # EOS only at the end; short ones must end in EOS
            total = sum(float(step_logprobs(list(seq[:i]))[t]) for i, t in enumerate(seq))
            cands.append((seq, total))
    return _ranked(cands, alpha)


def show(seq):
    return " ".join("<eos>" if t == 0 else "abc"[t - 1] for t in seq)


def main() -> None:
    step = toy_model()
    g, gt = greedy(step, 4, 0, 4)
    print(f"greedy: {show(g):<12} p={math.exp(gt):.3f}")
    for k in (1, 2, 3):
        best, sc = beam_search(step, 4, 0, k, 4)[0]
        print(f"beam k={k}: {show(best):<10} p={math.exp(sc):.3f}")
    ex_best, ex_sc = exhaustive(step, 4, 0, 4)[0]
    print(f"exhaustive: {show(ex_best):<8} p={math.exp(ex_sc):.3f}")

    print("\nlength bias on a random bigram model (V=5, eos=0, max_len=6):")
    rb = random_bigram_model(5, 3910)
    for alpha in (0.0, 0.6, 1.0):
        top = beam_search(rb, 5, 0, 3, 6, alpha)[:3]
        print(f"  alpha={alpha}: " + "; ".join(f"{list(s)} score={sc:.3f}" for s, sc in top))
    for alpha in (0.0, 0.7, 1.0):
        same = beam_search(rb, 5, 0, 5 ** 6, 6, alpha)[0] == exhaustive(rb, 5, 0, 6, alpha)[0]
        print(f"  huge beam == exhaustive (alpha={alpha}):", same)


if __name__ == "__main__":
    main()
