# Research Brief: Baseline (No Dimensions Suite)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-11
**Parent Condition**: baseline
**Analysis Type**: Prompt suite exclusion robustness check

---

## Overview

This analysis removes prompts from the **dimensions suite** (which directly probe for the 9 behavioral dimensions) to test whether the sophistication-disinhibition relationship holds without dimension-specific probing.

**Excluded Suites**: dimensions
**Included Suites**: broad, extended, affective, general

**Rationale**: The dimensions suite contains prompts that explicitly ask models to demonstrate specific behavioral traits. Removing these tests whether the H1a/H2 effects are artifacts of direct probing or emerge naturally from general conversation scenarios.

---

## Sample

| Metric | Full Dataset | No Dimensions |
|--------|--------------|---------------|
| **N (models)** | 46 | 40 |
| **High-Sophistication** | 23 | 20 |
| **Low-Sophistication** | 23 | 20 |
| **Median Sophistication** | 5.930 | 5.392 |

---

## Results Comparison

### H1a: Group Comparison

| Metric | Full Dataset | No Dimensions | Change |
|--------|--------------|---------------|--------|
| **Cohen's d** | 2.17 | 2.04 | -0.12 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Full Dataset | No Dimensions | Change |
|--------|--------------|---------------|--------|
| **Pearson r** | 0.738 | 0.778 | +0.039 |

### Per-Dimension H1a Effects

| Dimension | Full Dataset d | No Dimensions d | Change |
|-----------|----------------|-----------------|--------|
| Transgression | 1.85 | 1.73 | -0.12 |
| Aggression | 2.21 | 1.64 | -0.57 |
| Tribalism | 1.31 | 1.52 | +0.21 |
| Grandiosity | 1.74 | 1.61 | -0.13 |

---

## Interpretation

Removing dimensions suite **weakens** the H1a effect, suggesting direct probing contributed to the observed effect.

H2 correlation strengthens without dimensions suite, suggesting cleaner signal from natural scenarios.

**Conclusion**: The core findings are robust and not driven by dimension-specific probing. The sophistication-disinhibition relationship emerges naturally from general conversation scenarios.

---

## Files in This Directory

- `sensitivity_analysis_info.json` - Analysis configuration and comparison statistics
- `median_split_classification.json` - Classification data without dimensions suite
- `h1_bar_chart_comparison.png` - H1a group comparison visualization
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - H2 scatter with regression
- `h2_scatter_all_dimensions.png` - Per-dimension H2 scatters
- `profiles/` - Model profiles (n=40)

---

**Parent Analysis**: `../baseline/RESEARCH_BRIEF.md`
**Generated**: 2026-01-11 16:50
