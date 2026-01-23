# Research Brief: Baseline (No Dimensions Suite)

**Status**: Sensitivity Analysis
**Last Updated**: 2026-01-23
**Parent Condition**: baseline
**Analysis Type**: Prompt suite exclusion robustness check

---

## Overview

This analysis removes prompts from the **dimensions suite** (which directly probe for the 9 behavioral dimensions) to test whether the sophistication-disinhibition relationship holds without dimension-specific probing.

**Excluded Suites**: dimensions
**Included Suites**: broad, affective, general, typical, love

**Rationale**: The dimensions suite contains prompts that explicitly ask models to demonstrate specific behavioral traits. Removing these tests whether the H1a/H2 effects are artifacts of direct probing or emerge naturally from general conversation scenarios.

---

## Sample

| Metric | Full Dataset | No Dimensions |
|--------|--------------|---------------|
| **N (models)** | 45 | 46 |
| **High-Sophistication** | 23 | 23 |
| **Low-Sophistication** | 22 | 23 |
| **Median Sophistication** | 5.937 | 5.786 |

---

## Results Comparison

### H1a: Group Comparison

| Metric | Full Dataset | No Dimensions | Change |
|--------|--------------|---------------|--------|
| **Cohen's d** | 2.13 | 2.12 | -0.01 |
| **Effect Size** | large | large | — |
| **p-value** | p < .001 | p < .001 | — |

### H2: Correlation

| Metric | Full Dataset | No Dimensions | Change |
|--------|--------------|---------------|--------|
| **Pearson r** | 0.778 | 0.783 | +0.004 |

### Per-Dimension H1a Effects

| Dimension | Full Dataset d | No Dimensions d | Change |
|-----------|----------------|-----------------|--------|
| Transgression | 1.81 | 1.69 | -0.12 |
| Aggression | 2.17 | 1.80 | -0.36 |
| Tribalism | 1.26 | 1.39 | +0.12 |
| Grandiosity | 1.71 | 1.59 | -0.12 |

---

## Interpretation

H1a effect is **robust** to dimensions suite removal.

H2 correlation is stable regardless of dimensions suite inclusion.

**Conclusion**: The core findings are robust and not driven by dimension-specific probing. The sophistication-disinhibition relationship emerges naturally from general conversation scenarios.

---

## Files in This Directory

- `sensitivity_analysis_info.json` - Analysis configuration and comparison statistics
- `median_split_classification.json` - Classification data without dimensions suite
- `h1_bar_chart_comparison.png` - H1a group comparison visualization
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - H2 scatter with regression
- `h2_scatter_all_dimensions.png` - Per-dimension H2 scatters
- `profiles/` - Model profiles (n=46)

---

**Parent Analysis**: `../baseline/RESEARCH_BRIEF.md`
**Generated**: 2026-01-23 13:40
