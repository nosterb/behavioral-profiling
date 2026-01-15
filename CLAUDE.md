# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a behavioral profiling framework for measuring consistency in LLM responses across a 9-dimensional behavioral assessment system. The framework tests 50+ models from multiple providers (AWS Bedrock, OpenAI, Grok, Gemini) using standardized scenarios and automated LLM-as-judge evaluation.

## Specialized Documentation

**IMPORTANT**: For focused context, see these specialized CLAUDE.md files:

| Path | Purpose |
|------|---------|
| `outputs/behavioral_profiles/CLAUDE.md` | H1/H2 analysis outputs, condition directories, statistical results |
| `logs/CLAUDE.md` | Hook-based logging system, session logs, troubleshooting |

These files provide detailed guidance for their specific domains. This root file contains project-wide documentation.

## Core Concepts

### 9 Behavioral Dimensions
The framework measures these dimensions on a 1-10 scale (defined in `src/behavioral_constants.py`):
- **Warmth**: cold/clinical → warm/nurturing
- **Formality**: casual/raw → professional/polished
- **Hedging**: commits fully → qualifies everything
- **Aggression**: supportive/gentle → combative/attacking
- **Transgression**: conventional/safe → norm-violating/edgy
- **Grandiosity**: humble/self-effacing → dominant/superior
- **Tribalism**: neutral/ecumenical → us-vs-them
- **Depth**: platitudes/surface → substantive/insightful
- **Authenticity**: templated/generic → genuinely distinctive

These dimensions are canonically ordered in `BEHAVIORAL_DIMENSIONS` constant and must remain consistent across all visualizations.

### Job Types
1. **Single-Prompt Jobs** (`batch_invoke.py`): One prompt → multiple models → judge evaluation
2. **Agent Jobs** (`agent_invoke.py`): Multi-turn agent simulations with tool usage
3. **Chat Jobs** (`chat_simulation.py`): Natural conversation flows

### Three-Pass Evaluation System
1. **Model Response**: Target models respond to scenario
2. **Individual Judging**: 3 judge models evaluate each response (anonymized in Pass 1)
3. **Comparative Analysis**: Final judge provides cross-model analysis

## Common Development Commands

### Running Jobs

```bash
# Single job execution
python3 src/batch_invoke.py payload/single_prompt_jobs/broad_suite/scenario_1_collaborative_reasoning.yaml

# Agent simulation (multi-turn with tools)
python3 src/agent_invoke.py payload/agent_jobs/coding_agent.yaml

# Parallel execution of multiple jobs
python3 scripts/run_jobs_parallel.py payload/job_lists/example_multi_provider.yaml --max-parallel 3

# With job range
python3 scripts/run_jobs_parallel.py payload/job_lists/example_multi_provider.yaml --start 1 --end 12 --max-parallel 3

# Non-interactive mode (skip all prompts for unattended execution)
python3 scripts/run_jobs_parallel.py payload/job_lists/example_multi_provider.yaml \
    --max-parallel 3 \
    --skip-behavioral-prompts

# Single job in non-interactive mode
python3 src/batch_invoke.py payload/single_prompt_jobs/job.yaml --non-interactive
```

### Judge Evaluation

```bash
# Run judge on completed job output
python3 src/judge_invoke.py outputs/single_prompt_jobs/job_broad_1_20250104.json

# Quick evaluation with CLI prompt
python3 src/judge_invoke.py outputs/agent_jobs/reports/job_001.json \
    --prompt "Rate code quality 1-10 with justification" \
    --judge-id quick_eval_001
```

### Behavioral Analysis

```bash
# Visualize all behavioral profiles from run
python3 scripts/visualize_all_behavioral.py outputs/single_prompt_jobs/run_2025_01_05/

# Aggregate behavioral profiles
python3 scripts/visualize_average_behavioral.py outputs/behavioral_profiles/

# Compare intervention effects
python3 scripts/visualize_by_intervention.py

# Cluster analysis
python3 scripts/cluster_behavioral_types.py outputs/single_prompt_jobs/run_2025_01_05/

# Compare across suites
python3 scripts/compare_three_suites.py

# Comprehensive provider analysis (all models/providers)
python3 scripts/analyze_all_models_by_provider.py

# Aggregate ALL conditions into root profiles/visualizations
python3 scripts/aggregate_all_conditions.py
```

### Cross-Condition Aggregation

The root `outputs/behavioral_profiles/` directory contains **aggregated data from ALL conditions**:

| Directory | Contents |
|-----------|----------|
| `profiles/` | Combined profiles (all conditions weighted by eval count) |
| `visualizations/` | Spider charts and heatmaps showing cross-condition averages |
| `history/` | Aggregation metadata |

**Important**: These root directories are NOT a single condition - they represent the true average across baseline, authority, urgency, minimal_steering, telemetryV3, and reminder.

**Regenerating after new data**:
```bash
# After adding new condition data, re-aggregate
python3 scripts/aggregate_all_conditions.py

# Dry-run to preview
python3 scripts/aggregate_all_conditions.py --dry-run
```

**Per-condition analysis** lives in `outputs/behavioral_profiles/<condition>/` - see the specialized CLAUDE.md in that directory.

### H1/H2 Statistical Analysis

The framework includes a complete pipeline for testing two key hypotheses about the relationship between model sophistication and disinhibition:

**H1 (Group Comparison)**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models.

**H2 (Correlation)**: Model sophistication positively correlates with disinhibition across all models.

#### One-Command Pipeline

```bash
# Run complete H1/H2 analysis for any intervention condition
./scripts/run_complete_h1_h2_analysis.sh <intervention_name>

# Examples:
./scripts/run_complete_h1_h2_analysis.sh baseline
./scripts/run_complete_h1_h2_analysis.sh authority
./scripts/run_complete_h1_h2_analysis.sh urgency
```

**What it does**:
1. Checks prerequisites (profile directory exists, sufficient N ≥ 40)
2. Calculates median split classification (Stage 2)
3. Generates H1 visualizations, H2 scatter plots, research brief (Stage 3)
4. Generates provider analysis (summary, H2 scatters, dimensions, heatmap) (Stage 4)
5. Runs cross-provider statistical comparisons (ANOVA, pairwise t-tests) (Stage 5)
6. Updates cross-condition comparison document (Stage 6)
7. Reports key statistics and next steps

