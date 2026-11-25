# Chapter 35. ML Math, Statistics and Metrics

★ Core · Tracks M, L · Study time ≈ 7 h · Prerequisites: Ch. 33 (NumPy), Ch. 8 (Big-O)

**Learning objectives**

- Derive a gradient and prove it with finite differences.
- Answer Bayes, bootstrap and A/B questions with the right formula and caveat.
- Implement every common metric from scratch, ties and 0/0 included, naming the definition.
- Compute log-sum-exp and cross-entropy without overflow; spot CV leakage.

> **Recognise it**
>
> | Signal | Reach for |
> |---|---|
> | "verify your gradient" | central differences (§35.2) |
> | "accurate test, rare disease" | Bayes with the base rate (§35.3) |
> | "CI for a median / AUC" | bootstrap (§35.5) |
> | "is B better?" | z-test, power, no peeking (§35.6) |
> | "imbalanced", "top-K results" | P/R, AP (§35.7); MRR, NDCG (§35.9) |
> | "loss is NaN"; "CV too good" | log-sum-exp (§35.10); leakage (§35.11) |

NumPy idioms: → §33.4, §33.8. Models that use these metrics: → §36.1, §36.2.

## 35.1 Linear algebra refresher for ML

X is (n, d), rows are examples; know each product's shape.

| Object | Formula | Note |
|---|---|---|
| Predictions | Xw | (n,) |
| Cosine | u·v / (‖u‖‖v‖) | in [−1, 1] |
| Projection of u on v | (u·v / v·v) v | nearest point on v's line |
| Covariance | XcᵀXc / (n − 1), Xc = X − column means | (d, d), symmetric PSD |

Gradient identities: ∇(aᵀw) = a, ∇(wᵀAw) = (A + Aᵀ)w, ∇‖Xw − y‖² = 2Xᵀ(Xw − y).
Solves and norms: → §33.6; PCA via SVD: → §36.8.

```python
import numpy as np

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3))
Xc = X - X.mean(axis=0)                       # centre each column
cov = Xc.T @ Xc / (len(X) - 1)                # ddof=1
print(np.allclose(cov, np.cov(X, rowvar=False)), cov.shape)
```

```text
True (3, 3)
```

## 35.2 Calculus refresher: gradients, chain rule

Chain rule: L(w) = mean(ℓ(Xw)) has ∇L = Xᵀℓ′(Xw)/n. Logistic ℓ = log(1 + eᶻ) − yz has
ℓ′ = σ(z) − y; MSE/2 gives Xᵀ(Xw − y)/n.

**Worked problem 1 — Prove a hand-derived gradient.** Rung 1, the forward difference
(f(w + εeᵢ) − f(w))/ε: d + 1 evaluations, error O(ε). Rung 2, the central difference
(f(w + εeᵢ) − f(w − εeᵢ))/(2ε): 2d evaluations, error O(ε²) because the ε Taylor terms
cancel. With O(nd) per evaluation the check is O(nd²); rung 3, the analytic gradient, is one
O(nd) product. The check validates rung 3, then is switched off.

```python
import numpy as np

def numerical_grad(f, w, eps=1e-5):
    g = np.zeros_like(w)
    for i in range(w.size):                   # 2d evaluations of f
        e = np.zeros_like(w)
        e[i] = eps
        g[i] = (f(w + e) - f(w - e)) / (2 * eps)
    return g

def rel_err(a, b):
    return np.linalg.norm(a - b) / max(np.linalg.norm(a) + np.linalg.norm(b), 1e-12)

rng = np.random.default_rng(35)
X, w = rng.normal(size=(50, 4)), rng.normal(size=4)
y = (rng.random(50) < 0.5).astype(float)
softplus = lambda z: np.maximum(z, 0) + np.log1p(np.exp(-np.abs(z)))   # log(1 + e^z)
loss = lambda w: np.mean(softplus(X @ w) - y * (X @ w))
grad = lambda w: X.T @ (1 / (1 + np.exp(-X @ w)) - y) / len(y)
buggy = lambda w: X.T @ (1 / (1 + np.exp(-X @ w)) - y)                # forgot 1/n
print(f"{rel_err(numerical_grad(loss, w), grad(w)):.0e}",
      round(rel_err(numerical_grad(loss, w), buggy(w)), 3))
```

