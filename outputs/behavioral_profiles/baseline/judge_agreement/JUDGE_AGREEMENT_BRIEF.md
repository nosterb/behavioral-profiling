# Judge Agreement Analysis: Baseline

**Generated**: 2026-01-24
**Condition**: baseline

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,202 |
| Models | 45 |
| **Overall ICC(3)** | **0.813** (Good) |
| Mean Absolute Diff | 0.96 |
| Within-1 Agreement | 60.5% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,202 | 0.800 | 0.732 | **0.891** | 1.13 | 55.4% | Good |
| formality | 2,202 | 0.653 | 0.426 | **0.690** | 1.37 | 39.5% | Moderate |
| hedging | 2,202 | 0.745 | 0.630 | **0.837** | 1.45 | 35.8% | Good |
| aggression | 2,202 | 0.847 | 0.836 | **0.939** | 0.30 | 95.0% | Excellent |
| transgression | 2,202 | 0.694 | 0.667 | **0.857** | 0.58 | 87.7% | Good |
| grandiosity | 2,202 | 0.593 | 0.446 | **0.707** | 0.84 | 73.2% | Moderate |
| tribalism | 2,202 | 0.663 | 0.660 | **0.854** | 0.16 | 93.6% | Good |
| depth | 2,202 | 0.737 | 0.482 | **0.736** | 1.44 | 29.6% | Moderate |
| authenticity | 2,202 | 0.710 | 0.577 | **0.804** | 1.33 | 35.0% | Good |
| **OVERALL** | — | 0.716 | 0.606 | **0.813** | 0.96 | 60.5% | Good |

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
