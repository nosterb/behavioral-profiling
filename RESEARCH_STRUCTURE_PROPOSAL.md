# Research Analytics Structure Proposal

**Date**: 2026-01-10
**Purpose**: Organize H1/H2 replication, cross-condition (H3), and combined analyses

---

## Proposed Directory Structure

```
outputs/behavioral_profiles/
│
├── baseline/                           # Per-condition analysis (existing)
│   ├── profiles/                       # Individual model profiles
│   ├── history/                        # Contribution tracking
│   ├── median_split_classification.json
│   ├── h1_bar_chart_comparison.png
│   ├── h1_summary_table.png
│   ├── h2_scatter_sophistication_composite.png
│   ├── h2_scatter_all_dimensions.png
│   └── RESEARCH_BRIEF.md               # Per-condition brief
│
├── affective/                          # Same structure as baseline
├── authority/
├── urgency/
├── [other interventions...]/
│
├── research_synthesis/                 # NEW: Cross-condition & combined analysis
│   │
│   ├── cross_condition/                # H3: Intervention effect comparisons
│   │   ├── h3_correlation_by_condition.png
│   │   ├── h3_effect_size_comparison.png
│   │   ├── h3_median_shift_analysis.png
│   │   ├── condition_comparison_table.json
│   │   ├── intervention_effects_summary.json
│   │   └── CROSS_CONDITION_BRIEF.md    # H3 analysis brief
│   │
│   ├── combined/                       # Meta-analysis (all conditions pooled)
│   │   ├── all_conditions_pooled.json
│   │   ├── h1_h2_meta_analysis.json
│   │   ├── pooled_scatter_plots.png
│   │   ├── model_stability_across_conditions.png
│   │   └── COMBINED_ANALYSIS_BRIEF.md  # Pooled analysis brief
│   │
│   ├── MAIN_RESEARCH_BRIEF.md          # Top-level synthesis document
│   └── INDEX.md                        # Navigation guide for all analyses
│
└── README.md                           # Updated to reference research_synthesis/
```

---

## Analysis Phases

### Phase 1: Per-Condition H1/H2 Replication ✅ (Current)
**Location**: `outputs/behavioral_profiles/<intervention>/`

**What**: Run complete H1/H2 analysis for each intervention condition independently.

**Command**:
```bash
./scripts/run_complete_h1_h2_analysis.sh <intervention>
```

**Outputs per condition**:
- Median split classification
- H1 group comparison visualizations
- H2 correlation scatter plots
- Individual RESEARCH_BRIEF.md

**Status**: Pipeline ready, validated on baseline

---

### Phase 2: Cross-Condition Comparison (H3)
**Location**: `outputs/behavioral_profiles/research_synthesis/cross_condition/`

**What**: Compare H1/H2 effects across different intervention conditions.

**Research Questions (H3 variants)**:
- **H3a**: Do interventions shift the median sophistication threshold?
- **H3b**: Do interventions modulate the sophistication-disinhibition correlation strength?
- **H3c**: Do interventions affect H1 effect sizes (group differences)?
- **H3d**: Which dimensions show strongest intervention effects?

**Command** (to be created):
```bash
./scripts/run_cross_condition_analysis.sh
```

**Planned Outputs**:
1. **h3_correlation_by_condition.png**: r values across conditions with confidence intervals
2. **h3_effect_size_comparison.png**: Cohen's d comparison across interventions
3. **h3_median_shift_analysis.png**: How median sophistication changes by condition
4. **condition_comparison_table.json**: Statistical comparisons between conditions
5. **CROSS_CONDITION_BRIEF.md**: H3 hypothesis testing and interpretation

**Analysis Methods**:
- Fisher's r-to-z transformation for correlation comparisons
- Effect size confidence intervals
- Condition × Sophistication interaction tests
- Dimension-level intervention effects

---

### Phase 3: Combined/Pooled Analysis
**Location**: `outputs/behavioral_profiles/research_synthesis/combined/`

**What**: Meta-analysis pooling data across all conditions.

**Research Questions**:
- What is the overall H1/H2 effect when pooling all interventions?
- Which models show consistent patterns across conditions?
- Are there models that respond differentially to interventions?
- What is the grand mean sophistication-disinhibition relationship?

**Command** (to be created):
```bash
./scripts/run_combined_analysis.sh
```

**Planned Outputs**:
1. **all_conditions_pooled.json**: Combined dataset with condition labels
2. **h1_h2_meta_analysis.json**: Pooled effect sizes with heterogeneity statistics
3. **pooled_scatter_plots.png**: Grand scatter plot with condition colors
4. **model_stability_across_conditions.png**: Model consistency heatmap
5. **COMBINED_ANALYSIS_BRIEF.md**: Meta-analytic synthesis

**Analysis Methods**:
- Random effects meta-analysis
- Heterogeneity assessment (I², Q statistic)
- Model-level stability coefficients
- Condition as random effect

---

### Phase 4: Main Research Brief
**Location**: `outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md`

**What**: Executive synthesis document integrating all findings.

