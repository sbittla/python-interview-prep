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

Approach ladder (the debugging order, not the code)
---------------------------------------------------
1. Train on everything and stare at the curve — one run costs epochs x n examples, and a
   flat curve does not say *which* part is wrong.
2. Overfit one batch first — O(steps x B) work, seconds; separates code bugs (cannot fit
   even B examples) from data/capacity problems.
3. Optimal — overfit-one-batch, then full training with a held-out eval in ``eval()`` mode
   and per-epoch logging of loss, accuracy and LR. Why move up: each rung fails faster and
   localises the fault better.

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
    g = torch.Generator().manual_seed(seed)
    centres = torch.tensor([[0.0, 2.0], [2.0, -1.0], [-2.0, -1.0]])
    X = torch.cat([c + 1.0 * torch.randn(n_per_class, 2, generator=g) for c in centres])
    y = torch.arange(3).repeat_interleave(n_per_class)
    return X, y


def make_model(seed: int = 0) -> nn.Module:
    torch.manual_seed(seed)                       # weight init draws from the global RNG
    return nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Dropout(0.2), nn.Linear(32, 3))


def train_one_epoch(model, loader, opt, loss_fn) -> float:
    model.train()
    total, count = 0.0, 0
    for xb, yb in loader:
        opt.zero_grad()                           # 1. clear old gradients
        loss = loss_fn(model(xb), yb)             # 2. forward + loss (mean over batch)
        loss.backward()                           # 3. gradients into p.grad
        opt.step()                                # 4. update
        total += loss.item() * len(yb)            # .item(): a float, keeps no graph alive
        count += len(yb)
    return total / count


@torch.no_grad()
def evaluate(model, loader, loss_fn) -> tuple[float, float]:
    model.eval()                                  # dropout off, batch norm uses running stats
    total, correct, count = 0.0, 0, 0
    for xb, yb in loader:
        logits = model(xb)
        total += loss_fn(logits, yb).item() * len(yb)
        correct += (logits.argmax(dim=1) == yb).sum().item()
        count += len(yb)
    return total / count, correct / count


def fit(model, train_loader, val_loader, epochs: int, lr: float) -> dict[str, list[float]]:
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.5)
    loss_fn = nn.CrossEntropyLoss()               # takes raw logits + class indices
    hist: dict[str, list[float]] = {"train_loss": [], "val_loss": [], "val_acc": [], "lr": []}
    for _ in range(epochs):
        hist["lr"].append(opt.param_groups[0]["lr"])
        hist["train_loss"].append(train_one_epoch(model, train_loader, opt, loss_fn))
        vl, va = evaluate(model, val_loader, loss_fn)
        hist["val_loss"].append(vl)
        hist["val_acc"].append(va)
        sched.step()                              # once per epoch, after opt.step()
    return hist


def overfit_one_batch(model, xb, yb, steps: int = 200, lr: float = 0.05) -> float:
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    for _ in range(steps):
        opt.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        return loss_fn(model(xb), yb).item()


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