```text
5e-11 0.961
```

Below ~10⁻⁷ passes (float64). Repo ε sweep on eˣ: central error 6e-11 at ε = 10⁻⁵, 1e-05 at
ε = 10⁻¹¹, where round-off (≈ ε_machine·|f|/ε) dominates. **Wrong but tempting:**
absolute instead of relative error; ε = 10⁻¹²; float32. **Edge cases:** kinks (ReLU at 0),
huge logits (softplus), millions of parameters (check a random subset). **Follow-up:** checking
a layer against autograd (→ §37.1).
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex02_gradient_check.py`

## 35.3 Probability: Bayes' rule problems

P(H | E) = P(E | H)P(H) / [P(E | H)P(H) + P(E | ¬H)P(¬H)]. Odds form: posterior odds =
prior odds × LR, with LR₊ = sensitivity / (1 − specificity).

```python
from fractions import Fraction as F

def posterior(prior, sens, spec):
    tp, fp = sens * prior, (1 - spec) * (1 - prior)   # P(+, sick), P(+, healthy)
    return tp / (tp + fp)

p1 = posterior(F(1, 100), F(9, 10), F(91, 100))
print(p1, round(float(p1), 3), posterior(p1, F(9, 10), F(91, 100)))   # 2nd positive test
```

```text
10/109 0.092 100/199
```

Only 9 %: per 10,000 people, 90 true and 891 false positives. Chaining tests assumes they
are independent given the true state. The repo also counts and simulates.
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex03_bayes_rule.py`

## 35.4 Distributions, sampling, sampling bias

| Distribution | Models | Mean | Variance |
|---|---|---|---|
| Bernoulli(p) / Binomial(n, p) | a click / clicks in n views | p / np | p(1 − p) / np(1 − p) |
| Poisson(λ) | events per interval | λ | λ |
| Exponential(λ) | waiting time | 1/λ | 1/λ² |
| Normal(μ, σ²) | sums of many effects | μ | σ² |

CLT: the sample mean is ≈ Normal(μ, σ²/n), so standard errors shrink as 1/√n. Sample variance
divides by n − 1 (`ddof=1`) because x̄ is fitted to the data; NumPy's `var` defaults to
`ddof=0`, pandas' to `ddof=1`. (Σx² − (Σx)²/n)/(n − 1) cancels catastrophically; Welford is one
pass, O(1) per value:

```python
def welford(xs):
    n, mean, m2 = 0, 0.0, 0.0
    for x in xs:
        n += 1
        d = x - mean
        mean += d / n
        m2 += d * (x - mean)                 # old deviation times new deviation
    return mean, m2 / (n - 1)                # ddof=1

xs = [1e9 + v for v in (4.0, 7.0, 13.0, 16.0)]          # true sample variance 30
naive = (sum(x * x for x in xs) - sum(xs) ** 2 / len(xs)) / (len(xs) - 1)
print(naive, welford(xs))
```

```text
0.0 (1000000010.0, 30.0)
```

Two (n, mean, m2) summaries merge in O(1) (repo). **Sampling bias** survives any n: selection,
survivorship, non-response, time drift. Randomise or stratify, or reweight by 1/P(sampled).
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex01_welford_variance.py`

## 35.5 Bootstrap and confidence intervals

Resample the n observations *with replacement* B times, recompute the statistic, take the
α/2 and 1 − α/2 quantiles: the **percentile** bootstrap. One (B, n) index matrix vectorises it;
the work is O(B·n) either way, the loop just pays interpreter overhead.

```python
import numpy as np

def bootstrap_ci(x, stat=np.mean, n_boot=2000, alpha=0.05, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))   # B resamples
    return np.quantile(stat(x[idx], axis=1), [alpha / 2, 1 - alpha / 2])

