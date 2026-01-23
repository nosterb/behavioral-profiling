# Project Directory Map

**Last Updated**: 2026-01-23
**Purpose**: Comprehensive directory mapping for project handoff

---

## Quick Reference

| What You Want | Where To Find It |
|--------------|------------------|
| Main research findings | `outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md` |
| Run the analysis pipeline | `./scripts/run_complete_h1_h2_analysis.sh <condition>` |
| Add new models | Edit `model_config/all`, run jobs, aggregate profiles |
| Understand the codebase | Start with `CLAUDE.md` (root) |
| Cross-condition comparison | `outputs/behavioral_profiles/research_synthesis/cross_condition/CONDITION_COMPARISON.md` |

---

## Root Directory

```
behavioral-profiling/
├── CLAUDE.md                    # Main project documentation (read first)
├── DIRECTORY_MAP.md             # This file
├── requirements.txt             # Python dependencies
├── .env                         # API keys (not in git)
├── .env.example                 # Template for .env
│
├── src/                         # Core Python modules
├── scripts/                     # Analysis & orchestration scripts
├── payload/                     # Job definitions & prompts
├── model_config/                # Model selection lists
├── outputs/                     # All generated outputs
├── logs/                        # Hook-based logging
├── experiments/                 # Archived/experimental runs
└── venv/                        # Python virtual environment
```

---

## `src/` - Core Modules

| File | Purpose |
|------|---------|
| `batch_invoke.py` | Single-prompt job executor - sends prompts to models |
| `judge_invoke.py` | LLM-as-judge evaluation system |
| `model_providers.py` | Multi-provider abstraction (Bedrock, OpenAI, Grok, Gemini) |
| `behavioral_profile_manager.py` | Profile storage, averaging, visualization |
| `behavioral_constants.py` | 9 dimension definitions, scale anchors |

**Execution Flow**:
```
Job YAML → batch_invoke.py → Model Response → judge_invoke.py → Scores → Profile Manager
```

---

## `scripts/` - Analysis & Orchestration

### Primary Pipeline Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_complete_h1_h2_analysis.sh` | **One-command full pipeline** | `./scripts/run_complete_h1_h2_analysis.sh baseline` |
| `run_jobs_parallel.py` | Run multiple jobs concurrently | `python3 scripts/run_jobs_parallel.py payload/job_lists/example.yaml` |
| `update_behavioral_profiles.py` | Aggregate job results into profiles | `python3 scripts/update_behavioral_profiles.py outputs/single_prompt_jobs --recursive --condition baseline` |
| `regenerate_main_brief_v2.py` | Regenerate main research brief | `python3 scripts/regenerate_main_brief_v2.py` |

### H1/H2 Analysis Scripts

| Script | Purpose |
|--------|---------|
| `calculate_median_split.py` | Classify models into High/Low sophistication groups |
| `create_h1_bar_chart.py` | Generate H1a group comparison visualizations |
| `create_h2_color_coded_scatters.py` | Generate H2 correlation scatter plots |
| `analyze_outliers_removed.py` | Sensitivity analysis excluding outliers |
| `analyze_provider_comparisons.py` | Cross-provider ANOVA and pairwise tests |

### Specialized Analysis

| Script | Purpose |
|--------|---------|
| `extract_qualitative_examples.py` | Extract representative response examples |
| `create_no_dimensions_analysis.py` | No-dimensions sensitivity analysis |
| `analyze_factor_structure.py` | PCA/factor analysis of dimensions |
| `run_repeated_measures_anova.py` | Cross-condition repeated measures ANOVA |
| `check_judge_agreement.py` | Inter-rater reliability (3-judge panel) |

### Utility Scripts

| Script | Purpose |
|--------|---------|
| `export_chat.py` | Export job as markdown chat |
| `sync_research_assets.py` | Sync images to CDN for publication |
| `validate_condition_data.py` | Verify data integrity |
| `aggregate_all_conditions.py` | Aggregate root-level cross-condition profiles |

---

## `payload/` - Job Definitions