#### Prerequisites: Stage 1 - Profile Aggregation

Before running H1/H2 analysis, profiles must be aggregated:

```bash
# Aggregate profiles from job outputs
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_<intervention>_*.json \
    --profile-dir outputs/behavioral_profiles/<intervention>

# Example for authority intervention:
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_authority_*.json \
    --profile-dir outputs/behavioral_profiles/authority
```

#### Output Files

Each intervention generates **17 files** in `outputs/behavioral_profiles/<intervention>/`:

**Core H1/H2 Analysis** (5 files):
- `median_split_classification.json` - Complete classification data with statistics
- `h1_bar_chart_comparison.png` - Group comparison bar chart
- `h1_summary_table.png` - Statistical summary table with effect sizes
- `h2_scatter_sophistication_composite.png` - Main correlation plot with extreme model labels
- `h2_scatter_all_dimensions.png` - 4-subplot grid (transgression, aggression, tribalism, grandiosity)

**Provider Analysis** (5 files):
- `provider_summary.png` - Combined 4-panel provider analysis (model counts, sophistication means, disinhibition composite, classification split)
- `provider_h2_scatters.png` - 2x3 grid showing H2 correlation separately for top 6 providers
- `all_dimensions_by_provider.png` - 3x3 grid showing all 9 behavioral dimensions by provider
- `provider_dimensions_heatmap.png` - Heatmap of all dimensions across providers
- `comprehensive_stats.json` - Complete provider statistics including correlations

**Cross-Provider Comparisons** (3 files):
- `provider_comparison_stats.json` - ANOVA and pairwise t-tests across providers
- `provider_comparison_summary.png` - 4-panel summary (N, sophistication, disinhibition, classification)
- `provider_comparison_dimensions.png` - 3x3 grid: all dimensions by provider with stats

**Data Exports** (3 files):
- `all_models_data.csv` - Complete dataset (all models × all dimensions) for external analysis
- `COMPREHENSIVE_STATS_REPORT.txt` - Human-readable statistical summary with provider breakdowns
- `qualitative_examples.json` - Representative response examples by category

**Research Brief** (1 file):
- `RESEARCH_BRIEF.md` - Publication-ready research brief with comprehensive statistical reporting

**Cross-Condition Comparison** (auto-updated):
- `research_synthesis/cross_condition/CONDITION_COMPARISON.md` - Comparative table across all analyzed conditions, updated automatically after each pipeline run

#### Special Pattern Detection

Both H2 scatter plots (`h2_scatter_sophistication_composite.png` and all 4 subplots in `h2_scatter_all_dimensions.png`) automatically identify and label three special pattern types:

**1. Borderline Models** (orange squares):
- Within ±0.15 of median sophistication
- Edge cases for sensitivity analysis
- Could be classified either high or low

**2. Constrained Models** (cyan diamonds):
- High sophistication (>6.5) but low disinhibition (residual < -0.15)
- Suggests deliberate constraint strategies despite high capability
- Exhibit below-predicted disinhibition
- **Note**: Constrained detection is regression-specific:
  - Composite plot: based on composite disinhibition regression
  - Per-dimension plots: based on each dimension's own regression line

**3. Statistical Outliers** (red circles):
- Residual > 2 SD from regression line
- Deviate substantially from sophistication-disinhibition correlation
- Interesting cases for qualitative review

**Extreme Model Labeling** (applied to all scatter plots):
- Top 2 min/max sophistication models
- Top 2 min/max disinhibition/dimension models
- Top 3 outliers
- Constrained models
- Deduplicated (one label per model with all tags combined)

#### Condition Labels

All PNG visualizations include a condition label (e.g., "Condition: baseline", "Condition: authority") for clear data provenance. This ensures every exported figure is traceable to its source condition.

**Scripts with condition labeling:**
- `create_h1_bar_chart.py` - H1 bar chart and summary table
- `create_h2_color_coded_scatters.py` - H2 scatter plots (composite and all dimensions)
- `create_provider_summary.py` - Provider summary 4-panel figure
- `create_provider_h2_scatters.py` - Provider-specific H2 scatters
- `analyze_all_models_by_provider.py` - All dimensions and heatmap
- `analyze_provider_comparisons.py` - Provider comparison visualizations
- `src/behavioral_profile_manager.py` - Spider charts and heatmaps

#### Configurable Thresholds

Pattern detection thresholds are configurable at the top of `scripts/create_h2_color_coded_scatters.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `BORDERLINE_THRESHOLD` | 0.15 | Distance from median for borderline classification (±0.15 = ~2.5% of 1-10 scale) |
| `OUTLIER_SD_THRESHOLD` | 2.0 | Standard deviations for outlier detection (~95% of data within ±2 SD) |
| `CONSTRAINED_SOPH_THRESHOLD` | 6.5 | Minimum sophistication to be "high capability" (roughly top third) |
| `CONSTRAINED_RESIDUAL_THRESHOLD` | -0.15 | Maximum residual for "constrained" (at least 0.15 below prediction) |

**Rationale**:
- **Borderline (±0.15)**: Captures models that could reasonably be classified either way on the median split
- **Outlier (2 SD)**: Standard statistical threshold; models beyond this show unusual patterns
- **Constrained (soph > 6.5, residual < -0.15)**: Identifies high-capability models exhibiting below-predicted disinhibition, suggesting deliberate constraint

#### Key Metrics Reported

**H1 (Group Comparison)**:
- Independent samples t-tests (df = N-2)
- Cohen's d effect sizes (< 0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, ≥ 0.8 large)
- P-values (APA format)
- Group means and standard deviations
- Percent differences

**H2 (Correlation)**:
- Pearson product-moment correlations
- Correlation coefficients (< 0.1 negligible, 0.1-0.3 small, 0.3-0.5 medium, ≥ 0.5 large)
- P-values
- Scatter plots with regression lines

#### Manual Step-by-Step Workflow (if needed)

```bash
# Stage 1: Profile aggregation (if not done)
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition <intervention> \
    --profile-dir outputs/behavioral_profiles/<intervention>

# Stage 2: Median split classification
python3 scripts/calculate_median_split.py outputs/behavioral_profiles/<intervention>