x = np.random.default_rng(35).exponential(scale=2.0, size=40)
print(bootstrap_ci(x, seed=7).round(3), bootstrap_ci(x, np.median, seed=7).round(3))
```

```text
[1.079 2.056] [0.849 1.787]
```

x̄ ± 1.96·s/√n suffices for a large-sample mean; bootstrap medians, ratios, AUC. Coverage, 300
skewed datasets (repo):

```text
coverage n=10  bootstrap=0.84  normal=0.86  (target 0.95)
coverage n=100 bootstrap=0.95  normal=0.95  (target 0.95)
```

Small n undercovers (try BCa). "95 %" describes the procedure. Resample independent units
(users, not views); it fails for the max.
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex04_bootstrap_ci.py`

## 35.6 A/B testing and significance

**Worked problem 2 — Is B's conversion higher?** A: 200 of 2,000; B: 250 of 2,000. Rung 1, a
permutation test, shuffles arm labels 10⁴ times: O(n_perm·n), no normal approximation. Rung 2,
the pooled two-proportion z-test, is O(1): under H₀ both arms share rate p̂,
SE = √(p̂(1 − p̂)(1/n_a + 1/n_b)), z = (p̂_b − p̂_a)/SE. Rung 3 sizes the test *before* it runs.

```python
from math import ceil, erfc, sqrt
from statistics import NormalDist

def ztest(x_a, n_a, x_b, n_b):
    pooled = (x_a + x_b) / (n_a + n_b)               # H0: one shared rate
    se = sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    if se == 0:
        raise ValueError("zero standard error")
    z = (x_b / n_b - x_a / n_a) / se
    return z, erfc(abs(z) / sqrt(2))                 # two-sided: 2 * (1 - Phi(|z|))

def n_per_arm(p1, p2, alpha=0.05, power=0.8):
    za, zb = NormalDist().inv_cdf(1 - alpha / 2), NormalDist().inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = za * sqrt(2 * pbar * (1 - pbar)) + zb * sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return ceil(num ** 2 / (p2 - p1) ** 2)

z, p = ztest(200, 2000, 250, 2000)
print(round(z, 3), round(p, 4), n_per_arm(0.10, 0.12))
```

```text
2.502 0.0124 3841
```

Repo cross-checks, then an A/A test (no effect) stopped at the first of 20 looks with p < 0.05:

```text
permutation p (10,000 shuffles): 0.0130
simulated power at that n: 0.799
A/A, test once at the end : 0.052
A/A, peek 20 times, stop early: 0.243
```

**Wrong but tempting:** "p = 0.012: a 1.2 % chance H₀ is true" (p is P(data this extreme | H₀));
one-sided after seeing the direction; peeking; analysing sessions when users were randomised. **Edge cases:** SE = 0, unequal arms, n·p < 10 (exact test). **Follow-ups:** many
metrics (Bonferroni α/m or FDR); sequential tests; half the effect ≈ 4× the users.
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex05_ab_test.py`

## 35.7 Classification metrics: accuracy, precision, recall, F1, ROC-AUC, calibration

| Metric | Formula | Use when |
|---|---|---|
| Accuracy | (TP + TN)/n | balanced classes, equal costs |
| Precision / Recall | TP/(TP + FP) / TP/(TP + FN) | false alarms / misses costly |
| F1 | 2PR/(P + R) | one threshold, both matter |
| ROC-AUC | P(s₊ > s₋) + ½P(s₊ = s₋) | threshold-free ranking |
| Average precision | Σₖ (Rₖ − Rₖ₋₁)Pₖ | rare positives |

Rows are truth, columns predictions. Declare 0/0 (the repo returns 0.0, also when P + R = 0).
Macro averages classes equally; micro pools counts (micro-F1 = accuracy, single-label);
weighted uses support. At 1 % positives "always negative" scores 0.99 accuracy, 0 recall.

**Worked problem 3 — ROC-AUC with ties, O(n log n).** Rung 1 compares all (positive,
negative) pairs, ties worth ½: O(n₊n₋). Rung 2 sorts and sums trapezoids over one ROC point per
*distinct* threshold: O(n log n); a tied block's diagonal trapezoid is exactly the ½ credit. Rung 3 skips the curve: AUC = U/(n₊n₋), Mann–Whitney
U = R₊ − n₊(n₊ + 1)/2, R₊ the sum of positive ranks, tied scores sharing their average rank.

```python
import numpy as np

