"""
Exercise 07 — Checkpointing and reproducibility                [Tier: ★ Core]
Chapter 37 · Pattern: save everything the next step depends on · Target time: 30 min

Problem
-------
Make "train 6 epochs" and "train 3, save, restart the process, load, train 3 more" produce
bit-identical weights.

1. ``seed_everything(seed)``: seed Python's ``random``, NumPy's legacy global RNG and torch.
2. ``train_epochs(model, opt, X, y, start, end, seed)``: for each epoch e in [start, end), shuffle
   with a fresh ``torch.Generator`` seeded ``seed * 1000 + e`` (so the order of epoch e does not
   depend on how many epochs ran before), then mini-batch Adam steps. The model contains dropout,
   which draws from torch's *global* RNG.
3. ``save_checkpoint(path, model, opt, epoch)``: ``torch.save`` a dict with the model and
   optimizer ``state_dict``s, the next epoch, and ``torch.get_rng_state()``.
4. ``load_checkpoint(path, model, opt, restore_rng=True)``: load with ``weights_only=True``,
   restore everything, return the epoch to resume from.

Examples
--------
>>> straight == resumed          # parameters compared with torch.equal
True

Constraints
-----------
- Write only inside a ``tempfile.TemporaryDirectory()``; CPU; single thread.

Approach ladder
---------------
1. ``torch.save(model)`` (the whole pickled object) — breaks when the class moves or changes,
   and cannot be loaded with ``weights_only=True``; still loses optimizer state.
2. Model ``state_dict`` only — weights resume, but Adam's moment estimates and step counts
   restart from zero, so the next updates differ.
3. Optimal — model + optimizer (+ scheduler) ``state_dict``s, epoch counter, RNG states, with
   data order derived from (seed, epoch). Checkpoint size O(P) for SGD, about 3P for Adam
   (weights + two moments). Why move up: each missing piece changes the trajectory.

Follow-ups
----------
- GPU: also save ``torch.cuda.get_rng_state_all()``; set ``torch.use_deterministic_algorithms(True)``
  (some CUDA ops then need ``CUBLAS_WORKSPACE_CONFIG`` or raise).
- DataLoader workers: the loader's generator already seeds each worker's torch, ``random`` and
  NumPy (base seed + worker id); ``worker_init_fn`` is only for other libraries or per-worker
  state. Checkpoint the generator's state too if you resume mid-epoch.
- ``map_location="cpu"`` to load a GPU checkpoint on a CPU-only machine.
- ``weights_only`` defaults to True from PyTorch 2.6 (version-specific); it refuses arbitrary
  pickled objects such as NumPy arrays, which is the point.
"""
from __future__ import annotations

import random
import tempfile
from pathlib import Path

import numpy as np
import torch
from torch import nn

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def make_setup(seed: int = 0):
    seed_everything(seed)
    model = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Dropout(0.3), nn.Linear(16, 3))
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    return model, opt


def make_data(n: int = 64, seed: int = 0):
    g = torch.Generator().manual_seed(seed)
    X = torch.randn(n, 2, generator=g)
    y = (X[:, 0] > 0).long() + (X[:, 1] > 0).long()     # 3 classes
    return X, y


def train_epochs(model, opt, X, y, start: int, end: int, seed: int, batch: int = 16) -> None:
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    for epoch in range(start, end):
        g = torch.Generator().manual_seed(seed * 1000 + epoch)   # order depends only on epoch
        order = torch.randperm(len(X), generator=g)
        for i in range(0, len(X), batch):
            idx = order[i:i + batch]
            opt.zero_grad()
            loss_fn(model(X[idx]), y[idx]).backward()           # dropout: global RNG
            opt.step()


def save_checkpoint(path: Path, model, opt, epoch: int) -> None:
    torch.save({"model": model.state_dict(), "optimizer": opt.state_dict(),
                "epoch": epoch, "torch_rng": torch.get_rng_state()}, path)


def load_checkpoint(path: Path, model, opt, restore_rng: bool = True) -> int:
    ckpt = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(ckpt["model"])
    if opt is not None:
        opt.load_state_dict(ckpt["optimizer"])
    if restore_rng:
        torch.set_rng_state(ckpt["torch_rng"])
    return ckpt["epoch"]


def params(model) -> list[torch.Tensor]:
    return [p.detach().clone() for p in model.parameters()]


def same(a, b) -> bool:
    return all(torch.equal(x, y) for x, y in zip(a, b))


def resume_run(tmp: Path, *, keep_opt: bool = True, restore_rng: bool = True, seed: int = 0):
    X, y = make_data()
    model, opt = make_setup(seed)
    train_epochs(model, opt, X, y, 0, 3, seed)
    save_checkpoint(tmp / "ckpt.pt", model, opt, epoch=3)
    seed_everything(999)                                # "new process": RNG elsewhere
    model2, opt2 = make_setup(seed=123)                 # fresh, different init
    start = load_checkpoint(tmp / "ckpt.pt", model2, opt2 if keep_opt else None, restore_rng)
    train_epochs(model2, opt2, X, y, start, 6, seed)
    return params(model2)


def main() -> None:
    X, y = make_data()
    model, opt = make_setup(0)
    train_epochs(model, opt, X, y, 0, 6, seed=0)
    straight = params(model)

    model_b, opt_b = make_setup(0)
    train_epochs(model_b, opt_b, X, y, 0, 6, seed=0)
    print("same seed, two straight runs identical:", same(straight, params(model_b)))

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        print("resume with model+optimizer+RNG identical:", same(straight, resume_run(tmp)))
        print("resume without optimizer state identical:", same(straight, resume_run(tmp, keep_opt=False)))
        print("resume without RNG state identical:", same(straight, resume_run(tmp, restore_rng=False)))
        ckpt = torch.load(tmp / "ckpt.pt", weights_only=True)
        print("checkpoint keys:", sorted(ckpt), " epoch:", ckpt["epoch"])
        n_adam = sum(t.numel() for s in ckpt["optimizer"]["state"].values()
                     for k, t in s.items() if k != "step")
        print("Adam moments stored:", n_adam, "= 2 x params:",
              n_adam == 2 * sum(p.numel() for p in model.parameters()))
        torch.save({"arr": np.arange(3)}, tmp / "np.pt")
        try:
            torch.load(tmp / "np.pt", weights_only=True)
        except Exception as e:          # pickle.UnpicklingError
            print("weights_only=True refuses a NumPy array:", type(e).__name__)


if __name__ == "__main__":
    main()
