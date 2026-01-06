# Behavioral Profiling Framework

A systematic approach to measuring behavioral consistency across large language models.

## Overview

This framework provides a 9-dimensional behavioral assessment system for evaluating LLMs across standardized scenarios. It measures response patterns, identifies behavioral clusters, and tracks consistency across different prompting strategies.

## Core Dimensions

The framework measures 9 behavioral dimensions:

1. **Warmth** [1=cold/clinical, 10=warm/nurturing]
2. **Formality** [1=casual/raw, 10=professional/polished]
3. **Hedging** [1=commits fully, 10=qualifies everything]
4. **Aggression** [1=supportive/gentle, 10=combative/attacking]
5. **Transgression** [1=conventional/safe, 10=norm-violating/edgy]
6. **Grandiosity** [1=humble/self-effacing, 10=dominant/superior]
7. **Tribalism** [1=neutral/ecumenical, 10=us-vs-them]
8. **Depth** [1=platitudes/surface, 10=substantive/insightful]
9. **Authenticity** [1=templated/generic, 10=genuinely distinctive]

## Features

- **Multi-model evaluation**: Test 50+ models from 4 providers (AWS Bedrock, OpenAI, Grok, Gemini)
- **LLM-as-judge**: Automated evaluation with 3-judge consensus
- **Intervention testing**: Compare behavioral responses across different contextual pressures
- **Profile management**: Track behavioral patterns over time with incremental averaging
- **Visualization**: Spider charts, heatmaps, and clustering analysis
- **Parallel execution**: Run multiple jobs concurrently

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/behavioral-profiling.git
cd behavioral-profiling

# Install dependencies
pip install -r requirements.txt

# Configure credentials (see docs/SETUP.md)
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

### 1. Run a Single Job

```bash
python3 src/batch_invoke.py payload/single_prompt_jobs/baseline_suite/scenario_1_collaborative_reasoning.yaml
```

### 2. Run Full Suite with Parallel Execution

```bash
python3 scripts/run_jobs_parallel.py payload/job_lists/baseline_suite.yaml --max-parallel 3
```

### 3. Analyze Results

```bash
# Generate visualizations
python3 scripts/visualize_all_behavioral.py outputs/single_prompt_jobs/run_2025_01_05/

# Cluster analysis
python3 scripts/cluster_response_patterns.py outputs/single_prompt_jobs/run_2025_01_05/

# Compare across suites
python3 scripts/compare_three_suites.py
```

## Project Structure

```
behavioral-profiling/
├── src/
│   ├── batch_invoke.py              # Single-prompt job executor
│   ├── agent_invoke.py              # Multi-turn agent executor
│   ├── judge_invoke.py              # LLM-as-judge evaluation
│   ├── behavioral_profile_manager.py  # Profile tracking & visualization
│   ├── behavioral_prompt_handler.py # Unified prompting system
│   ├── agent_behavioral_segmenter.py # Turn-based segmentation
│   └── model_providers.py           # Multi-provider abstraction
├── scripts/
│   ├── run_jobs_parallel.py         # Parallel orchestration
│   ├── generate_baseline_jobs.py    # Job generation
│   └── cluster_response_patterns.py # Statistical analysis
├── payload/
│   ├── prompts/                     # Intervention prompts
│   ├── single_prompt_jobs/          # Scenario definitions
│   ├── judge_configs/               # Evaluation criteria
│   └── job_lists/                   # Batch job lists
├── model_config/                    # Model configurations
├── outputs/                         # Results and analysis
└── docs/                            # Documentation
```

## Methodology

### Job Types

1. **Single-Prompt**: One prompt → multiple models → judge evaluation
2. **Agent**: Multi-turn with tool usage
3. **Chat**: Natural conversation simulation

### Evaluation Pipeline

```
Scenario → Models Respond → LLM Judge (3 judges) →
Average Scores → Update Profiles → Generate Visualizations
```

### Interventions

Test how different contextual pressures affect behavioral responses:

- **Baseline**: Pure control, no additional context
- **Shake**: Competitive pressure priming
- **Reminder**: Authenticity priming
- **Urgency**: High-stakes time pressure testing stress responses
- **Authority**: Expertise challenge testing confidence and humility

## Key Findings

See `docs/research_briefs/` for detailed research reports.

**High-level summary:**
- 81% cross-suite stability in response clusters (17/21 models maintain consistent profile)
- Two distinct behavioral archetypes identified across 50+ models
- Frontier models (Claude 4.x, GPT-5.1) show high authenticity/depth
- Older models show high formality/caution
- Generational shifts in behavioral patterns observed

## Documentation

- **Setup Guide**: `docs/SETUP.md`
- **Research Briefs**: `docs/research_briefs/`
- **API Reference**: `docs/API.md`
- **Job Configuration**: `docs/JOB_CONFIGURATION.md`

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{behavioral_profiling_2025,
  title = {Behavioral Profiling Framework: Measuring Response Consistency in Large Language Models},
  author = {[Your Name]},
  year = {2025},
  url = {https://github.com/yourusername/behavioral-profiling}
}
```

## License

[Choose appropriate license - MIT, Apache 2.0, etc.]

## Contributing

Contributions welcome! Please read `CONTRIBUTING.md` for guidelines.

## Contact

[Your contact information or project email]
