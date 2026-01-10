# Combined/Pooled Analysis - Research Brief

**Status**: 🚧 **TEMPLATE - PENDING PHASE 3**
**Date**: TBD
**Conditions Pooled**: TBD
**Total Models**: TBD
**Total Observations**: TBD

---

## Overview

This brief reports meta-analytic results pooling data across all intervention conditions to assess overall H1/H2 effects and model-level consistency.

**Prerequisites**: Requires all planned intervention conditions to have completed H1/H2 analysis.

---

## Research Questions

### Overall Effects
**Question**: What are the grand H1 and H2 effects when pooling all conditions?

**Analysis**: Random effects meta-analysis with condition as random effect.

### Model Consistency
**Question**: Which models show consistent behavioral patterns across conditions?

**Analysis**: Model-level stability coefficients, intraclass correlations.

### Differential Responding
**Question**: Do some models respond more strongly to interventions than others?

**Analysis**: Model × Condition interaction, heterogeneity assessment.

### Grand Relationship
**Question**: What is the overall sophistication-disinhibition relationship across all contexts?

**Analysis**: Multi-level modeling with condition nesting.

---

## Methods

### Conditions Pooled
- **Baseline**: N = [X] models
- **Affective**: N = [X] models
- **Authority**: N = [X] models
- **Urgency**: N = [X] models
- [Additional conditions...]

**Total Observations**: [N] model-condition pairs

### Pooling Approach

**Random Effects Model**:
- Condition as random effect
- Accounts for between-condition heterogeneity
- Provides weighted average effect sizes

**Heterogeneity Assessment**:
- I² statistic (proportion of variance due to heterogeneity)
- Q statistic (test for heterogeneity)
- Tau² (between-condition variance)

**Model-Level Stability**:
- Intraclass correlation coefficients
- Consistency ratio (within-model vs. between-model variance)
- Rank-order stability across conditions

---

## Results

### Meta-Analytic H1 Effect

**Pooled Cohen's d**: TBD (95% CI: [TBD, TBD])

**Heterogeneity**:
- I² = TBD%
- Q(df=[X]) = TBD, p = TBD
- Tau² = TBD

[TABLE: Per-condition contributions to pooled effect]

**Interpretation**: TBD

### Meta-Analytic H2 Correlation

**Pooled r**: TBD (95% CI: [TBD, TBD])

**Heterogeneity**:
- I² = TBD%
- Q(df=[X]) = TBD, p = TBD
- Tau² = TBD

[VISUALIZATION: pooled_scatter_plots.png - Grand scatter with condition colors]

[TABLE: Per-condition contributions to pooled correlation]

**Interpretation**: TBD

### Model Stability Analysis

[VISUALIZATION: model_stability_across_conditions.png - Consistency heatmap]

**High Stability Models** (ICC > 0.80):
- TBD

**Moderate Stability Models** (ICC 0.50-0.80):
- TBD

**Variable Models** (ICC < 0.50):
- TBD

**Interpretation**: TBD

### Differential Responding

**Models with Strong Intervention Effects**:
- TBD

**Models with Weak Intervention Effects**:
- TBD

[TABLE: Model × Condition interaction statistics]

**Interpretation**: TBD

---

## Discussion

### Grand Sophistication-Disinhibition Relationship
TBD

### Consistency Across Contexts
TBD

### Model-Level Insights
TBD

### Intervention Sensitivity
TBD

### Theoretical Implications
TBD

### Limitations
- Unequal condition representation
- Fixed model set across conditions
- Limited intervention types
- [Additional limitations...]

---

## Supporting Files

### Visualizations
- `pooled_scatter_plots.png` - Grand scatter plot with condition colors
- `model_stability_across_conditions.png` - Model consistency heatmap
- [Additional visualizations]

### Data Files
- `all_conditions_pooled.json` - Complete pooled dataset
- `h1_h2_meta_analysis.json` - Meta-analytic results with heterogeneity stats
- [Additional data files]

---

## Comparison to Per-Condition Results

### Baseline vs. Pooled
- **H1 (Baseline)**: d = [X]
- **H1 (Pooled)**: d = [X]
- **Difference**: [X]

- **H2 (Baseline)**: r = [X]
- **H2 (Pooled)**: r = [X]
- **Difference**: [X]

### Condition-Specific Deviations
[TABLE: How each condition deviates from pooled estimates]

---

## References

### Per-Condition Briefs
- [Baseline](../../baseline/RESEARCH_BRIEF.md)
- [Affective](../../affective/RESEARCH_BRIEF.md)
- [Authority](../../authority/RESEARCH_BRIEF.md)
- [Urgency](../../urgency/RESEARCH_BRIEF.md)

### Cross-Condition Analysis
- [Cross-Condition Brief](../cross_condition/CROSS_CONDITION_BRIEF.md)

### Analysis Scripts
- `scripts/run_combined_analysis.sh` - Pipeline script
- `scripts/meta_analysis_h1_h2.py` - Meta-analysis computation
- `scripts/generate_combined_brief.py` - Brief generator

---

**Analysis Version**: 1.0 (Meta-Analysis)
**Statistical Software**: Python 3.x with scipy.stats, statsmodels, meta-analysis packages
**Effect Size Conventions**: Cohen (1988), Borenstein et al. (2009)
**Meta-Analytic Framework**: Random effects model with restricted maximum likelihood (REML)
