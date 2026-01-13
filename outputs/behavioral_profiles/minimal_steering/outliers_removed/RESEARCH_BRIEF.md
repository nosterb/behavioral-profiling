# Research Brief: Minimal Steering (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-11
**Parent Condition**: minimal_steering
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Minimal Steering condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 46 | 45 |
| **Outliers Removed** | — | 1 |
| **High-Sophistication** | 23 | 23 |
| **Low-Sophistication** | 23 | 22 |
| **Median Sophistication** | 5.172 | 5.339 |

---

## Outliers Removed (1)

- **Llama-3-70B**: Soph=2.55, Disinhib=1.30, 2.2 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.83 | 1.83 | +0.01 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.509 | 0.472 | -0.036 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.56 | 1.54 | -0.02 |
| Aggression | 1.39 | 1.65 | +0.26 |
| Tribalism | 0.68 | 0.71 | +0.03 |
| Grandiosity | 0.84 | 0.79 | -0.05 |

---

## Interpretation

H1a effect is **robust** to outlier removal.

H2 correlation weakens slightly without outliers.

**Conclusion**: The core findings are robust and not driven by outlier models.

---

## Files in This Directory

- `outlier_removal_info.json` - Details of removed models and detection parameters
- `median_split_classification.json` - Classification data without outliers
- `h1_bar_chart_comparison.png` - H1a group comparison visualization
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - H2 scatter with regression
- `h2_scatter_all_dimensions.png` - Per-dimension H2 scatters
- `profiles/` - Retained model profiles (n=45)

---

**Parent Analysis**: `../minimal_steering/RESEARCH_BRIEF.md`
**Generated**: 2026-01-11 16:38
