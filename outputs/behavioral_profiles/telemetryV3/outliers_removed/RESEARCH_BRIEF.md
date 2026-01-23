# Research Brief: Telemetryv3 (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-20
**Parent Condition**: telemetryV3
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the Telemetryv3 condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > 2.0 SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | 45 | 43 |
| **Outliers Removed** | — | 2 |
| **High-Sophistication** | 23 | 22 |
| **Low-Sophistication** | 22 | 21 |
| **Median Sophistication** | 5.106 | 4.926 |

---

## Outliers Removed (2)

- **Claude-4.5-Haiku-Thinking (Thinking)**: Soph=7.29, Disinhib=1.97, 4.6 SD above line
- **Grok-4-0709**: Soph=5.60, Disinhib=1.74, 3.6 SD above line

---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | 1.09 | 1.80 | +0.71 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | 0.625 | 0.799 | +0.175 |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
| Transgression | 1.07 | 1.45 | +0.39 |
| Aggression | 0.80 | 1.15 | +0.35 |
| Tribalism | 0.60 | 0.31 | -0.29 |
| Grandiosity | 1.21 | 1.39 | +0.18 |

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
- `profiles/` - Retained model profiles (n=43)

---

**Parent Analysis**: `../telemetryV3/RESEARCH_BRIEF.md`
**Generated**: 2026-01-20 09:24
