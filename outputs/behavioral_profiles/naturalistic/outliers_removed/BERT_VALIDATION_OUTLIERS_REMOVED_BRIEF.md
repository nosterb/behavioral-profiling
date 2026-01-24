# BERT Validation - Outliers Removed (naturalistic)

**Generated**: 2026-01-24 09:26

## Summary

| Metric | Original | Outliers Removed | Delta |
|--------|----------|------------------|-------|
| N | 44 | 43 | -1 |
| r (Toxicity) | 0.478 | 0.341 | -0.137 |
| r (Insult) | 0.497 | 0.324 | -0.173 |

## Outliers Removed

| Model | Sophistication | Disinhibition | SD from Line |
|-------|----------------|---------------|--------------|
| Gemini-3-Pro-Preview | 7.73 | 1.86 | 4.97 |

## Correlations (Outliers Removed)

| Measure | r | p | R² | Effect Size |
|---------|---|---|----|----|
| BERT Toxicity | 0.341 | 2.53e-02 | 0.116 | medium |
| BERT Insult | 0.324 | 3.40e-02 | 0.105 | medium |

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `outputs/behavioral_profiles/research_synthesis/bert_validation/naturalistic/bert_validation_results.json` | Original BERT validation results |
| `outputs/behavioral_profiles/naturalistic/outliers_removed/outlier_removal_info.json` | H1/H2 outlier detection info |

### Audit Files
| File | Description |
|------|-------------|
| `bert_validation_outliers_removed_audit.json` | Complete audit data with per-model scores |

### Reproducibility
```bash
python3 scripts/run_bert_validation_outliers_removed.py --condition naturalistic
```
