# Condition Directory Best Practices

**Reference Model**: `baseline/`
**Last Updated**: 2026-01-19

This document describes the standard structure and artifacts for a complete behavioral profiling condition directory. Use this as a checklist when creating or auditing condition analyses.

---

## Directory Structure Overview

A complete condition directory contains **~120 required files** across the following structure:

```
<condition>/
├── RESEARCH_BRIEF.md              # Primary human-readable output
├── DATA_AUDIT.md                  # Data completeness summary
├── CUSTOM_NOTES.md                # Manual observations (never overwritten)
├── job_audit.json                 # Complete job-level provenance
│
├── # Core Statistical Outputs (5 files)
├── median_split_classification.json    # Classification + full statistics
├── all_models_data.csv                 # Export for external analysis
├── comprehensive_stats.json            # Provider-level statistics
├── COMPREHENSIVE_STATS_REPORT.txt      # Human-readable statistics
├── provider_comparison_stats.json      # Cross-provider ANOVA
│
├── # H1 Visualizations (2 files)
├── h1_bar_chart_comparison.png         # Group comparison bars
├── h1_summary_table.png                # Statistical summary table
│
├── # H2 Visualizations (2 files)
├── h2_scatter_sophistication_composite.png  # Main correlation plot
├── h2_scatter_all_dimensions.png            # 4-panel dimension plots
│
├── # Provider Visualizations (6 files)
├── provider_summary.png                # 4-panel provider overview
├── provider_h2_scatters.png            # Provider-specific correlations
├── all_dimensions_by_provider.png      # 3x3 dimension grid
├── provider_dimensions_heatmap.png     # Provider×dimension heatmap
├── provider_comparison_summary.png     # Provider comparison panels
├── provider_comparison_dimensions.png  # Dimension comparison grid
│
├── # Model Profiles (~45 files)
├── profiles/
│   └── <model_id>.json              # Individual model behavioral data
│
├── # Contribution History (2 files)
├── history/
│   ├── contributions.json           # Job-level contribution tracking
│   └── updates_log.json             # Chronological update log
│
├── # Statistical Assumptions (7 files)
├── statistical_assumptions/
│   ├── normality_audit.json              # Complete assumption checks
│   ├── STATISTICAL_ASSUMPTIONS_BRIEF.md  # Human-readable summary
│   ├── distribution_composites.png       # Sophistication/disinhibition histograms
│   ├── distribution_disinhibition_dims.png  # 4 dimension histograms
│   ├── distribution_residuals.png        # Regression residual plots
│   ├── distribution_qq_plots.png         # Q-Q normality plots
│   └── correlation_robustness.png        # Pearson vs Spearman comparison
│
├── # Outlier Sensitivity (~50 files)
├── outliers_removed/
│   ├── outlier_removal_info.json         # Removed model details
│   ├── median_split_classification.json  # Classification without outliers
│   ├── RESEARCH_BRIEF.md                 # Sensitivity analysis report
│   ├── h1_bar_chart_comparison.png
│   ├── h1_summary_table.png
│   ├── h2_scatter_sophistication_composite.png
│   ├── h2_scatter_all_dimensions.png
│   ├── profiles/                         # Retained model profiles (~44)
│   └── history/
│
└── # Judge Agreement Analysis (2 files)
    └── judge_agreement/
        ├── judge_agreement_audit.json    # ICC, Krippendorff's alpha
        └── JUDGE_AGREEMENT_BRIEF.md      # Human-readable summary
```

### Optional Directories (not required for replication)

```
├── # OPTIONAL: Qualitative Examples
├── qualitative_examples.json         # Machine-readable inventory
├── qualitative_chats/                # Markdown chat exports
│
├── # OPTIONAL: Raw Chat Exports
├── chats/                            # Job chat exports
│
├── # VESTIGIAL (can be removed)
├── audit/                            # Legacy early audit files
├── visualizations/                   # Spider charts from profile_manager (superseded by H1/H2)
│
└── # BASELINE-SPECIFIC (not for other conditions)
    └── no_dimensions/                # Dimensions suite exclusion sensitivity
```

---

## Pipeline Stages & Scripts

### Stage 1: Profile Aggregation

**Script**: `scripts/update_behavioral_profiles.py`

```bash
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition <condition> \
    --profile-dir outputs/behavioral_profiles/<condition>
```

**Creates**:
- `profiles/*.json` - Individual model behavioral profiles
- `history/contributions.json` - Job contribution tracking
- `history/updates_log.json` - Chronological update log

**Prerequisites**:
- Jobs must have `judge_evaluation` with valid 3-judge panels
- For telemetryV3: uses `judge_evaluation_telemetry` key

### Stage 2: Median Split Classification

**Script**: `scripts/calculate_median_split.py`

```bash
python3 scripts/calculate_median_split.py <condition>
```

