# Factor Structure Analysis: Dimension Collapse Justification

**Condition**: baseline
**N**: 45 models
**Generated**: 2026-01-11 21:39

---

## Executive Summary

The 9 behavioral dimensions collapse to 2 composites based on empirical correlations:

| Composite | Dimensions | Justification |
|-----------|------------|---------------|
| **Sophistication** | depth, authenticity | r = 0.964 (near-identical constructs) |
| **Disinhibition** | transgression, aggression, tribalism, grandiosity | avg r = 0.755 (shared factor) |

---

## Sophistication: 2 → 1

| Pair | r |
|------|---|
| depth ↔ authenticity | **0.964** |

Depth and authenticity correlate at r = 0.96 (n = 45), indicating they measure essentially the same underlying construct. Treating them as separate predictors would introduce multicollinearity; averaging them into a single "sophistication" score is statistically appropriate.

---

## Disinhibition: 4 → 1

| Pair | r |
|------|---|
| transgression ↔ aggression | 0.966 |
| tribalism ↔ grandiosity | 0.811 |
| transgression ↔ tribalism | 0.783 |
| aggression ↔ tribalism | 0.775 |
| aggression ↔ grandiosity | 0.620 |
| transgression ↔ grandiosity | 0.573 |

**Average inter-correlation: r = 0.755**

All four dimensions correlate positively (range: 0.57–0.97), suggesting a common "disinhibition" or "boundary-violation" factor. The strongest pairing is transgression ↔ aggression; the weakest involves grandiosity. Averaging into a composite reduces measurement noise while preserving the shared signal.

---

## Cross-Factor Correlations

| Sophistication | Disinhibition | r |
|----------------|---------------|---|
| authenticity | aggression | 0.805 |
| authenticity | transgression | 0.779 |
| depth | grandiosity | 0.728 |
| depth | aggression | 0.690 |
| authenticity | grandiosity | 0.667 |
| depth | transgression | 0.651 |
| authenticity | tribalism | 0.597 |
| depth | tribalism | 0.560 |

**Average cross-factor correlation: r = 0.685** (range: 0.56–0.81)

Sophistication and disinhibition are correlated but not redundant. This supports H2: capability (sophistication) predicts boundary-pushing (disinhibition), but they remain distinguishable constructs.

---

## Full Correlation Matrix

```
            depth  authen  transg  aggres  tribal  grandi
 depth     1.000   0.964   0.651   0.690   0.560   0.728
authen     0.964   1.000   0.779   0.805   0.597   0.667
transg     0.651   0.779   1.000   0.966   0.783   0.573
aggres     0.690   0.805   0.966   1.000   0.775   0.620
tribal     0.560   0.597   0.783   0.775   1.000   0.811
grandi     0.728   0.667   0.573   0.620   0.811   1.000
```

---

## Interpretation Guide

| r value | Interpretation |
|---------|----------------|
| > 0.90 | Near-identical (collapse appropriate) |
| 0.70-0.90 | High (shared factor likely) |
| 0.50-0.70 | Moderate (related but distinct) |
| 0.30-0.50 | Low-moderate (weakly related) |
| < 0.30 | Low (largely independent) |
