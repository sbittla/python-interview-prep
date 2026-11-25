import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def test_blobs(load):
    m = load("ex05_training_loop")
    X, y = m.make_blobs(10, seed=0)
    assert X.shape == (30, 2) and X.dtype == torch.float32
    assert torch.bincount(y).tolist() == [10, 10, 10]
    assert torch.equal(X, m.make_blobs(10, seed=0)[0])


def test_fit_learns_and_schedules(load):
    m = load("ex05_training_loop")
    train, val = m.loaders()
    hist = m.fit(m.make_model(0), train, val, epochs=30, lr=0.01)
    assert all(len(v) == 30 for v in hist.values())
    assert hist["train_loss"][-1] < 0.5 * hist["train_loss"][0]
    assert hist["val_acc"][-1] > 0.9
    assert hist["lr"][0] == 0.01 and hist["lr"][9] == 0.01      # first LR not skipped
    assert hist["lr"][10] == 0.005 and hist["lr"][29] == 0.0025


def test_train_one_epoch_updates_and_weights_loss(load):
    m = load("ex05_training_loop")
    X, y = m.make_blobs(5, seed=2)                 # 15 examples, batch 4: last batch is 3
    model = m.make_model(0)
    before = [p.detach().clone() for p in model.parameters()]
    loader = DataLoader(TensorDataset(X, y), batch_size=4)
    opt = torch.optim.SGD(model.parameters(), lr=0.0)  # lr 0: every batch sees the same weights
    loss_fn = nn.CrossEntropyLoss()
    model.eval()
    model[2].p = 0.0                               # dropout off so the loss is deterministic
    got = m.train_one_epoch(model, loader, opt, loss_fn)
    with torch.no_grad():
        full = loss_fn(model(X), y).item()
    assert abs(got - full) < 1e-6                  # example-weighted mean == full-batch mean
    opt2 = torch.optim.SGD(model.parameters(), lr=0.1)
    m.train_one_epoch(model, loader, opt2, loss_fn)
    assert any(not torch.equal(a, b) for a, b in zip(before, model.parameters()))
    assert model.training                          # train_one_epoch switches to train mode


def test_evaluate_uses_eval_mode_and_no_grad(load):
    m = load("ex05_training_loop")
    X, y = m.make_blobs(10, seed=3)
    model = m.make_model(0)
    model.train()
    loader = DataLoader(TensorDataset(X, y), batch_size=7)
    l1, a1 = m.evaluate(model, loader, nn.CrossEntropyLoss())
    model.train()
    l2, a2 = m.evaluate(model, loader, nn.CrossEntropyLoss())
    assert (l1, a1) == (l2, a2)                    # dropout off -> deterministic
    assert not model.training
    assert all(p.grad is None for p in model.parameters())
    assert 0.0 <= a1 <= 1.0


def test_overfit_one_batch(load):
    m = load("ex05_training_loop")
    X, y = m.make_blobs(40, seed=0)
    assert m.overfit_one_batch(m.make_model(1), X[::15], y[::15]) < 0.05


def test_gradients_are_zeroed_every_batch(load):
    m = load("ex05_training_loop")
    X, y = m.make_blobs(4, seed=5)                 # 12 examples -> batches of 6, 6
    model = m.make_model(0)
    model[2].p = 0.0
    loader = DataLoader(TensorDataset(X, y), batch_size=6)
    opt = torch.optim.SGD(model.parameters(), lr=0.0)
    loss_fn = nn.CrossEntropyLoss()
    m.train_one_epoch(model, loader, opt, loss_fn)
    got = [p.grad.clone() for p in model.parameters()]
    model.zero_grad()
    loss_fn(model(X[6:]), y[6:]).backward()        # the last batch alone
    assert all(torch.allclose(a, p.grad) for a, p in zip(got, model.parameters()))