def average_ranks(s):
    order = np.argsort(s, kind="mergesort")
    s_sorted = s[order]
    new = np.r_[True, s_sorted[1:] != s_sorted[:-1]]   # first item of each tied block
    starts = np.flatnonzero(new)
    ends = np.r_[starts[1:], len(s)]                    # block holds ranks starts+1..ends
    ranks = np.empty(len(s))
    ranks[order] = ((starts + 1 + ends) / 2)[np.cumsum(new) - 1]
    return ranks

def auc_rank(y, s):
    y, s = np.asarray(y), np.asarray(s, dtype=float)
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("need both classes")
    u = average_ranks(s)[y == 1].sum() - n_pos * (n_pos + 1) / 2   # Mann-Whitney U
    return u / (n_pos * n_neg)

y, s = [1, 0, 1, 0, 1, 0], [0.9, 0.9, 0.5, 0.5, 0.5, 0.1]
print(round(auc_rank(y, s), 6), round(auc_rank(y[::-1], s[::-1]), 6), round(auc_rank(y, np.exp(s)), 6))
```

```text
0.611111 0.611111 0.611111
```

By hand: the positive at 0.9 earns ½ + 1 + 1, each at 0.5 earns 0 + ½ + 1: 5.5/9; the repo's
all-pairs rung agrees on 2,000 tied scores. `exp` changes nothing: AUC ignores calibration. **Wrong but tempting:**
`argsort().argsort()` ranks or one ROC point per sample: order dependent under ties (0.556
vs 0.667 reversed, repo). **Edge cases:** one class (raise), all tied (0.5), inverted
(flip). **Follow-ups:** a CI by bootstrap (§35.5); why AP under imbalance.
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex07_roc_auc.py`

**Average precision** here is the step-wise, non-interpolated sum over distinct thresholds
(scikit-learn's definition); 11-point interpolated AP and the PR trapezoid differ (no classifier
achieves linear interpolation in PR space). A random ranker's AP ≈ prevalence, its ROC-AUC 0.5,
so AP exposes rare-class rankers that ROC-AUC flatters. **Calibration:** cases scored 0.8 should be ~80 % positive. Brier =
mean((p − y)²) is a proper scoring rule; ECE bins p into ten equal-width bins and averages
|mean(y) − mean(p)| weighted by bin size. Sharpening logits ×3 keeps AP, ruins calibration:

```text
hand case AP: 0.833333  brute: 0.833333  trapezoid: 0.791667
1% prevalence: ROC-AUC=0.846  AP=0.113  random-ranker AP ~ 0.010
calibrated   : ECE=0.005  Brier=0.174  AP=0.8190
overconfident: ECE=0.147  Brier=0.200  AP=0.8190
```

Recalibrate on held-out data (Platt, isotonic, temperature).
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex06_confusion_prf.py`,
`chapters/ch35_ml_math_stats_metrics/solutions/ex08_pr_auc_calibration.py`

## 35.8 Regression metrics: MSE, MAE, R²

| Metric | Formula | Best constant | Note |
|---|---|---|---|
| MSE / RMSE | mean((y − ŷ)²) / its root | mean | outliers dominate |
| MAE | mean(\|y − ŷ\|) | median | robust |
| R² | 1 − SS_res/SS_tot | scores 0 | < 0: worse than the mean |
| MAPE | mean(\|y − ŷ\|/\|y\|) | — | undefined at y = 0 |

The loss decides what you estimate. Constant target: R² is 1.0 if perfect, else 0.0
(scikit-learn's default). Line 1: y = [3, −0.5, 2, 7]; then y = [1, 2, 2, 3,
50]; last, y = [1, 2, 3] predicted reversed:

```text
mse 0.375  rmse 0.6124  mae 0.5  r2 0.9486
mean 11.6  median 2.0
best constant under MSE: 11.6  under MAE: 2.0
r2 predicting the mean : 0.0
r2 worse than the mean : -3.0
```

Adjusted R² = 1 − (1 − R²)(n − 1)/(n − p − 1). Batch RMSE: average MSEs, then take the root.
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex09_regression_metrics.py`