```
payload/
├── CLAUDE.md                    # Payload documentation
├── single_prompt_jobs/          # Job YAML definitions by suite
│   ├── broad_suite/             # Baseline broad scenarios
│   ├── dimensions_suite/        # Dimension-probing scenarios
│   ├── affective_suite/         # Emotional scenarios
│   ├── general_suite/           # General task scenarios
│   ├── naturalistic_suite/      # Real user-style prompts
│   ├── *_authority/             # Authority intervention variants
│   ├── *_urgency/               # Urgency intervention variants
│   ├── *_reminder/              # Reminder intervention variants
│   └── all_suites_*             # Combined suite variants
├── prompts/                     # Reusable prompt templates
├── judge_configs/               # Judge evaluation configurations
└── job_lists/                   # YAML lists for batch runs
```

### Job File Format (YAML)

```yaml
job_id: "job_broad_01"
prompt: "Your prompt here..."
models: ["model_config/all"]
judge_config: "payload/judge_configs/behavioral_9dim.yaml"
intervention: null  # or "authority", "urgency", etc.
```

---

## `model_config/` - Model Selection

| File | Contents |
|------|----------|
| `all` | Primary model list (46 models across 9 providers) |
| `anthropic_only` | Anthropic Claude models only |
| `frontier_models` | Latest frontier models |
| `quick_test` | Small subset for testing |

**Format**: One model per line
```
bedrock:us.anthropic.claude-3-5-sonnet-20241022-v2:0:Claude-3.5-Sonnet-v2
openai:gpt-4:GPT-4
```

---

## `outputs/` - Generated Outputs

### `outputs/single_prompt_jobs/`

Raw job outputs organized by job ID:
```
single_prompt_jobs/
├── job_broad_01_20260115_143022/
│   ├── job_broad_01_20260115_143022.json    # Main output file
│   └── visualizations/                       # Per-job visualizations
└── ...
```

**JSON Output Structure**:
```json
{
  "job_id": "job_broad_01",
  "prompt": "...",
  "model_responses": {...},
  "judge_evaluation": {
    "model_name": {
      "scores": {"warmth": 6.5, "formality": 7.2, ...},
      "reasoning": "..."
    }
  }
}
```

### `outputs/behavioral_profiles/`

**Main analysis directory** - See `outputs/behavioral_profiles/CLAUDE.md` for full details.

```
behavioral_profiles/
├── CLAUDE.md                    # Behavioral profiles documentation
├── profiles/                    # Cross-condition aggregate profiles
├── visualizations/              # Cross-condition visualizations
├── history/                     # Aggregation metadata
│
├── baseline/                    # Control condition (no intervention)
├── authority/                   # Authority challenge intervention
├── urgency/                     # Time pressure intervention
├── minimal_steering/            # Boundary constraint intervention
├── naturalistic/                # Real user-style prompts
├── reminder/                    # Authenticity priming intervention
├── telemetryV3/                 # Self-monitoring intervention
├── all_combined/                # All conditions aggregated
│
└── research_synthesis/          # Cross-condition research outputs
    ├── MAIN_RESEARCH_BRIEF.md   # Primary research document
    ├── cross_condition/         # Comparative analyses
    ├── bert_validation/         # External BERT toxicity validation
    └── limitations/             # Limitation analyses
```

### Per-Condition Directory Structure

Each condition directory (e.g., `baseline/`) contains:

| File/Dir | Purpose |
|----------|---------|
| `profiles/` | Individual model JSON profiles |
| `history/` | Contribution tracking, update logs |
| `visualizations/` | Spider charts per model |
| `median_split_classification.json` | H1/H2 classification data |
| `h1_bar_chart_comparison.png` | H1a group comparison |
| `h1_summary_table.png` | Statistical summary |
| `h2_scatter_sophistication_composite.png` | Main H2 scatter |
| `h2_scatter_all_dimensions.png` | Per-dimension H2 scatters |
| `provider_summary.png` | Provider analysis 4-panel |
| `provider_comparison_stats.json` | ANOVA results |
| `all_models_data.csv` | Complete dataset export |
| `RESEARCH_BRIEF.md` | Condition-specific findings |
| `PROMPTS.md` | All prompts used |
| `qualitative_examples.json` | Representative examples |
| `qualitative_chats/` | Example chat exports |
| `outliers_removed/` | Sensitivity analysis |

---

## `outputs/behavioral_profiles/research_synthesis/`

Cross-condition research synthesis:

```
research_synthesis/
├── MAIN_RESEARCH_BRIEF.md       # Primary publication document
├── MAIN_RESEARCH_BRIEF_PUBLIC.md # CDN URLs for images
│
├── cross_condition/
│   ├── CONDITION_COMPARISON.md   # Side-by-side metrics table
│   └── cross_condition_patterns.json
│
├── bert_validation/              # External BERT toxicity validation
│   ├── all_combined/
│   ├── baseline/
│   └── naturalistic/
│
├── limitations/
│   ├── judge_limitations/        # Inter-rater reliability
│   ├── external_evals/           # GPQA benchmark correlation
│   ├── factor_structure/         # PCA analysis
│   ├── median_split/             # Classification stability
│   └── provider_constraint/      # Provider-level patterns
│
├── publish_audits/               # Pre-publication audit reports
└── framework/                    # Statistical methodology
```

---

## Key Hypotheses Tested

| Hypothesis | Description | Key Metric |
|------------|-------------|------------|
| **H1** | Two distinct sophistication groups exist | Median split d > 2.0 |
| **H1a** | High-sophistication → higher disinhibition | Cohen's d for group difference |
| **H2** | Sophistication correlates with disinhibition | Pearson r |
| **H3** | Interventions modulate the relationship | Cross-condition comparison |

---

## 9 Behavioral Dimensions

| Dimension | Low (1) | High (10) |
|-----------|---------|-----------|
| **Warmth** | Cold, clinical | Warm, nurturing |
| **Formality** | Casual, raw | Professional, polished |
| **Hedging** | Commits fully | Qualifies everything |
| **Aggression** | Supportive, gentle | Combative, attacking |
| **Transgression** | Conventional, safe | Norm-violating, edgy |
| **Grandiosity** | Humble, self-effacing | Dominant, superior |
| **Tribalism** | Neutral, ecumenical | Us-vs-them |
| **Depth** | Platitudes, surface | Substantive, insightful |
| **Authenticity** | Templated, generic | Genuinely distinctive |

**Composites**:
- **Sophistication** = (Depth + Authenticity) / 2
- **Disinhibition** = (Transgression + Aggression + Tribalism + Grandiosity) / 4

---

## Common Workflows

### Run Full Analysis for a New Condition

```bash
# 1. Aggregate profiles
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition <condition> \
    --profile-dir outputs/behavioral_profiles/<condition>

# 2. Run H1/H2 pipeline
./scripts/run_complete_h1_h2_analysis.sh <condition>

# 3. Update cross-condition comparison
python3 scripts/update_cross_condition_comparison.py

# 4. Regenerate main brief
python3 scripts/regenerate_main_brief_v2.py
```

### Add New Models

1. Add model to `model_config/all`
2. Run jobs: `python3 scripts/run_jobs_parallel.py payload/job_lists/<list>.yaml`
3. Re-aggregate profiles for affected conditions
4. Re-run analysis pipeline

### Generate Qualitative Examples

```bash
python3 scripts/extract_qualitative_examples.py <condition> --force
```

---

## Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env with API keys:
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
#   OPENAI_API_KEY
#   GROK_API_KEY
#   GEMINI_API_KEY
```

---

## Key Statistics (Current State)

| Condition | Models | Evaluations | H1a d | H2 r |
|-----------|--------|-------------|-------|------|
| baseline | 45 | ~2,200 | 2.13 | 0.778 |
| all_combined | 46 | 13,984 | 2.30 | 0.815 |
| naturalistic | 44 | 2,241 | 2.09 | 0.841 |
| authority | 45 | ~2,200 | 1.84 | 0.770 |
| urgency | 45 | ~2,200 | 1.77 | 0.743 |
| minimal_steering | 45 | ~2,200 | 2.32 | 0.854 |
| reminder | 45 | ~2,200 | 1.65 | 0.720 |
| telemetryV3 | 45 | ~2,200 | 1.09 | 0.625 |

---

## Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Main CLAUDE.md | `CLAUDE.md` | Project overview, quick commands |
| Behavioral Profiles | `outputs/behavioral_profiles/CLAUDE.md` | H1/H2 analysis details |
| Payload | `payload/CLAUDE.md` | Job definitions, interventions |
| Logs | `logs/CLAUDE.md` | Hook-based logging |
| Reproducibility | `outputs/behavioral_profiles/REPRODUCIBILITY.md` | Full regeneration guide |

---

## Contact & Support

- Issues: https://github.com/anthropics/claude-code/issues
- Primary researcher: [Your contact info]
