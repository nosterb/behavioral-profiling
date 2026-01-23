# Judge Agreement Analysis: Baseline

**Generated**: 2026-01-19
**Condition**: baseline

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,252 |
| Models | 46 |
| **Overall ICC(3)** | **0.808** (Good) |
| Mean Absolute Diff | 0.98 |
| Within-1 Agreement | 59.8% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,252 | 0.788 | 0.732 | **0.891** | 1.16 | 54.2% | Good |
| formality | 2,252 | 0.629 | 0.407 | **0.674** | 1.44 | 38.6% | Moderate |
| hedging | 2,252 | 0.731 | 0.621 | **0.831** | 1.48 | 35.0% | Good |
| aggression | 2,252 | 0.839 | 0.826 | **0.934** | 0.31 | 94.2% | Excellent |
| transgression | 2,252 | 0.689 | 0.662 | **0.854** | 0.58 | 87.3% | Good |
| grandiosity | 2,252 | 0.585 | 0.431 | **0.695** | 0.85 | 72.1% | Moderate |
| tribalism | 2,252 | 0.654 | 0.651 | **0.848** | 0.17 | 93.5% | Good |
| depth | 2,252 | 0.729 | 0.492 | **0.744** | 1.49 | 28.9% | Moderate |
| authenticity | 2,252 | 0.703 | 0.577 | **0.804** | 1.37 | 34.2% | Good |
| **OVERALL** | — | 0.705 | 0.600 | **0.808** | 0.98 | 59.8% | Good |

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
