# Chapter 37. PyTorch Training and Debugging

◆ Extended · Tracks M, L · Study time ≈ 6 h · Prerequisites: §33.3 (broadcasting), §35.10 (stable
softmax and cross-entropy), §36.9–§36.10 (optimisers, schedules, clipping)

**Learning objectives**

- Explain `backward`, `.grad`, `no_grad`, `detach`, and why `.grad` accumulates.
- Register parameters correctly; re-implement the core layers and cross-check them.
- Write the loop, a seeded `DataLoader`, accumulation and a bit-identical resume.
- Debug a broken loop from its symptom.

> **Recognise it**
>
> | Signal in the prompt | Reach for |
> |---|---|
> | "loss isn't going down", "here's our script" | symptom table (§37.9), overfit one batch |
> | "implement BatchNorm / conv / dropout without nn" | §37.3, cross-check with `torch.allclose` |
> | "batch doesn't fit in memory" | accumulation, autocast (§37.6) |
> | "results differ between runs", "resume training" | seeds, generators, full checkpoint (§37.7) |
> | "loss becomes NaN", "shape mismatch" | hooks, shape asserts, stable losses (§37.8) |

Code verified on CPU with torch 2.15.0+cpu; version-specific details are flagged.

## 37.1 Tensors, autograd, devices

A tensor with `requires_grad=True` records operations into a graph; `loss.backward()` walks it
in reverse, costing a small multiple of the forward whatever the parameter count P (finite
differences need 2P forwards: for *checking*, §37.8). Only **leaf** tensors keep `.grad`
(`retain_grad()` for intermediates), and `backward` **adds** into it:

```python
import torch

x = torch.tensor(3.0, requires_grad=True)
for _ in range(3):
    (x ** 2).backward()          # new graph each time; d/dx = 6
    print(x.grad.item(), end=" ")
with torch.no_grad():
    y = x * 2                    # nothing recorded
print("| y.requires_grad:", y.requires_grad)
```

```text
6.0 12.0 18.0 | y.requires_grad: False
```

Accumulation is a feature (§37.6) and why loops call `zero_grad()`. `detach()` returns a
graph-free tensor sharing storage. A second `backward` through the same graph raises once its
saved tensors have been freed (most ops save some); `retain_graph=True` keeps them. Broadcasting follows NumPy (→ §33.3). Devices: pick
`torch.device("cuda" if torch.cuda.is_available() else "cpu")` once and move the model *and* every
batch with `.to(device)`; mixing devices raises.
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex01_tensors_autograd.py`

## 37.2 `nn.Module`, layers, parameters

`nn.Module.__setattr__` registers attributes that are Modules or Parameters (buffers need
`register_buffer`). A plain list hides them from `parameters()`, `state_dict()` and `.to()`:

```python
import torch
from torch import nn

class ListMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = [nn.Linear(4, 8), nn.Linear(8, 3)]                  # BUG: plain list

class GoodMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.ModuleList([nn.Linear(4, 8), nn.Linear(8, 3)])   # registered

count = lambda m: sum(p.numel() for p in m.parameters())
print("list:", count(ListMLP()), " ModuleList:", count(GoodMLP()), " formula:", 4*8+8 + 8*3+3)
```

```text
list: 0  ModuleList: 67  formula: 67
```

| Holds | `parameters()` | `state_dict()` | Trained |
|---|---|---|---|
| `nn.Parameter` / sub-module | yes | yes | yes |
| `register_buffer` (running stats) | no | yes | no |
| plain tensor attribute | no | no | no |

Freeze with `p.requires_grad_(False)`.
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex02_module_parameters.py`

## 37.3 Core layers by hand: linear, convolution, batch norm, layer norm, dropout, embedding

Interviewers test the *state* and *mode* rules. Cross-check against `F.*` in float64.

