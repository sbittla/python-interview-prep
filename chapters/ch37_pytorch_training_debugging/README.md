# Chapter 37 — PyTorch Training and Debugging

Manuscript: `manuscript/ch37_pytorch_training_debugging.md`. Uses `torch` (CPU only; verified on
torch 2.15.0+cpu), `numpy` and the standard library. Every file calls `torch.set_num_threads(1)`,
fixes its seeds, and prints rounded numbers or booleans, so `outputs/` is byte-identical run to run.

| # | Exercise | Tier | Pattern | Rungs / bugs covered | Section |
|---|---|---|---|---|---|
| 01 | [Tensors, autograd and devices](solutions/ex01_tensors_autograd.py) | ★ | reverse-mode autodiff | hand derivative → finite differences → autograd; `.grad` accumulation, `no_grad`, `detach`, `retain_grad` | 37.1 |
| 02 | [nn.Module, layers and parameters](solutions/ex02_module_parameters.py) | ★ | module registration | attributes → plain list (0 params, the bug) → `ModuleList`; buffers, freezing | 37.2 |
| 03 | [Core layers by hand](solutions/ex03_layers_by_hand.py) | ★ | re-implement + cross-check | linear; conv loops → im2col; batch norm (train/eval, running stats); layer norm; inverted dropout; embedding | 37.3 |
| 04 | [Custom Dataset and DataLoader](solutions/ex04_dataset_dataloader.py) | ★ | map-style dataset + seeded loader | manual slicing → default collate (fails on ragged) → own `Generator` + padding collate with mask | 37.4 |
| 05 | [The training loop](solutions/ex05_training_loop.py) | ★ | forward/loss/backward/step, eval | overfit one batch → fit with eval mode, weighted epoch loss, `StepLR` | 37.5 |
| 06 | [Gradient accumulation and mixed precision](solutions/ex06_accumulation_mixed_precision.py) | ◆ | micro-batches, loss scaling | smaller batch → accumulate (÷k) → + autocast; fp16 under/overflow; dynamic loss scaler | 37.6 |
| 07 | [Checkpointing and reproducibility](solutions/ex07_checkpoint_reproducibility.py) | ★ | save everything the next step depends on | whole model → model `state_dict` → model + optimizer + RNG + epoch; bit-identical resume | 37.7 |
| 08 | [Gradient check against finite differences](solutions/ex08_gradient_check.py) | ◆ | numeric vs analytic gradients | forward diff → central diff in float64 → `gradcheck`; custom `autograd.Function` | 37.1, 37.8 |
| 09 | [Debugging shape errors and NaNs](solutions/ex09_shapes_and_nans.py) | ★ | hooks, shape asserts, stable losses | prints → forward hooks / anomaly mode → prevention | 37.8 |
| 10 | [Debug this broken training loop](solutions/ex10_broken_training_loops.py) | ★ | symptom → probe → fix | no `zero_grad`, softmax before CE, detached features, no `eval()`, in-place on saved tensor, (N,1) vs (N,) broadcast | 37.9 |
| 11 | [Gradient clipping and LR schedules in torch](solutions/ex11_clipping_lr_schedules.py) | ◆ | optimizer hygiene | lower LR → clip by value → clip by norm; warm-up + cosine via `LambdaLR` | 37.5 (maths in §36.10) |

Tests are written to fail on the classic bugs: each solution was mutated (missing `zero_grad`,
wrong batch-norm momentum or variance, no dropout rescale, unseeded loader, missing optimizer or
RNG state in a checkpoint, `/eps` instead of `/2eps`, clipping that also scales small gradients up, …) and every mutant
made its test file fail.

## How to run

```bash
OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 .venv/Scripts/python chapters/ch37_pytorch_training_debugging/solutions/ex10_broken_training_loops.py
.venv/Scripts/python -m pytest chapters/ch37_pytorch_training_debugging                    # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch37_pytorch_training_debugging   # your stubs
.venv/Scripts/python tools/run_all.py --chapter 37                                          # regenerate outputs/
```

Work in `exercises/` (stubs raise `NotImplementedError` and carry hints and wrong-but-tempting
answers instead of the approach ladder); compare with `solutions/`; expected output is in `outputs/`.