**Sections**:
1. **Executive Summary**: Key findings across all analyses
2. **H1/H2 Replication**: Summary of per-condition results
3. **H3 Intervention Effects**: Cross-condition comparison findings
4. **Combined Analysis**: Meta-analytic synthesis
5. **Model-Level Insights**: Consistent patterns and exceptions
6. **Theoretical Implications**: What this tells us about LLM behavior
7. **Methodological Notes**: Limitations and considerations
8. **Appendices**: Links to detailed per-condition briefs

**Command** (to be created):
```bash
./scripts/generate_main_brief.sh
```

---

## Navigation Structure

### Index File: `research_synthesis/INDEX.md`

```markdown
# Research Analytics Index

## Quick Navigation

### Per-Condition Analysis (H1/H2)
- [Baseline](../baseline/RESEARCH_BRIEF.md)
- [Affective](../affective/RESEARCH_BRIEF.md)
- [Authority](../authority/RESEARCH_BRIEF.md)
- [Urgency](../urgency/RESEARCH_BRIEF.md)

### Cross-Condition Analysis (H3)
- [Cross-Condition Brief](cross_condition/CROSS_CONDITION_BRIEF.md)
- [Correlation Comparison](cross_condition/h3_correlation_by_condition.png)
- [Effect Size Comparison](cross_condition/h3_effect_size_comparison.png)

### Combined Analysis
- [Combined Brief](combined/COMBINED_ANALYSIS_BRIEF.md)
- [Meta-Analysis Results](combined/h1_h2_meta_analysis.json)

### Main Synthesis
- [Main Research Brief](MAIN_RESEARCH_BRIEF.md) ⭐
```

---

## Workflow Summary

### Current Workflow (Phase 1)
```bash
# 1. Aggregate profiles per condition
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_<intervention>_*.json \
    --profile-dir outputs/behavioral_profiles/<intervention>

# 2. Run H1/H2 analysis
./scripts/run_complete_h1_h2_analysis.sh <intervention>

# Repeat for all conditions
```

### Future Workflow (Phase 2-4)
```bash
# After all per-condition analyses complete:

# 3. Cross-condition comparison (H3)
./scripts/run_cross_condition_analysis.sh

# 4. Combined/pooled analysis
./scripts/run_combined_analysis.sh

# 5. Generate main brief
./scripts/generate_main_brief.sh
```

---

## File Naming Conventions

### Per-Condition Files (existing)
- `median_split_classification.json`
- `h1_bar_chart_comparison.png`
- `h1_summary_table.png`
- `h2_scatter_sophistication_composite.png`
- `h2_scatter_all_dimensions.png`
- `RESEARCH_BRIEF.md`

### Cross-Condition Files (H3)
- `h3_*.png` - H3-specific visualizations
- `condition_comparison_*.json` - Statistical comparisons
- `intervention_effects_*.json` - Effect summaries
- `CROSS_CONDITION_BRIEF.md`

### Combined Files
- `all_conditions_*.json` - Pooled datasets
- `h1_h2_meta_analysis.json` - Meta-analytic results
- `pooled_*.png` - Combined visualizations
- `COMBINED_ANALYSIS_BRIEF.md`

### Main Files
- `MAIN_RESEARCH_BRIEF.md` - Top-level synthesis
- `INDEX.md` - Navigation guide

---

## Implementation Priority

### Immediate (Ready Now)
✅ Phase 1: Per-condition H1/H2 replication (pipeline complete)

### Near-Term (After ≥3 conditions complete)
- Phase 2: Cross-condition analysis (H3)
- Scripts needed:
  - `run_cross_condition_analysis.sh`
  - `compare_h1_h2_across_conditions.py`
  - `generate_cross_condition_brief.py`

### Medium-Term (After all conditions complete)
- Phase 3: Combined/pooled analysis
- Scripts needed:
  - `run_combined_analysis.sh`
  - `meta_analysis_h1_h2.py`
  - `generate_combined_brief.py`

### Final Step
- Phase 4: Main research brief generation
- Script needed:
  - `generate_main_brief.sh`

---

## Benefits of This Structure

1. **Separation of Concerns**: Per-condition, cross-condition, and combined analyses clearly separated
2. **Easy Navigation**: INDEX.md provides one-stop navigation to all analyses
3. **Scalable**: Easy to add new intervention conditions
4. **Publication-Ready**: Main brief consolidates everything for papers/reports
5. **Hierarchical**: Individual → Comparative → Meta → Synthesis
6. **Consistent Naming**: Clear prefixes (h1_, h2_, h3_, pooled_) indicate analysis type

---

## Next Steps

1. ✅ **Continue Phase 1**: Run H1/H2 analysis for remaining conditions
2. **After ≥3 conditions**: Create research_synthesis/ directory structure
3. **After ≥3 conditions**: Implement Phase 2 (H3 cross-condition scripts)
4. **After all conditions**: Implement Phase 3 (combined analysis scripts)
5. **Final**: Implement Phase 4 (main brief generation)

---

**Recommendation**: Start Phase 1 replication on affective, authority, and urgency conditions. Once we have 4 conditions total (including baseline), we can begin Phase 2 (H3 cross-condition comparison).
