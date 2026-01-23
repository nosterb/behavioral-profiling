# Research Brief: Reminder (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-21
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
| **Median Sophistication** | 6.900 | 6.900 |

---

## Outliers Removed (1)

- **Gemini-3-Pro-Preview**: Soph=8.36, Disinhib=4.12, 5.0 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.69 | 2.18 | +0.49 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.732 | 0.806 | +0.074 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 2.32 | 2.87 | +0.54 |
| Aggression | 1.77 | 2.17 | +0.39 |
| Tribalism | 0.94 | 0.93 | -0.02 |
| Grandiosity | 0.75 | 0.71 | -0.05 |

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

**Parent Analysis**: `../reminder/RESEARCH_BRIEF.md`
**Generated**: 2026-01-21 13:02
