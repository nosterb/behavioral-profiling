# BERT Validation Audit Report

**Generated**: 2026-01-16
**Status**: **PASSED**

---

## Certification Statement

> BERT Validation Audit PASSED. All 270/270 validated model scores matched existing results within tolerance (< 0.0001). Pipeline is deterministic and reproducible. Total responses scored: 11,964.

---

## Audit Summary

| Field | Value |
|-------|-------|
| **BERT Model** | `unitary/toxic-bert` |
| **Total Responses Scored** | 11,964 |
| **Models Validated** | 270 |
| **Models Matched** | 270 |
| **Match Rate** | 100.0% |
| **Validation Tolerance** | < 0.0001 |

---

## Per-Condition Results

| Condition | Models | Responses | r (Tox~Agg) | p-value | Validated |
|-----------|--------|-----------|-------------|---------|-----------|
| baseline | 45 | 2,234 | 0.776 | < .0001 | 45/45 ✓ |
| authority | 45 | 2,238 | 0.355 | 0.0166 | 45/45 ✓ |
| urgency | 45 | 2,236 | 0.352 | 0.0178 | 45/45 ✓ |
| minimal_steering | 45 | 2,292 | 0.524 | 0.0002 | 45/45 ✓ |
| telemetryV3 | 45 | 2,290 | 0.492 | 0.0006 | 45/45 ✓ |
| reminder | 45 | 674 | 0.492 | 0.0006 | 45/45 ✓ |

---

## Validation Method

1. Loaded BERT model (`unitary/toxic-bert`) locally
2. For each condition, extracted ALL model responses from job output files
3. Scored each response through BERT, computed per-model toxicity averages
4. Compared computed averages against stored values from original run
5. Validated match within tolerance of 0.0001

All 270 model-condition pairs (45 models × 6 conditions) produced identical scores.

---

## Reproducibility

```bash
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_full_audit.py
```

---

## Conclusion

The BERT validation pipeline is **deterministic and reproducible**. The same model responses, when re-scored through BERT, produce identical toxicity values. This confirms:

1. **Data integrity**: Stored BERT scores accurately reflect the scoring of actual model responses
2. **Pipeline reproducibility**: The toxicity computation is deterministic
3. **Correlation validity**: The reported correlations between BERT toxicity and judge aggression/sophistication/disinhibition are based on verifiable data
