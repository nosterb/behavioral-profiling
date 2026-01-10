# Cross-Condition Analysis (H3) - Research Brief

**Status**: 🚧 **TEMPLATE - PENDING PHASE 2**
**Date**: TBD
**Conditions Analyzed**: TBD

---

## Overview

This brief reports cross-condition comparisons testing how different interventions modulate the H1/H2 relationships observed in individual conditions.

**Prerequisites**: Requires ≥3 intervention conditions with completed H1/H2 analysis.

---

## Research Questions (H3 Variants)

### H3a: Median Sophistication Threshold Shifts
**Question**: Do different interventions shift the median sophistication value used for classification?

**Hypothesis**: Interventions that prime for certain behaviors (e.g., urgency → hedging) may shift the relative sophistication threshold.

**Analysis**: Compare median sophistication values across conditions with confidence intervals.

### H3b: Correlation Strength Modulation
**Question**: Do interventions affect the strength of the sophistication-disinhibition correlation?

**Hypothesis**: Some interventions may strengthen or weaken the H2 correlation compared to baseline.

**Analysis**: Fisher's r-to-z transformation to compare correlation coefficients across conditions.

### H3c: Effect Size Variations
**Question**: Do interventions affect the magnitude of H1 group differences?

**Hypothesis**: Interventions may amplify or dampen the disinhibition difference between high/low sophistication groups.

**Analysis**: Compare Cohen's d values across conditions with confidence intervals.

### H3d: Dimension-Specific Effects
**Question**: Do different interventions selectively affect specific behavioral dimensions?

**Hypothesis**: Interventions target different dimensions (e.g., urgency → hedging, authority → grandiosity).

**Analysis**: Dimension-level comparison of intervention effects.

---

## Methods

### Conditions Included
- **Baseline**: [Description]
- **Affective**: [Description]
- **Authority**: [Description]
- **Urgency**: [Description]
- [Additional conditions...]

### Statistical Approaches

**Correlation Comparison**:
- Fisher's r-to-z transformation
- Test for equality of correlations
- Confidence intervals for r values

**Effect Size Comparison**:
- Cohen's d confidence intervals
- Overlap assessment
- Magnitude comparison tests

**Median Comparison**:
- Bootstrapped confidence intervals
- Difference testing
- Effect on classification balance

**Dimension-Level Analysis**:
- Repeated measures design
- Intervention × Dimension interaction
- Bonferroni correction for multiple comparisons

---

## Results

### H3a: Median Sophistication Shifts

[TABLE: Median values by condition with 95% CI]

**Findings**: TBD

### H3b: Correlation Strength Changes

[VISUALIZATION: h3_correlation_by_condition.png]

[TABLE: Correlation coefficients with significance tests]

**Findings**: TBD

### H3c: Effect Size Variations

[VISUALIZATION: h3_effect_size_comparison.png]

[TABLE: Cohen's d values with 95% CI]

**Findings**: TBD

### H3d: Dimension-Specific Effects

[VISUALIZATION: Intervention × Dimension interaction plot]

[TABLE: Per-dimension effect sizes across conditions]

**Findings**: TBD

---

## Discussion

### Key Findings
TBD

### Theoretical Implications
TBD

### Intervention Effectiveness
TBD

### Limitations
TBD

---

## Supporting Files

### Visualizations
- `h3_correlation_by_condition.png` - Correlation comparison chart
- `h3_effect_size_comparison.png` - Cohen's d comparison
- `h3_median_shift_analysis.png` - Threshold shift analysis
- [Additional visualizations]

### Data Files
- `condition_comparison_table.json` - Statistical comparison results
- `intervention_effects_summary.json` - Effect size summaries
- [Additional data files]

---

## References

### Per-Condition Briefs
- [Baseline](../../baseline/RESEARCH_BRIEF.md)
- [Affective](../../affective/RESEARCH_BRIEF.md)
- [Authority](../../authority/RESEARCH_BRIEF.md)
- [Urgency](../../urgency/RESEARCH_BRIEF.md)

### Analysis Scripts
- `scripts/run_cross_condition_analysis.sh` - Pipeline script
- `scripts/compare_h1_h2_across_conditions.py` - Statistical comparison
- `scripts/generate_cross_condition_brief.py` - Brief generator

---

**Analysis Version**: 1.0 (Cross-Condition Comparison)
**Statistical Software**: Python 3.x with scipy.stats, statsmodels
**Effect Size Conventions**: Cohen (1988), APA Publication Manual (7th ed.)
