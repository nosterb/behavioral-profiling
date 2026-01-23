# Judge Agreement Analysis: Minimal_Steering

**Generated**: 2026-01-19
**Condition**: minimal_steering

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | 2,317 |
| Models | 46 |
| Unique Prompts | 51 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Jobs Complete | 48/51 |
| **Overall ICC(3)** | **0.718** (Moderate) |
| Mean Absolute Diff | 0.96 |
| Within-1 Agreement | 60.3% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
| warmth | 2,317 | 0.792 | 0.749 | **0.899** | 1.06 | 59.8% | Good |
| formality | 2,317 | 0.574 | 0.314 | **0.578** | 1.42 | 36.4% | Moderate |
| hedging | 2,317 | 0.746 | 0.575 | **0.802** | 1.63 | 27.6% | Good |
| aggression | 2,317 | 0.702 | 0.667 | **0.857** | 0.25 | 97.0% | Good |
| transgression | 2,317 | 0.588 | 0.515 | **0.761** | 0.50 | 91.8% | Good |
| grandiosity | 2,317 | 0.419 | 0.158 | **0.360** | 0.78 | 78.1% | Poor |
| tribalism | 2,317 | 0.485 | 0.472 | **0.729** | 0.10 | 96.5% | Moderate |
| depth | 2,317 | 0.710 | 0.451 | **0.711** | 1.54 | 25.1% | Moderate |
| authenticity | 2,317 | 0.665 | 0.515 | **0.761** | 1.40 | 30.1% | Good |
| **OVERALL** | — | 0.631 | 0.491 | **0.718** | 0.96 | 60.3% | Moderate |

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
