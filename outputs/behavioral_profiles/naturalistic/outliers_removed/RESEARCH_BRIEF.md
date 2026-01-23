# Research Brief: Naturalistic (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-23
**Parent Condition**: naturalistic
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Naturalistic condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 44 | 44 |
| **Outliers Removed** | — | 1 |
| **High-Sophistication** | 22 | 22 |
| **Low-Sophistication** | 22 | 22 |
| **Median Sophistication** | 6.357 | 6.272 |

---

## Outliers Removed (1)

- **Gemini-3-Pro-Preview**: Soph=7.73, Disinhib=1.86, 5.1 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 2.09 | 2.40 | +0.31 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.841 | 0.911 | +0.071 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.28 | 1.28 | +0.01 |
| Aggression | 2.08 | 2.18 | +0.10 |
| Tribalism | 1.29 | 1.79 | +0.50 |
| Grandiosity | 1.83 | 1.64 | -0.19 |

---

## Interpretation

Removing outliers **strengthens** the H1a effect, suggesting outliers were noise.

H2 correlation strengthens without outliers.

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

**Parent Analysis**: `../naturalistic/RESEARCH_BRIEF.md`
**Generated**: 2026-01-23 14:50