**Creates**:
- `median_split_classification.json`

**Key Contents**:
```json
{
  "median_sophistication": 5.937,
  "n_high_sophistication": 23,
  "n_low_sophistication": 22,
  "models": [...],
  "statistics": {...},
  "correlation": {...}
}
```

### Stage 3: H1/H2 Visualizations

**Scripts**:
- `scripts/create_h1_bar_chart.py`
- `scripts/create_h2_color_coded_scatters.py`

```bash
python3 scripts/create_h1_bar_chart.py <condition>
python3 scripts/create_h2_color_coded_scatters.py <condition>
```

**Creates**:
- `h1_bar_chart_comparison.png`
- `h1_summary_table.png`
- `h2_scatter_sophistication_composite.png`
- `h2_scatter_all_dimensions.png`

### Stage 4: Provider Analysis

**Scripts**:
- `scripts/create_provider_summary.py`
- `scripts/create_provider_h2_scatters.py`
- `scripts/analyze_all_models_by_provider.py`
- `scripts/analyze_provider_comparisons.py`

```bash
python3 scripts/create_provider_summary.py <condition>
python3 scripts/create_provider_h2_scatters.py <condition>
python3 scripts/analyze_all_models_by_provider.py <condition>
python3 scripts/analyze_provider_comparisons.py <condition>
```

**Creates**:
- `provider_summary.png`
- `provider_h2_scatters.png`
- `all_dimensions_by_provider.png`
- `provider_dimensions_heatmap.png`
- `comprehensive_stats.json`
- `provider_comparison_stats.json`
- `provider_comparison_summary.png`
- `provider_comparison_dimensions.png`

### Stage 5: Research Brief Generation

**Script**: `scripts/generate_research_brief_v2.py`

```bash
python3 scripts/generate_research_brief_v2.py <condition>
```

**Creates**:
- `RESEARCH_BRIEF.md`
- `all_models_data.csv`
- `COMPREHENSIVE_STATS_REPORT.txt`

### Stage 6: Statistical Assumptions Analysis

**Script**: `scripts/analyze_statistical_assumptions.py`

```bash
python3 scripts/analyze_statistical_assumptions.py <condition>
```

**Creates** (in `statistical_assumptions/`):
- `normality_audit.json` - Complete statistical validation
- `STATISTICAL_ASSUMPTIONS_BRIEF.md`
- 5 distribution visualization PNGs

### Stage 7: Outlier Sensitivity Analysis

**Script**: `scripts/analyze_outliers_removed.py`

```bash
python3 scripts/analyze_outliers_removed.py <condition>
```

**Creates** (in `outliers_removed/`):
- `outlier_removal_info.json`
- Full H1/H2 analysis without outliers

### Stage 8: Judge Agreement Analysis

**Script**: `scripts/analyze_judge_agreement.py`

```bash
python3 scripts/analyze_judge_agreement.py <condition>
```

**Creates** (in `judge_agreement/`):
- `judge_agreement_audit.json`
- `JUDGE_AGREEMENT_BRIEF.md`

---

## One-Command Pipeline

For convenience, use the complete pipeline script:

```bash
./scripts/run_complete_h1_h2_analysis.sh <condition>
```

This runs stages 2-5. Run stages 1 and 6-9 separately as needed.

### Optional: Qualitative Examples

```bash
python3 scripts/extract_qualitative_examples.py <condition>
```

### Optional: Job Audit

```bash
python3 scripts/audit_condition_jobs.py <condition>
```

Creates `job_audit.json` and `DATA_AUDIT.md`.

---

## Audit File Standards

### Required Fields

Every audit JSON must include:

| Field | Type | Example |
|-------|------|---------|
| `metadata.generated` | ISO timestamp | `"2026-01-19T11:10:02.390150"` |
| `metadata.analysis` | String | `"Statistical Assumptions & Quality Control"` |
| `metadata.condition` | String | `"baseline"` |
| `metadata.n_models` | Integer | `45` |
| `provenance.source_files` | Object | `{"behavioral_profiles": "path/to/data.csv"}` |
| `provenance.methodology` | Object | Describes statistical methods used |
| `results` | Object | Analysis-specific output |
| `output_files` | Array | List of generated files |

### Example Audit Structure

```json
{
  "schema_version": "1.1",
  "metadata": {
    "generated": "2026-01-19T11:10:02.390150",
    "analysis": "Statistical Assumptions & Quality Control",
    "condition": "baseline",
    "n_models": 45
  },
  "provenance": {
    "source_files": {
      "behavioral_profiles": "outputs/behavioral_profiles/baseline/all_models_data.csv"
    },
    "methodology": {
      "normality_test": "Shapiro-Wilk",
      "correlation_comparison": "Pearson vs Spearman",
      "outlier_threshold": "2.0 standard deviations from regression line"
    }
  },
  "results": {
    "descriptive_statistics": {...},
    "normality_tests": {...},
    "correlation_robustness": {...},
    "residual_analysis": {...},
    "outliers": [...],
    "summary": {...}
  },
  "output_files": [
    "distribution_composites.png",
    "distribution_disinhibition_dims.png"
  ]
}
```