| Layer | Core formula | Gotcha |
|---|---|---|
| Linear | x Wᵀ + b, W is (out, in) | the transpose |
| Conv2d | H' = (H + 2p − k) // s + 1 | cross-correlation, no kernel flip |
| BatchNorm | (x − μ_B)/√(σ²_B + ε)·γ + β | train vs eval; running stats |
| LayerNorm | same, over the last dim of each example | no running stats, no modes (→ §39.5) |
| Dropout | x·mask/(1 − p) in training | identity in eval |
| Embedding | table[ids] | gradient only for looked-up rows (→ §38.7) |

**Convolution ladder.** (1) Loops over output cells: O(N·F·H'·W'·C·k²) work as N·F·H'·W'
Python-level ops. (2) im2col: `F.unfold` copies patches into columns, then one matmul with w
reshaped to (F, C·k²): same FLOPs, vectorised, O(N·C·k²·H'·W') extra memory.

### Worked problem: batch norm by hand

*Implement 1-D batch norm matching `nn.BatchNorm1d` in both modes, running stats included.*

Ladder: (1) loop over channels, O(N·C) work with C Python iterations; (2) reduce over dim 0 in one
call, O(N·C) vectorised, buffers updated under `no_grad`. Why move up: C Python iterations
dominate for wide layers, and in-graph buffer updates would leak state into autograd.

```python
import torch

def batch_norm(x, gamma, beta, run_mean, run_var, training, momentum=0.1, eps=1e-5):
    if training:
        if x.shape[0] < 2:
            raise ValueError("need more than 1 value per channel")
        mean, var = x.mean(0), x.var(0, unbiased=False)       # biased: to normalise
        with torch.no_grad():                                 # state, not graph
            run_mean.mul_(1 - momentum).add_(momentum * mean)
            run_var.mul_(1 - momentum).add_(momentum * x.var(0, unbiased=True))
    else:
        mean, var = run_mean, run_var
    return gamma * (x - mean) / torch.sqrt(var + eps) + beta

torch.manual_seed(0)
d = torch.float64
x = torch.randn(8, 3, dtype=d) * 2 + 1
bn = torch.nn.BatchNorm1d(3).double()
rm, rv, g, b = torch.zeros(3, dtype=d), torch.ones(3, dtype=d), torch.ones(3, dtype=d), torch.zeros(3, dtype=d)
print("train:", torch.allclose(batch_norm(x, g, b, rm, rv, True), bn(x)),
      "buffers:", torch.allclose(rm, bn.running_mean) and torch.allclose(rv, bn.running_var))
bn.eval()
print("eval:", torch.allclose(batch_norm(x, g, b, rm, rv, False), bn(x)))
```

```text
train: True buffers: True
eval: True
```

→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex03_layers_by_hand.py`

**Edge cases:** batch of 1 in training (PyTorch raises too); eval before any training (stats
0/1); tiny N, where biased and unbiased variance differ most; float32 tolerance.
**Wrong-but-tempting:** `running = m·running + (1 − m)·batch` (PyTorch's momentum weights the
*new* value); normalising with the unbiased variance. **Follow-ups:** why does batch norm fail
with tiny or correlated batches? (Noisy statistics; use layer or group norm.) Why does inverted
dropout scale at train time? (E[output] = input, so eval needs no change.)

## 37.4 Custom `Dataset` and `DataLoader`

A map-style `Dataset` needs `__len__` and `__getitem__`. Give the `DataLoader` its **own
generator** (order independent of other global-RNG draws) and a `collate_fn` for ragged data (the
default `torch.stack`s and raises on unequal lengths).

```python
import torch
from torch.utils.data import DataLoader

def pad_collate(batch, pad_id=0):
    seqs, labels = zip(*batch)
    lengths = torch.tensor([len(s) for s in seqs])
    padded = torch.full((len(seqs), int(lengths.max())), pad_id)
    for row, s in enumerate(seqs):
        padded[row, :len(s)] = s
    mask = torch.arange(padded.shape[1]) < lengths[:, None]      # True on real tokens
    return padded, mask, torch.tensor(labels)

