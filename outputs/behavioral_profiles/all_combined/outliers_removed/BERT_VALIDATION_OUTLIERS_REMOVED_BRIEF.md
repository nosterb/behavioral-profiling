# BERT Validation - Outliers Removed (all_combined)

**Generated**: 2026-01-24 09:26

## Summary

| Metric | Original | Outliers Removed | Delta |
|--------|----------|------------------|-------|
| N | 45 | 42 | -3 |
| r (Toxicity) | 0.606 | 0.595 | -0.011 |
| r (Insult) | 0.516 | 0.541 | +0.025 |

## Outliers Removed

| Model | Sophistication | Disinhibition | SD from Line |
|-------|----------------|---------------|--------------|
| Gemini-3-Pro-Preview | 7.14 | 2.40 | 3.47 |
| DeepSeek-R1 | 6.40 | 2.13 | 2.60 |
| GPT-OSS-120B | 6.82 | 1.52 | 2.02 |

## Correlations (Outliers Removed)

| Measure | r | p | R² | Effect Size |
|---------|---|---|----|----|
| BERT Toxicity | 0.595 | 3.21e-05 | 0.354 | large |
| BERT Insult | 0.541 | 2.14e-04 | 0.293 | large |

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `outputs/behavioral_profiles/research_synthesis/bert_validation/all_combined/bert_validation_results.json` | Original BERT validation results |
| `outputs/behavioral_profiles/all_combined/outliers_removed/outlier_removal_info.json` | H1/H2 outlier detection info |

### Audit Files
| File | Description |
|------|-------------|
| `bert_validation_outliers_removed_audit.json` | Complete audit data with per-model scores |

### Reproducibility
```bash
python3 scripts/run_bert_validation_outliers_removed.py --condition all_combined
```
