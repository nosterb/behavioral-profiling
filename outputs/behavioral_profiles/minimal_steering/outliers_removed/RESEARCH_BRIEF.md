# Research Brief: Minimal Steering (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-21
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
| **N** | 46 | 43 |
| **Outliers Removed** | — | 2 |
| **High-Sophistication** | 23 | 22 |
| **Low-Sophistication** | 23 | 21 |
| **Median Sophistication** | 5.255 | 5.088 |

---

## Outliers Removed (2)

- **Gemini-2.5-Pro**: Soph=6.16, Disinhib=1.29, 2.5 SD below line
- **Claude-4.5-Opus-Global**: Soph=6.91, Disinhib=1.58, 2.2 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 2.36 | 2.46 | +0.10 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.860 | 0.875 | +0.016 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.93 | 2.15 | +0.21 |
| Aggression | 2.13 | 1.97 | -0.15 |
| Tribalism | 1.33 | 1.09 | -0.24 |
| Grandiosity | 1.02 | 0.96 | -0.06 |

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
- `profiles/` - Retained model profiles (n=43)

---

**Parent Analysis**: `../minimal_steering/RESEARCH_BRIEF.md`
**Generated**: 2026-01-21 13:01
