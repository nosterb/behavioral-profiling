# Research Brief: Naturalistic 50 (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-20
**Parent Condition**: naturalistic_50
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Naturalistic 50 condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 44 | 42 |
| **Outliers Removed** | — | 2 |
| **High-Sophistication** | 22 | 21 |
| **Low-Sophistication** | 22 | 21 |
| **Median Sophistication** | 29.854 | 29.798 |

---

## Outliers Removed (2)

- **Gemini-3-Pro-Preview**: Soph=37.75, Disinhib=8.62, 3.9 SD above line
- **Claude-4.5-Opus-Global**: Soph=34.63, Disinhib=7.04, 2.0 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.57 | 1.94 | +0.37 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.698 | 0.729 | +0.031 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.45 | 1.44 | -0.01 |
| Aggression | 1.11 | 1.35 | +0.24 |
| Tribalism | 0.50 | 0.55 | +0.05 |
| Grandiosity | 1.87 | 2.18 | +0.31 |

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

**Parent Analysis**: `../naturalistic_50/RESEARCH_BRIEF.md`
**Generated**: 2026-01-20 09:25
