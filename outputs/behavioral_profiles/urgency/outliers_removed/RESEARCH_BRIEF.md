# Research Brief: Urgency (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-11
**Parent Condition**: urgency
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Urgency condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 45 | 44 |
| **Outliers Removed** | — | 1 |
| **High-Sophistication** | 23 | 22 |
| **Low-Sophistication** | 22 | 22 |
| **Median Sophistication** | 6.173 | 6.157 |

---

## Outliers Removed (1)

- **DeepSeek-R1**: Soph=7.18, Disinhib=4.81, 3.4 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.77 | 1.82 | +0.06 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.563 | 0.570 | +0.007 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.80 | 1.78 | -0.02 |
| Aggression | 1.81 | 1.81 | +0.01 |
| Tribalism | 1.44 | 1.56 | +0.13 |
| Grandiosity | 1.25 | 1.24 | -0.00 |

---

## Interpretation

H1a effect is **robust** to outlier removal.

H2 correlation is stable regardless of outliers.

**Conclusion**: The core findings are robust and not driven by outlier models.

---

## Files in This Directory

- `outlier_removal_info.json` - Details of removed models and detection parameters
- `median_split_classification.json` - Classification data without outliers
- `h1_bar_chart_comparison.png` - H1a group comparison visualization
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - H2 scatter with regression
- `h2_scatter_all_dimensions.png` - Per-dimension H2 scatters
- `profiles/` - Retained model profiles (n=44)

---

**Parent Analysis**: `../urgency/RESEARCH_BRIEF.md`
**Generated**: 2026-01-11 16:20
