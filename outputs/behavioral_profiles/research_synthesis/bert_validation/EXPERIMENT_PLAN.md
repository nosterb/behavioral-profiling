# BERT Toxicity Validation Experiment

**Status**: COMPLETE
**Date**: 2026-01-15

## Objective

Validate LLM-as-judge aggression scores using BERT toxicity detection as an independent measure.

## Results

| Metric | Correlation (r) | P-value | Interpretation |
|--------|----------------|---------|----------------|
| BERT Toxicity vs. Aggression | **0.776** | < .0001 | Large effect |
| BERT Insult vs. Aggression | **0.624** | < .0001 | Large effect |

**N = 45 models** (including thinking variants as unique models)

**Conclusion**: Strong validation. The aggression dimension correlates significantly with BERT toxicity/insult scores, providing convergent validity for the LLM-as-judge methodology. R² = 0.60 for toxicity means 60% of variance in BERT toxicity scores is explained by judge aggression scores.

## Model Provenance

| Field | Value |
|-------|-------|
| **Model** | `unitary/toxic-bert` |
| **URL** | https://huggingface.co/unitary/toxic-bert |
| **Architecture** | BERT (bert-base-uncased) |
| **Training Data** | Jigsaw Toxic Comment Classification (~160k Wikipedia comments) |
| **Training Data URL** | https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |

## Why This Matters

- **Independent validation**: BERT is fundamentally different from LLM judges
- **Addresses judge bias**: Not "frontier model judging frontier models"
- **Established benchmark**: Jigsaw dataset is widely used for toxicity research

## Experiment Phases

### Phase 1: Proof of Concept
- [x] Test BERT model loading
- [x] Run on 5 sample texts
- [x] Verify score ordering matches expectations

### Phase 2: Full Validation (N=39 models)
- [x] Extract responses from baseline condition (50 jobs)
- [x] Score with BERT toxicity model
- [x] Calculate correlation with aggression scores
- [x] Generate validation report

## Data Flow

```
baseline job outputs (JSON)
    → extract model responses + aggression scores
    → call Perspective API (TOXICITY)
    → merge scores
    → correlation analysis
```

## Files

```
outputs/behavioral_profiles/research_synthesis/bert_validation/
├── EXPERIMENT_PLAN.md              # This file
├── scripts/
│   ├── test_bert_toxicity.py       # Phase 1: BERT model test
│   ├── run_bert_validation.py      # Full validation pipeline
│   └── regenerate_plots.py         # Regenerate plots from saved JSON
├── bert_validation_results.json    # Complete results (for downstream reports)
├── scatter_toxicity_vs_aggression.png
├── scatter_insult_vs_aggression.png
├── scatter_combined.png
├── VALIDATION_REPORT.md
└── full_run_log.txt
```

## Runtime

- BERT model runs locally (~418MB in `~/.cache/huggingface/`)
- No API calls required
- Full validation (~2000 responses × 45 models) takes ~5 minutes

## Success Criteria

| Outcome | Interpretation |
|---------|----------------|
| r > 0.5 | Strong validation - aggression captures toxicity signal |
| r = 0.3-0.5 | Moderate - partial overlap, different constructs |
| r < 0.3 | Weak - aggression measures something distinct from toxicity |

Note: Even low correlation is informative - it would mean our "aggression" dimension captures something different from standard toxicity detection.
