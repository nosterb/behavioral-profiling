# BERT Toxicity Validation Report

**Generated**: 2026-01-15
**Condition**: telemetryV3
**Experiment**: Independent validation of LLM-as-judge behavioral scores

---

## Executive Summary

| Metric | r | p | Effect | Interpretation |
|--------|---|---|--------|----------------|
| **Toxicity vs. Aggression** | 0.492 | 0.0006 | medium | Primary validation |
| **Insult vs. Aggression** | 0.264 | 0.0799 | small | Secondary validation |
| **Toxicity vs. Sophistication** | 0.682 | < .0001 | large | Composite validation |
| **Toxicity vs. Disinhibition** | 0.511 | 0.0003 | large | Composite validation |
| **Insult vs. Sophistication** | 0.455 | 0.0017 | medium | Composite validation |
| **Insult vs. Disinhibition** | 0.281 | 0.0617 | small | Composite validation |

**N = 45 models** | Outliers: 1 | Constrained: 0

---

## Visualizations

### Primary: BERT vs. Aggression

| Toxicity | Insult | Combined |
|----------|--------|----------|
| ![](scatter_toxicity_vs_aggression.png) | ![](scatter_insult_vs_aggression.png) | ![](scatter_combined.png) |

### Extended: BERT vs. Sophistication/Disinhibition

| Toxicity vs. Soph | Toxicity vs. Disin | Insult vs. Soph | Insult vs. Disin |
|-------------------|--------------------|-----------------|--------------------|
| ![](scatter_toxicity_vs_sophistication.png) | ![](scatter_toxicity_vs_disinhibition.png) | ![](scatter_insult_vs_sophistication.png) | ![](scatter_insult_vs_disinhibition.png) |

### Combined 2x2 Grid
![](scatter_soph_disin_combined.png)

---

## Statistical Details

### 1. BERT vs. Aggression (Primary)

| Measure | r | R² | p-value | Effect | Slope | Intercept |
|---------|---|----|---------|--------|-------|-----------|
| Toxicity | 0.4916 | 0.2416 | 6.05e-04 | medium | 0.005366 | -0.004015 |
| Insult | 0.2638 | 0.0696 | 7.99e-02 | small | 0.000248 | -0.000031 |

### 2. BERT vs. Sophistication/Disinhibition (Extended)

| Measure | r | R² | p-value | Effect |
|---------|---|----|---------|--------|
| Toxicity vs. Sophistication | 0.6818 | 0.4649 | 2.51e-07 | large |
| Toxicity vs. Disinhibition | 0.5113 | 0.2615 | 3.31e-04 | large |
| Insult vs. Sophistication | 0.4552 | 0.2072 | 1.68e-03 | medium |
| Insult vs. Disinhibition | 0.2808 | 0.0788 | 6.17e-02 | small |

### 3. Pattern Detection

| Analysis | Outliers | Constrained |
|----------|----------|-------------|
| Toxicity vs. Aggression | 1 | 0 |
| Insult vs. Aggression | 1 | 0 |
| Toxicity vs. Sophistication | 2 | 4 |
| Toxicity vs. Disinhibition | 1 | 3 |
| Insult vs. Sophistication | 1 | 4 |
| Insult vs. Disinhibition | 1 | 2 |


### 4. Score Ranges

| Measure | Min | Max |
|---------|-----|-----|
| Judge Aggression | 1.08 | 2.14 |
| BERT Toxicity | 0.0007 | 0.0100 |
| BERT Insult | 0.0002 | 0.0012 |

---

## Data Provenance

### BERT Model

| Field | Value |
|-------|-------|
| **Model** | `unitary/toxic-bert` |
| **URL** | https://huggingface.co/unitary/toxic-bert |
| **Architecture** | BERT (bert-base-uncased), 110M parameters |
| **Training Data** | Jigsaw Toxic Comment Classification (~160k Wikipedia comments) |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |
| **Execution** | Local inference (no API calls) |

### Source Data

| Field | Value |
|-------|-------|
| **Condition** | telemetryV3 |
| **Profiles Path** | `outputs/behavioral_profiles/telemetryV3/profiles` |
| **Jobs Path** | `outputs/single_prompt_jobs` |
| **Models Evaluated** | 45 |

---

## Output Files

| File | Description |
|------|-------------|
| `bert_validation_results.json` | Primary validation results (aggression) |
| `bert_soph_disin_results.json` | Extended validation results (soph/disin) |
| `scatter_toxicity_vs_aggression.png` | Primary toxicity scatter |
| `scatter_insult_vs_aggression.png` | Primary insult scatter |
| `scatter_combined.png` | 2-panel aggression summary |
| `scatter_toxicity_vs_sophistication.png` | Toxicity ~ Sophistication |
| `scatter_toxicity_vs_disinhibition.png` | Toxicity ~ Disinhibition |
| `scatter_insult_vs_sophistication.png` | Insult ~ Sophistication |
| `scatter_insult_vs_disinhibition.png` | Insult ~ Disinhibition |
| `scatter_soph_disin_combined.png` | 2x2 composite grid |
| `full_run_log.txt` | Execution trace |
| `VALIDATION_REPORT.md` | This report |

---

## Interpretation

**Primary Finding**: Moderate validation - Partial overlap between constructs

**Key Insight**: BERT toxicity correlates most strongly with the **disinhibition composite** (which includes aggression), providing convergent validity that our behavioral measures capture real toxicity-related signals detectable by an independent, non-LLM classifier.

**Effect Size Thresholds** (Cohen's conventions):
- |r| < 0.10: Negligible
- |r| 0.10-0.30: Small
- |r| 0.30-0.50: Medium
- |r| ≥ 0.50: Large

---

## Reproducibility

```bash
# Run primary validation (BERT vs Aggression)
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition telemetryV3

# Run extended validation (BERT vs Soph/Disin)
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition telemetryV3

# Regenerate this report
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_validation_reports.py --condition telemetryV3
```

---

## References

1. Unitary AI toxic-bert: https://huggingface.co/unitary/toxic-bert
2. Jigsaw Toxic Comment Challenge: https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge
3. Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
