"""
Exercise 10 — Debug this broken training loop                  [Tier: ★ Core]
Chapter 37 · Pattern: symptom -> hypothesis -> one-line fix · Target time: 40 min

Problem
-------
``train(bug=None)`` trains a small classifier on three 2-D blobs (full batch, SGD with
momentum, 100 steps). Each ``bug`` value switches on one classic mistake. For each one, name
the symptom, then make ``train(None)`` the correct loop.

| bug              | the mistake                                         |
|------------------|-----------------------------------------------------|
| "no_zero_grad"   | ``opt.zero_grad()`` never called                     |
| "softmax_ce"     | ``CrossEntropyLoss`` fed ``softmax(logits)``         |
| "detached_body"  | hidden features ``.detach()``-ed before the head     |
| "no_eval"        | evaluation without ``model.eval()`` (dropout on)     |
| "inplace"        | ``h.add_(...)`` on a ReLU output autograd saved      |

``train`` returns a dict: ``first_loss``, ``last_loss``, ``acc`` (eval accuracy),
``body_changed`` (did the first layer's weight move?), ``eval_repeatable`` (do two evaluations
agree?), ``error`` (exception class name or None).

``regression(bug)`` does the same for a 1-output regression where ``bug="broadcast"`` compares a
(N, 1) prediction with an (N,) target.

Examples
--------
>>> r = train(None); r["acc"] > 0.9 and r["last_loss"] < 0.3
True
>>> train("softmax_ce")["last_loss"] >= SOFTMAX_CE_FLOOR     # log(1 + 2/e) for 3 classes
True

Constraints
-----------
- Deterministic: seeds fixed, single thread; each run < 1 s.

Hints
-----
- Write the correct loop first (zero_grad, forward, ``F.cross_entropy`` on raw logits,
  backward, step; ``model.eval()`` before evaluating), then add each bug behind an ``if``.
- ``body_changed``: clone ``model.body.weight`` before training, compare with ``torch.equal``.
- ``eval_repeatable``: two forward passes under ``no_grad``, compared with ``torch.equal``.
- Catch ``RuntimeError`` around the loop and return its class name and message.

Wrong-but-tempting
------------------
- "Accuracy is 1.0, so the loop is fine": softmax-before-CE and a detached body both still
  reach high accuracy on easy data.

Follow-ups
----------
- Why does a missing ``zero_grad`` not crash? ``.grad`` accumulates by design (gradient
  accumulation, Exercise 06); the step just uses the sum of all past gradients.
- Why is the softmax_ce floor log(1 + (C - 1)/e)? The "logits" are probabilities in [0, 1],
  so the best case is (1, 0, ..., 0): softmax of that puts e/(e + C - 1) on the right class.
- ``loss.item()`` vs keeping ``loss`` in a list: the tensor keeps the whole graph alive (memory
  leak); ``.item()`` returns a float.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import nn

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

SOFTMAX_CE_FLOOR = math.log(1 + 2 / math.e)        # 3 classes


def make_blobs(n_per_class: int = 40, seed: int = 0):
    g = torch.Generator().manual_seed(seed)
    centres = torch.tensor([[0.0, 2.0], [2.0, -1.0], [-2.0, -1.0]])
    X = torch.cat([c + 0.8 * torch.randn(n_per_class, 2, generator=g) for c in centres])
    return X, torch.arange(3).repeat_interleave(n_per_class)


class Net(nn.Module):
    def __init__(self, inplace_bug: bool = False, detach_bug: bool = False) -> None:
        super().__init__()
        self.body, self.drop, self.head = nn.Linear(2, 32), nn.Dropout(0.3), nn.Linear(32, 3)
        self.inplace_bug, self.detach_bug = inplace_bug, detach_bug

    def forward(self, x):
        h = torch.relu(self.body(x))
        if self.inplace_bug:
            h.add_(0.1)                    # BUG: relu saved h for backward
        if self.detach_bug:
            h = h.detach()                 # BUG: no gradient reaches self.body
        return self.head(self.drop(h))


def train(bug: str | None = None, steps: int = 100, seed: int = 0) -> dict:
    raise NotImplementedError("TODO")


def regression(bug: str | None = None, steps: int = 300, seed: int = 0) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    print(f"softmax_ce loss floor log(1 + 2/e) = {SOFTMAX_CE_FLOOR:.4f}")
    for bug in (None, "no_zero_grad", "softmax_ce", "detached_body", "no_eval", "inplace"):
        r = train(bug)
        if r["error"]:
            print(f"{bug!s:>13}: {r['error']}  in-place message: "
                  f"{'modified by an inplace operation' in r['message']}")
            continue
        print(f"{bug!s:>13}: loss {r['first_loss']:.3g} -> {r['last_loss']:.3g}  acc {r['acc']:.2f}  "
              f"body moved {r['body_changed']}  eval repeatable {r['eval_repeatable']}")
    print(f"regression fixed: true MSE {regression(None):.4f}")
    print(f"regression broadcast bug: true MSE {regression('broadcast'):.4f}")


if __name__ == "__main__":
    main()
