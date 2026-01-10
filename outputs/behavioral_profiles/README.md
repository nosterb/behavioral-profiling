# Behavioral Profiles Directory

This directory contains behavioral profiles and statistical analyses for all intervention conditions.

---

## Directory Structure

### Per-Condition Directories

Each intervention condition has its own directory with complete H1/H2 analysis:

```
<condition_name>/                   # e.g., baseline/, affective/, authority/
├── profiles/                       # Individual model profiles
│   └── <model_name>.json          # Per-model behavioral averages
├── history/                        # Profile tracking
│   ├── contributions.json         # Job-level contribution tracking
│   └── updates_log.json          # Chronological update history
├── visualizations/                # Condition-specific visualizations
├── median_split_classification.json # H1/H2 classification data
├── h1_bar_chart_comparison.png    # H1 group comparison
├── h1_summary_table.png           # H1 statistical table
├── h2_scatter_sophistication_composite.png # H2 main scatter
├── h2_scatter_all_dimensions.png  # H2 4-subplot grid
└── RESEARCH_BRIEF.md              # Per-condition research brief
```

### Research Synthesis

Cross-condition comparisons and meta-analyses:

```
research_synthesis/
├── cross_condition/               # H3: Intervention effects
│   ├── CROSS_CONDITION_BRIEF.md
│   ├── h3_correlation_by_condition.png
│   ├── h3_effect_size_comparison.png
│   ├── h3_median_shift_analysis.png
│   ├── condition_comparison_table.json
│   └── intervention_effects_summary.json
├── combined/                      # Meta-analysis (pooled)
│   ├── COMBINED_ANALYSIS_BRIEF.md
│   ├── all_conditions_pooled.json
│   ├── h1_h2_meta_analysis.json
│   ├── pooled_scatter_plots.png
│   └── model_stability_across_conditions.png
├── MAIN_RESEARCH_BRIEF.md        # Top-level synthesis
├── INDEX.md                      # Navigation guide
└── README.md                     # Structure documentation
```

---

## Current Conditions

### Completed
- ✅ **baseline/** - Control condition (no intervention)

### In Progress
- 🚧 **affective/** - Emotional/empathetic prompting
- 🚧 **authority/** - Expertise challenge
- 🚧 **urgency/** - Time pressure
- 🚧 **minimal_steering/** - Lightweight constraints

---

## Legacy Structure (Root Level)

**Note**: The following root-level directories are **legacy files** from before per-condition organization was implemented. They are retained for backward compatibility but should not be used for new analyses.

```
profiles/          # Legacy: Pre-condition profile aggregation
history/           # Legacy: Old contribution tracking
visualizations/    # Legacy: Old visualizations
```

**Migration Status**: These will be deprecated once all active analyses use per-condition directories.

---

## Quick Start

### Running H1/H2 Analysis for New Condition

```bash
# 1. Aggregate profiles
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_<intervention>_*.json \
    --profile-dir outputs/behavioral_profiles/<intervention>

# 2. Run complete H1/H2 analysis
./scripts/run_complete_h1_h2_analysis.sh <intervention>
```

### Viewing Results

```bash
# View research brief
cat outputs/behavioral_profiles/<intervention>/RESEARCH_BRIEF.md

# Open visualizations
open outputs/behavioral_profiles/<intervention>/*.png
```

### Navigation

See [research_synthesis/INDEX.md](research_synthesis/INDEX.md) for complete navigation of all analyses.

---

## Documentation

Comprehensive guides available in repository root:

- **[QUICK_START_H1_H2.md](../../QUICK_START_H1_H2.md)** - Quick reference
- **[H1_H2_ANALYSIS_GUIDE.md](../../H1_H2_ANALYSIS_GUIDE.md)** - Detailed methodology
- **[H1_H2_QUALITY_CONTROL.md](../../H1_H2_QUALITY_CONTROL.md)** - Validation framework
- **[H1_H2_REPLICATION_READY.md](../../H1_H2_REPLICATION_READY.md)** - Go/no-go checklist
- **[RESEARCH_STRUCTURE_PROPOSAL.md](../../RESEARCH_STRUCTURE_PROPOSAL.md)** - Overall organization

---

## Analysis Pipeline

### Phase 1: Per-Condition H1/H2 (Current)
Run `./scripts/run_complete_h1_h2_analysis.sh <intervention>` for each condition

### Phase 2: Cross-Condition (H3)
Run `./scripts/run_cross_condition_analysis.sh` after ≥3 conditions

### Phase 3: Combined Meta-Analysis
Run `./scripts/run_combined_analysis.sh` after all conditions

### Phase 4: Main Brief
Run `./scripts/generate_main_brief.sh` for final synthesis

---

## File Naming Conventions

### Per-Condition Files
- `median_split_classification.json` - Classification data
- `h1_bar_chart_comparison.png` - H1 visualization
- `h1_summary_table.png` - H1 statistics
- `h2_scatter_sophistication_composite.png` - H2 main plot
- `h2_scatter_all_dimensions.png` - H2 dimension grid
- `RESEARCH_BRIEF.md` - Condition brief

### Cross-Condition Files (H3)
- `h3_*.png` - H3-specific visualizations
- `condition_comparison_*.json` - Statistical comparisons
- `CROSS_CONDITION_BRIEF.md` - H3 brief

### Combined Files
- `all_conditions_*.json` - Pooled data
- `h1_h2_meta_analysis.json` - Meta-analysis
- `pooled_*.png` - Combined visualizations
- `COMBINED_ANALYSIS_BRIEF.md` - Meta-analysis brief

---

**Last Updated**: 2026-01-10
**Structure Version**: 2.0 (Per-condition organization with research synthesis)
