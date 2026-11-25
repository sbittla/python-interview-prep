"""
Exercise 05 — The training loop                                [Tier: ★ Core]
Chapter 37 · Pattern: forward / loss / backward / step, then eval · Target time: 30 min

Problem
-------
Write the canonical supervised loop for a 3-class classifier on 2-D synthetic blobs.

1. ``make_blobs(n_per_class, seed)``: three Gaussian clusters, returns ``X`` (3n, 2) float32
   and ``y`` (3n,) long.
2. ``train_one_epoch(model, loader, opt, loss_fn)``: ``model.train()``; for each batch
   zero the gradients, forward, loss, backward, step. Return the *example-weighted* mean loss.
3. ``evaluate(model, loader, loss_fn)``: ``model.eval()`` and ``torch.no_grad()``; return
   ``(mean_loss, accuracy)``.
4. ``fit(model, train_loader, val_loader, epochs, lr)``: Adam + ``StepLR(step_size=10,
   gamma=0.5)`` stepped once per epoch *after* the optimizer steps. Return a history dict with
   ``train_loss``, ``val_loss``, ``val_acc`` and ``lr`` lists (one entry per epoch).
5. ``overfit_one_batch(model, xb, yb, steps, lr)``: the sanity check — train on one fixed
   batch and return the final loss. A correct model + loop drives it towards 0; if it cannot,
   the bug is in the code, not the data.

Examples
--------
>>> hist = fit(model, train_loader, val_loader, epochs=30, lr=0.01)
>>> hist["val_acc"][-1] > 0.9
True

Constraints
-----------
- CPU, < 1 s of training; seeds fixed; dropout inside the model so train/eval differ.

Hints
-----
- Order inside the loop: ``zero_grad`` -> forward -> loss -> ``backward`` -> ``step``.
- Accumulate ``loss.item() * len(yb)`` and divide by the number of examples.
- ``evaluate``: decorate with ``@torch.no_grad()`` and call ``model.eval()`` first.
- ``scheduler.step()`` once per epoch, after the optimizer steps.

Wrong-but-tempting
------------------
- Forgetting ``model.train()`` at the start of each epoch after an ``evaluate`` call: dropout
  stays off for the rest of training.
- Appending ``loss`` (the tensor) to a list: keeps every graph alive.

Follow-ups
----------
- Why weight the epoch loss by batch size? The last batch may be smaller; averaging batch
  means over-weights it.
- Why ``scheduler.step()`` after ``optimizer.step()``? Since PyTorch 1.1 that is the required
  order; calling it first skips the initial LR (and PyTorch warns).
- Where do schedules and clipping come from? Built from scratch in §36.10; Exercise 11 uses
  the torch API.
"""
from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def make_blobs(n_per_class: int, seed: int):
    raise NotImplementedError("TODO")


def make_model(seed: int = 0) -> nn.Module:
    torch.manual_seed(seed)                       # weight init draws from the global RNG
    return nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Dropout(0.2), nn.Linear(32, 3))


def train_one_epoch(model, loader, opt, loss_fn) -> float:
    raise NotImplementedError("TODO")


@torch.no_grad()
def evaluate(model, loader, loss_fn) -> tuple[float, float]:
    raise NotImplementedError("TODO")


def fit(model, train_loader, val_loader, epochs: int, lr: float) -> dict[str, list[float]]:
    raise NotImplementedError("TODO")


def overfit_one_batch(model, xb, yb, steps: int = 200, lr: float = 0.05) -> float:
    raise NotImplementedError("TODO")


def loaders(seed: int = 0, batch_size: int = 16):
    X, y = make_blobs(40, seed=seed)
    Xv, yv = make_blobs(20, seed=seed + 1)
    g = torch.Generator().manual_seed(seed)
    train = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True, generator=g)
    val = DataLoader(TensorDataset(Xv, yv), batch_size=64)
    return train, val


def main() -> None:
    X, y = make_blobs(40, seed=0)
    print("data:", tuple(X.shape), X.dtype, " labels:", torch.bincount(y).tolist())
    xb, yb = X[:: 15], y[:: 15]                   # one fixed batch of 8 examples, mixed classes
    final = overfit_one_batch(make_model(1), xb, yb)
    print(f"overfit one batch of {len(yb)}: final loss < 0.05: {final < 0.05}")

    train, val = loaders()
    hist = fit(make_model(0), train, val, epochs=30, lr=0.01)
    for e in (0, 9, 10, 29):
        print(f"epoch {e + 1:>2}: lr={hist['lr'][e]:.4f} train={hist['train_loss'][e]:.2f} "
              f"val={hist['val_loss'][e]:.2f} acc={hist['val_acc'][e]:.2f}")
    print("train loss decreased:", hist["train_loss"][-1] < hist["train_loss"][0])
    print("val accuracy > 0.9:", hist["val_acc"][-1] > 0.9)

    model = make_model(0)
    model.train()
    with torch.no_grad():
        same_train = torch.equal(model(X[:5]), model(X[:5]))
        model.eval()
        same_eval = torch.equal(model(X[:5]), model(X[:5]))
    print("two forwards equal in train mode:", same_train, " in eval mode:", same_eval)


if __name__ == "__main__":
    main()
