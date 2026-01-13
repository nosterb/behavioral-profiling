# Research Brief: Authority (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-11
**Parent Condition**: authority
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Authority condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 45 | 44 |
| **Outliers Removed** | — | 1 |
| **High-Sophistication** | 23 | 22 |
| **Low-Sophistication** | 22 | 22 |
| **Median Sophistication** | 6.722 | 6.644 |

---

## Outliers Removed (1)

- **Gemini-3-Pro-Preview**: Soph=8.24, Disinhib=2.75, 4.8 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.86 | 2.47 | +0.61 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.588 | 0.574 | -0.014 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.97 | 2.17 | +0.20 |
| Aggression | 1.79 | 2.14 | +0.36 |
| Tribalism | 1.07 | 1.42 | +0.34 |
| Grandiosity | 0.96 | 0.97 | +0.01 |

---

## Interpretation

Removing outliers **strengthens** the H1a effect, suggesting outliers were noise.

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

**Parent Analysis**: `../authority/RESEARCH_BRIEF.md`
**Generated**: 2026-01-11 16:20