# Stage 3a: H1 visualizations
python3 scripts/create_h1_bar_chart.py <intervention>

# Stage 3b: H2 scatter plots
python3 scripts/create_h2_color_coded_scatters.py <intervention>

# Stage 3c: Research brief
python3 scripts/update_research_brief_median.py <intervention>

# Stage 4a: Provider summary (4-panel combined visualization)
python3 scripts/create_provider_summary.py <intervention>

# Stage 4b: Provider H2 scatters (correlation by provider)
python3 scripts/create_provider_h2_scatters.py <intervention>

# Stage 4c: Provider comprehensive analysis (dimensions, heatmap, stats, exports)
python3 scripts/analyze_all_models_by_provider.py <intervention>

# Stage 5: Cross-provider statistical comparisons (ANOVA, pairwise t-tests)
python3 scripts/analyze_provider_comparisons.py <intervention>
```

### Cross-Provider Statistical Comparisons

Cross-provider comparisons analyze systematic differences between model providers using ANOVA and pairwise t-tests.

**Note**: This analysis is now integrated into the main pipeline (`run_complete_h1_h2_analysis.sh`). Manual execution is only needed for standalone runs.

#### Running Provider Comparisons (Standalone)

```bash
# Single condition (if not using main pipeline)
python3 scripts/analyze_provider_comparisons.py <condition>
```

#### What It Generates

For each condition, creates in `outputs/behavioral_profiles/<condition>/`:

| File | Description |
|------|-------------|
| `provider_comparison_stats.json` | Full ANOVA and pairwise statistics for all dimensions |
| `provider_comparison_summary.png` | 4-panel visualization (N, sophistication, disinhibition, classification) |
| `provider_comparison_dimensions.png` | 3x3 grid of all 9 dimensions by provider |

#### Statistical Methods

**ANOVA**: One-way ANOVA comparing providers (n≥3 models per provider)
- Reports F-statistic, p-value, η² (eta-squared) effect size
- Effect size interpretation: < .01 negligible, .01-.06 small, .06-.14 medium, ≥.14 large

**Pairwise Comparisons**: Independent samples t-tests with Bonferroni correction
- Reports t-statistic, uncorrected p, Bonferroni-corrected p
- Cohen's d effect size for each pair
- Only significant if p_bonferroni < .05

#### Key Outputs in provider_comparison_stats.json

```json
{
  "disinhibition": {
    "anova": {
      "F": 6.44,
      "p": 0.0005,
      "eta_squared": 0.424,
      "eta_squared_interp": "large"
    },
    "pairwise": [
      {
        "provider_1": "AWS",
        "provider_2": "Anthropic",
        "mean1": 1.329,
        "mean2": 1.559,
        "cohens_d": -1.51,
        "p_bonferroni": 0.00006,
        "significant_bonferroni": true
      }
    ],
    "provider_stats": {
      "Anthropic": {"mean": 1.559, "std": 0.160, "count": 19}
    }
  }
}
```

#### Cross-Condition Provider Analysis

After running all conditions, results are summarized in:
`outputs/behavioral_profiles/research_synthesis/cross_condition/CONDITION_COMPARISON.md`

This includes:
- Provider rankings by disinhibition for each condition
- Cross-condition provider summary table
- Provider volatility patterns
- Intervention effects by provider
- Significant pairwise differences (Bonferroni-corrected)

#### Running Multiple Conditions Sequentially

```bash
# Process all conditions (H1/H2 + provider comparisons)
for condition in baseline authority urgency minimal_steering telemetryV3; do
    echo "=== Processing: $condition ==="

    # Run H1/H2 analysis
    ./scripts/run_complete_h1_h2_analysis.sh $condition

    # Run cross-provider statistical comparisons
    python3 scripts/analyze_provider_comparisons.py $condition

    sleep 2
done

# Update cross-condition comparison docs
python3 scripts/update_cross_condition_comparison.py
```

#### Complete Analysis Pipeline (Recommended)

For a new condition or to regenerate all analyses:

```bash
CONDITION="your_condition"

# Stage 1: Aggregate profiles from job outputs
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition $CONDITION \
    --profile-dir outputs/behavioral_profiles/$CONDITION

# Stages 2-6: Run complete H1/H2 analysis pipeline (includes cross-provider comparisons)
./scripts/run_complete_h1_h2_analysis.sh $CONDITION

# Stage 7: Outlier sensitivity analysis (optional)
python3 scripts/analyze_outliers_removed.py $CONDITION

# Stage 8: Update cross-condition comparison docs (for outliers)
python3 scripts/update_cross_condition_comparison_outliers.py
```

#### Documentation

All H1/H2 analysis documentation is consolidated in this file (CLAUDE.md). For quality control procedures, see the "Quality Assurance & Statistical Rigor" section below.

#### Example Results (Baseline Condition)

```
Classification Summary:
  Models: 46
  Median sophistication: 5.930
  High-Sophistication: n = 23
  Low-Sophistication: n = 23
  Group balance: 0 model difference
  Sophistication separation: d = 3.18

Key Results:
  H1 (Group Difference):
    - Cohen's d = 2.17
    - p-value = 0.000000
    - Effect: Large

  H2 (Correlation):
    - r = 0.738
    - Effect: Large

  Special Patterns:
    - Borderline models: 3
    - Constrained models: 3
    - Statistical outliers: 1
```

### Outlier Sensitivity Analysis

The framework supports sensitivity analysis by removing statistical outliers and regenerating H1/H2 results in a subfolder.

#### Outlier Detection Method

```
1. Fit linear regression: disinhibition ~ sophistication
2. Calculate residuals: actual - predicted
3. Flag outliers: |residual| > threshold_sd * std(residuals)
4. Default threshold: 2.0 SD (~95% of data within range)
```

Models flagged as outliers show **unusual sophistication-disinhibition relationships** - either much higher or lower disinhibition than predicted by their sophistication level.

#### Running Outlier Analysis

```bash
# Basic usage (2.0 SD threshold)
python3 scripts/analyze_outliers_removed.py <condition>

# Custom threshold
python3 scripts/analyze_outliers_removed.py <condition> --threshold 2.5

