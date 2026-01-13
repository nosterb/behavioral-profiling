# Research Brief: Baseline (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-11
**Parent Condition**: baseline
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Baseline condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 46 | 44 |
| **Outliers Removed** | — | 1 |
| **High-Sophistication** | 23 | 22 |
| **Low-Sophistication** | 23 | 22 |
| **Median Sophistication** | 5.930 | 5.930 |

---

## Outliers Removed (1)

- **Gemini-3-Pro-Preview**: Soph=7.50, Disinhib=2.31, 4.4 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 2.17 | 2.84 | +0.68 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.738 | 0.696 | -0.042 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.85 | 2.01 | +0.16 |
| Aggression | 2.21 | 2.46 | +0.26 |
| Tribalism | 1.31 | 1.56 | +0.25 |
| Grandiosity | 1.74 | 1.87 | +0.13 |

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

**Parent Analysis**: `../baseline/RESEARCH_BRIEF.md`
**Generated**: 2026-01-11 16:19