## 35.9 Ranking/retrieval metrics: Precision@K, Recall@K, MRR, MAP, NDCG

Ranks are 1-based. P@K = top-K hits / K; R@K = hits / |relevant|; MRR averages 1/rank of
the first hit (0 if none). AP@K averages P@i at each relevant i ≤ K; this book
divides by min(|relevant|, K) (others use |relevant| or hits found). NDCG@K = DCG/IDCG with
DCG = Σ (2^gᵢ − 1)/log₂(i + 1); IDCG sorts *all judged* gains descending, optimal because
discounts fall with rank.

```python
from math import log2

def ap_at_k(ranked, relevant, k):
    hits, total = 0, 0.0
    for i, d in enumerate(ranked[:k], start=1):
        if d in relevant:
            hits += 1
            total += hits / i                      # P@i at each relevant position
    return total / min(len(relevant), k) if relevant else 0.0

def ndcg_at_k(ranked, gains, k):
    dcg = lambda gs: sum((2 ** g - 1) / log2(i + 1) for i, g in enumerate(gs, start=1))
    ideal = dcg(sorted(gains.values(), reverse=True)[:k])
    return dcg([gains.get(d, 0) for d in ranked[:k]]) / ideal if ideal > 0 else 0.0

ranked = ["d3", "d1", "d7", "d2", "d9"]
print(round(ap_at_k(ranked, {"d1", "d2", "d4"}, 5), 4),
      round(ndcg_at_k(ranked, {"d1": 3, "d2": 2, "d3": 0, "d4": 1, "d7": 1}, 3), 4))
```

```text
0.3333 0.5234
```

O(K) per query plus O(m log m) for IDCG. MRR when only the first hit matters; Recall@K for a
retriever feeding a reranker (→ §40.6, §40.9); NDCG for graded relevance.
**Wrong but tempting:** IDCG from only the *retrieved* items (missing relevant documents then
scores 1.0); a log₂(i) discount (division by zero at rank 1).
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex10_ranking_metrics.py`

## 35.10 Numerical stability: log-sum-exp, stable softmax and cross-entropy (lab)

**Worked problem 4 — Cross-entropy from logits that never overflows.** Rung 1,
`log(exp(z).sum())`, overflows past z ≈ 709. Rung 2, softmax with the row max subtracted
(`chapters/ch33_numpy_vectorization/solutions/ex09_softmax.py`), still underflows tiny
probabilities to 0, whose log is −inf. Rung 3 stays in log space:
lse(z) = m + log Σ e^(z − m), log-softmax = z − lse(z), CE picks one entry. O(nC) throughout.

```python
import numpy as np

def logsumexp(Z):
    m = Z.max(axis=1, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)          # all -inf row: shift by 0, not NaN
    with np.errstate(divide="ignore"):
        return (m + np.log(np.exp(Z - m).sum(axis=1, keepdims=True)))[:, 0]

def cross_entropy(Z, y):                          # mean over rows, natural log
    return np.mean(logsumexp(Z) - Z[np.arange(len(y)), y])

Z = np.array([[1000.0, 1000.0], [800.0, 0.0], [-np.inf, -np.inf]])
print(logsumexp(Z).tolist(), cross_entropy(Z[1:2], np.array([1])))
with np.errstate(over="ignore"):
    print(np.log(np.exp(Z[:2]).sum(axis=1)).tolist())          # naive: overflow
```

```text
[1000.6931471805599, 800.0, -inf] 800.0
[inf, inf]
```

The gradient is (softmax(Z) − onehot(y))/n, from ∂/∂zⱼ[lse(z) − z_y] = softmaxⱼ − [j = y]; the
repo matches it to central differences within 8e-11. Binary labels: loss = softplus(z) − yz. Clipping
probabilities to [10⁻¹⁵, 1 − 10⁻¹⁵] only caps the damage: logit 40, label 0 has true loss 40,
clipped ≈ 34.5. PyTorch's `cross_entropy` takes logits; NaN losses: → §37.8. **Wrong but
tempting:** `log(softmax(z))`; one global max for a batch. **Edge cases:** all −inf row, C = 1. **Follow-ups:** label smoothing; softmax(z/T).
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex11_stable_logsumexp_ce.py`

