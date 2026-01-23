# Judge Agreement Analysis: Reminder

**Generated**: 2026-01-19
**Condition**: reminder

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 674 |
| Models | 46 |
| Unique Prompts | 15 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 14/15 |
| **Overall ICC(3)** | **0.827** (Good) |
| Mean Absolute Diff | 1.05 |
| Within-1 Agreement | 57.7% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 674 | 0.818 | 0.768 | **0.908** | 0.94 | 67.8% | Excellent |
| formality | 674 | 0.629 | 0.302 | **0.565** | 1.72 | 27.2% | Moderate |
| hedging | 674 | 0.728 | 0.644 | **0.844** | 1.50 | 28.3% | Good |
| aggression | 674 | 0.873 | 0.861 | **0.949** | 0.53 | 88.9% | Excellent |
| transgression | 674 | 0.762 | 0.724 | **0.887** | 0.82 | 75.8% | Good |
| grandiosity | 674 | 0.677 | 0.591 | **0.812** | 0.88 | 67.4% | Good |
| tribalism | 674 | 0.719 | 0.685 | **0.867** | 0.35 | 86.1% | Good |
| depth | 674 | 0.748 | 0.511 | **0.758** | 1.42 | 34.7% | Good |
| authenticity | 674 | 0.779 | 0.656 | **0.851** | 1.28 | 42.9% | Good |
| **OVERALL** | — | 0.748 | 0.638 | **0.827** | 1.05 | 57.7% | Good |

---

## ICC Interpretation

| ICC Value | Interpretation |
|-----------|----------------|
| > 0.90 | Excellent |
| 0.75-0.90 | Good |
| 0.50-0.75 | Moderate |
| < 0.50 | Poor |

---

## Data Provenance

**Source**: Job files from `outputs/single_prompt_jobs/`
**Audit File**: `judge_agreement_audit.json`
