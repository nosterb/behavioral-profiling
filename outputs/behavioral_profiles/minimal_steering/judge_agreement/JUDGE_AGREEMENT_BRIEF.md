# Judge Agreement Analysis: Minimal_Steering

**Generated**: 2026-01-24
**Condition**: minimal_steering

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,266 |
| Models | 45 |
| Unique Prompts | 51 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 48/51 |
| **Overall ICC(3)** | **0.727** (Moderate) |
| Mean Absolute Diff | 0.94 |
| Within-1 Agreement | 61.0% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,266 | 0.807 | 0.747 | **0.899** | 1.02 | 60.9% | Good |
| formality | 2,266 | 0.586 | 0.307 | **0.571** | 1.35 | 37.2% | Moderate |
| hedging | 2,266 | 0.758 | 0.577 | **0.804** | 1.61 | 28.2% | Good |
| aggression | 2,266 | 0.727 | 0.698 | **0.874** | 0.24 | 97.7% | Good |
| transgression | 2,266 | 0.601 | 0.530 | **0.772** | 0.50 | 92.3% | Good |
| grandiosity | 2,266 | 0.430 | 0.174 | **0.387** | 0.76 | 79.3% | Poor |
| tribalism | 2,266 | 0.524 | 0.518 | **0.763** | 0.09 | 96.7% | Good |
| depth | 2,266 | 0.725 | 0.447 | **0.708** | 1.50 | 25.6% | Moderate |
| authenticity | 2,266 | 0.674 | 0.516 | **0.762** | 1.37 | 30.8% | Good |
| **OVERALL** | — | 0.648 | 0.501 | **0.727** | 0.94 | 61.0% | Moderate |

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
