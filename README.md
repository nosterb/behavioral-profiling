# Behavioral Profiling Framework

Measuring the relationship between model sophistication and behavioral disinhibition across 50+ LLMs.

## Research Summary

This framework investigates the **sophistication-disinhibition relationship** in language models:

- **Sophistication** (depth + authenticity): Proxy for model capability
- **Disinhibition** (transgression, aggression, tribalism, grandiosity): Boundary-pushing behavior

### Key Findings

| Finding | Evidence |
|---------|----------|
| **H1: Two distinct groups exist** | d = 3.09-4.25 separation across 6 conditions |
| **H2: Sophistication predicts disinhibition** | r = 0.46-0.74, all p < .001 |
| **External validity** | ARC-AGI r = 0.80, GPQA r = 0.88 |
| **76% classification stability** | 35/46 models stable across interventions |
| **Provider constraint differences** | OpenAI soph/dis ratio 4.21 vs Anthropic 3.75 |

### Notable Patterns

- **OpenAI**: Top 5 constrained models (high capability, suppressed disinhibition)
- **Gemini-3-Pro-Preview**: Consistent 4+ SD disinhibition outlier despite top benchmarks
- **Transitional class**: 10 models (22%) flip classification based on context

## Framework Overview

9-dimensional behavioral assessment across standardized scenarios with LLM-as-judge evaluation.

### Dimensions

**Sophistication Composite:**
- Depth [1=platitudes, 10=substantive]
- Authenticity [1=templated, 10=distinctive]

**Disinhibition Composite:**
- Transgression [1=safe, 10=norm-violating]
- Aggression [1=gentle, 10=combative]
- Tribalism [1=neutral, 10=us-vs-them]
- Grandiosity [1=humble, 10=superior]

**Other Dimensions:** Warmth, Formality, Hedging

### Intervention Conditions

| Condition | Type | Effect |
|-----------|------|--------|
| baseline | Control | Reference point |
| authority | Pressure | Challenges expertise |
| urgency | Pressure | Time pressure, high stakes |
| reminder | Priming | Authenticity prompt |
| minimal_steering | Constraint | Direct behavioral targets |
| telemetryV3 | Constraint | Self-monitoring with layers |

## Quick Start

```bash
# Install
pip install -r requirements.txt
cp .env.example .env  # Add API keys

# Run single job
python3 src/batch_invoke.py payload/single_prompt_jobs/broad_suite/scenario_1.yaml

# Run full analysis pipeline
./scripts/run_complete_h1_h2_analysis.sh baseline

# Cross-provider comparisons
python3 scripts/analyze_provider_comparisons.py baseline
```

## Project Structure

```
behavioral-profiling/
├── src/                          # Core execution modules
├── scripts/                      # Analysis & orchestration
├── payload/
│   ├── single_prompt_jobs/       # 51 scenarios across 4 suites
│   ├── prompts/                  # Intervention prompts
│   └── judge_configs/            # 3-judge evaluation configs
├── model_config/                 # 50+ models, 9 providers
├── outputs/behavioral_profiles/
│   ├── baseline/                 # Per-condition analysis
│   ├── authority/
│   ├── ...
│   └── research_synthesis/       # Cross-condition comparisons
└── CLAUDE.md                     # Full documentation
```

## Methodology

### Evaluation Pipeline

```
Scenario → 50+ Models → 3-Judge Panel → Dimension Scores → Profile Aggregation
```

### Statistical Methods

- **H1a (Group Comparison)**: Independent t-test, Cohen's d
- **H2 (Correlation)**: Pearson r
- **Cross-condition**: Repeated-measures ANOVA, Greenhouse-Geisser correction
- **Sensitivity**: Outlier removal, no-dimensions suite exclusion

### Judge Panel

| Judge | Provider | Sophistication |
|-------|----------|----------------|
| Claude-4.5-Sonnet | Anthropic | High |
| Llama-4-Maverick-17B | Meta | Low |
| DeepSeek-R1 | DeepSeek | Low |

ICC(3) = 0.843 (good reliability)

## Key Outputs

| File | Description |
|------|-------------|
| `MAIN_RESEARCH_BRIEF.md` | Comprehensive statistical report |
| `h2_scatter_*.png` | Correlation visualizations |
| `median_split_classification.json` | Model classifications |
| `all_models_data.csv` | Full dataset for external analysis |

## Documentation

- **Full docs**: `CLAUDE.md` (root)
- **Output docs**: `outputs/behavioral_profiles/CLAUDE.md`
- **Research brief**: `outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md`

## Models Tested

50+ models across 9 providers:
- **Anthropic**: Claude 3.x, 4.x, 4.5
- **OpenAI**: GPT-3.5, 4, 4.1, 5, 5.1, 5.2, O3
- **Google**: Gemini 2.0, 2.5, 3.0
- **Meta**: Llama 3.x, 4
- **xAI**: Grok 3, 4
- **Others**: DeepSeek, Mistral, AWS Nova, Alibaba Qwen

## Citation

```bibtex
@software{behavioral_profiling_2026,
  title = {Behavioral Profiling: Sophistication-Disinhibition Relationships in LLMs},
  year = {2026},
  url = {https://github.com/yourusername/behavioral-profiling}
}
```
