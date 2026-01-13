# Behavioral Profiles Directory

**Purpose**: Storage and analysis outputs for the H1/H2 statistical analysis pipeline.

## Directory Structure

```
behavioral_profiles/
├── CLAUDE.md                           # This file
├── profiles/                           # CROSS-CONDITION AGGREGATE (all conditions combined)
├── visualizations/                     # CROSS-CONDITION AGGREGATE (spider charts, heatmaps)
├── history/                            # CROSS-CONDITION AGGREGATE (aggregation metadata)
├── baseline/                           # Control condition (no intervention)
├── authority/                          # Authority intervention
├── urgency/                            # Urgency intervention
├── minimal_steering/                   # Minimal steering intervention
├── telemetryV3/                        # Telemetry V3 (uses judge_evaluation_telemetry)
├── reminder/                           # Reminder intervention
├── <future_interventions>/             # Additional conditions as analyzed
└── research_synthesis/
    └── cross_condition/
        └── CONDITION_COMPARISON.md     # Auto-updated comparative table
```

## Root Directories (Cross-Condition Aggregate)

The root-level `profiles/`, `visualizations/`, and `history/` directories contain **aggregated data from ALL conditions** - NOT a single condition.

| Directory | Contents |
|-----------|----------|
| `profiles/` | Combined profiles weighted by evaluation count across all conditions |
| `visualizations/` | Spider charts and heatmaps showing cross-condition averages |
| `history/` | Aggregation metadata (which conditions contributed) |

**Regenerating after new condition data**:
```bash
python3 scripts/aggregate_all_conditions.py
```

**Note**: Per-condition analysis is in `<condition>/profiles/`, `<condition>/visualizations/`, etc.

## Condition Directory Contents

Each condition directory contains **18 items** after running the complete analysis pipeline:

### Core H1/H2 Analysis (5 files)
| File | Description |
|------|-------------|
| `median_split_classification.json` | Complete classification data with statistics |
| `h1_bar_chart_comparison.png` | Group comparison bar chart |
| `h1_summary_table.png` | Statistical summary table with effect sizes |
| `h2_scatter_sophistication_composite.png` | Main correlation plot with labels |
| `h2_scatter_all_dimensions.png` | 4-subplot grid (transgression, aggression, tribalism, grandiosity) |

### Provider Analysis (5 files)
| File | Description |
|------|-------------|
| `provider_summary.png` | Combined 4-panel provider analysis |
| `provider_h2_scatters.png` | 2x3 grid showing H2 by provider |
| `all_dimensions_by_provider.png` | 3x3 grid of all 9 dimensions |
| `provider_dimensions_heatmap.png` | Heatmap across providers |
| `comprehensive_stats.json` | Complete provider statistics |

### Cross-Provider Comparisons (3 files)
| File | Description |
|------|-------------|
| `provider_comparison_stats.json` | ANOVA and pairwise t-tests across providers |
| `provider_comparison_summary.png` | 4-panel summary (N, sophistication, disinhibition, classification) |
| `provider_comparison_dimensions.png` | 3x3 grid: all dimensions by provider with stats |

### Data Exports (3 files)
| File | Description |
|------|-------------|
| `all_models_data.csv` | Complete dataset for external analysis |
| `COMPREHENSIVE_STATS_REPORT.txt` | Human-readable statistical summary |
| `RESEARCH_BRIEF.md` | Publication-ready research brief |

### Qualitative Examples (2 items)
| Path | Description |
|------|-------------|
| `qualitative_examples.json` | Inventory of representative responses |
| `qualitative_chats/` | Chat exports organized by category |

### Supporting Directories
| Directory | Description |
|-----------|-------------|
| `profiles/` | Individual model profile JSON files |
| `history/` | Contribution tracking and update logs |

## Key Metrics

### H1 (Group Difference)
- **Test**: Independent samples t-test
- **Effect Size**: Cohen's d
- **Interpretation**: d > 0.8 = large effect

### H2 (Correlation)
- **Test**: Pearson correlation
- **Effect Size**: r coefficient
- **Interpretation**: r > 0.5 = large correlation

### Results Location
See `research_synthesis/cross_condition/CONDITION_COMPARISON.md` for current aggregate results across all conditions.

