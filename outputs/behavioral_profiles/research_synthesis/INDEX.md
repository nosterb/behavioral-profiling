# Research Analytics Index

**Last Updated**: 2026-01-10

This directory contains consolidated research analyses across all intervention conditions.

---

## Quick Navigation

### 🎯 Main Synthesis
- **[Main Research Brief](MAIN_RESEARCH_BRIEF.md)** ⭐ - Executive synthesis of all findings (Phase 4)

---

## Per-Condition Analysis (H1/H2 Replication)

Individual intervention condition analyses. Each condition tests:
- **H1**: High-sophistication models show higher disinhibition than low-sophistication models
- **H2**: Sophistication positively correlates with disinhibition

### Completed Conditions
- [Baseline](../baseline/RESEARCH_BRIEF.md) ✅ - No intervention control
- [Affective](../affective/RESEARCH_BRIEF.md) - Emotional/empathetic prompting
- [Authority](../authority/RESEARCH_BRIEF.md) - Expertise challenge
- [Urgency](../urgency/RESEARCH_BRIEF.md) - Time pressure
- [Minimal Steering](../minimal_steering/RESEARCH_BRIEF.md) - Lightweight constraints

### In Progress
- [ ] Additional conditions...

---

## Cross-Condition Analysis (H3)

Comparative analysis testing intervention effects on H1/H2 relationships.

### Research Questions (H3 Variants)
- **H3a**: Do interventions shift the median sophistication threshold?
- **H3b**: Do interventions modulate the sophistication-disinhibition correlation strength?
- **H3c**: Do interventions affect H1 effect sizes (group differences)?
- **H3d**: Which dimensions show strongest intervention effects?

### Files (Phase 2 - After ≥3 conditions)
- [Cross-Condition Brief](cross_condition/CROSS_CONDITION_BRIEF.md) - H3 hypothesis testing
- [Correlation Comparison](cross_condition/h3_correlation_by_condition.png) - r values across conditions
- [Effect Size Comparison](cross_condition/h3_effect_size_comparison.png) - Cohen's d comparison
- [Median Shift Analysis](cross_condition/h3_median_shift_analysis.png) - Threshold changes
- [Comparison Table](cross_condition/condition_comparison_table.json) - Statistical comparisons
- [Intervention Effects](cross_condition/intervention_effects_summary.json) - Effect summaries

---

## Combined/Pooled Analysis (Meta-Analysis)

Meta-analysis pooling data across all conditions.

### Research Questions
- What is the overall H1/H2 effect when pooling all interventions?
- Which models show consistent patterns across conditions?
- Are there models that respond differentially to interventions?
- What is the grand mean sophistication-disinhibition relationship?

### Files (Phase 3 - After all conditions)
- [Combined Analysis Brief](combined/COMBINED_ANALYSIS_BRIEF.md) - Meta-analytic synthesis
- [Pooled Dataset](combined/all_conditions_pooled.json) - Combined data with condition labels
- [Meta-Analysis Results](combined/h1_h2_meta_analysis.json) - Pooled effect sizes & heterogeneity
- [Pooled Scatter Plots](combined/pooled_scatter_plots.png) - Grand scatter with condition colors
- [Model Stability](combined/model_stability_across_conditions.png) - Consistency heatmap

---

## Analysis Phases

### Phase 1: Per-Condition H1/H2 Replication ✅ (Current)
**Status**: Pipeline ready, validated on baseline

Run for each intervention:
```bash
./scripts/run_complete_h1_h2_analysis.sh <intervention>
```

### Phase 2: Cross-Condition Comparison (H3)
**Status**: Pending (requires ≥3 conditions)

After sufficient conditions complete:
```bash
./scripts/run_cross_condition_analysis.sh
```

### Phase 3: Combined/Pooled Analysis
**Status**: Pending (requires all conditions)

After all conditions complete:
```bash
./scripts/run_combined_analysis.sh
```

### Phase 4: Main Research Brief
**Status**: Pending (requires Phases 1-3 complete)

Generate final synthesis:
```bash
./scripts/generate_main_brief.sh
```

---

## Documentation

### H1/H2 Analysis Pipeline Guides
- [Quick Start Guide](../../../QUICK_START_H1_H2.md) - One-command usage
- [Analysis Guide](../../../H1_H2_ANALYSIS_GUIDE.md) - Detailed methodology
- [Quality Control](../../../H1_H2_QUALITY_CONTROL.md) - Validation framework (Phase 1 specific)
- [Replication Ready](../../../H1_H2_REPLICATION_READY.md) - Go/no-go checklist
- [Complete Summary](../../../H1_H2_COMPLETE_SUMMARY.md) - Implementation overview
- [Research Structure](../../../RESEARCH_STRUCTURE_PROPOSAL.md) - Overall organization

### Quality Assurance (All Phases)
- **[Statistical QC Framework](STATISTICAL_QC_FRAMEWORK.md)** ⭐ - Comprehensive quality control
  - Statistical methods standards (H1/H2, H3, Combined, Main)
  - Validation checklists for all analysis phases
  - Audit protocols and procedures
  - Data integrity requirements
  - Reproducibility requirements
  - Reporting standards (tables, figures, statistics)
  - Troubleshooting decision trees

---

## File Naming Conventions

### Per-Condition (in each condition directory)
- `median_split_classification.json` - Classification data
- `h1_bar_chart_comparison.png` - Group comparison
- `h1_summary_table.png` - Statistical table
- `h2_scatter_sophistication_composite.png` - Main scatter plot
- `h2_scatter_all_dimensions.png` - 4-subplot grid
- `RESEARCH_BRIEF.md` - Condition-specific brief

### Cross-Condition (H3)
- `h3_*.png` - H3-specific visualizations
- `condition_comparison_*.json` - Statistical comparisons
- `CROSS_CONDITION_BRIEF.md` - H3 analysis brief

### Combined
- `all_conditions_*.json` - Pooled datasets
- `h1_h2_meta_analysis.json` - Meta-analytic results
- `pooled_*.png` - Combined visualizations
- `COMBINED_ANALYSIS_BRIEF.md` - Meta-analysis brief

---

## For Developers

### Adding New Intervention Conditions
1. Aggregate profiles: `python3 scripts/update_behavioral_profiles.py ...`
2. Run H1/H2: `./scripts/run_complete_h1_h2_analysis.sh <intervention>`
3. Update this INDEX.md to list the new condition
4. After ≥3 conditions total, run Phase 2 (cross-condition)

### Implementing Future Phases
- **Phase 2 scripts**: `run_cross_condition_analysis.sh`, `compare_h1_h2_across_conditions.py`
- **Phase 3 scripts**: `run_combined_analysis.sh`, `meta_analysis_h1_h2.py`
- **Phase 4 scripts**: `generate_master_brief.sh`

---

**Last Phase Completed**: Phase 1 (baseline condition)
**Next Milestone**: Complete ≥3 conditions to enable Phase 2
