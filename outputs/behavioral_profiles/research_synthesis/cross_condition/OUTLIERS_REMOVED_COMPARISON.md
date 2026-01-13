# Cross-Condition Comparison: Outlier Sensitivity Analysis

**Last Updated**: 2026-01-12
**Conditions**: 5
**Threshold**: 2.0 SD from regression line
**Status**: PRELIMINARY - Reserved for H3 Hypothesis Development

> **Note**: Cross-condition outlier analysis is reserved for future H3 hypothesis work. Current research efforts are focused on H1/H2 validation. Data in this file is auto-generated but interpretation is pending.

---

## Summary Table (Original → Outliers Removed)

| Metric | baseline | authority | minimal_steering | telemetryV3 | urgency |
|--------|--------|--------|--------|--------|--------|
| **N** | 46 → 44 | 45 → 44 | 46 → 45 | 46 → 43 | 45 → 44 |
| **Median Soph** | 5.93 → 5.93 (+0.00) | 6.72 → 6.64 (-0.08) | 5.17 → 5.34 (+0.17) | 5.02 → 4.93 (-0.09) | 6.17 → 6.16 (-0.02) |
| **H1: d** | 2.17 → 2.84 (+0.68) | 1.86 → 2.47 (+0.61) | 1.83 → 1.83 (+0.01) | 1.14 → 1.80 (+0.66) | 1.77 → 1.82 (+0.06) |
| **H2: r** | 0.738 → 0.696 (-0.042) | 0.588 → 0.574 (-0.014) | 0.509 → 0.472 (-0.036) | 0.724 → 0.707 (-0.017) | 0.563 → 0.570 (+0.007) |

---

## Outliers Removed by Condition

| Condition | Outliers Removed | SD from Line |
|-----------|------------------|--------------|
| **baseline** | Gemini-3-Pro-Preview | 4.43 |
| **authority** | Gemini-3-Pro-Preview | 4.81 |
| **minimal_steering** | Llama-3-70B | 2.19 |
| **telemetryV3** | Claude-4.5-Haiku-Thinking (Thinking) | 4.60 |
| | Grok-4-0709 | 3.58 |
| **urgency** | DeepSeek-R1 | 3.36 |

---

## Robustness Assessment

**Baseline**: **Sensitive** - Results substantially affected by outliers
  - H1 change: d 2.17 → 2.84 (Δ = +0.68)
  - H2 change: r 0.738 → 0.696 (Δ = -0.042)

**Authority**: **Sensitive** - Results substantially affected by outliers
  - H1 change: d 1.86 → 2.47 (Δ = +0.61)
  - H2 change: r 0.588 → 0.574 (Δ = -0.014)

**Minimal_steering**: **Highly Robust** - Results stable with/without outliers
  - H1 change: d 1.83 → 1.83 (Δ = +0.01)
  - H2 change: r 0.509 → 0.472 (Δ = -0.036)

**Telemetryv3**: **Sensitive** - Results substantially affected by outliers
  - H1 change: d 1.14 → 1.80 (Δ = +0.66)
  - H2 change: r 0.724 → 0.707 (Δ = -0.017)

**Urgency**: **Highly Robust** - Results stable with/without outliers
  - H1 change: d 1.77 → 1.82 (Δ = +0.06)
  - H2 change: r 0.563 → 0.570 (Δ = +0.007)


---

## Interpretation

### What This Analysis Shows

This sensitivity analysis tests whether the H1 and H2 findings are robust to the
removal of statistical outliers (models > 2 SD from the sophistication-disinhibition
regression line).

### Key Questions Answered

1. **Are findings robust?** If H1 (d) and H2 (r) remain similar after outlier removal,
   the findings are robust and not driven by a few extreme cases.

2. **Which conditions are most affected?** Large changes indicate sensitivity to
   specific outlier models.

3. **Are outliers consistent across conditions?** The same model appearing as an
   outlier in multiple conditions may indicate systematic measurement issues.

### Robustness Criteria

| Change | H1 (d) | H2 (r) | Interpretation |
|--------|--------|--------|----------------|
| Minimal | < 0.2 | < 0.05 | Highly robust |
| Moderate | 0.2-0.5 | 0.05-0.1 | Moderately robust |
| Large | > 0.5 | > 0.1 | Sensitive to outliers |

---

## Files Referenced

- `../baseline/median_split_classification.json`
- `../baseline/outliers_removed/median_split_classification.json`
- `../baseline/outliers_removed/outlier_removal_info.json`
- `../authority/median_split_classification.json`
- `../authority/outliers_removed/median_split_classification.json`
- `../authority/outliers_removed/outlier_removal_info.json`
- `../minimal_steering/median_split_classification.json`
- `../minimal_steering/outliers_removed/median_split_classification.json`
- `../minimal_steering/outliers_removed/outlier_removal_info.json`
- `../telemetryV3/median_split_classification.json`
- `../telemetryV3/outliers_removed/median_split_classification.json`
- `../telemetryV3/outliers_removed/outlier_removal_info.json`
- `../urgency/median_split_classification.json`
- `../urgency/outliers_removed/median_split_classification.json`
- `../urgency/outliers_removed/outlier_removal_info.json`