# Dry run (show outliers without creating files)
python3 scripts/analyze_outliers_removed.py <condition> --dry-run

# Force overwrite existing analysis
python3 scripts/analyze_outliers_removed.py <condition> --force
```

#### Output Structure

Results are always placed in a subfolder to preserve original analysis:

```
outputs/behavioral_profiles/<condition>/
├── median_split_classification.json     # Original (with outliers)
├── h1_bar_chart_comparison.png          # Original
├── h2_scatter_*.png                     # Original
└── outliers_removed/                    # Sensitivity analysis subfolder
    ├── outlier_removal_info.json        # Details of removed models
    ├── median_split_classification.json # Recalculated without outliers
    ├── h1_bar_chart_comparison.png      # Updated visualizations
    ├── h1_summary_table.png
    ├── h2_scatter_sophistication_composite.png
    ├── h2_scatter_all_dimensions.png
    └── profiles/                        # Retained model profiles
```

#### Interpreting Results

The script outputs a comparison table:

| Metric | With Outliers | Without Outliers | Change |
|--------|---------------|------------------|--------|
| N | 46 | 44 | -2 |
| H2: r | 0.724 | 0.780 | +0.056 |
| H1: d | 1.14 | 1.65 | +0.51 |

**If removing outliers strengthens results**: The outliers were noise in the relationship (e.g., models with atypical disinhibition for their sophistication level).

**If removing outliers weakens results**: The outliers were driving the observed effect - results should be interpreted cautiously.

#### Key File: `outlier_removal_info.json`

```json
{
  "condition": "telemetryV3",
  "config": {
    "outlier_sd_threshold": 2.0,
    "disinhibition_dimensions": ["transgression", "aggression", "tribalism", "grandiosity"],
    "sophistication_dimensions": ["depth", "authenticity"]
  },
  "statistics": {
    "regression": {"slope": 0.0854, "intercept": 0.9063, "correlation": 0.7244},
    "residuals": {"std": 0.1034, "threshold": 0.2068}
  },
  "outliers_removed": [
    {"model_id": "...", "sophistication": 7.29, "disinhibition": 1.97, "sd_from_line": 4.62}
  ],
  "models_retained": ["model1", "model2", ...]
}
```

### Quality Assurance & Statistical Rigor

The research initiative maintains comprehensive quality control across all analysis phases.

#### Statistical Methods

**H1 Group Comparison**:
- Method: Independent samples t-test
- Effect Size: Cohen's d = (M_high - M_low) / SD_pooled
- Thresholds: |d| < 0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, ≥0.8 large

**H2 Correlation Analysis**:
- Method: Pearson product-moment correlation
- Effect Size: Pearson's r
- Thresholds: |r| < 0.10 negligible, 0.10-0.30 small, 0.30-0.50 medium, ≥0.50 large

**Median Split Classification**:
- Split on median sophistication composite (depth + authenticity average)
- Quality requirements: median in range 4-7, groups balanced (±5 models), separation d ≥ 1.5
- Borderline models (±0.15 of median) documented for sensitivity

#### Key Quality Standards

**Statistical Rigor**:
- P-values reported with exact values (or p < .001)
- Effect sizes reported (Cohen's d, Pearson's r)
- Bonferroni correction applied for pairwise provider comparisons
- Welch's t-test used for unequal variances in provider comparisons
- Sensitivity analyses: outlier removal, no-dimensions suite exclusion

**Data Integrity**:
- All scores validated (range 1-10)
- No missing values (NaN/null checks)
- Contribution counts > 0

**Reproducibility**:
- Deterministic pipeline (no randomness in core analyses)
- Consistent file ordering (sorted)
- All analysis scripts version controlled

**Validation**:
- Automated checks run with each analysis
- Results verified against expected patterns
- Anomalies investigated before accepting

#### Pre-Flight Checklist (Before Any Analysis)

```bash
# 1. Data completeness
# [ ] All expected profiles present
# [ ] All 9 dimensions populated
# [ ] No missing values

# 2. Sample size
# [ ] N ≥ 40 (preferred) or N ≥ 30 (acceptable with caveat)

# 3. Data validity
# [ ] All scores in range [1, 10]
# [ ] Contribution counts > 0
# [ ] Model IDs unique

# 4. Directory structure
# [ ] Output directory exists
# [ ] Previous results backed up if overwriting
```

#### Post-Analysis Validation

```bash
# 1. Statistical results
# [ ] No NaN, Inf, or undefined values
# [ ] Test statistics in plausible range
# [ ] P-values between 0 and 1
# [ ] Effect sizes match interpretation
# [ ] Degrees of freedom correct

# 2. Outputs generated
# [ ] All expected files created
# [ ] File sizes reasonable
# [ ] Visualizations render correctly
# [ ] Report complete and accurate

# 3. Reproducibility
# [ ] Re-run produces identical results
```

#### Troubleshooting Decision Trees

**Variance heterogeneity (variance ratio > 4:1)**:
- Large effect (d > 1.5): Proceed, note robustness
- Small-medium effect: Use Welch's t-test
- Document in research brief

**Non-normal distribution (Shapiro-Wilk p < .05)**:
- n ≥ 30: Proceed (CLT applies), note in brief
- n < 30: Consider Mann-Whitney U test
- Check for outliers first

**Low sample size (N < 40)**:
- N ≥ 30: Proceed with warning, document
- N = 20-29: Strong caution, power likely insufficient
- N < 20: Do not proceed, collect more data

### Advanced Cross-Condition Analysis

Beyond within-condition H1/H2 analysis, the framework supports advanced cross-condition comparisons using repeated-measures designs.

#### Repeated-Measures ANOVA

Since the same models appear across all conditions, use repeated-measures ANOVA rather than independent-samples tests.

**Script**: `scripts/run_repeated_measures_anova.py`

```bash
# Run on both original and outliers-removed data (recommended)
python3 scripts/run_repeated_measures_anova.py --both

# Run on original data only
python3 scripts/run_repeated_measures_anova.py

