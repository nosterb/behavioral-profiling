# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a behavioral profiling framework for measuring consistency in LLM responses across a 9-dimensional behavioral assessment system. The framework tests 50+ models from multiple providers (AWS Bedrock, OpenAI, Grok, Gemini) using standardized scenarios and automated LLM-as-judge evaluation.

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
```

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
./scripts/run_complete_h1_h2_analysis.sh affective
./scripts/run_complete_h1_h2_analysis.sh authority
./scripts/run_complete_h1_h2_analysis.sh urgency
```

**What it does**:
1. Checks prerequisites (profile directory exists, sufficient N ≥ 40)
2. Calculates median split classification (Stage 2)
3. Generates H1 visualizations (bar charts + statistical table)
4. Generates H2 scatter plots (composite + 4-dimension grid)
5. Generates publication-ready research brief
6. Reports key statistics and next steps

#### Prerequisites: Stage 1 - Profile Aggregation

Before running H1/H2 analysis, profiles must be aggregated:

```bash
# Aggregate profiles from job outputs
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_<intervention>_*.json \
    --profile-dir outputs/behavioral_profiles/<intervention>

# Example for affective intervention:
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_affective_*.json \
    --profile-dir outputs/behavioral_profiles/affective
```

#### Output Files

Each intervention generates **13 files** in `outputs/behavioral_profiles/<intervention>/`:

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

**Data Exports** (2 files):
- `all_models_data.csv` - Complete dataset (all models × all dimensions) for external analysis
- `COMPREHENSIVE_STATS_REPORT.txt` - Human-readable statistical summary with provider breakdowns

**Research Brief** (1 file):
- `RESEARCH_BRIEF.md` - Publication-ready research brief with comprehensive statistical reporting

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
```

#### Running Multiple Conditions Sequentially

```bash
# Process all conditions
for condition in baseline affective authority urgency; do
    echo "Processing: $condition"
    ./scripts/run_complete_h1_h2_analysis.sh $condition
    sleep 2
done
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

### Quality Assurance & Statistical Rigor

The research initiative maintains comprehensive quality control across all analysis phases.

#### Statistical QC Framework

**Location**: `outputs/behavioral_profiles/research_synthesis/STATISTICAL_QC_FRAMEWORK.md`

**Coverage**:
- Statistical methods standards for all phases (H1/H2, H3, Combined, Main)
- Validation checklists and acceptance criteria
- Audit protocols (automated and manual)
- Data integrity requirements
- Reproducibility standards
- Reporting standards (APA format)
- Troubleshooting decision trees

#### Key Quality Standards

**Statistical Rigor**:
- All effect sizes reported with 95% confidence intervals
- P-values reported with exact values (or p < .001)
- Assumptions verified and violations documented
- Alternative methods used when assumptions violated
- Multiple comparison corrections applied
- Sensitivity analyses for borderline cases

**Data Integrity**:
- All scores validated (range 1-10)
- No missing values (NaN/null checks)
- Contribution counts > 0
- Timestamps sequential and valid
- Profile checksums for critical data

**Reproducibility**:
- Deterministic pipeline (no randomness in core analyses)
- Fixed random seeds for bootstrap/permutation tests
- Software versions documented
- Consistent file ordering (sorted)
- All analysis scripts version controlled

**Audit Procedures**:
- Automated checks: Every analysis run
- Spot audits: After each new condition
- Full audits: After baseline, before cross-condition, before publication
- Audit logs maintained in `<condition>/audit/`

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
# [ ] Random seeds documented if applicable
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
python3 scripts/generate_behavioral_v2_jobs.py
python3 scripts/generate_intervention_jobs.py
python3 scripts/generate_minimal_steering_jobs.py

# Judge JSON repair (fixes malformed judge evaluations)
python3 scripts/repair_judge_json.py --flag-only              # Show flagged evaluations
python3 scripts/repair_judge_json.py                          # Repair with Claude 4.5
python3 scripts/find_json_validation_repairs.py              # Report on all repairs
python3 scripts/find_json_validation_repairs.py --needs-repair  # List files needing repair
```

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
- **Shake**: Competitive pressure priming
- **Reminder**: Authenticity priming
- **Telemetry V3**: Minimal constraint monitoring with visible observation layers
- **Minimal Steering**: Simple constraint boundaries (≤3 on 1-10 scale)

Intervention prompts stored in `payload/prompts/`:
- `urgency.txt` - Tests hedging, formality under time pressure
- `authority.txt` - Tests grandiosity, confidence calibration
- `urgency_authority.txt` - Combined dual stressors
- `shake.txt` - Competitive framing
- `reminder.txt` - Authenticity priming
- `telemetryV3.txt` - Observable constraint checking with layer markers
- `minimal_steering.txt` - Lightweight steering instructions

**Naming Convention Note**: Job files use "baseline" to refer to scenario suites (baseline_affective, baseline_broad, baseline_dimensions, baseline_general) which contain jobs that can run with OR without interventions. This is distinct from the "baseline" intervention condition (no interventions applied).

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
│   │   ├── urgency_authority.txt    # Combined stressors
│   │   ├── shake.txt                # Competitive pressure
│   │   └── reminder.txt             # Authenticity priming
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
│   └── job_logs/                    # Parallel execution logs
├── templates/                        # Job templates
└── docs/research_briefs/            # Research findings
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

This framework measures **observable behavioral patterns** across models using standardized scenarios and consistent evaluation criteria. The interventions (urgency, authority, shake, reminder) test how different contextual pressures affect response characteristics.

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

For detailed research findings, see `docs/research_briefs/behavioral_profiling_overview.md`.
