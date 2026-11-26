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

Hints
-----
- ``np.unique(history)`` gives the distinct ids; branch on the sign of each logit.
- ``np.bincount(history, minlength=V)`` gives the counts.
- n-gram ban: find earlier places where the last n-1 tokens occurred; ban what followed.
- Streaming: after each piece, look for a complete stop in the pending text; otherwise
  release everything except the longest suffix that is a prefix of some stop string.

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
    raise NotImplementedError("TODO")


def repetition_penalty_wrong(logits, history, theta: float) -> np.ndarray:
    """Wrong-but-tempting: divide every seen logit by theta."""
    z = np.asarray(logits, dtype=float).copy()
    ids = np.unique(np.asarray(history, dtype=int))
    z[ids] = z[ids] / theta
    return z


def frequency_presence(logits, history, freq: float, presence: float) -> np.ndarray:
    raise NotImplementedError("TODO")


def no_repeat_ngram(logits, history, n: int) -> np.ndarray:
    raise NotImplementedError("TODO")


def _holdback(text: str, stops: list[str]) -> int:
    """Length of the longest suffix of text that is a proper prefix of some stop string."""
    raise NotImplementedError("TODO")


def stream_with_stops(pieces, stop_strings, eos_piece, max_new_tokens: int):
    raise NotImplementedError("TODO")


def stops_brute(pieces, stop_strings, eos_piece, max_new_tokens: int):
    """Rung 1: rescan everything after each token; return (final_text, reason) only."""
    raise NotImplementedError("TODO")


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