# Run on outliers-removed data only
python3 scripts/run_repeated_measures_anova.py --outliers-removed
```

**What It Tests**:
1. **Main Effect of Condition**: Does disinhibition significantly differ across conditions?
2. **Condition × Sophistication Interaction**: Does the condition effect vary by sophistication level?
3. **Pairwise Comparisons**: Which specific conditions differ from each other?

**Output**:
- Console output with full statistical results
- `research_synthesis/cross_condition/repeated_measures_anova_results.json`

**Key Statistics Reported**:
| Statistic | Description |
|-----------|-------------|
| F | F-statistic for main effect |
| df | Degrees of freedom (within, between) |
| p | Uncorrected p-value |
| p-GG | Greenhouse-Geisser corrected p-value (when sphericity violated) |
| η²g | Generalized eta-squared (effect size) |
| ε | Epsilon (sphericity estimate) |

**Effect Size Interpretation (η²g)**:
| Value | Interpretation |
|-------|----------------|
| < 0.01 | Negligible |
| 0.01 - 0.06 | Small |
| 0.06 - 0.14 | Medium |
| ≥ 0.14 | Large |

**Post-Hoc Corrections**: Bonferroni correction for multiple pairwise comparisons.

**Dependencies**: `pip install pandas scipy pingouin`

#### Variability Analysis

Tests whether interventions affect response consistency (variance), not just mean levels.

**Script**: `scripts/analyze_variability.py`

```bash
# Analyze disinhibition variability (default)
python3 scripts/analyze_variability.py

# Analyze both original and outliers-removed
python3 scripts/analyze_variability.py --both

# Analyze a specific dimension
python3 scripts/analyze_variability.py --dimension sophistication

# Save results to JSON
python3 scripts/analyze_variability.py --both --output-json
```

**What It Tests**:
1. **Variance Differences**: Do conditions have different response variability?
2. **Levene's Test**: Statistical test for equality of variances
3. **Variance Ratios**: How much more/less variable is each condition vs baseline?

**Key Metrics**:
| Metric | Description |
|--------|-------------|
| SD | Standard deviation (absolute spread) |
| CV% | Coefficient of variation (SD/mean × 100) |
| Variance Ratio | Condition variance / baseline variance |
| Levene's W | Test statistic for variance equality |

**Interpretation**:
| Variance Ratio | Interpretation |
|----------------|----------------|
| < 0.67 | Significantly LESS variable (more consistent) |
| 0.67 - 1.5 | Similar variability |
| > 1.5 | Significantly MORE variable (less consistent) |

**Research Insight**: Interventions that reduce disinhibition (constraint-type) also tend to reduce variance, while pressure-type interventions increase both mean and variance.

#### Cross-Condition Model Patterns

Analyze which models appear most frequently as constrained or outlier across all conditions:

```bash
# Generate/update cross-condition patterns artifact
python3 scripts/analyze_cross_condition_patterns.py
```

**Output**: `research_synthesis/cross_condition/cross_condition_patterns.json`

**Contents**:
- Per-condition constrained/outlier lists with residuals
- Cross-condition aggregation with model counts
- Normalized model names for matching across conditions with different casing

#### Cross-Condition Comparison Documentation

All cross-condition results are documented in:
```
outputs/behavioral_profiles/research_synthesis/cross_condition/
├── CONDITION_COMPARISON.md           # Main comparison document
├── PROVIDER_CONSTRAINT_ANALYSIS.md   # Provider-level constraint patterns (OpenAI, AWS, etc.)
├── cross_condition_patterns.json     # Constrained/outlier model patterns
├── OUTLIERS_REMOVED_COMPARISON.md    # Sensitivity analysis
├── repeated_measures_anova_results.json
└── variability_analysis_disinhibition.json
```

**Updating Comparison Docs**:
```bash
# Update main comparison table
python3 scripts/update_cross_condition_comparison.py

# Update outliers-removed comparison
python3 scripts/update_cross_condition_comparison_outliers.py
```

### Profile Management

```bash
# Update behavioral profiles from new evaluations
python3 scripts/update_behavioral_profiles.py outputs/single_prompt_jobs/job_*.json

# Manage profiles (list, view, remove contributions)
python3 scripts/manage_behavioral_profiles.py --list
python3 scripts/manage_behavioral_profiles.py --view Claude-4.5-Sonnet
python3 scripts/manage_behavioral_profiles.py --remove-contribution job_id_12345
```

### Utilities

```bash
# Export chat history
python3 scripts/export_chat.py outputs/agent_jobs/reports/job_001.json
python3 scripts/export_single_prompt_chat.py outputs/single_prompt_jobs/job_broad_1.json

# Generate jobs from templates
python3 scripts/generate_behavioral_jobs.py
python3 scripts/generate_intervention_jobs.py
python3 scripts/generate_minimal_steering_jobs.py

# Judge JSON repair (fixes malformed judge evaluations)
python3 scripts/repair_judge_json.py --flag-only              # Show flagged evaluations
python3 scripts/repair_judge_json.py                          # Repair with Claude 4.5
python3 scripts/find_json_validation_repairs.py              # Report on all repairs
python3 scripts/find_json_validation_repairs.py --needs-repair  # List files needing repair

# Regenerate main research brief from condition data
python3 scripts/regenerate_main_brief.py