data = [(torch.tensor([i + 1] * (1 + i % 3)), i) for i in range(6)]   # a list works as a dataset
loader = DataLoader(data, batch_size=4, shuffle=True, collate_fn=pad_collate,
                    generator=torch.Generator().manual_seed(7))
padded, mask, labels = next(iter(loader))
print(padded.tolist(), labels.tolist(), int(mask.sum()), len(loader))
```

```text
[[2, 2, 0], [3, 3, 3], [6, 6, 6], [4, 0, 0]] [1, 2, 5, 3] 9 2
```

With `num_workers > 0`, the loader's
generator already seeds each worker's torch, `random` and NumPy (base seed + worker id); use
`worker_init_fn` only for other libraries or per-worker state. Guard the entry point with
`if __name__ == "__main__"` (Windows/macOS).
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex04_dataset_dataloader.py`

## 37.5 The training loop: forward, loss, backward, step, eval mode

```python
import torch
from torch import nn

def train_one_epoch(model, loader, opt, loss_fn):
    model.train()                                  # dropout on, batch norm uses batch stats
    total = count = 0
    for xb, yb in loader:
        opt.zero_grad()                            # 1. clear old gradients
        loss = loss_fn(model(xb), yb)              # 2. forward; CE takes raw logits
        loss.backward()                            # 3. fill p.grad
        opt.step()                                 # 4. update
        total += loss.item() * len(yb)             # .item(): no graph kept alive
        count += len(yb)
    return total / count                           # example-weighted mean

@torch.no_grad()
def accuracy(model, X, y):
    model.eval()                                   # dropout off, running stats
    return (model(X).argmax(1) == y).float().mean().item()

torch.manual_seed(0)
X = torch.randn(8, 2); y = (X[:, 0] > 0).long()    # one tiny batch
model = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Dropout(0.1), nn.Linear(16, 2))
opt = torch.optim.Adam(model.parameters(), lr=0.05)
losses = [train_one_epoch(model, [(X, y)], opt, nn.CrossEntropyLoss()) for _ in range(100)]
print(f"overfit one batch: {losses[0]:.2f} -> below 0.05: {losses[-1] < 0.05}, acc {accuracy(model, X, y):.2f}")
```

```text
overfit one batch: 0.78 -> below 0.05: True, acc 1.00
```

**Overfit one batch first:** a correct loop drives 8 examples' loss to ≈ 0 in seconds; if not,
the bug is in the code, not the data. Ladder: stare at a full-run curve (epochs × n work,
localises nothing) → overfit one batch (steps × B) → then full runs with `eval()`-mode validation
and per-epoch loss, accuracy and LR.

Schedulers step **after** `opt.step()` (since PyTorch 1.1; the reverse warns and skips the first
LR). Clip with `nn.utils.clip_grad_norm_` between `backward` and `step` (maths: §36.10). In the
repo one corrupted label leaves clean MSE 7.94 unclipped, 0.00223 clipped.
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex05_training_loop.py`,
`chapters/ch37_pytorch_training_debugging/solutions/ex11_clipping_lr_schedules.py`

## 37.6 Mixed precision and gradient accumulation

### Worked problem: accumulate k micro-batches

*The batch of B examples does not fit in memory. Get exactly the full-batch gradient.*

Ladder: (1) shrink the batch: O(B_small) memory but a different, noisier optimisation;
(2) accumulate k micro-batches of B/k, each loss ÷ k, then step: O(B/k) activation memory, same
compute, identical gradient for mean losses; (3) add mixed precision for speed.

```python
import torch
from torch import nn

torch.manual_seed(0)
model = nn.Sequential(nn.Linear(3, 8), nn.Tanh(), nn.Linear(8, 1)).double()
X, y = torch.randn(12, 3, dtype=torch.float64), torch.randn(12, dtype=torch.float64)
loss_of = lambda xb, yb: ((model(xb).squeeze(-1) - yb) ** 2).mean()

