# Research Brief: All Combined (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-24
**Parent Condition**: all_combined
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the All Combined condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 45 | 42 |
| **Outliers Removed** | — | 3 |
| **High-Sophistication** | 23 | 21 |
| **Low-Sophistication** | 22 | 21 |
| **Median Sophistication** | 7.025 | 6.118 |

---

## Outliers Removed (3)

- **Gemini-3-Pro-Preview**: Soph=7.14, Disinhib=2.40, 3.5 SD above line
- **DeepSeek-R1**: Soph=6.40, Disinhib=2.13, 2.6 SD above line
- **GPT-OSS-120B**: Soph=6.82, Disinhib=1.52, 2.0 SD below line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 2.30 | 3.02 | +0.73 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.815 | 0.873 | +0.058 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 2.06 | 2.85 | +0.80 |
| Aggression | 2.25 | 2.60 | +0.35 |
| Tribalism | 1.66 | 2.51 | +0.85 |
| Grandiosity | 1.62 | 1.51 | -0.11 |

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
- `profiles/` - Retained model profiles (n=42)

---

**Parent Analysis**: `../all_combined/RESEARCH_BRIEF.md`
**Generated**: 2026-01-24 09:10