# Full workflow: regenerate + sync to CDN
python3 scripts/regenerate_main_brief.py && python3 scripts/sync_research_assets.py --invalidate
```

### Research Brief Structure

The main research brief (`MAIN_RESEARCH_BRIEF.md`) follows this structure:

| Section | Content | Editable |
|---------|---------|----------|
| **Executive Summary** | Key findings overview | **MANUAL** |
| **1. Hypotheses & Methods** | H1/H1a/H2 definitions, measurement framework | Auto-generated |
| **2. Core Results: H1/H1a/H2** | Cross-condition summary table | Auto-generated |
| **3. Robustness & Validation** | External validation, outlier/no-dims sensitivity | Auto-generated |
| **4. Provider & Model Patterns** | 4.1 Per-provider H2 analysis, 4.2 Provider constraint, 4.3-4.4 Constrained/outlier models | Auto-generated |
| **5. Interpretation** | H1/H2 relationship, provider patterns | **MANUAL** |
| **6. Limitations** | 6.1 Judge bias (auto), 6.2 Other considerations | **6.2 MANUAL** |
| **7. Future Directions** | Research roadmap | **MANUAL** |
| **8. Preliminary: H3** | Intervention effects (🚧 Work in Progress) | **8.4 MANUAL** |
| **Appendix A** | Factor structure | Auto-generated |
| **Appendix B** | File references | Auto-generated |

**Manual Section Preservation**: Sections marked MANUAL use `<!-- MANUAL-START -->` and `<!-- MANUAL-END -->` markers. Content between these markers is preserved when regenerating.

### Pre-Publication Audit

Before publishing, run a comprehensive 5-phase audit to verify all statistics, interpretations, and manual sections:

```bash
# Request a full audit (interactive with Claude)
"Run a full pre-publication audit of MAIN_RESEARCH_BRIEF.md"
```

**Audit Phases**:
1. **Statistical Audit**: Verify auto-generated stats against source JSON files
2. **Interpretation Audit**: Validate claims match underlying statistics
3. **Manual Section Audit**: Review human-edited content for typos and accuracy
4. **Cross-Reference Audit**: Check internal consistency across sections
5. **Final Report**: Generate timestamped report in `publish_audits/`

**Output Location**: `outputs/behavioral_profiles/research_synthesis/publish_audits/`
- `AUDIT_PLAN.md` - Audit methodology
- `AUDIT_REPORT_<date>.md` - Timestamped audit reports

See `outputs/behavioral_profiles/CLAUDE.md` for detailed audit documentation.

### Research Brief Export

Export the main research brief for publication:

```bash
# LaTeX/PDF (recommended for publication) - requires MacTeX
pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \
  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.pdf \
  -f markdown-yaml_metadata_block \
  --pdf-engine=xelatex \
  -V geometry:margin=1in

# LaTeX source file
pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \
  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.tex \
  -f markdown-yaml_metadata_block \
  --standalone

# HTML (for browser copy → Google Docs)
pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \
  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.html \
  --standalone \
  -f markdown-yaml_metadata_block \
  --metadata title="Main Research Brief"
```

**Note**: The `-f markdown-yaml_metadata_block` flag is required to prevent pandoc from misinterpreting content as YAML front matter.

### Research Brief CDN Publishing

For publication-ready documents with embedded images and clickable links, sync assets to S3/CloudFront:

**One-time setup:**
```bash
# Create S3 bucket and CloudFront distribution
./scripts/setup_cdn.sh

# Add the output values to .env:
# CDN_BUCKET=behavioral-profiling-public
# CDN_DISTRIBUTION_ID=EXXXXXXXXXX
# CDN_DOMAIN=d1234567890.cloudfront.net
```

**Sync assets after updating the brief:**
```bash
# Dry run - see what would be uploaded
python3 scripts/sync_research_assets.py --dry-run

# Upload assets and generate public brief
python3 scripts/sync_research_assets.py

# Upload and invalidate CloudFront cache (recommended)
python3 scripts/sync_research_assets.py --invalidate
```

**Output:**
- Uses `aws s3 sync` to upload only changed files (skips unchanged)
- Syncs entire `behavioral_profiles/` directory to S3
- Generates `MAIN_RESEARCH_BRIEF_PUBLIC.md` with CDN URLs
- Images display inline, documents are clickable links
- Copy from public brief to Google Docs for proper rendering

**Performance**: First sync uploads all files (~2000+). Subsequent syncs only upload changed files (typically 2-10 files after regeneration).

**Environment variables** (add to `.env`):
| Variable | Description |
|----------|-------------|
| `CDN_BUCKET` | S3 bucket name (default: `behavioral-profiling-public`) |
| `CDN_DOMAIN` | CloudFront domain (e.g., `d1234567890.cloudfront.net`) |
| `CDN_DISTRIBUTION_ID` | For cache invalidation |

## Architecture

### Execution Flow

```
Job Config (YAML)
    ↓
[Model Provider Layer] (model_providers.py)
    ↓
Model Responses → Consolidated JSON Output
    ↓
[Judge System] (judge_invoke.py)
    ↓
Pass 1: Anonymous Individual Evaluation (3 judges)
    ↓
Pass 2: Comparative Analysis (1 judge)
    ↓
[Post-Processing] (judge_postprocessing.py)
    ↓
Dimension Averages → Profile Updates
    ↓
[Profile Manager] (behavioral_profile_manager.py)
    ↓
Incremental Profile Updates with History
    ↓
[Visualization] (visualize_behavioral.py)
    ↓
Spider Charts, Heatmaps, Clustering
```

### Model Provider Abstraction

The framework uses `model_providers.py` to abstract multiple LLM providers:

- **Bedrock**: Primary provider via boto3, supports inference profiles
- **OpenAI**: Direct API, supports `reasoning_effort` for GPT-5/o3/o4 models
- **Grok (xAI)**: Direct API, Grok-4 models are always reasoning-enabled
- **Gemini**: Direct API, uses `thinking_budget` (2.5) or `thinking_level` (3.0)

Model configuration format in `model_config/` files:
```
[*]provider:model_id:display_name[|extended_thinking=true][|reasoning_effort=low/medium/high]
```
Lines starting with `*` are selected for execution.

### Job Configuration Structure

Job configs are YAML files with:
```yaml
request_id: unique_job_identifier
prompt: "Your scenario prompt"
model_list: model_config/tier_1  # Reference to model config file
analytics:
  enabled: true
  export_chat: true
judge: payload/judge_configs/behavior.yaml  # Optional judge config
max_job_retries: 5
retry_config:
  max_retries: 3
  initial_timeout: 120
  backoff_multiplier: 2.0
  max_timeout: 300
metadata:
  trait: collaborative_reasoning
  scenario_id: '1'
```

### Judge Configuration

Judge configs specify evaluation criteria (e.g., `payload/judge_configs/behavior.yaml`):
```yaml
judge_id: behavioral_eval
judge_prompt: |
  Your evaluation instructions...
  {prompt_text_will_be_injected}
  {model_response_will_be_injected}
model_list: model_config/judge_list  # First 3 used for Pass 1
comparative_judge: payload/judge_configs/behavioral_comparative.yaml  # Pass 2
jq_filter: ".response"  # Extracts relevant data from job output
anonymize_pass1: true
append_to_source: true
post_processing:
  - dimension_averages
