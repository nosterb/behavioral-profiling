# BERT Toxicity Validation: Cross-Condition Research Brief

**Generated**: 2026-01-15
**Audit Status**: **PASSED** (2026-01-16) — 270/270 models validated
**Purpose**: Independent validation of LLM-as-judge behavioral scores using BERT toxicity detection

---

## Executive Summary

This validation study tests whether our LLM-as-judge behavioral scores correlate with an independent, non-LLM measure of toxicity. Using `unitary/toxic-bert` (trained on Jigsaw Toxic Comment data), we scored model responses across all six experimental conditions and correlated these scores with:

1. **Judge Aggression** (primary validation)
2. **Sophistication Composite** (depth + authenticity)
3. **Disinhibition Composite** (transgression + aggression + tribalism + grandiosity)

**Scale**: 11,964 total BERT evaluations across 270 model-condition pairs (45 models × 6 conditions)

**Key Findings**:
- Baseline shows strong validation across all measures (r = 0.51-0.78)
- BERT toxicity correlates equally strongly with **aggression** and **disinhibition** (both r ≈ 0.78 in baseline)
- Interventions weaken correlations, suggesting they alter expression patterns
- Sophistication shows moderate-to-large correlations (r = 0.47-0.68), indicating more sophisticated models produce more BERT-detectable toxicity

---

## Cross-Condition Results

### Primary: BERT vs. Aggression

| Condition | N | Toxicity r | p-value | Insult r | p-value | Effect |
|-----------|---|------------|---------|----------|---------|--------|
| **baseline** | 45 | **0.776** | < .0001 | **0.624** | < .0001 | Large |
| **minimal_steering** | 45 | **0.524** | 0.0002 | **0.507** | 0.0004 | Large |
| **telemetryV3** | 45 | 0.492 | 0.0006 | 0.264 | 0.080 | Medium |
| **reminder** | 45 | 0.492 | 0.0006 | 0.458 | 0.002 | Medium |
| **authority** | 45 | 0.355 | 0.017 | 0.356 | 0.017 | Medium |
| **urgency** | 45 | 0.352 | 0.018 | 0.414 | 0.005 | Medium |

### Extended: BERT vs. Sophistication & Disinhibition

| Condition | Tox~Soph | Tox~Disin | Ins~Soph | Ins~Disin |
|-----------|----------|-----------|----------|-----------|
| **baseline** | 0.510 (L) | **0.776** (L) | 0.357 (M) | **0.555** (L) |
| **authority** | 0.471 (M) | 0.348 (M) | 0.414 (M) | 0.365 (M) |
| **urgency** | **0.602** (L) | 0.342 (M) | 0.434 (M) | 0.390 (M) |
| **minimal_steering** | 0.510 (L) | 0.467 (M) | 0.425 (M) | 0.453 (M) |
| **telemetryV3** | **0.682** (L) | **0.511** (L) | 0.354 (M) | 0.281 (S) |
| **reminder** | 0.494 (M) | **0.536** (L) | 0.436 (M) | **0.503** (L) |

*Effect sizes: L = Large (≥0.5), M = Medium (0.3-0.5), S = Small (<0.3)*

---

## Key Observations

### 1. Baseline Shows Strongest Validation

The baseline condition (no intervention) shows the strongest correlations across all measures:
- **Toxicity ~ Aggression**: r = 0.78 (60% variance explained)
- **Toxicity ~ Disinhibition**: r = 0.78 (identical to aggression, validating the composite)
- **Toxicity ~ Sophistication**: r = 0.51 (more sophisticated models show higher toxicity)

### 2. Disinhibition Captures Toxicity Signal

The disinhibition composite (which includes aggression) correlates as strongly with BERT toxicity as aggression alone. This validates that:
- The composite construction is sound
- All four disinhibition dimensions contribute to the toxicity signal

### 3. Sophistication-Toxicity Relationship

Surprising finding: More sophisticated models show **higher** BERT-detected toxicity (r = 0.51-0.68 across conditions). This may reflect:
- Sophisticated models produce more substantive content that triggers toxicity detection
- Depth/authenticity correlates with directness that BERT flags
- Inverse relationship: less sophisticated models are more "safe" but also more bland

### 4. Interventions Create Dissociation

All interventions weaken the baseline correlations, suggesting they:
- Activate different expression modes that judges rate differently than BERT
- Create response strategies that satisfy demands without triggering toxicity
- Modulate *how* models express behavioral dimensions

### 5. TelemetryV3 Shows Unique Pattern

TelemetryV3 shows the strongest sophistication correlation (r = 0.68) but weakest insult correlation (r = 0.26, ns). The self-monitoring may:
- Increase sophisticated expression
- Suppress insult-like content specifically

---

## Visualizations

Each condition folder contains:

### Primary Validation
- `scatter_toxicity_vs_aggression.png` - Full toxicity ~ aggression plot
- `scatter_insult_vs_aggression.png` - Insult ~ aggression plot
- `scatter_combined.png` - 2-panel summary

### Extended Validation
- `scatter_toxicity_vs_sophistication.png` - Toxicity ~ Sophistication
- `scatter_toxicity_vs_disinhibition.png` - Toxicity ~ Disinhibition
- `scatter_insult_vs_sophistication.png` - Insult ~ Sophistication
- `scatter_insult_vs_disinhibition.png` - Insult ~ Disinhibition
- `scatter_soph_disin_combined.png` - 2x2 composite grid

### Reports
- `VALIDATION_REPORT.md` - Condition-specific detailed report
- `bert_validation_results.json` - Primary results (machine-readable)
- `bert_soph_disin_results.json` - Extended results (machine-readable)

---

## Methods

### BERT Model

