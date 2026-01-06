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
python3 scripts/generate_behavioral_v2_jobs.py
python3 scripts/generate_intervention_jobs.py
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
- **Baseline**: No additional context
- **Urgency**: High-stakes time pressure testing stress responses
- **Authority**: Expertise challenge testing confidence and humility
- **Shake**: Competitive pressure priming
- **Reminder**: Authenticity priming

Intervention prompts stored in `payload/prompts/`:
- `urgency.txt` - Tests hedging, formality under time pressure
- `authority.txt` - Tests grandiosity, confidence calibration
- `urgency_authority.txt` - Combined dual stressors
- `shake.txt` - Competitive framing
- `reminder.txt` - Authenticity priming

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
│   ├── visualize_*.py               # Various visualization tools
│   ├── cluster_behavioral_types.py  # Statistical clustering
│   ├── generate_*_jobs.py           # Job generation utilities
│   └── compare_three_suites.py      # Cross-suite comparison
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

### Non-Git Repository

This is NOT a git repository. Do not attempt to use `git` commands. Use `mv` for file operations, not `git mv`.

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