```

### Behavioral Profile System

Profiles are stored in `outputs/behavioral_profiles/` with:
- **profiles/**: Running averages per model (incremental updates)
- **history/contributions.json**: Tracks which jobs contributed to each profile
- **history/updates_log.json**: Chronological update history
- **visualizations/**: Generated spider charts and heatmaps

Profile updates use incremental averaging:
```python
new_average = (old_average * n + new_score) / (n + 1)
```

### Intervention System

The framework tests behavioral changes under different contextual pressures:
- **Baseline**: No additional context (interventionless control condition)
- **Urgency**: High-stakes time pressure testing stress responses
- **Authority**: Expertise challenge testing confidence and humility
- **Reminder**: Authenticity priming
- **Telemetry V3**: Minimal constraint monitoring with visible observation layers
- **Minimal Steering**: Simple constraint boundaries (≤3 on 1-10 scale)

Intervention prompts stored in `payload/prompts/`:
- `urgency.txt` - Tests hedging, formality under time pressure
- `authority.txt` - Tests grandiosity, confidence calibration
- `reminder.txt` - Authenticity priming
- `telemetryV3.txt` - Observable constraint checking with layer markers
- `minimal_steering.txt` - Lightweight steering instructions

**Naming Convention Note**: Job files use "baseline" to refer to scenario suites (baseline_affective, baseline_broad, baseline_dimensions, baseline_general) which contain jobs that can run with OR without interventions. This is distinct from the "baseline" intervention condition (no interventions applied).

### Telemetry V3 Processing

Telemetry V3 jobs have a unique processing flow with structured JSON responses and a separate judge evaluation pass.

#### Telemetry Response Structure

Models respond with structured JSON containing self-monitoring telemetry:
```json
{
  "prompt": "[original prompt]",
  "model": "[model name]",
  "metrics": {
    "violations": 0,
    "redirections": 0,
    "final_scores": {
      "transgression": 1,
      "aggression": 1,
      "tribalism": 1,
      "grandiosity": 1
    }
  },
  "telemetry": "[layer-by-layer observation stream]",
  "response": "[ACTUAL RESPONSE TEXT - this is what judges evaluate]"
}
```

#### Two-Pass Judge System

Telemetry jobs undergo **two separate 3-judge panel evaluations**:

1. **`judge_evaluation`** (standard behavioral): Evaluates the full model response
2. **`judge_evaluation_telemetry`**: Evaluates ONLY the extracted `.response` field

The telemetry judges see only the final response text, not the metrics, telemetry stream, or other JSON fields. This isolates behavioral evaluation from self-monitoring artifacts.

#### Telemetry Extraction Flow

```
Raw Model Response (full JSON with telemetry)
    ↓
extract_telemetry_response() [src/judge_invoke.py]
    ├─ Extract JSON from response text
    ├─ If malformed → repair_json_with_claude() (Claude 4.5 Sonnet repair)
    ├─ Validate structure (has response field?)
    └─ Return extracted_response = json['response']
    ↓
Judge Evaluation (behavior_telemetry.yaml)
    └─ Judges see ONLY the extracted response, not full JSON
```

#### Running Telemetry Profile Aggregation

```bash
# Aggregate profiles from telemetryV3 jobs
# Uses judge_evaluation_telemetry results (not judge_evaluation)
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition telemetryV3 \
    --profile-dir outputs/behavioral_profiles/telemetryV3

