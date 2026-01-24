# BERT Validation - Outliers Removed (baseline)

**Generated**: 2026-01-24 09:26

## Summary

| Metric | Original | Outliers Removed | Delta |
|--------|----------|------------------|-------|
| N | 45 | 44 | -1 |
| r (Toxicity) | 0.776 | 0.703 | -0.074 |
| r (Insult) | 0.624 | 0.639 | +0.015 |

## Outliers Removed

| Model | Sophistication | Disinhibition | SD from Line |
|-------|----------------|---------------|--------------|
| Gemini-3-Pro-Preview | 7.50 | 2.31 | 4.43 |

## Correlations (Outliers Removed)

| Measure | r | p | R² | Effect Size |
|---------|---|---|----|----|
| BERT Toxicity | 0.703 | 1.04e-07 | 0.494 | large |
| BERT Insult | 0.639 | 3.06e-06 | 0.408 | large |

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `outputs/behavioral_profiles/research_synthesis/bert_validation/baseline/bert_validation_results.json` | Original BERT validation results |
| `outputs/behavioral_profiles/baseline/outliers_removed/outlier_removal_info.json` | H1/H2 outlier detection info |

### Audit Files
| File | Description |
|------|-------------|
| `bert_validation_outliers_removed_audit.json` | Complete audit data with per-model scores |

### Reproducibility
```bash
python3 scripts/run_bert_validation_outliers_removed.py --condition baseline
```
