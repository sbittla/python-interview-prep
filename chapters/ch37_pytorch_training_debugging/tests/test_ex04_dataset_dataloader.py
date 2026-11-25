import math

import pytest
import torch


def _ds(m, n=10):
    return m.SequenceDataset([[i + 1] * (1 + i % 4) for i in range(n)], list(range(n)))


def test_dataset_protocol(load):
    m = load("ex04_dataset_dataloader")
    ds = _ds(m)
    assert len(ds) == 10
    seq, label = ds[6]
    assert seq.tolist() == [7, 7, 7] and label == 6 and seq.dtype == torch.long
    with pytest.raises(ValueError):
        m.SequenceDataset([[1]], [0, 1])


def test_pad_collate(load):
    m = load("ex04_dataset_dataloader")
    padded, lengths, mask, labels = m.pad_collate([(torch.tensor([5, 6, 7]), 1), (torch.tensor([8]), 0)])
    assert padded.tolist() == [[5, 6, 7], [8, 0, 0]]
    assert lengths.tolist() == [3, 1] and labels.tolist() == [1, 0]
    assert mask.tolist() == [[True, True, True], [True, False, False]]
    padded, *_ = m.pad_collate([(torch.tensor([5]), 1), (torch.tensor([8, 9]), 0)], pad_id=-1)
    assert padded.tolist() == [[5, -1], [8, 9]]


def test_seeded_order_independent_of_global_rng(load):
    m = load("ex04_dataset_dataloader")
    ds = _ds(m)
    torch.manual_seed(0)
    a = m.epoch_orders(m.make_loader(ds, 3, True, seed=5), 3)
    torch.manual_seed(999)
    b = m.epoch_orders(m.make_loader(ds, 3, True, seed=5), 3)
    assert a == b
    assert all(sorted(o) == list(range(10)) for o in a)
    assert a[0] != a[1]
    assert m.epoch_orders(m.make_loader(ds, 3, True, seed=6), 1)[0] != a[0]
    assert m.epoch_orders(m.make_loader(ds, 3, False, seed=5), 1)[0] == list(range(10))


@pytest.mark.parametrize("n, bs", [(10, 4), (12, 4), (7, 10), (1, 1)])
def test_batch_counts(load, n, bs):
    m = load("ex04_dataset_dataloader")
    ds = _ds(m, n)
    assert len(m.make_loader(ds, bs, True, 0)) == math.ceil(n / bs)
    assert len(m.make_loader(ds, bs, True, 0, drop_last=True)) == n // bs
    sizes = [len(b[3]) for b in m.make_loader(ds, bs, True, 0, drop_last=True)]
    assert all(s == bs for s in sizes)