def grads(k, divide=True):
    model.zero_grad()                              # once, before the first chunk
    for xc, yc in zip(X.chunk(k), y.chunk(k)):
        loss = loss_of(xc, yc)
        (loss / k if divide else loss).backward()  # .grad accumulates
    return [p.grad.clone() for p in model.parameters()]

full = grads(1)
print("k=4 equals full batch:", all(torch.allclose(a, b) for a, b in zip(grads(4), full)))
print(f"forgot to divide: x{(grads(4, False)[0].norm() / full[0].norm()).item():.2f}")
```

```text
k=4 equals full batch: True
forgot to divide: x4.00
```

→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex06_accumulation_mixed_precision.py`

**Edge cases:** unequal last chunk (weight by size/B); batch norm (per-chunk statistics break
exactness); clip after the last chunk; `zero_grad` inside the loop keeps only the last chunk.
**Follow-ups:** with DDP, skip all-reduce on non-final chunks (`no_sync`); tune the LR for B.

**Mixed precision.** `torch.autocast` runs matmuls in 16 bits (`"cpu"` defaults to bf16,
CUDA to fp16); weights and precision-sensitive ops stay fp32:

| Type | Max | Needs loss scaling? |
|---|---|---|
| fp16 | 65,504; smallest positive ≈ 6e-8 | yes: small gradients underflow to 0 |
| bf16 | ≈ 3.4e38 (fp32's exponent) | usually no; but only a 7-bit mantissa |

Repo checks: under `torch.autocast("cpu", dtype=torch.bfloat16)` a Linear outputs bf16 with fp32
weights; a 1e-8 gradient is 0 in fp16 but survives at scale 2¹⁶. `GradScaler` multiplies the
loss by S, skips the step and halves S on inf/NaN gradients, and doubles S after a run of good
steps; `scaler.unscale_(opt)` before clipping.

## 37.7 Checkpointing and reproducibility (seeds)

Save everything the next step depends on: model and optimizer `state_dict`s (Adam: two moments,
2P floats), scheduler, epoch, and RNG state (dropout uses the global RNG). Derive each epoch's
shuffle from (seed, epoch).

```python
import os, tempfile, torch
from torch import nn

torch.manual_seed(0)
model = nn.Linear(2, 2)
opt = torch.optim.Adam(model.parameters(), lr=0.01)
model(torch.randn(4, 2)).sum().backward(); opt.step()       # create Adam state
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "ckpt.pt")
    torch.save({"model": model.state_dict(), "optimizer": opt.state_dict(),
                "epoch": 3, "torch_rng": torch.get_rng_state()}, path)
    ckpt = torch.load(path, map_location="cpu", weights_only=True)
    model2 = nn.Linear(2, 2)
    model2.load_state_dict(ckpt["model"])     # + opt.load_state_dict, torch.set_rng_state
    print(sorted(ckpt), "weights equal:", torch.equal(model.weight, model2.weight))
```

```text
['epoch', 'model', 'optimizer', 'torch_rng'] weights equal: True
```

The repo resumes 3 + 3 epochs bit-identically to 6 straight; dropping optimizer or RNG state
changes the weights. Version note:
`weights_only` defaults to True from PyTorch 2.6 and refuses arbitrary pickles (a NumPy array
raised `UnpicklingError` here). Seed
`random`, NumPy and torch; on GPU also `torch.use_deterministic_algorithms(True)` (some CUDA ops
then need `CUBLAS_WORKSPACE_CONFIG`).
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex07_checkpoint_reproducibility.py`

## 37.8 Debugging shape errors and NaNs

**Shapes.** Broadcasting turns shape bugs into silent wrong answers: prediction (N, 1) minus
target (N,) is (N, N), and `F.mse_loss` only *warns*. Assert shapes at the loss. After
`transpose`, `view` raises (non-contiguous); `reshape` copies if needed.

**NaNs.** Sources: exp overflow or log(0) in a hand-written softmax (use `F.cross_entropy` on
logits, → §35.10); √ at 0 in backward; zero std; fp16 overflow; too high an LR (on w², lr = 1.1
diverges since |1 − 2·lr| > 1). Find the *first* bad layer with forward hooks, no model edits:

```python
import torch
from torch import nn

def first_nonfinite(model, x):
    bad, handles = [], []
    for name, m in model.named_modules():
        if not list(m.children()):                         # leaf modules only
            handles.append(m.register_forward_hook(
                lambda mod, inp, out, name=name: bad.append(name)
                if not bad and not torch.isfinite(out).all() else None))
    try:
        with torch.no_grad():
            model(x)
    finally:
        for h in handles:
            h.remove()                                     # always clean up
    return bad[0] if bad else None

torch.manual_seed(0)
net = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 1))
print("clean:", first_nonfinite(net, torch.randn(3, 4)))
with torch.no_grad():
    net[0].bias[0] = float("nan")
