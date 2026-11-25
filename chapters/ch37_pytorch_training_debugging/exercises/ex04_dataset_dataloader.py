"""
Exercise 04 — Custom Dataset and DataLoader                    [Tier: ★ Core]
Chapter 37 · Pattern: map-style dataset + seeded loader + collate · Target time: 25 min

Problem
-------
1. ``SequenceDataset(seqs, labels)``: a map-style ``torch.utils.data.Dataset`` over
   variable-length integer sequences. ``__len__`` returns the number of examples;
   ``__getitem__(i)`` returns ``(torch.tensor(seqs[i]), labels[i])``.
2. ``pad_collate(batch, pad_id=0)``: turn a list of ``(seq, label)`` pairs into
   ``(padded, lengths, mask, labels)``: padded is (B, T_max) long, lengths (B,), mask (B, T_max)
   bool with True on real tokens, labels (B,) long.
3. ``make_loader(ds, batch_size, shuffle, seed, drop_last=False)``: a ``DataLoader`` whose
   shuffling is driven by its *own* ``torch.Generator`` seeded with ``seed`` (so the order is
   reproducible and independent of the global RNG), using ``pad_collate``.
4. ``epoch_orders(loader, epochs)``: list of the label order seen in each epoch.

Examples
--------
>>> padded, lengths, mask, labels = pad_collate([(torch.tensor([5, 6, 7]), 1), (torch.tensor([8]), 0)])
>>> padded.tolist(), lengths.tolist(), mask.sum().item()
([[5, 6, 7], [8, 0, 0]], [3, 1], 4)

Constraints
-----------
- Every sequence has length >= 1; ``num_workers=0`` (worker processes need
  ``worker_init_fn`` seeding and an ``if __name__ == "__main__"`` guard on Windows/macOS).

Hints
-----
- ``torch.full((B, T_max), pad_id)`` then copy each sequence into its row.
- Mask by broadcasting: ``torch.arange(T)[None, :] < lengths[:, None]``.
- ``DataLoader(..., generator=torch.Generator().manual_seed(seed))``.

Wrong-but-tempting
------------------
- Relying on ``torch.manual_seed`` for the order: any other global draw changes it.
- ``<=`` in the mask: marks one pad token per row as real.

Follow-ups
----------
- Batches per epoch: ceil(n / B), or floor(n / B) with ``drop_last=True``.
- Why sort/bucket by length? Less padding: cost per batch is B * T_max, not sum of lengths.
- Iterable-style datasets (streams) cannot be shuffled by index; shuffle with a buffer.
"""
from __future__ import annotations

import math

import torch
from torch.utils.data import DataLoader, Dataset

torch.set_num_threads(1)


class SequenceDataset(Dataset):
    def __init__(self, seqs: list[list[int]], labels: list[int]) -> None:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")

    def __getitem__(self, i: int):
        raise NotImplementedError("TODO")


def pad_collate(batch, pad_id: int = 0):
    raise NotImplementedError("TODO")


def make_loader(ds: Dataset, batch_size: int, shuffle: bool, seed: int,
                drop_last: bool = False) -> DataLoader:
    raise NotImplementedError("TODO")


def epoch_orders(loader: DataLoader, epochs: int) -> list[list[int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    seqs = [[i + 1] * (1 + i % 4) for i in range(10)]
    ds = SequenceDataset(seqs, list(range(10)))       # label i identifies example i
    print("len(ds):", len(ds), " ds[5]:", ds[5][0].tolist(), ds[5][1])
    padded, lengths, mask, labels = next(iter(make_loader(ds, 4, False, 0)))
    print("padded:", padded.tolist())
    print("lengths:", lengths.tolist(), " real tokens:", int(mask.sum()), " labels:", labels.tolist())

    a = epoch_orders(make_loader(ds, 4, True, seed=7), 2)
    b = epoch_orders(make_loader(ds, 4, True, seed=7), 2)
    torch.manual_seed(123)                            # global RNG must not matter
    c = epoch_orders(make_loader(ds, 4, True, seed=7), 2)
    print("same seed same orders:", a == b == c)
    print("epoch 1 != epoch 2:", a[0] != a[1], " each epoch a permutation:",
          all(sorted(o) == list(range(10)) for o in a))
    print("different seed differs:", epoch_orders(make_loader(ds, 4, True, seed=8), 1)[0] != a[0])
    for drop in (False, True):
        n = len(make_loader(ds, 4, True, 0, drop_last=drop))
        print(f"drop_last={drop}: batches={n}  formula={(10 // 4) if drop else math.ceil(10 / 4)}")
    try:
        next(iter(DataLoader(ds, batch_size=4)))       # default collate stacks unequal lengths
    except RuntimeError:
        print("default collate on ragged sequences -> RuntimeError")


if __name__ == "__main__":
    main()
