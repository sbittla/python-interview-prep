"""
Exercise 11 — Repetition Penalties and Stop Conditions             [Tier: ★ Core]
Chapter 39 · Pattern: logit processors + a streaming stop-string matcher · Target time: 30 min

Problem
-------
Logit processors (each returns a new array, input untouched):

1. ``repetition_penalty(logits, history, theta)``: for every *distinct* token id in history,
   divide its logit by theta if the logit is > 0, multiply by theta otherwise (theta >= 1).
   Dividing a negative logit would *raise* it: the classic sign bug.
2. ``frequency_presence(logits, history, freq, presence)``:
   logit[t] -= freq · count(t) + presence · [count(t) > 0]  (additive form).
3. ``no_repeat_ngram(logits, history, n)``: set to -inf every token that would complete an
   n-gram already present in history.

Stopping:

4. ``stream_with_stops(pieces, stop_strings, eos_piece, max_new_tokens)``: ``pieces`` is the
   decoded text of each generated token, in order. Emit text incrementally but never emit any
   part of a stop string: hold back the longest suffix of the pending text that is a prefix of
   some stop string. Stop on (in this priority per token) EOS, a stop string (output ends
   just before it; stop strings can span token boundaries), or max_new_tokens. Return
   ``(chunks_emitted, final_text, reason)`` with reason in {"eos", "stop", "length", "end"}.

Examples
--------
>>> repetition_penalty(np.array([2.0, -2.0, 1.0]), [0, 1, 1], 2.0).tolist()
[1.0, -4.0, 1.0]
>>> stream_with_stops(["Hel", "lo\\n", "\\nUs", "er:"], ["\\n\\nUser:"], None, 10)[1:]
('Hello', 'stop')

Constraints
-----------
- theta >= 1; n >= 1; max_new_tokens >= 0.

Approach ladder
---------------
1. Brute force (stops) — after every token, search the *whole* accumulated text for each stop
   string, emit nothing until the end: O(S·N) per token with linear-time search, so
   O(S·N²) overall when tokens are a few characters (N characters, S stop strings), and no
   streaming.
2. Optimal    — keep only an unreleased tail: search the tail for a complete stop, release
   everything except the longest suffix that could still start a stop string. The pending
   tail is < m + |piece| characters (m = longest stop), so one piece costs
   O(S·m·(m + |piece|)) with naive matching; streaming-safe. Aho–Corasick over all stops
   (KMP for one) brings this to O(1) amortised per character.
   Penalties: O(V + |history|) per step with ``np.bincount``; n-gram ban O(|history|·n).

Follow-ups
----------
- Multiplicative (theta) vs additive (frequency/presence) penalties: theta is scale-dependent
  because it multiplies the logit; additive penalties shift by the same amount whatever the
  logit's size.
- Penalising the prompt tokens too (common default) can hurt tasks that must copy from the prompt.
- Stop on token ids when you can (exact, O(1)); stop strings are for multi-token sequences.
- Always have max_new_tokens: a model that never emits EOS must still terminate.
- Edge cases: empty history, theta = 1 (no-op), zero logit, stop string inside one piece,
  stop string split over three pieces, a near-miss prefix that is later released.
"""
from __future__ import annotations

import numpy as np


def repetition_penalty(logits, history, theta: float) -> np.ndarray:
    if theta < 1:
        raise ValueError("theta must be >= 1")
    z = np.asarray(logits, dtype=float).copy()
    ids = np.unique(np.asarray(history, dtype=int))
    if ids.size:
        z[ids] = np.where(z[ids] > 0, z[ids] / theta, z[ids] * theta)
    return z


def repetition_penalty_wrong(logits, history, theta: float) -> np.ndarray:
    """Wrong-but-tempting: divide every seen logit by theta."""
    z = np.asarray(logits, dtype=float).copy()
    ids = np.unique(np.asarray(history, dtype=int))
    z[ids] = z[ids] / theta
    return z


def frequency_presence(logits, history, freq: float, presence: float) -> np.ndarray:
    z = np.asarray(logits, dtype=float)
    counts = np.bincount(np.asarray(history, dtype=int), minlength=z.size)[: z.size]
    return z - freq * counts - presence * (counts > 0)