print("poisoned:", first_nonfinite(net, torch.randn(3, 4)))
```

```text
clean: None
poisoned: 0
```

For backward, `torch.autograd.set_detect_anomaly(True)` raises at the op that produced NaN
(`SqrtBackward0` in the repo); it is slow, so debug only. Check gradients themselves with central
differences in float64 (error O(ε²) vs O(ε) forward; 2P evaluations) or
`torch.autograd.gradcheck`; the repo catches a custom `autograd.Function` missing a term.
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex09_shapes_and_nans.py`,
`chapters/ch37_pytorch_training_debugging/solutions/ex08_gradient_check.py`

## 37.9 "Debug this broken training loop" exercises

### Worked problem: one loop, many bugs

*"Our classifier trains but something's off." Find the bugs.*

Ladder: (1) re-read top to bottom: unbounded time, and softmax-before-CE reads as normal code;
(2) a symptom table narrows the causes; (3) table plus probes (overfit one batch, weights moved?,
eval twice, assert shapes), each a yes/no from one step.

```python
import torch
import torch.nn.functional as F
from torch import nn

def run(bug=None, steps=100):
    torch.manual_seed(0)
    X = torch.randn(120, 2); y = (X[:, 0] > 0).long() + (X[:, 1] > 0).long()
    body, head = nn.Linear(2, 32), nn.Linear(32, 3)
    w0 = body.weight.detach().clone()
    opt = torch.optim.SGD([*body.parameters(), *head.parameters()], lr=0.1, momentum=0.9)
    for _ in range(steps):
        if bug != "no_zero_grad":
            opt.zero_grad()
        h = torch.relu(body(X))
        if bug == "detach":
            h = h.detach()                        # features cut from the graph
        logits = head(h)
        if bug == "softmax":
            logits = logits.softmax(1)            # CE already applies log_softmax
        loss = F.cross_entropy(logits, y)
        loss.backward()
        opt.step()
    return f"{loss.item():.3g}", not torch.equal(w0, body.weight)

for bug in (None, "no_zero_grad", "softmax", "detach"):
    print(f"{bug!s:>12}: final loss, body moved = {run(bug)}")
```

```text
        None: final loss, body moved = ('0.0669', True)
no_zero_grad: final loss, body moved = ('3.8e+03', True)
     softmax: final loss, body moved = ('0.614', True)
      detach: final loss, body moved = ('0.188', False)
```

| Symptom | Likely cause | Probe / fix |
|---|---|---|
| loss explodes or oscillates | no `zero_grad` | `.grad` sums all past steps |
| loss floored above log(1 + (C−1)/e), 0.551 for C = 3 | softmax before `CrossEntropyLoss` | pass raw logits |
| part of the net never changes | `.detach()` mid-model | weights before/after a step |
| eval metrics change between identical calls | `model.eval()` missing | eval twice; compare |
| "modified by an inplace operation" | `h.add_()` / `relu_` on a saved tensor | out-of-place op |
| regression loss stuck high | (N, 1) vs (N,) broadcast | `squeeze(1)`; assert shapes |

