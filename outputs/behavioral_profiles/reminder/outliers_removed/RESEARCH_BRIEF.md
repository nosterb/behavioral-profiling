# Research Brief: Reminder (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-14
**Parent Condition**: reminder
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Reminder condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 46 | 44 |
| **Outliers Removed** | — | 1 |
| **High-Sophistication** | 23 | 22 |
| **Low-Sophistication** | 23 | 22 |
| **Median Sophistication** | 6.833 | 6.833 |

---

## Outliers Removed (1)

- **Gemini-3-Pro-Preview**: Soph=8.41, Disinhib=4.00, 5.4 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.51 | 2.10 | +0.59 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.458 | 0.412 | -0.046 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 2.05 | 2.56 | +0.51 |
| Aggression | 1.41 | 1.76 | +0.35 |
| Tribalism | 0.92 | 0.91 | -0.02 |
| Grandiosity | 0.64 | 0.57 | -0.06 |

---

## Interpretation

Removing outliers **strengthens** the H1a effect, suggesting outliers were noise.

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
- `profiles/` - Retained model profiles (n=44)

---

**Parent Analysis**: `../reminder/RESEARCH_BRIEF.md`
**Generated**: 2026-01-14 09:53