## Running Analysis

### One-Command Pipeline
```bash
./scripts/run_complete_h1_h2_analysis.sh <condition_name>
```

### Cross-Provider Comparisons (after H1/H2)
```bash
python3 scripts/analyze_provider_comparisons.py <condition_name>
```

### Complete Pipeline (Recommended)
```bash
CONDITION="your_condition"

# Stage 1: Aggregate profiles
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition $CONDITION \
    --profile-dir outputs/behavioral_profiles/$CONDITION

# Stages 2-4: H1/H2 analysis
./scripts/run_complete_h1_h2_analysis.sh $CONDITION

# Stage 5: Cross-provider comparisons
python3 scripts/analyze_provider_comparisons.py $CONDITION

# Stage 6: Update cross-condition docs
python3 scripts/update_cross_condition_comparison.py
```

### Prerequisites
Profiles must be aggregated first:
```bash
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition <condition_name> \
    --profile-dir outputs/behavioral_profiles/<condition_name>
```

### Supported Conditions
- `baseline` - No intervention suffix in job files
- `authority` - Jobs with `_authority` suffix
- `urgency` - Jobs with `_urgency` suffix
- `minimal_steering` - Jobs with `_minimal_steering` suffix
- `telemetryV3` - Jobs with `_telemetryV3` suffix (uses `judge_evaluation_telemetry` results)
- `reminder` - Jobs with `_reminder` suffix

**Note on telemetryV3**: This condition uses a separate judge evaluation key (`judge_evaluation_telemetry`) that evaluates only the extracted `.response` field from the telemetry JSON structure, not the full model output. See root `CLAUDE.md` for detailed telemetry processing documentation.

## Special Pattern Detection

The H2 scatter plots identify three special patterns:

### Borderline Models (Orange Squares)
- Within ±0.15 of median sophistication
- Edge cases for sensitivity analysis
- **Threshold**: `BORDERLINE_THRESHOLD = 0.15`

### Constrained Models (Cyan Diamonds)
- High sophistication (>6.5) but low disinhibition
- Suggests deliberate constraint despite capability
- **Thresholds**:
  - `CONSTRAINED_SOPH_THRESHOLD = 6.5`
  - `CONSTRAINED_RESIDUAL_THRESHOLD = -0.15`
