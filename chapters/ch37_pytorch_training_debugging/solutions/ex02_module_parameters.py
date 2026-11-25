"""
Exercise 02 — nn.Module, layers and parameters                 [Tier: ★ Core]
Chapter 37 · Pattern: module registration · Target time: 20 min

Problem
-------
1. ``MLP(sizes, dropout=0.0)``: an ``nn.Module`` with one ``nn.Linear`` per consecutive pair in
   ``sizes`` (e.g. [4, 8, 3] -> Linear(4, 8), Linear(8, 3)), ReLU (and optional dropout) between
   layers but not after the last one. Store layers in an ``nn.ModuleList``.
2. ``count_params(model, trainable_only=False)``: total number of scalar parameters.
3. ``expected_mlp_params(sizes)``: the closed-form count, sum of in*out + out per layer.
4. ``ListMLP`` (provided, buggy): stores its layers in a plain Python ``list``. Show that
   ``parameters()`` misses them: an optimizer built from it alone raises ``ValueError``;
   mixed with registered layers, the hidden ones would silently never train.
5. ``freeze(module)``: set ``requires_grad=False`` on every parameter of ``module``.
6. ``Standardise``: a module holding ``mean`` and ``std`` as *buffers* (saved in
   ``state_dict``, moved by ``.to()``, never trained) and returning (x - mean) / std.

Examples
--------
>>> count_params(MLP([4, 8, 3]))
67
>>> count_params(ListMLP([4, 8, 3]))
0

Constraints
-----------
- len(sizes) >= 2; all sizes positive.

Approach ladder
---------------
1. Plain attributes ``self.l1``, ``self.l2`` — registered, but the depth is fixed in code.
2. Python list of layers — flexible depth, but ``nn.Module.__setattr__`` only registers
   Modules, Parameters and buffers assigned directly; a list hides them: 0 parameters,
   ``.to(device)`` skips them, ``state_dict`` omits them.
3. Optimal — ``nn.ModuleList`` (or ``nn.Sequential``): flexible *and* registered. Forward is
   O(sum in*out) per example either way; the fix is about correctness, not speed.

Follow-ups
----------
- ``nn.Sequential`` vs ``ModuleList``: Sequential also defines forward; ModuleList is a
  registered container you iterate yourself.
- Plain tensor attribute vs ``register_buffer`` vs ``nn.Parameter``: only the latter two are in
  ``state_dict``; only Parameters are returned by ``parameters()``.
- Fine-tuning: freeze the backbone, pass only ``filter(lambda p: p.requires_grad, ...)`` or a
  param group with its own learning rate to the optimizer.
"""
from __future__ import annotations

import torch
from torch import nn

torch.set_num_threads(1)


class MLP(nn.Module):
    def __init__(self, sizes: list[int], dropout: float = 0.0) -> None:
        super().__init__()
        self.layers = nn.ModuleList(nn.Linear(a, b) for a, b in zip(sizes, sizes[1:]))
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if i < len(self.layers) - 1:          # no activation after the output layer
                x = self.drop(torch.relu(x))
        return x


class ListMLP(nn.Module):
    """BUGGY on purpose: a plain list hides the layers from nn.Module."""

    def __init__(self, sizes: list[int]) -> None:
        super().__init__()
        self.layers = [nn.Linear(a, b) for a, b in zip(sizes, sizes[1:])]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if i < len(self.layers) - 1:
                x = torch.relu(x)
        return x


def count_params(model: nn.Module, trainable_only: bool = False) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad or not trainable_only)


def expected_mlp_params(sizes: list[int]) -> int:
    return sum(a * b + b for a, b in zip(sizes, sizes[1:]))


def freeze(module: nn.Module) -> None:
    for p in module.parameters():
        p.requires_grad_(False)


class Standardise(nn.Module):
    def __init__(self, mean: torch.Tensor, std: torch.Tensor) -> None:
        super().__init__()
        self.register_buffer("mean", mean.clone())
        self.register_buffer("std", std.clone())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return (x - self.mean) / self.std


def main() -> None:
    torch.manual_seed(0)
    sizes = [4, 8, 3]
    good, bad = MLP(sizes), ListMLP(sizes)
    print("MLP params:", count_params(good), " closed form:", expected_mlp_params(sizes))
    print("ListMLP params:", count_params(bad), " state_dict keys:", list(bad.state_dict()))
    print("MLP state_dict keys:", list(good.state_dict()))
    print("output shape:", tuple(good(torch.randn(5, 4)).shape))
    try:
        torch.optim.SGD(bad.parameters(), lr=0.1)
    except ValueError as e:
        print("SGD(ListMLP.parameters()) raises ValueError:", "empty parameter list" in str(e))

    freeze(good.layers[0])
    print("trainable after freezing layer 0:", count_params(good, trainable_only=True))
    std = Standardise(torch.tensor([1.0, 2.0]), torch.tensor([2.0, 4.0]))
    print("buffers in state_dict:", sorted(std.state_dict()), " parameters:", count_params(std))
    print("standardised:", std(torch.tensor([[3.0, 6.0]])).tolist())
    print("named_parameters:", [n for n, _ in MLP([2, 2]).named_parameters()])


if __name__ == "__main__":
    main()