In the repo version (six bugs), softmax-before-CE and the detached body still reach accuracy
1.00: accuracy alone proves nothing. The broadcast bug's true MSE is 3.36 vs 0.0000 fixed.
→ repo: `chapters/ch37_pytorch_training_debugging/solutions/ex10_broken_training_loops.py`

**Edge-case checklist:** targets are long class indices; shapes equal at the loss;
`model.train()` re-enabled after eval; `scheduler.step()` after `opt.step()`; logged losses use
`.item()`. **Follow-ups:** "NaN after 1,000 steps": log the norm `clip_grad_norm_` returns, then
clip or lower the LR. "Validation beats training": dropout is on only in training.

## 37.10 Practice set

### Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Tensors, autograd and devices | ★ | reverse-mode autodiff |
| 02 | nn.Module, layers and parameters | ★ | module registration |
| 03 | Core layers by hand | ★ | re-implement + cross-check |
| 04 | Custom Dataset and DataLoader | ★ | seeded loader + collate |
| 05 | The training loop | ★ | forward/loss/backward/step, eval |
| 06 | Gradient accumulation and mixed precision | ◆ | micro-batches, loss scaling |
| 07 | Checkpointing and reproducibility | ★ | full-state checkpoint |
| 08 | Gradient check against finite differences | ◆ | numeric vs analytic gradients |
| 09 | Debugging shape errors and NaNs | ★ | hooks, asserts, stable losses |
| 10 | Debug this broken training loop | ★ | symptom → probe → fix |
| 11 | Gradient clipping and LR schedules in torch | ◆ | optimizer hygiene |

Index and run commands: `chapters/ch37_pytorch_training_debugging/README.md`.

## Interviewer's view

- **Rewarded:** the loop unprompted; `eval()` + `no_grad`; overfit one batch first; shape
  asserts; checkpointing optimizer and RNG.
- **Penalised:** softmax before `CrossEntropyLoss`; blaming the LR before any probe;
  `retain_graph=True` to silence an error.

## Checkpoint quiz

1. Three `backward` calls on fresh graphs of x² at x = 3, never zeroed: `x.grad`?
2. Why does `nn.Module` see no parameters in `self.layers = [nn.Linear(2, 2)]`?
3. Batch norm in eval mode: which statistics normalise the input?
4. Four micro-batches, mean losses, no division by 4: what happens to the update?
5. A classifier's loss never drops below 0.55 with 3 classes, yet accuracy is high. Diagnosis?

<details><summary>Answers</summary>

1. 18: each call adds 6.
2. Only Modules and Parameters assigned directly as attributes register (buffers need
   `register_buffer`); a list hides them. Use `nn.ModuleList`.
3. The running mean and (unbiased) variance accumulated in training.
4. The gradient is 4× the full-batch one: an effective LR change.
5. Softmax before `CrossEntropyLoss` (floor log(1 + 2/e) ≈ 0.551); pass raw logits.
</details>

## Summary card

- `backward` adds into `.grad`: `zero_grad` → forward → loss → `backward` → (clip) → `step` →
  scheduler. Evaluate under `eval()` + `no_grad()`.
- Register with `ModuleList` / `register_buffer`. Batch norm: biased variance to normalise,
  unbiased in the buffer, momentum weights the new value. Dropout scales by 1/(1 − p).
- Seeded `DataLoader` generator + `collate_fn`; accumulate with loss/k; fp16 needs loss scaling.
- Checkpoint = model + optimizer + scheduler + epoch + RNG; `weights_only=True`.
- Debug: overfit one batch, assert shapes, hooks for the first NaN, float64 gradcheck, weights
  moved?
