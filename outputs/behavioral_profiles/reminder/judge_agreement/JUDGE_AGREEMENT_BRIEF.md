# Judge Agreement Analysis: Reminder

**Generated**: 2026-01-24
**Condition**: reminder

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 659 |
| Models | 45 |
| Unique Prompts | 15 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 14/15 |
| **Overall ICC(3)** | **0.830** (Good) |
| Mean Absolute Diff | 1.02 |
| Within-1 Agreement | 58.2% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 659 | 0.840 | 0.775 | **0.912** | 0.90 | 69.0% | Excellent |
| formality | 659 | 0.658 | 0.323 | **0.589** | 1.65 | 27.8% | Moderate |
| hedging | 659 | 0.727 | 0.640 | **0.842** | 1.49 | 29.0% | Good |
| aggression | 659 | 0.875 | 0.864 | **0.950** | 0.52 | 89.1% | Excellent |
| transgression | 659 | 0.764 | 0.725 | **0.887** | 0.82 | 75.9% | Good |
| grandiosity | 659 | 0.680 | 0.598 | **0.817** | 0.87 | 68.1% | Good |
| tribalism | 659 | 0.722 | 0.687 | **0.868** | 0.34 | 85.7% | Good |
| depth | 659 | 0.748 | 0.502 | **0.751** | 1.37 | 35.5% | Good |
| authenticity | 659 | 0.779 | 0.654 | **0.850** | 1.25 | 43.9% | Good |
| **OVERALL** | — | 0.755 | 0.641 | **0.830** | 1.02 | 58.2% | Good |

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
