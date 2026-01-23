# BERT Toxicity Validation Report

**Generated**: 2026-01-19
**Experiment**: Independent validation of LLM-as-judge aggression scores

---

## Summary

| Metric | Value |
|--------|-------|
| **N (models)** | 45 |
| **BERT Toxicity vs. Aggression** | r = 0.635, p = 0.0000 |
| **BERT Insult vs. Aggression** | r = 0.562, p = 0.0001 |
| **Interpretation** | Strong validation - BERT toxicity validates aggression measure |

---

## Visualizations

### BERT Toxicity vs. Judge Aggression
![Toxicity Scatter](scatter_toxicity_vs_aggression.png)

### BERT Insult vs. Judge Aggression
![Insult Scatter](scatter_insult_vs_aggression.png)

### Combined View
![Combined Scatter](scatter_combined.png)

---

## Data Trail

### 1. BERT Model

| Field | Value |
|-------|-------|
| **Model Name** | `unitary/toxic-bert` |
| **Hosted On** | Hugging Face (downloaded locally) |
| **Model URL** | https://huggingface.co/unitary/toxic-bert |
| **Architecture** | BERT (bert-base-uncased), 110M parameters |
| **Training Data** | Jigsaw Toxic Comment Classification Challenge |
| **Training Data URL** | https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |
| **Max Sequence Length** | 512 tokens |
| **Execution** | Local inference (no API calls) |

### 2. Source Data

| Field | Value |
|-------|-------|
| **Condition** | minimal_steering |
| **Profiles Path** | `outputs/behavioral_profiles/minimal_steering/profiles` |
| **Jobs Path** | `outputs/single_prompt_jobs` |
| **Models Evaluated** | 45 |

### 3. Statistical Results

#### Correlations

| Measure | r | p-value | Effect Size |
|---------|---|---------|-------------|
| BERT Toxicity | 0.6350 | 0.000003 | large |
| BERT Insult | 0.5623 | 0.000058 | large |

#### Regression: Toxicity ~ Aggression

| Parameter | Value |
|-----------|-------|
| Slope | 0.041061 |
| Intercept | -0.046144 |
| R² | 0.4032 |
| Standard Error | 0.007617 |

#### Regression: Insult ~ Aggression

| Parameter | Value |
|-----------|-------|
| Slope | 0.003819 |
| Intercept | -0.004200 |
| R² | 0.3162 |
| Standard Error | 0.000856 |

### 4. Score Ranges

| Measure | Min | Max |
|---------|-----|-----|
| Judge Aggression | 1.08 | 1.54 |
| BERT Toxicity | 0.0006 | 0.0369 |
| BERT Insult | 0.0002 | 0.0039 |

---

## Output Files

| File | Description |
|------|-------------|
| `bert_validation_results.json` | Complete results with per-model scores (for downstream use) |
| `scatter_toxicity_vs_aggression.png` | Toxicity correlation scatter plot |
| `scatter_insult_vs_aggression.png` | Insult correlation scatter plot |
| `scatter_combined.png` | Combined 2-panel visualization |
| `VALIDATION_REPORT.md` | This report |
| `full_run_log.txt` | Complete execution log with per-response scores |

---

## Interpretation

Strong validation - BERT toxicity validates aggression measure

**Effect size thresholds** (Cohen's conventions):
- |r| < 0.10: Negligible
- |r| 0.10-0.30: Small
- |r| 0.30-0.50: Medium
- |r| ≥ 0.50: Large

---

## Reproducibility

```bash
# Activate virtual environment
source venv/bin/activate

# Run validation
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py

# With verbose logging
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/full_run_log.txt
```

---

## References

1. Unitary AI toxic-bert: https://huggingface.co/unitary/toxic-bert
2. Jigsaw Toxic Comment Challenge: https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge
3. BERT paper: Devlin et al. (2019) "BERT: Pre-training of Deep Bidirectional Transformers"
