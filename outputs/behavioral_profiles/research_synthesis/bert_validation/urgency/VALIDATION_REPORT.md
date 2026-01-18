# BERT Toxicity Validation Report

**Generated**: 2026-01-15
**Condition**: urgency
**Experiment**: Independent validation of LLM-as-judge behavioral scores

---

## Executive Summary

| Metric | r | p | Effect | Interpretation |
|--------|---|---|--------|----------------|
| **Toxicity vs. Aggression** | 0.352 | 0.0178 | medium | Primary validation |
| **Insult vs. Aggression** | 0.414 | 0.0047 | medium | Secondary validation |
| **Toxicity vs. Sophistication** | 0.602 | < .0001 | large | Composite validation |
| **Toxicity vs. Disinhibition** | 0.342 | 0.0215 | medium | Composite validation |
| **Insult vs. Sophistication** | 0.440 | 0.0025 | medium | Composite validation |
| **Insult vs. Disinhibition** | 0.390 | 0.0081 | medium | Composite validation |

**N = 45 models** | Outliers: 2 | Constrained: 9

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
| Toxicity | 0.3519 | 0.1238 | 1.78e-02 | medium | 0.002449 | 0.000546 |
| Insult | 0.4141 | 0.1715 | 4.69e-03 | medium | 0.000550 | -0.000542 |

### 2. BERT vs. Sophistication/Disinhibition (Extended)

| Measure | r | R² | p-value | Effect |
|---------|---|----|---------|--------|
| Toxicity vs. Sophistication | 0.6025 | 0.3630 | 1.19e-05 | large |
| Toxicity vs. Disinhibition | 0.3420 | 0.1170 | 2.15e-02 | medium |
| Insult vs. Sophistication | 0.4401 | 0.1937 | 2.49e-03 | medium |
| Insult vs. Disinhibition | 0.3899 | 0.1520 | 8.11e-03 | medium |

### 3. Pattern Detection

| Analysis | Outliers | Constrained |
|----------|----------|-------------|
| Toxicity vs. Aggression | 2 | 9 |
| Insult vs. Aggression | 2 | 0 |
| Toxicity vs. Sophistication | 4 | 4 |
| Toxicity vs. Disinhibition | 2 | 5 |
| Insult vs. Sophistication | 2 | 6 |
| Insult vs. Disinhibition | 2 | 6 |


### 4. Score Ranges

| Measure | Min | Max |
|---------|-----|-----|
| Judge Aggression | 1.24 | 5.80 |
| BERT Toxicity | 0.0006 | 0.0340 |
| BERT Insult | 0.0002 | 0.0088 |

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
| **Condition** | urgency |
| **Profiles Path** | `outputs/behavioral_profiles/urgency/profiles` |
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
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition urgency

# Run extended validation (BERT vs Soph/Disin)
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition urgency

# Regenerate this report
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_validation_reports.py --condition urgency
```

---

## References

1. Unitary AI toxic-bert: https://huggingface.co/unitary/toxic-bert
2. Jigsaw Toxic Comment Challenge: https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge
3. Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
