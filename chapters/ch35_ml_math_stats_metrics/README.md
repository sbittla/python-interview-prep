# Chapter 35 — ML Math, Statistics and Metrics

Manuscript: `manuscript/ch35_ml_math_stats_metrics.md`. NumPy plus the standard library only
(no scikit-learn or SciPy): every metric is cross-checked against a hand-computed case and a
brute-force rung.

| # | Exercise | Tier | Pattern | Rungs implemented | Section |
|---|---|---|---|---|---|
| 01 | [Streaming mean and variance (Welford)](solutions/ex01_welford_variance.py) | ★ | one-pass statistics | sum-of-squares → two-pass → Welford + Chan merge | 35.4 |
| 02 | [Gradient check by finite differences](solutions/ex02_gradient_check.py) | ★ | matrix calculus + numerical check | forward diff → central diff → analytic MSE / logistic gradients | 35.1–35.2 |
| 03 | [Bayes' rule: screening tests](solutions/ex03_bayes_rule.py) | ★ | Bayes, base rates | population count → Monte Carlo → formula; sequential / odds form | 35.3 |
| 04 | [Bootstrap confidence intervals](solutions/ex04_bootstrap_ci.py) | ★ | resampling | loop → vectorised percentile bootstrap; normal CI; coverage simulation | 35.5 |
| 05 | [A/B test: z-test, power, peeking](solutions/ex05_ab_test.py) | ★ | hypothesis testing | permutation test → pooled z-test; sample size + simulated power; A/A peeking | 35.6 |
| 06 | [Confusion matrix, precision, recall, F1](solutions/ex06_confusion_prf.py) | ★ | counting + averaging | O(k²n) count → `np.add.at`; macro / micro / weighted; F-beta | 35.7 |
| 07 | [ROC-AUC three ways, with ties](solutions/ex07_roc_auc.py) | ★ | Mann–Whitney rank statistic | all pairs → ROC + trapezoid → average-rank formula | 35.7 |
| 08 | [Average precision, PR-AUC, calibration](solutions/ex08_pr_auc_calibration.py) | ★ | threshold sweep + binning | per-threshold recount → sorted sweep; trapezoid contrast; Brier, ECE | 35.7 |
| 09 | [Regression metrics: MSE, MAE, R²](solutions/ex09_regression_metrics.py) | ★ | loss ↔ centre | grid-search best constant vs mean / median; R² conventions; MAPE | 35.8 |
| 10 | [Ranking metrics: P@K, R@K, MRR, MAP, NDCG](solutions/ex10_ranking_metrics.py) | ★ | position-weighted counting | recomputed P@i → running AP; permutation IDCG → sorted IDCG | 35.9 |
| 11 | [Lab: log-sum-exp, log-softmax, cross-entropy](solutions/ex11_stable_logsumexp_ce.py) | ★ | log-space arithmetic | naive → max-shift → log-softmax CE + gradient; binary loss from logits vs clipped probs | 35.10 |
| 12 | [Cross-validation splits without leakage](solutions/ex12_cv_leakage.py) | ★ | fit inside the fold | k-fold → stratified / group / time-series; leaky vs honest feature selection | 35.11 |

Stated conventions (the places definitions differ between libraries):
- variance: `ddof=1` (sample) unless `ddof=0` is passed;
- 0/0 in precision, recall, F1: 0.0;
- AUC ties: half credit; AP: step-wise, non-interpolated, tied scores form one step;
- AP@K (ranking): divided by min(|relevant|, K); NDCG gain 2^g − 1 unless `exp_gain=False`;
- p-values two-sided unless `alternative="larger"`; bootstrap intervals are percentile intervals;
- R² with a constant target: 1.0 if perfect, else 0.0.

## How to run

```bash
OPENBLAS_NUM_THREADS=4 .venv/Scripts/python chapters/ch35_ml_math_stats_metrics/solutions/ex07_roc_auc.py
.venv/Scripts/python -m pytest chapters/ch35_ml_math_stats_metrics                    # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch35_ml_math_stats_metrics   # your stubs
.venv/Scripts/python tools/run_all.py --chapter 35                                    # regenerate outputs/
```

Work in `exercises/` (stubs raise `NotImplementedError` and carry hints and wrong-but-tempting
answers instead of the approach ladder); compare with `solutions/`; expected program output is
in `outputs/`.
