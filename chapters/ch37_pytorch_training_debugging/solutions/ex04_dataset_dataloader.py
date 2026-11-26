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
- Every sequence has length >= 1; ``num_workers=0``. (With workers, the loader's generator
  already seeds each worker's torch, ``random`` and NumPy from base seed + worker id; use
  ``worker_init_fn`` only for other libraries or per-worker state, and add an
  ``if __name__ == "__main__"`` guard on Windows/macOS.)

Approach ladder
---------------
1. Hand-rolled ``for i in range(0, n, B)`` slicing of a list — fine for fixed-size tensors,
   but you re-implement shuffling, padding and the last partial batch. O(n) per epoch.
2. ``DataLoader(shuffle=True)`` with default collate — fails on variable lengths
   (``torch.stack`` needs equal shapes) and its order depends on the global RNG.
3. Optimal — ``DataLoader(..., generator=g, collate_fn=pad_collate)``: O(n) per epoch plus
   O(B T_max) padding per batch; reproducible order, explicit mask. Why move up: rung 2 breaks
   the moment any other code draws from the global RNG.

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
        if len(seqs) != len(labels):
            raise ValueError("seqs and labels differ in length")
        self.seqs, self.labels = seqs, labels

    def __len__(self) -> int:
        return len(self.seqs)

    def __getitem__(self, i: int):
        return torch.tensor(self.seqs[i], dtype=torch.long), self.labels[i]


def pad_collate(batch, pad_id: int = 0):
    seqs, labels = zip(*batch)
    lengths = torch.tensor([len(s) for s in seqs])
    padded = torch.full((len(seqs), int(lengths.max())), pad_id, dtype=torch.long)
    for row, s in enumerate(seqs):
        padded[row, :len(s)] = s
    mask = torch.arange(padded.shape[1]) < lengths[:, None]   # (B, T) by broadcasting
    return padded, lengths, mask, torch.tensor(labels, dtype=torch.long)


def make_loader(ds: Dataset, batch_size: int, shuffle: bool, seed: int,
                drop_last: bool = False) -> DataLoader:
    g = torch.Generator().manual_seed(seed)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, generator=g,
                      collate_fn=pad_collate, drop_last=drop_last, num_workers=0)


def epoch_orders(loader: DataLoader, epochs: int) -> list[list[int]]:
    return [[y for *_, labels in loader for y in labels.tolist()] for _ in range(epochs)]


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