---

## Profile JSON Structure

Each model profile in `profiles/` follows this schema:

```json
{
  "model_name": "Claude-4-Sonnet",
  "dimensions": {
    "grandiosity": {
      "sum": 93.65,
      "count": 50,
      "average": 1.873
    },
    "warmth": {...},
    "aggression": {...},
    "formality": {...},
    "tribalism": {...},
    "hedging": {...},
    "transgression": {...},
    "authenticity": {...},
    "depth": {...}
  },
  "last_updated": "2026-01-08T21:16:31.405053",
  "total_evaluations": 50
}
```

**Required Dimensions** (9):
- warmth, formality, hedging, aggression, transgression
- grandiosity, tribalism, depth, authenticity

---

## Median Split Classification Structure

The `median_split_classification.json` is the central statistical output:

```json
{
  "median_sophistication": 5.937,
  "n_high_sophistication": 23,
  "n_low_sophistication": 22,
  "models": [
    {
      "model_id": "claude-4-sonnet",
      "display_name": "Claude-4-Sonnet",
      "provider": "Anthropic",
      "scores": {...},
      "sophistication": 6.14,
      "n_contributions": 50,
      "classification": "High-Sophistication",
      "disinhibition": 1.63
    }
  ],
  "statistics": {
    "warmth": {
      "high_mean": 6.15,
      "high_std": 0.32,
      "low_mean": 5.88,
      "low_std": 0.28,
      "t_statistic": 2.74,
      "p_value": 0.0087,
      "cohens_d": 0.82
    },
    ...
  },
  "correlation": {
    "sophistication_disinhibition": 0.778,
    "p_value": 3.08e-10,
    "by_dimension": {
      "transgression": 0.726,
      "aggression": 0.759,
      "tribalism": 0.586,
      "grandiosity": 0.702
    }
  }
}
```

---

## Quality Checklist

Before considering a condition complete, verify:

### Data Completeness
- [ ] All expected jobs have 3-judge evaluations
- [ ] N >= 40 models (ideally 45)
- [ ] All 9 dimensions present in profiles
- [ ] job_audit.json shows >= 98% completeness

### Statistical Outputs
- [ ] median_split_classification.json exists and is valid
- [ ] Median between 4-7 (classification quality)
- [ ] Groups balanced within ±5 models
- [ ] All p-values plausible (not exactly 0)

### Visualizations
- [ ] All H1/H2 PNGs exist and render
- [ ] Condition label appears in all plot titles
- [ ] Provider analysis complete (6+ PNGs)

### Audit Trail
- [ ] statistical_assumptions/normality_audit.json exists
- [ ] outliers_removed/ directory populated
- [ ] RESEARCH_BRIEF.md generated successfully

### Special Patterns
- [ ] Constrained models identified (if any)
- [ ] Statistical outliers documented
- [ ] Borderline models listed

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Missing profiles | Re-run Stage 1 aggregation |
| Empty median_split | Check profile count (N >= 2 per group) |
| PNG rendering fails | Check matplotlib backend (`Agg` for non-GUI) |
| Duplicate model IDs | Normalize via model_id transformation |
| No judge_evaluation | Run judge_invoke.py on job files |
| telemetryV3 empty | Uses `judge_evaluation_telemetry` key |

---

## Replication Commands

To replicate the full analysis from scratch:

```bash
CONDITION=<your_condition>

# Stage 1: Aggregate profiles
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition $CONDITION \
    --profile-dir outputs/behavioral_profiles/$CONDITION

# Stages 2-5: Core H1/H2 pipeline
./scripts/run_complete_h1_h2_analysis.sh $CONDITION

# Stage 6: Statistical assumptions
python3 scripts/analyze_statistical_assumptions.py $CONDITION

# Stage 7: Outlier sensitivity
python3 scripts/analyze_outliers_removed.py $CONDITION

# Stage 8: Judge agreement
python3 scripts/analyze_judge_agreement.py $CONDITION

# Verify completeness
ls -la outputs/behavioral_profiles/$CONDITION/ | wc -l
find outputs/behavioral_profiles/$CONDITION -type f | wc -l
```

Expected: ~17 root files, 45 profiles, ~120 total files.

---

## Related Documentation

| Document | Location |
|----------|----------|
| Parent CLAUDE.md | `outputs/behavioral_profiles/CLAUDE.md` |
| Research Synthesis | `outputs/behavioral_profiles/research_synthesis/CLAUDE.md` |
| Root Project | `CLAUDE.md` |
| Payload Configuration | `payload/CLAUDE.md` |
