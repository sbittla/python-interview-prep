import math

import pytest
import torch
from torch import nn


@pytest.mark.parametrize("max_norm", [0.5, 1.0, 100.0])
def test_clip_matches_torch(load, max_norm):
    m = load("ex11_clipping_lr_schedules")
    torch.manual_seed(3)
    a = [torch.randn(3, 4), torch.randn(5), torch.randn(2, 2, 2)]
    params = [nn.Parameter(torch.zeros_like(t)) for t in a]
    for p, t in zip(params, a):
        p.grad = t.clone()
    total = m.clip_by_norm(a, max_norm)
    ref = nn.utils.clip_grad_norm_(params, max_norm).item()
    assert total == pytest.approx(ref, rel=1e-5)
    assert all(torch.allclose(x, p.grad) for x, p in zip(a, params))
    new = math.sqrt(sum(float((t ** 2).sum()) for t in a))
    assert new == pytest.approx(min(total, max_norm), rel=1e-4)


def test_warmup_cosine_values(load):
    m = load("ex11_clipping_lr_schedules")
    got = [round(m.warmup_cosine(s, 2, 6, 1.0), 3) for s in range(6)]
    assert got == [0.5, 1.0, 0.854, 0.5, 0.146, 0.0]
    lrs = [m.warmup_cosine(s, 3, 20, 0.1) for s in range(20)]
    assert max(lrs) == pytest.approx(0.1) and lrs[-1] == pytest.approx(0.0, abs=1e-12)
    assert all(a <= b for a, b in zip(lrs[:3], lrs[1:3]))           # warm-up rises
    assert all(a >= b for a, b in zip(lrs[2:], lrs[3:]))             # then decays


def test_lambda_lr_matches(load):
    m = load("ex11_clipping_lr_schedules")
    mine = [m.warmup_cosine(s, 4, 10, 0.3) for s in range(10)]
    assert m.torch_schedule(4, 10, 0.3) == pytest.approx(mine, abs=1e-12)


def test_clipping_survives_spike(load):
    m = load("ex11_clipping_lr_schedules")
    assert m.spike_run(None) > 1.0
    assert m.spike_run(1.0) < 0.05