- **Detection**: Regression-specific (composite plot uses composite regression; per-dimension plots use each dimension's own regression line)

### Statistical Outliers (Red Circles)
- Residual > 2 SD from regression line
- **Threshold**: `OUTLIER_SD_THRESHOLD = 2.0`

## Outlier Sensitivity Analysis

Each condition can have an `outliers_removed/` subfolder containing sensitivity analysis with statistical outliers excluded.

### Subfolder Structure
```
<condition>/outliers_removed/
├── outlier_removal_info.json           # Details of removed models
├── median_split_classification.json    # Classification without outliers
├── h1_bar_chart_comparison.png         # H1 visualization
├── h1_summary_table.png                # Statistical table
├── h2_scatter_sophistication_composite.png
├── h2_scatter_all_dimensions.png
├── profiles/                           # Retained model profiles
└── history/                            # Contribution tracking
```

### Generating Outlier Analysis
```bash
# Default 2.0 SD threshold
python3 scripts/analyze_outliers_removed.py <condition>

# Custom threshold
python3 scripts/analyze_outliers_removed.py <condition> --threshold 2.5

# Preview without creating files
python3 scripts/analyze_outliers_removed.py <condition> --dry-run

# Overwrite existing
python3 scripts/analyze_outliers_removed.py <condition> --force
```

### Outlier Detection Method
1. Fit linear regression: disinhibition ~ sophistication
2. Calculate residuals for each model
3. Flag models with |residual| > threshold × residual_std
4. Remove flagged models and regenerate H1/H2 analysis

### Example Output (telemetryV3)
```
Outliers Removed: 2
  - Claude-4.5-Haiku-Thinking (4.62 SD above line)
  - Grok-4-0709 (3.61 SD above line)

Results Comparison:
  H1: d = 1.14 → 1.65 (+0.51)
  H2: r = 0.724 → 0.780 (+0.056)
```

## Cross-Condition Comparison

Auto-updated after each pipeline run:
```
outputs/behavioral_profiles/research_synthesis/cross_condition/CONDITION_COMPARISON.md
```

Manual updates:
```bash
# Update comparison tables
python3 scripts/update_cross_condition_comparison.py

# Update constrained/outlier model patterns (creates cross_condition_patterns.json)
python3 scripts/analyze_cross_condition_patterns.py
```

## Qualitative Examples

Representative response examples extracted from job data, organized by behavioral characteristics.

### Generation

```bash
# Single condition
python3 scripts/extract_qualitative_examples.py baseline

# All conditions
python3 scripts/extract_qualitative_examples.py --all

# Force overwrite
python3 scripts/extract_qualitative_examples.py baseline --force
```

### Output Structure

```
<condition>/
├── qualitative_examples.json       # Inventory artifact (data trail)
└── qualitative_chats/              # Markdown chat exports
    ├── dimension_extremes/
    │   ├── warmth_max/
    │   ├── warmth_min/
    │   └── ...
    ├── composite_extremes/
    │   ├── sophistication_max/
    │   └── disinhibition_max/
    ├── percentiles/
    │   ├── percentile_5/
    │   ├── percentile_50/
    │   └── percentile_95/
    └── pattern_types/
        ├── constrained/
        ├── outlier/
        └── borderline/
```

### Categories

| Category | Description | Count |
|----------|-------------|-------|
| Dimension Extremes | Top 5 min/max per dimension | 90 |
| Composite Extremes | Sophistication/disinhibition extremes | 20 |
| Percentiles | 5th, 25th, 50th, 75th, 95th on disinhibition | 25 |
| Pattern Types | Constrained, outlier, borderline models | 15 |

**Note**: Examples can appear in multiple categories. Each chat export shows all categories the example qualifies for.

### Consolidated Manifest

Cross-condition summary of all qualitative examples:

```
research_synthesis/limitations/prompt_design/
├── qualitative_examples_manifest.json  # Machine-readable aggregate data
└── QUALITATIVE_MANIFEST.md             # Human-readable summary
```

Regenerate after updating examples:
```bash
# Manifest is auto-generated when running extract script
python3 scripts/extract_qualitative_examples.py --all --force
```

### Prompt Pattern Analysis

Analysis of which prompts/scenarios drive high sophistication and disinhibition scores.

**Location**:
```
research_synthesis/limitations/prompt_design/
├── qualitative_pattern_analysis.json      # Machine-readable analysis
└── QUALITATIVE_PROMPT_PATTERN_ANALYSIS.md # Comprehensive report
```

**See**: `research_synthesis/limitations/prompt_design/QUALITATIVE_PROMPT_PATTERN_ANALYSIS.md` for findings.

Regenerate analysis:
```bash
python3 scripts/analyze_qualitative_patterns.py
```

## Judge Agreement Analysis

Inter-rater reliability analysis for the 3-judge evaluation panel.

**Location**:
```
research_synthesis/limitations/judge_limitations/
├── judge_agreement_analysis.json      # Machine-readable results
└── JUDGE_AGREEMENT_ANALYSIS.md        # Comprehensive report
```

**See**: `research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md` for findings.

## Sensitivity Analyses

### No-Dimensions Suite Analysis

Robustness test excluding dimensions suite prompts.

**Location**:
```
baseline/no_dimensions/
├── median_split_classification.json
├── sensitivity_analysis_info.json
├── RESEARCH_BRIEF.md
├── h1_*.png, h2_*.png
└── profiles/, history/
```

**See**: `baseline/no_dimensions/RESEARCH_BRIEF.md` for findings.

## IMPORTANT Notes

- **NEVER** manually edit `median_split_classification.json` - regenerate via pipeline
- **ALWAYS** use baseline as the anchor for cross-condition comparisons
- **DO NOT** delete `profiles/` or `history/` directories - they contain source data
- Profile aggregation is **idempotent** - re-running won't duplicate data

## Related Documentation

- Root: `CLAUDE.md` - Complete project documentation
- Logs: `logs/CLAUDE.md` - Hook logging system
- Scripts: See `scripts/` for analysis scripts