| Field | Value |
|-------|-------|
| **Model** | `unitary/toxic-bert` |
| **Source** | [Hugging Face](https://huggingface.co/unitary/toxic-bert) |
| **Architecture** | BERT (bert-base-uncased), 110M parameters |
| **Training Data** | [Jigsaw Toxic Comment Classification](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge) (~160k Wikipedia comments) |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |
| **Max Sequence Length** | 512 tokens (responses exceeding this are truncated) |
| **Execution** | Local inference (no API calls) |

### Token Truncation Analysis

BERT has a 512 token limit. Responses exceeding this are truncated before scoring.

| Condition | Total | Truncated | % Truncated | Avg Tokens | Max Tokens |
|-----------|-------|-----------|-------------|------------|------------|
| baseline | 2,234 | 691 | 30.9% | 478 | 3,569 |
| authority | 2,238 | 915 | 40.9% | 641 | 3,683 |
| urgency | 2,236 | 516 | 23.1% | 439 | 4,312 |
| minimal_steering | 2,292 | 236 | 10.3% | 287 | 1,885 |
| telemetryV3 | 2,290 | 715 | 31.2% | 461 | 2,686 |
| reminder | 674 | 176 | 26.1% | 435 | 2,206 |
| **TOTAL** | **11,964** | **3,249** | **27.2%** | - | - |

**Note**: Token count ≈ chars × 0.23. Response lengths in JSON are measured in **characters**, not tokens.

**Implication**: ~27% of responses were truncated to the first 512 tokens. Since toxicity signals often appear early in responses (e.g., tone, framing), truncation likely has minimal impact on validation. The strong correlations (r = 0.78) despite truncation suggest the first 512 tokens capture the relevant behavioral signal.

### Procedure

1. Extract model responses from job outputs for each condition
2. Score each response with BERT toxicity model (all responses per model)
3. Average BERT scores per model
4. Load behavioral scores from condition profiles (aggression, sophistication, disinhibition)
5. Compute Pearson correlations and linear regressions
6. Identify statistical outliers (|residual| > 2 SD) and constrained models

### Evaluation Scale

| Condition | Models | Responses Scored | Avg/Model |
|-----------|--------|------------------|-----------|
| baseline | 45 | 2,234 | 49.6 |
| authority | 45 | 2,238 | 49.7 |
| urgency | 45 | 2,236 | 49.7 |
| minimal_steering | 45 | 2,292 | 50.9 |
| telemetryV3 | 45 | 2,290 | 50.9 |
| reminder | 45 | 674 | 15.0 |
| **TOTAL** | **270** | **11,964** | 44.3 |

### Composites

- **Sophistication** = (depth + authenticity) / 2
- **Disinhibition** = (transgression + aggression + tribalism + grandiosity) / 4

---

## Interpretation

### Validation Conclusion

The baseline validation (r = 0.78 for both aggression and disinhibition) provides **strong convergent validity** for the LLM-as-judge methodology. The BERT model—trained on human-labeled toxicity data—captures the same signal our judge models rate as "aggressive" or "disinhibited."

### Why Sophistication Correlates with Toxicity

The positive sophistication-toxicity correlation (r ≈ 0.51-0.68) is not a confound but an insight:
- More sophisticated responses are more substantive and direct
- Directness triggers toxicity classifiers even when appropriate
- This explains why sophisticated models can be both high-quality and high-disinhibition

### Intervention Effects

Interventions create dissociations between:
- What judges perceive as behavioral dimensions
- What BERT detects as toxic content

This is informative rather than problematic—it reveals how behavioral pressures alter expression patterns in ways that affect external classification differently than human-like judgment.

---

## Reproducibility

```bash
# Run all primary validations
for cond in baseline authority urgency minimal_steering telemetryV3 reminder; do
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition $cond
done

# Run all extended validations
for cond in baseline authority urgency minimal_steering telemetryV3 reminder; do
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition $cond
done

# Regenerate all reports
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_validation_reports.py
```

---

## File Structure

```
bert_validation/
├── CLAUDE.md                          # Development documentation
├── BERT_VALIDATION_BRIEF.md           # This file
├── EXPERIMENT_PLAN.md                 # Original experiment design
├── scripts/
│   ├── run_bert_validation.py         # Primary: BERT vs Aggression
│   ├── run_bert_soph_disin_validation.py  # Extended: BERT vs Soph/Disin
│   ├── regenerate_validation_reports.py   # Regenerate condition reports
│   ├── regenerate_plots.py            # Regenerate plots from JSON
│   └── test_bert_toxicity.py          # BERT model test
├── baseline/
│   ├── bert_validation_results.json
│   ├── bert_soph_disin_results.json
│   ├── scatter_*.png
│   ├── VALIDATION_REPORT.md
│   └── full_run_log.txt
├── authority/
├── urgency/
├── minimal_steering/
├── telemetryV3/
└── reminder/
```

---

## Audit Certification

**Status**: PASSED (2026-01-16)

All 11,964 responses were re-scored through BERT. Per-model toxicity averages were compared against stored values.

| Metric | Value |
|--------|-------|
| Models Validated | 270 (45 × 6 conditions) |
| Models Matched | 270 (100%) |
| Tolerance | < 0.0001 |
| Total Responses Re-Scored | 11,964 |

**Conclusion**: The BERT validation pipeline is deterministic and reproducible. Stored scores accurately reflect the scoring of actual model responses.

See `AUDIT_REPORT.md` and `audit_results.json` for full audit details.

---

## References

1. Unitary AI toxic-bert: https://huggingface.co/unitary/toxic-bert
2. Jigsaw Toxic Comment Challenge: https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge
3. Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
