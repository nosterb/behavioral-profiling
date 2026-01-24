# Judge Agreement Analysis: Telemetryv3

**Generated**: 2026-01-24
**Condition**: telemetryV3

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,053 |
| Models | 45 |
| Unique Prompts | 51 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 30/51 |
| **Overall ICC(3)** | **0.789** (Good) |
| Mean Absolute Diff | 0.93 |
| Within-1 Agreement | 62.0% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,053 | 0.804 | 0.756 | **0.903** | 1.10 | 54.8% | Excellent |
| formality | 2,053 | 0.603 | 0.423 | **0.688** | 1.22 | 46.7% | Moderate |
| hedging | 2,053 | 0.712 | 0.563 | **0.794** | 1.60 | 32.3% | Good |
| aggression | 2,053 | 0.697 | 0.672 | **0.860** | 0.30 | 95.2% | Good |
| transgression | 2,053 | 0.672 | 0.631 | **0.837** | 0.48 | 92.3% | Good |
| grandiosity | 2,053 | 0.543 | 0.383 | **0.651** | 0.67 | 83.3% | Moderate |
| tribalism | 2,053 | 0.590 | 0.587 | **0.810** | 0.12 | 95.3% | Good |
| depth | 2,053 | 0.759 | 0.544 | **0.782** | 1.49 | 26.3% | Good |
| authenticity | 2,053 | 0.686 | 0.544 | **0.781** | 1.37 | 32.0% | Good |
| **OVERALL** | — | 0.674 | 0.567 | **0.789** | 0.93 | 62.0% | Good |

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
