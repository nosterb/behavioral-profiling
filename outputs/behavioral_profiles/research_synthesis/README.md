# Research Synthesis

This directory consolidates cross-condition comparisons and meta-analyses across all intervention conditions.

## Purpose

While individual intervention conditions are analyzed in their respective directories (`../baseline/`, `../affective/`, etc.), this directory contains:

1. **Cross-Condition Comparisons (H3)**: Testing how different interventions modulate H1/H2 effects
2. **Combined/Pooled Analysis**: Meta-analysis across all conditions
3. **Main Research Brief**: Executive synthesis integrating all findings

## Directory Structure

```
research_synthesis/
├── cross_condition/           # H3: Intervention effect comparisons
│   ├── h3_correlation_by_condition.png
│   ├── h3_effect_size_comparison.png
│   ├── h3_median_shift_analysis.png
│   ├── condition_comparison_table.json
│   ├── intervention_effects_summary.json
│   └── CROSS_CONDITION_BRIEF.md
│
├── combined/                  # Meta-analysis (all conditions pooled)
│   ├── all_conditions_pooled.json
│   ├── h1_h2_meta_analysis.json
│   ├── pooled_scatter_plots.png
│   ├── model_stability_across_conditions.png
│   └── COMBINED_ANALYSIS_BRIEF.md
│
├── MAIN_RESEARCH_BRIEF.md     # Top-level synthesis document
├── INDEX.md                   # Navigation guide for all analyses
└── README.md                  # This file
```

## Navigation

**Start here**: [INDEX.md](INDEX.md) - Complete navigation guide with links to all analyses

**Executive summary**: [MAIN_RESEARCH_BRIEF.md](MAIN_RESEARCH_BRIEF.md) - Top-level synthesis (Phase 4)

## Research Hypotheses

### H1: Group Comparison (Per-Condition)
High-sophistication models exhibit significantly higher disinhibition than low-sophistication models.

### H2: Correlation (Per-Condition)
Model sophistication positively correlates with disinhibition across all models.

### H3: Intervention Effects (Cross-Condition)
Different contextual interventions modulate the H1/H2 relationships:
- **H3a**: Median sophistication threshold shifts
- **H3b**: Correlation strength changes
- **H3c**: Effect size variations
- **H3d**: Dimension-specific effects

## Status

- **Phase 1** (Per-Condition): ✅ In progress - baseline complete, pipeline ready
- **Phase 2** (Cross-Condition): ⏳ Pending - requires ≥3 conditions
- **Phase 3** (Combined): ⏳ Pending - requires all conditions
- **Phase 4** (Main Brief): ⏳ Pending - requires Phases 1-3 complete

## Quick Commands

See [QUICK_START_H1_H2.md](../../../QUICK_START_H1_H2.md) for detailed usage.

```bash
# Run H1/H2 for new condition
./scripts/run_complete_h1_h2_analysis.sh <intervention>

# Run cross-condition analysis (Phase 2 - after ≥3 conditions)
./scripts/run_cross_condition_analysis.sh

# Run combined analysis (Phase 3 - after all conditions)
./scripts/run_combined_analysis.sh

# Generate main brief (Phase 4 - final step)
./scripts/generate_main_brief.sh
```

## Documentation

### Core Documentation (Repository Root)
- `QUICK_START_H1_H2.md` - Quick reference
- `H1_H2_ANALYSIS_GUIDE.md` - Detailed methodology
- `H1_H2_QUALITY_CONTROL.md` - Validation framework (Phase 1)
- `H1_H2_REPLICATION_READY.md` - Go/no-go checklist
- `RESEARCH_STRUCTURE_PROPOSAL.md` - Overall organization plan

### Quality Assurance
- **[STATISTICAL_QC_FRAMEWORK.md](STATISTICAL_QC_FRAMEWORK.md)** - Comprehensive QC framework
  - Standards for all analysis phases (H1/H2, H3, Combined, Main)
  - Statistical methods and rigor requirements
  - Audit protocols and validation checklists
  - Data integrity and reproducibility standards