## 35.11 Data leakage, cross-validation, class imbalance, feature engineering

**Leakage** is training information absent at prediction time: *target leakage* (a feature
from the label or the future, "refund issued" predicting fraud) or *contamination* (scaling,
imputation, feature selection, encoding or oversampling fitted before splitting).

| Splitter | Guarantees | Use for |
|---|---|---|
| k-fold | each row tested once; sizes differ ≤ 1 | i.i.d. rows |
| stratified | per-class counts differ ≤ 1 | imbalance |
| group | no group in both train and test | several rows per user |
| time series | train strictly before test | forecasting, drift |

Repo: 60 rows, 2,000 noise features, random labels; top-20 features, 5-fold nearest-centroid CV:

```text
random labels, select features BEFORE CV: 0.95
random labels, select features INSIDE CV: 0.52 (chance = 0.5)
```

Fit every step inside the fold; nested CV keeps tuning out of the reported score.
**Imbalance:** stratify, report PR metrics, reweight (w_c = n/(C·n_c): 0.625 and 2.5 for 12:3),
resample the *training fold only*, or move the threshold.
→ repo: `chapters/ch35_ml_math_stats_metrics/solutions/ex12_cv_leakage.py`

## Interviewer's view

- **Definition before number** (ddof, 0/0, ties, which AP, sidedness); cross-check by hand.
- **Metric fits the cost:** imbalance → AP; ranking → NDCG/MRR.
- **Name the trap:** base rates, peeking, leakage, overflow.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Welford variance | ★ | one-pass stats |
| ex02 | Gradient check | ★ | finite differences |
| ex03 | Bayes screening | ★ | base rates |
| ex04 | Bootstrap CIs | ★ | resampling |
| ex05 | A/B test, power, peeking | ★ | hypothesis test |
| ex06 | Confusion, P/R/F1 | ★ | counting |
| ex07 | ROC-AUC three ways | ★ | rank statistic |
| ex08 | AP, calibration | ★ | threshold sweep |
| ex09 | MSE, MAE, R² | ★ | loss ↔ centre |
| ex10 | P@K, MRR, MAP, NDCG | ★ | position weights |
| ex11 | Log-sum-exp lab | ★ | log space |
| ex12 | CV without leakage | ★ | fit in fold |

Index: `chapters/ch35_ml_math_stats_metrics/README.md`.

## Checkpoint quiz

1. Why does the central difference beat the forward difference?
2. Prevalence 1 %, sensitivity 0.9, specificity 0.91: P(sick | +)?
3. Why does stopping at the first p < 0.05 inflate false positives?
4. A positive and a negative both score 0.9: that pair's AUC credit?
5. Why does selecting features before CV inflate the score?

<details>
<summary>Answers</summary>

1. Its O(ε) Taylor terms cancel: error O(ε²).
2. 0.009 / (0.009 + 0.0891) = 10/109 ≈ 0.092.
3. Each look is another chance to cross: 24 % with 20 looks.
4. ½.
5. Test-fold labels chose the features: 0.95 on random labels.

</details>

## Summary card

- **Gradients:** logistic ∇ = Xᵀ(σ(Xw) − y)/n; check by central differences, rel. error < 10⁻⁷.
- **Bayes:** include the base rate. **Variance:** state ddof; Welford for streams.
- **Bootstrap:** resample units with replacement. **A/B:** pooled z; size first; never peek.
- **P/R/F1:** declare 0/0. **AUC:** ties ½, ranks, O(n log n). **AP:** baseline = prevalence.
- **Regression:** MSE → mean, MAE → median, R² < 0 possible. **NDCG:** IDCG over all judged.
- **Stability:** log-sum-exp, losses from logits. **CV:** fit every step inside the fold.
