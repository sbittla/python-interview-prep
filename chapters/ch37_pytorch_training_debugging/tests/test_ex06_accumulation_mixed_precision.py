import pytest
import torch
from torch import nn


def _setup():
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(3, 8), nn.Tanh(), nn.Linear(8, 1)).double()
    X, y = torch.randn(12, 3, dtype=torch.float64), torch.randn(12, dtype=torch.float64)
    return model, X, y


@pytest.mark.parametrize("micro", [1, 2, 3, 4, 6, 12])
def test_accumulation_equals_full_batch(load, micro):
    m = load("ex06_accumulation_mixed_precision")
    model, X, y = _setup()
    full = m.full_batch_grads(model, X, y)
    acc = m.accumulated_grads(model, X, y, micro)
    assert all(torch.allclose(a, f) for a, f in zip(acc, full))


def test_forgetting_division_scales_by_micro(load):
    m = load("ex06_accumulation_mixed_precision")
    model, X, y = _setup()
    full = m.full_batch_grads(model, X, y)
    bad = m.accumulated_grads(model, X, y, 4, scale_loss=False)
    assert all(torch.allclose(b, 4 * f) for b, f in zip(bad, full))


def test_accumulation_starts_from_zero(load):
    m = load("ex06_accumulation_mixed_precision")
    model, X, y = _setup()
    first = m.accumulated_grads(model, X, y, 3)
    again = m.accumulated_grads(model, X, y, 3)     # stale .grad from the last call must go
    assert all(torch.allclose(a, b) for a, b in zip(first, again))


def test_indivisible_raises(load):
    m = load("ex06_accumulation_mixed_precision")
    model, X, y = _setup()
    with pytest.raises(ValueError):
        m.accumulated_grads(model, X, y, 5)


def test_fp16_roundtrip(load):
    m = load("ex06_accumulation_mixed_precision")
    assert m.fp16_roundtrip(1e-8, 1.0) == 0.0
    assert m.fp16_roundtrip(1e-8, 2.0**16) == pytest.approx(1e-8, rel=1e-2)
    assert m.fp16_roundtrip(1e-3, 2.0**27) == float("inf")
    assert m.fp16_roundtrip(0.5, 1.0) == 0.5


def test_scaler_policy(load):
    m = load("ex06_accumulation_mixed_precision")
    s = m.DynamicLossScaler(init_scale=8.0, growth_interval=2)
    assert s.update(False) and s.scale == 8.0
    assert s.update(False) and s.scale == 16.0       # 2 good steps -> grow
    assert not s.update(True) and s.scale == 8.0     # inf -> skip and halve
    assert s.update(False) and s.scale == 8.0        # counter was reset
    assert s.update(False) and s.scale == 16.0


def test_autocast_dtypes(load):
    out, w, loss = load("ex06_accumulation_mixed_precision").autocast_dtypes()
    assert (out, w, loss) == (torch.bfloat16, torch.float32, torch.float32)


def test_scaler_resets_good_streak_on_inf(load):
    m = load("ex06_accumulation_mixed_precision")
    s = m.DynamicLossScaler(init_scale=8.0, growth_interval=2)
    s.update(False)                                  # streak 1
    s.update(True)                                   # overflow: scale 4, streak reset
    assert s.update(False) and s.scale == 4.0        # streak 1 again, no growth yet
    assert s.update(False) and s.scale == 8.0
