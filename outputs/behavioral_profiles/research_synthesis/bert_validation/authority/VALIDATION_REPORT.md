# BERT Toxicity Validation Report

**Generated**: 2026-01-15
**Condition**: authority
**Experiment**: Independent validation of LLM-as-judge behavioral scores

---

## Executive Summary

| Metric | r | p | Effect | Interpretation |
|--------|---|---|--------|----------------|
| **Toxicity vs. Aggression** | 0.355 | 0.0166 | medium | Primary validation |
| **Insult vs. Aggression** | 0.356 | 0.0165 | medium | Secondary validation |
| **Toxicity vs. Sophistication** | 0.471 | 0.0011 | medium | Composite validation |
| **Toxicity vs. Disinhibition** | 0.348 | 0.0193 | medium | Composite validation |
| **Insult vs. Sophistication** | 0.314 | 0.0360 | medium | Composite validation |
| **Insult vs. Disinhibition** | 0.365 | 0.0138 | medium | Composite validation |

**N = 45 models** | Outliers: 3 | Constrained: 5

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
| Toxicity | 0.3553 | 0.1262 | 1.66e-02 | medium | 0.007643 | -0.006655 |
| Insult | 0.3556 | 0.1264 | 1.65e-02 | medium | 0.001561 | -0.001694 |

### 2. BERT vs. Sophistication/Disinhibition (Extended)

| Measure | r | R² | p-value | Effect |
|---------|---|----|---------|--------|
| Toxicity vs. Sophistication | 0.4712 | 0.2221 | 1.09e-03 | medium |
| Toxicity vs. Disinhibition | 0.3476 | 0.1208 | 1.93e-02 | medium |
| Insult vs. Sophistication | 0.3135 | 0.0983 | 3.60e-02 | medium |
| Insult vs. Disinhibition | 0.3647 | 0.1330 | 1.38e-02 | medium |

### 3. Pattern Detection

| Analysis | Outliers | Constrained |
|----------|----------|-------------|
| Toxicity vs. Aggression | 3 | 5 |
| Insult vs. Aggression | 1 | 0 |
| Toxicity vs. Sophistication | 2 | 7 |
| Toxicity vs. Disinhibition | 4 | 7 |
| Insult vs. Sophistication | 1 | 8 |
| Insult vs. Disinhibition | 1 | 7 |


### 4. Score Ranges

| Measure | Min | Max |
|---------|-----|-----|
| Judge Aggression | 1.08 | 2.68 |
| BERT Toxicity | 0.0006 | 0.0253 |
| BERT Insult | 0.0002 | 0.0085 |

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
| **Condition** | authority |
| **Profiles Path** | `outputs/behavioral_profiles/authority/profiles` |
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
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition authority

# Run extended validation (BERT vs Soph/Disin)
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition authority

# Regenerate this report
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_validation_reports.py --condition authority
```

---

## References

1. Unitary AI toxic-bert: https://huggingface.co/unitary/toxic-bert
2. Jigsaw Toxic Comment Challenge: https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge
3. Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
