# Judge Agreement Analysis: Authority

**Generated**: 2026-01-19
**Condition**: authority

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,261 |
| Models | 45 |
| Unique Prompts | 51 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 50/51 |
| **Overall ICC(3)** | **0.765** (Good) |
| Mean Absolute Diff | 0.93 |
| Within-1 Agreement | 63.1% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,261 | 0.700 | 0.486 | **0.740** | 1.55 | 34.3% | Moderate |
| formality | 2,261 | 0.637 | 0.414 | **0.680** | 1.14 | 54.8% | Moderate |
| hedging | 2,261 | 0.796 | 0.700 | **0.875** | 1.17 | 53.7% | Good |
| aggression | 2,261 | 0.742 | 0.714 | **0.882** | 0.39 | 93.5% | Good |
| transgression | 2,261 | 0.608 | 0.546 | **0.783** | 0.66 | 79.7% | Good |
| grandiosity | 2,261 | 0.458 | 0.319 | **0.585** | 0.73 | 72.0% | Moderate |
| tribalism | 2,261 | 0.538 | 0.530 | **0.772** | 0.17 | 94.1% | Good |
| depth | 2,261 | 0.743 | 0.585 | **0.808** | 1.14 | 50.7% | Good |
| authenticity | 2,261 | 0.640 | 0.521 | **0.765** | 1.42 | 34.8% | Good |
| **OVERALL** | — | 0.651 | 0.535 | **0.765** | 0.93 | 63.1% | Good |

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
