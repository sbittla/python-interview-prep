import random
import tempfile
from pathlib import Path

import numpy as np
import torch


def _straight(m, seed=0):
    X, y = m.make_data()
    model, opt = m.make_setup(seed)
    m.train_epochs(model, opt, X, y, 0, 6, seed)
    return m.params(model)


def test_seed_everything(load):
    m = load("ex07_checkpoint_reproducibility")
    m.seed_everything(5)
    a = (random.random(), np.random.rand(), torch.rand(1).item())
    m.seed_everything(5)
    assert a == (random.random(), np.random.rand(), torch.rand(1).item())


def test_resume_is_bit_identical(load):
    m = load("ex07_checkpoint_reproducibility")
    straight = _straight(m)
    with tempfile.TemporaryDirectory() as d:
        assert m.same(straight, m.resume_run(Path(d)))


def test_missing_pieces_change_result(load):
    m = load("ex07_checkpoint_reproducibility")
    straight = _straight(m)
    with tempfile.TemporaryDirectory() as d:
        assert not m.same(straight, m.resume_run(Path(d), keep_opt=False))
        assert not m.same(straight, m.resume_run(Path(d), restore_rng=False))


def test_checkpoint_contents(load):
    m = load("ex07_checkpoint_reproducibility")
    model, opt = m.make_setup(0)
    X, y = m.make_data()
    m.train_epochs(model, opt, X, y, 0, 1, 0)
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "c.pt"
        m.save_checkpoint(path, model, opt, epoch=1)
        model2, opt2 = m.make_setup(7)
        assert m.load_checkpoint(path, model2, opt2) == 1
        assert m.same(m.params(model), m.params(model2))
        assert opt2.state_dict()["state"]            # Adam moments restored, not empty
        ckpt = torch.load(path, weights_only=True)
        assert {"model", "optimizer", "epoch", "torch_rng"} <= set(ckpt)