def no_repeat_ngram(logits, history, n: int) -> np.ndarray:
    if n < 1:
        raise ValueError("n must be >= 1")
    z = np.asarray(logits, dtype=float).copy()
    h = list(history)
    if len(h) < n - 1:
        return z
    prefix = tuple(h[len(h) - (n - 1):]) if n > 1 else ()
    banned = {h[i + n - 1] for i in range(len(h) - n + 1) if tuple(h[i:i + n - 1]) == prefix}
    if banned:
        z[sorted(banned)] = -np.inf
    return z


def _holdback(text: str, stops: list[str]) -> int:
    """Length of the longest suffix of text that is a proper prefix of some stop string."""
    best = 0
    for s in stops:
        for L in range(min(len(s) - 1, len(text)), 0, -1):
            if text.endswith(s[:L]):
                best = max(best, L)
                break
    return best


def stream_with_stops(pieces, stop_strings, eos_piece, max_new_tokens: int):
    stops = [s for s in stop_strings if s]
    emitted, pending, released = [], "", ""
    reason = "end"
    for count, piece in enumerate(pieces):
        if count >= max_new_tokens:
            reason = "length"
            break
        if eos_piece is not None and piece == eos_piece:
            reason = "eos"
            break
        pending += piece
        hits = [i for i in (pending.find(s) for s in stops) if i >= 0]
        if hits:
            pending = pending[: min(hits)]          # keep the text before the earliest stop
            reason = "stop"
            break
        keep = _holdback(pending, stops)
        out, pending = pending[: len(pending) - keep], pending[len(pending) - keep:]
        if out:
            emitted.append(out)
            released += out
    if pending:                                      # flush what is provably not a stop
        emitted.append(pending)
        released += pending
    return emitted, released, reason


def stops_brute(pieces, stop_strings, eos_piece, max_new_tokens: int):
    """Rung 1: rescan everything after each token; return (final_text, reason) only."""
    text = ""
    for count, piece in enumerate(pieces):
        if count >= max_new_tokens:
            return text, "length"
        if piece == eos_piece:
            return text, "eos"
        text += piece
        hits = [text.find(s) for s in stop_strings if s and s in text]
        if hits:
            return text[: min(hits)], "stop"
    return text, "end"


def main() -> None:
    z = np.array([2.0, -2.0, 1.0, 0.0])
    print("repetition_penalty theta=2, history [0, 1, 1, 3]:", repetition_penalty(z, [0, 1, 1, 3], 2.0).tolist())
    print("wrong (divide all)                            :", repetition_penalty_wrong(z, [0, 1, 1, 3], 2.0).tolist(),
          "<- token 1 got MORE likely")
    print("frequency 0.5, presence 1.0, history [0, 0, 2]:", frequency_presence(z, [0, 0, 2], 0.5, 1.0).tolist())
    hist = [5, 1, 2, 5, 1, 3, 5, 1]
    banned = np.where(np.isinf(no_repeat_ngram(np.zeros(6), hist, 3)))[0].tolist()
    print("no_repeat_ngram n=3 after", hist, "-> banned next tokens:", banned)

    cases = [
        (["Hel", "lo\n", "\nUs", "er:", " hi"], ["\n\nUser:"], None, 10),
        (["The", " end", "<eos>", "junk"], ["STOP"], "<eos>", 10),
        (["a", "b", "c", "d", "e"], [], None, 3),
        (["x = 1", "\n#", " not", " a stop"], ["\n##"], None, 10),
        (["yes", "STO", "P", "!"], ["STOP"], None, 10),
    ]
    print()
    for pieces, stops, eos, mx in cases:
        chunks, text, reason = stream_with_stops(pieces, stops, eos, mx)
        same = (text, reason) == stops_brute(pieces, stops, eos, mx)
        print(f"pieces={pieces!r}\n  stops={stops!r} -> chunks={chunks!r} text={text!r} "
              f"reason={reason} | brute agrees: {same}")


if __name__ == "__main__":
    main()
