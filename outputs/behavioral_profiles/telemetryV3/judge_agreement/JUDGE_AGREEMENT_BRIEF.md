# Judge Agreement Analysis: Telemetryv3

**Generated**: 2026-01-20
**Condition**: telemetryV3

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,094 |
| Models | 46 |
| Unique Prompts | 51 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 30/51 |
| **Overall ICC(3)** | **0.795** (Good) |
| Mean Absolute Diff | 0.93 |
| Within-1 Agreement | 62.1% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,094 | 0.805 | 0.764 | **0.906** | 1.10 | 55.1% | Excellent |
| formality | 2,094 | 0.619 | 0.446 | **0.707** | 1.26 | 45.8% | Moderate |
| hedging | 2,094 | 0.696 | 0.557 | **0.791** | 1.61 | 32.3% | Good |
| aggression | 2,094 | 0.692 | 0.666 | **0.857** | 0.30 | 95.1% | Good |
| transgression | 2,094 | 0.672 | 0.630 | **0.836** | 0.48 | 92.3% | Good |
| grandiosity | 2,094 | 0.543 | 0.384 | **0.651** | 0.66 | 83.3% | Moderate |
| tribalism | 2,094 | 0.589 | 0.586 | **0.809** | 0.12 | 95.4% | Good |
| depth | 2,094 | 0.772 | 0.573 | **0.801** | 1.48 | 27.2% | Good |
| authenticity | 2,094 | 0.696 | 0.561 | **0.793** | 1.36 | 32.8% | Good |
| **OVERALL** | — | 0.676 | 0.574 | **0.795** | 0.93 | 62.1% | Good |

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