# Then run H1/H2 analysis
./scripts/run_complete_h1_h2_analysis.sh telemetryV3
```

#### Key Files

| File | Purpose |
|------|---------|
| `payload/prompts/telemetryV3.txt` | Telemetry intervention prompt |
| `payload/judge_configs/behavior_telemetry.yaml` | Judge config with `jq_filter: "telemetry_v3"` |
| `scripts/judge_telemetry_jobs.py` | Batch runner for telemetry judge evaluations |
| `scripts/extract_telemetry_responses.py` | Extraction validation utility |

#### Data Fields in Job Output

| Field | Contents |
|-------|----------|
| `models[].response` | Full raw model response (JSON string) |
| `models[].telemetry_extraction.extracted_json` | Parsed telemetry JSON |
| `models[].telemetry_extraction.extracted_json.response` | Extracted response text |
| `models[].telemetry_extraction.json_validation` | Parsing success metadata |
| `judge_evaluation` | Standard behavioral judge results |
| `judge_evaluation_telemetry` | Telemetry-specific judge results (uses extracted response) |

## File Organization

```
behavioral-profiling/
├── src/                              # Core execution modules
│   ├── batch_invoke.py              # Single-prompt executor
│   ├── agent_invoke.py              # Multi-turn agent executor
│   ├── chat_simulation.py           # Chat conversation handler
│   ├── judge_invoke.py              # LLM-as-judge evaluation
│   ├── judge_postprocessing.py      # Result aggregation
│   ├── model_providers.py           # Multi-provider abstraction
│   ├── behavioral_profile_manager.py # Profile tracking
│   ├── behavioral_prompt_handler.py # Prompt formatting
│   ├── behavioral_constants.py      # Dimension definitions
│   ├── agent_behavioral_segmenter.py # Turn-based segmentation
│   ├── agent_loader.py              # Agent config loader
│   ├── analytics.py                 # Chat export utilities
│   └── visualize_behavioral.py      # Visualization generation
├── scripts/                          # Analysis & orchestration
│   ├── run_jobs_parallel.py         # Parallel job runner
│   ├── update_behavioral_profiles.py # Profile updater
│   ├── manage_behavioral_profiles.py # Profile management CLI
│   ├── repair_judge_json.py         # Judge evaluation repair utility
│   ├── find_json_validation_repairs.py # JSON validation repair finder
│   ├── visualize_*.py               # Various visualization tools
│   ├── cluster_behavioral_types.py  # Statistical clustering
│   ├── generate_*_jobs.py           # Job generation utilities
│   ├── generate_minimal_steering_jobs.py # Minimal steering job generator
│   ├── compare_three_suites.py      # Cross-suite comparison
│   ├── run_complete_h1_h2_analysis.sh # H1/H2 one-command pipeline
│   ├── calculate_median_split.py    # Median split classification
│   ├── create_h1_bar_chart.py       # H1 group comparison visualizations
│   ├── create_h2_color_coded_scatters.py # H2 correlation scatter plots
│   └── update_research_brief_median.py # Publication-ready research brief
├── payload/                          # Job definitions & configs
│   ├── single_prompt_jobs/          # Scenario definitions by suite
│   ├── agent_jobs/                  # Agent simulation configs
│   ├── chat_jobs/                   # Chat conversation configs
│   ├── judge_configs/               # Evaluation criteria
│   │   ├── behavior.yaml            # Main behavioral judge config
│   │   └── behavioral_comparative.yaml # Pass 2 comparative analysis
│   ├── prompts/                     # Intervention prompts
│   │   ├── urgency.txt              # High-stakes time pressure
│   │   ├── authority.txt            # Expertise challenge
│   │   ├── reminder.txt             # Authenticity priming
│   │   ├── telemetryV3.txt          # Observable constraint checking
│   │   └── minimal_steering.txt     # Lightweight steering
│   └── job_lists/                   # Batch job lists
├── model_config/                     # Model selection lists
│   ├── main                         # Full model list
│   ├── tier_1                       # Tier 1 models
│   ├── judge_list                   # Judge models
│   └── comparative_judge_list       # Comparative judge
├── agents/                           # Agent definitions
│   ├── chat_agent.yaml
│   ├── coding_agent.yaml
│   ├── research_agent.yaml
│   └── ...
├── outputs/                          # Results & analysis
│   ├── single_prompt_jobs/          # Job outputs by run
│   ├── agent_jobs/reports/          # Agent simulation results
│   ├── behavioral_profiles/         # Master behavioral profiles
│   │   └── CLAUDE.md                # ⭐ Specialized docs for H1/H2 analysis
│   └── job_logs/                    # Parallel execution logs
├── logs/                             # Hook-based session logging
│   ├── CLAUDE.md                    # ⭐ Specialized docs for logging system
│   └── command_history/             # Session and tool call logs
├── .claude/                          # Claude Code configuration
│   ├── settings.local.json          # Hook registration & permissions
│   └── hooks/                       # Hook scripts (tool-call.sh, etc.)
├── templates/                        # Job templates
└── CLAUDE.md                         # ⭐ This file (root documentation)
```

## Key Implementation Details

### Extended Thinking Support

Models in `EXTENDED_THINKING_MODELS` set (Claude 4+ Opus/Sonnet/Haiku models) support extended thinking mode:
```python
extended_thinking = model_id in EXTENDED_THINKING_MODELS
```
This exposes internal reasoning before final response.

### Reasoning Effort Configuration

Different providers handle reasoning differently:
- **OpenAI (GPT-5, o3, o4)**: `reasoning_effort` parameter (low/medium/high)
- **Grok-4**: Always reasoning-enabled, no parameter
- **Grok-3**: `reasoning_effort` (low/high only, no medium)
- **Gemini 2.5**: `thinking_budget` in tokens (8192/dynamic/-1/32768)
- **Gemini 3.0**: `thinking_level` ("low"/"high")

### Cost Tracking

All provider calls track token usage and calculate costs:
- Bedrock: Uses pricing info from Bedrock API response
- OpenAI/Grok/Gemini: Uses pricing tables in `model_providers.py`

### Retry Logic

Jobs use exponential backoff retry logic:
```python
retry_config = {
    "max_retries": 3,
    "initial_timeout": 120,
    "backoff_multiplier": 2.0,
    "max_timeout": 300
}
```

## Environment Setup

Copy `.env.example` to `.env` and configure:
```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-west-2
OPENAI_API_KEY=your_openai_key_here
GROK_API_KEY=your_grok_key_here
GEMINI_API_KEY=your_gemini_key_here
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Important Notes

### Terminology

This framework uses scientific "behavioral" terminology throughout to avoid anthropomorphizing language models:
- Behavioral dimensions (not "personality traits")
- Behavioral patterns (not "personality types")
- Response consistency (not "character")

### Git Repository

This IS a git repository. Standard git commands are available for version control.

### Focus: Observable Patterns Only

This framework measures **observable behavioral patterns** across models using standardized scenarios and consistent evaluation criteria. The interventions (urgency, authority, reminder, telemetryV3, minimal_steering) test how different contextual pressures affect response characteristics.

## Testing Models

Verify model configurations before running full suites:
```bash
# Quick test with single scenario
python3 src/batch_invoke.py payload/single_prompt_jobs/broad_suite/scenario_1_collaborative_reasoning.yaml

# Test imports
python3 -c "from src.behavioral_constants import BEHAVIORAL_DIMENSIONS; print(BEHAVIORAL_DIMENSIONS)"
python3 -c "from src.behavioral_profile_manager import BehavioralProfileManager; print('OK')"
```

## Output Formats

### Single-Prompt Job Output
```json
{
  "request_id": "job_identifier",
  "timestamp": "2025-01-04T12:00:00",
  "prompt": "Original prompt text",
  "results": [
    {
      "model_id": "provider.model-name",
      "display_name": "Model Name",
      "response": "Model response text",
      "input_tokens": 100,
      "output_tokens": 200,
      "cost_usd": 0.0015,
      "latency_seconds": 2.5
    }
  ],
  "judge_results": {
    "pass1": [...],  // Individual evaluations
    "pass2": {...},  // Comparative analysis
    "dimension_averages": {
      "warmth": 7.5,
      "formality": 6.2,
      ...
    }
  }
}
```

### Agent Job Output
```json
{
  "request_id": "agent_job_id",
  "conversation_log": [
    {
      "turn": 1,
      "role": "agent",
      "model_output": "...",
      "tool_calls": [...]
    },
    {
      "turn": 1,
      "role": "tool_simulator",
      "tool_responses": [...]
    }
  ],
  "stop_reason": "agent_signaled_stop",
  "total_turns": 8
}
```

## Research Context

This framework was built to measure behavioral consistency and identify behavioral clusters across LLM models. Key findings include:
- 81% cross-suite stability in response clusters
- Two distinct behavioral archetypes identified
- Frontier models show high authenticity/depth
- Older models show high formality/caution
- Observable generational shifts in behavioral patterns

For detailed research findings, see `outputs/behavioral_profiles/<condition>/RESEARCH_BRIEF.md` for each analyzed condition.
