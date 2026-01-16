# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Behavioral profiling framework for measuring consistency in LLM responses across a 9-dimensional behavioral assessment system. Tests 50+ models from multiple providers (AWS Bedrock, OpenAI, Grok, Gemini) using standardized scenarios and LLM-as-judge evaluation.

## Specialized Documentation

**For detailed guidance, see these specialized files:**

| Path | Purpose |
|------|---------|
| `outputs/behavioral_profiles/CLAUDE.md` | **H1/H2 analysis**, statistical methods, cross-condition comparisons, research brief export |
| `payload/CLAUDE.md` | Job definitions, intervention prompts, judge configs |
| `logs/CLAUDE.md` | Hook-based logging system |

## Core Concepts

### 9 Behavioral Dimensions

Measured on a 1-10 scale (defined in `src/behavioral_constants.py`):

| Dimension | Scale |
|-----------|-------|
| Warmth | cold/clinical → warm/nurturing |
| Formality | casual/raw → professional/polished |
| Hedging | commits fully → qualifies everything |
| Aggression | supportive/gentle → combative/attacking |
| Transgression | conventional/safe → norm-violating/edgy |
| Grandiosity | humble/self-effacing → dominant/superior |
| Tribalism | neutral/ecumenical → us-vs-them |
| Depth | platitudes/surface → substantive/insightful |
| Authenticity | templated/generic → genuinely distinctive |

### Key Hypotheses

| Hypothesis | Description |
|------------|-------------|
| **H1** | Two distinct sophistication groups exist (median split) |
| **H1a** | High-sophistication models exhibit higher disinhibition |
| **H2** | Sophistication positively correlates with disinhibition |

### Intervention Conditions

- **baseline** — No intervention (control)
- **authority** — Expertise challenge
- **urgency** — Time pressure
- **minimal_steering** — Simple constraint boundaries
- **telemetryV3** — Self-monitoring with telemetry
- **reminder** — Authenticity priming

## Quick Command Reference

### Running Jobs

```bash
# Single job
python3 src/batch_invoke.py payload/single_prompt_jobs/broad_suite/scenario_1.yaml

# Parallel batch
python3 scripts/run_jobs_parallel.py payload/job_lists/example.yaml --max-parallel 3

# Non-interactive
python3 scripts/run_jobs_parallel.py payload/job_lists/example.yaml --skip-behavioral-prompts
```

### Profile Aggregation

```bash
# Aggregate profiles for a condition
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition <condition> \
    --profile-dir outputs/behavioral_profiles/<condition>
```

### H1/H2 Analysis Pipeline

```bash
# Complete analysis pipeline (see behavioral_profiles/CLAUDE.md for details)
./scripts/run_complete_h1_h2_analysis.sh <condition>
```

### Visualization

```bash
# Visualize behavioral profiles
python3 scripts/visualize_all_behavioral.py outputs/single_prompt_jobs/run_*/

# Aggregate all conditions
python3 scripts/aggregate_all_conditions.py
```

### Judge Evaluation

```bash
python3 src/judge_invoke.py outputs/single_prompt_jobs/job_*.json
```

### Research Brief

```bash
# Regenerate + publish
python3 scripts/regenerate_main_brief.py && python3 scripts/sync_research_assets.py --invalidate
```

## Architecture

### Execution Flow

```
Job Config (YAML) → Model Providers → Model Responses
    → Judge System (Pass 1: Individual, Pass 2: Comparative)
    → Post-Processing → Profile Manager → Visualizations
```

### Model Provider Abstraction

`model_providers.py` abstracts multiple providers:
- **Bedrock**: Primary provider via boto3
- **OpenAI**: Direct API, `reasoning_effort` for GPT-5/o3/o4
- **Grok**: Direct API, Grok-4 always reasoning-enabled
- **Gemini**: Direct API, `thinking_budget` (2.5) or `thinking_level` (3.0)

Model config format: `[*]provider:model_id:display_name[|extended_thinking=true][|reasoning_effort=low/medium/high]`

### Three-Pass Evaluation

1. **Model Response**: Target models respond to scenario
2. **Individual Judging**: 3 judges evaluate each response (anonymized)
3. **Comparative Analysis**: Final judge provides cross-model analysis

### Behavioral Profile System

Profiles stored in `outputs/behavioral_profiles/`:
- `profiles/` — Running averages per model
- `history/` — Contribution tracking
- `visualizations/` — Spider charts, heatmaps

Profile updates use incremental averaging: `new_avg = (old_avg * n + new_score) / (n + 1)`

## File Organization

```
behavioral-profiling/
├── src/                    # Core modules
│   ├── batch_invoke.py     # Single-prompt executor
│   ├── judge_invoke.py     # LLM-as-judge evaluation
│   ├── model_providers.py  # Multi-provider abstraction
│   ├── behavioral_profile_manager.py
│   └── behavioral_constants.py
├── scripts/                # Analysis & orchestration
│   ├── run_jobs_parallel.py
│   ├── run_complete_h1_h2_analysis.sh  # One-command pipeline
│   └── update_behavioral_profiles.py
├── payload/                # Job definitions (see payload/CLAUDE.md)
│   ├── single_prompt_jobs/
│   ├── judge_configs/
│   └── prompts/
├── model_config/           # Model selection lists
├── outputs/
│   ├── single_prompt_jobs/ # Job outputs
│   └── behavioral_profiles/ # Analysis outputs (see CLAUDE.md there)
└── logs/                   # Hook logs (see logs/CLAUDE.md)
```

## Environment Setup

Copy `.env.example` to `.env`:

```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-west-2
OPENAI_API_KEY=your_key
GROK_API_KEY=your_key
GEMINI_API_KEY=your_key
```

Install: `pip install -r requirements.txt`

## Key Implementation Details

### Extended Thinking

Claude 4+ models support extended thinking mode via `EXTENDED_THINKING_MODELS` set.

### Reasoning Effort by Provider

| Provider | Parameter |
|----------|-----------|
| OpenAI (GPT-5, o3, o4) | `reasoning_effort` (low/medium/high) |
| Grok-4 | Always reasoning-enabled |
| Gemini 2.5 | `thinking_budget` in tokens |
| Gemini 3.0 | `thinking_level` ("low"/"high") |

### Telemetry V3 Processing

TelemetryV3 jobs extract `.response` field from structured JSON for judge evaluation. Uses `judge_evaluation_telemetry` key (not `judge_evaluation`).

### Retry Logic

```python
retry_config = {"max_retries": 3, "initial_timeout": 120, "backoff_multiplier": 2.0, "max_timeout": 300}
```

## Important Notes

### Terminology

Uses scientific terminology to avoid anthropomorphizing:
- Behavioral dimensions (not "personality traits")
- Behavioral patterns (not "personality types")

### Git Repository

This IS a git repository. Standard git commands available.

### Focus

Measures **observable behavioral patterns** using standardized scenarios and consistent evaluation criteria.

## Testing

```bash
# Quick test
python3 src/batch_invoke.py payload/single_prompt_jobs/broad_suite/scenario_1_collaborative_reasoning.yaml

# Test imports
python3 -c "from src.behavioral_constants import BEHAVIORAL_DIMENSIONS; print(BEHAVIORAL_DIMENSIONS)"
```

## Research Context

Key findings:
- 81% cross-suite stability in response clusters
- Two distinct behavioral archetypes identified
- Frontier models show high authenticity/depth
- Older models show high formality/caution

For detailed findings, see `outputs/behavioral_profiles/<condition>/RESEARCH_BRIEF.md`.
