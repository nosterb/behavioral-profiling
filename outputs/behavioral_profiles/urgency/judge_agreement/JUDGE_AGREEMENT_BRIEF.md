# Judge Agreement Analysis: Urgency

**Generated**: 2026-01-19
**Condition**: urgency

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,259 |
| Models | 45 |
| Unique Prompts | 51 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 50/51 |
| **Overall ICC(3)** | **0.835** (Good) |
| Mean Absolute Diff | 1.09 |
| Within-1 Agreement | 54.5% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,259 | 0.789 | 0.726 | **0.888** | 1.19 | 50.8% | Good |
| formality | 2,259 | 0.634 | 0.428 | **0.692** | 1.30 | 47.9% | Moderate |
| hedging | 2,259 | 0.766 | 0.685 | **0.867** | 1.27 | 45.2% | Good |
| aggression | 2,259 | 0.841 | 0.819 | **0.931** | 0.80 | 71.5% | Excellent |
| transgression | 2,259 | 0.657 | 0.596 | **0.816** | 0.99 | 67.0% | Good |
| grandiosity | 2,259 | 0.718 | 0.675 | **0.862** | 1.15 | 50.0% | Good |
| tribalism | 2,259 | 0.696 | 0.685 | **0.867** | 0.35 | 85.5% | Good |
| depth | 2,259 | 0.707 | 0.505 | **0.754** | 1.44 | 34.2% | Good |
| authenticity | 2,259 | 0.676 | 0.629 | **0.836** | 1.33 | 38.2% | Good |
| **OVERALL** | — | 0.721 | 0.639 | **0.835** | 1.09 | 54.5% | Good |

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
