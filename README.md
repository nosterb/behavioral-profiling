# Behavioral Profiling Framework

Investigating the relationship between model sophistication and behavioral disinhibition across 45 LLMs, 9 providers, and 8 experimental conditions.

## Key Findings

| Hypothesis | Result |
|------------|--------|
| **H1: Group Separation** | d = 3.09-4.25 (large effect) |
| **H1a: Disinhibition Difference** | d = 1.09-2.32, all p < .001 |
| **H2: Correlation** | r = 0.63-0.85, all p < .001 |
| **External Validity** | GPQA r = 0.88, ARC-AGI r = 0.80, AIME r = 0.83 |
| **BERT Toxicity** | r = 0.78 with aggression, r = 0.51-0.68 with sophistication |

## Constructs

**Sophistication** = (Depth + Authenticity) / 2 — proxy for reasoning capability
**Disinhibition** = mean(Transgression, Aggression, Tribalism, Grandiosity)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add API keys

# Run analysis pipeline
./scripts/run_complete_h1_h2_analysis.sh baseline
```

## Structure

```
behavioral-profiling/
├── src/                              # Core modules
├── scripts/                          # Analysis pipelines
├── payload/single_prompt_jobs/       # 51 scenarios
├── model_config/                     # 45 models, 9 providers
├── outputs/behavioral_profiles/
│   ├── <condition>/                  # Per-condition results
│   └── research_synthesis/           # Cross-condition analysis
│       └── MAIN_RESEARCH_BRIEF.md    # Full research report
└── CLAUDE.md                         # Complete documentation
```

## Statistics

- **Models**: 45 (Anthropic, OpenAI, Google, Meta, xAI, DeepSeek, Mistral, AWS, Alibaba)
- **Conditions**: 8 (baseline, authority, urgency, minimal_steering, telemetryV3, reminder, naturalistic, all_combined)
- **Evaluations**: 14,088 judge + 14,203 BERT
- **Judge Panel**: 3-judge (ICC = 0.843)

## Author

**Nicholas Osterbur** — Independent Researcher
[nosterb@gmail.com](mailto:nosterb@gmail.com) | [@nosterb](https://github.com/nosterb)

## License

Code: Apache 2.0 | Results & Analyses: CC BY 4.0
