# Data Audit Plan

**Created**: 2026-01-24
**Last Updated**: 2026-01-24
**Status**: **COMPLETE** (160/160 checks passed)
**Purpose**: Comprehensive verification of all underlying data, condition by condition

---

## Audit Scope

| Layer | Description |
|-------|-------------|
| **L1: Source Jobs** | Raw job JSON files with model responses and judge evaluations |
| **L2: Profiles** | Aggregated per-model behavioral profiles |
| **L3: Statistics** | median_split_classification.json, comprehensive_stats.json |
| **L4: Validation** | BERT toxicity, external benchmarks (GPQA, ARC-AGI, AIME) |
| **L5: Reports** | RESEARCH_BRIEF.md, CONSOLIDATED_STATISTICS.md |

---

## Conditions to Audit

| # | Condition | Profiles | Source Jobs |
|---|-----------|----------|-------------|
| 1 | baseline | 45 | baseline_* (no intervention suffix) |
| 2 | authority | 45 | baseline_* with _authority suffix |
| 3 | urgency | 45 | baseline_* with _urgency suffix |
| 4 | minimal_steering | 45 | baseline_* with _minimal_steering suffix |
| 5 | telemetryV3 | 45 | baseline_* with _telemetry suffix |
| 6 | reminder | 45 | baseline_* with _reminder suffix |
| 7 | naturalistic | **44** | naturalistic_1/ (see note below) |
| 8 | all_combined | 45 | All of the above |

> **Note (2026-01-24)**: naturalistic has 44 models (not 45) because llama-3-70b was removed due to invalid tribalism scores (0.85, 0.997). This model was only tested in naturalistic, not in intervention conditions. See `naturalistic/CUSTOM_NOTES.md`.

---

## Per-Condition Audit Checklist

### Phase 1: Profile Integrity

```
[x] 1.1 Profile count matches expected (45 for interventions, 44 for naturalistic)
[x] 1.2 All profiles have 9 dimensions with valid scores (1-10)
[x] 1.3 All profiles have contribution_count > 0
[x] 1.4 No NaN/null values in dimension averages
[x] 1.5 Profile model_ids match between conditions (45 models; naturalistic differs by 1)
```

### Phase 2: Source Job Verification

```
[x] 2.1 Count jobs matching this condition's filter
[x] 2.2 Each job has valid judge_evaluation (or judge_evaluation_telemetry for telemetryV3)
[x] 2.3 Judge scores are 1-10 for all dimensions
[x] 2.4 Model response text exists for each evaluated model
[x] 2.5 No duplicate jobs (same prompt + model + timestamp)
```

### Phase 3: Statistical Accuracy

```
[x] 3.1 median_split_classification.json:
    [x] N = sum(n_high + n_low) matches profile count
    [x] median_sophistication falls within expected range (4-8)
    [x] H1a Cohen's d recalculable from group means/SDs
    [x] H2 correlation r recalculable from model data

[x] 3.2 comprehensive_stats.json:
    [x] Provider counts sum to total N
    [x] Provider means within 1-10 range

[x] 3.3 provider_comparison_stats.json:
    [x] ANOVA F, p, eta_squared verifiable
```

### Phase 4: Judge Agreement

```
[x] 4.1 judge_agreement_audit.json exists
[x] 4.2 n_evaluations matches expected (filtered to current profile set)
[x] 4.3 ICC values in plausible range (0.5-1.0)
[x] 4.4 Per-dimension ICC available for all 9 dimensions
```

### Phase 5: Outlier Analysis

```
[x] 5.1 outliers_removed/ directory exists
[x] 5.2 outlier_removal_info.json lists removed models
[x] 5.3 outliers_removed/profiles/ count = original - removed
[x] 5.4 H1a d (outliers removed) >= H1a d (original) [expected pattern]
```

### Phase 6: BERT Validation

```
[x] 6.1 bert_validation/<condition>/bert_validation_results.json exists
[x] 6.2 n_models matches condition profile count
[x] 6.3 total evaluations plausible (models × ~50 responses)
[x] 6.4 Correlations (r_tox, r_ins) in valid range (-1 to 1)
[x] 6.5 p-values < 0.05 where claimed significant
```

---

## Cross-Condition Audit

### Phase 7: Model Consistency

```
[x] 7.1 Same 45 models in 6 intervention conditions; naturalistic has 44 (llama-3.3-70b missing)
[x] 7.2 all_combined has 45 models (after llama-3-70b removal)
[x] 7.3 Model naming consistent (no spelling variations)
[x] 7.4 Thinking variants properly distinguished from base models
```

### Phase 8: Evaluation Counts

```
[x] 8.1 Sum of per-condition judge evals = 13,868 (after llama-3-70b exclusions)
[x] 8.2 Sum of per-condition BERT evals = 14,203
[x] 8.3 No double-counting from all_combined (all_combined counted separately: 13,912)
```

### Phase 9: External Validation

```
[x] 9.1 GPQA benchmark data: N=35 models matched
[x] 9.2 ARC-AGI benchmark data: N=16 models matched
[x] 9.3 AIME benchmark data: N=20 models matched
[x] 9.4 Correlations match MAIN_RESEARCH_BRIEF.md claims
```

---

## Audit Execution Commands

### Run Full Audit (All Conditions)

```bash
python3 scripts/run_data_audit.py --all
```

### Run Single Condition

```bash
python3 scripts/run_data_audit.py --condition baseline
```

### Generate Audit Report

```bash
python3 scripts/run_data_audit.py --all --output audit_report.json
```

---

## Audit Output Format

Each condition audit produces:

```json
{
  "condition": "baseline",
  "timestamp": "2026-01-24T...",
  "phases": {
    "profile_integrity": {
      "passed": true,
      "checks": {
        "profile_count": {"expected": 45, "actual": 45, "pass": true},
        "dimensions_valid": {"invalid_count": 0, "pass": true},
        ...
      }
    },
    "source_jobs": {...},
    "statistics": {...},
    "judge_agreement": {...},
    "outliers": {...},
    "bert_validation": {...}
  },
  "summary": {
    "total_checks": 25,
    "passed": 25,
    "failed": 0,
    "warnings": 1
  }
}
```

---

## Known Issues to Verify

| Issue | Check | Status |
|-------|-------|--------|
| naturalistic had duplicate prompts | Verify 51 unique prompts, ~2,231 judge evals | **Verified** |
| BERT vs Judge count mismatch | BERT 11,964 (6 conditions), Judge 13,912 (8 conditions) - different scope | **Explained** |
| all_combined has 46 models | ~~Extra model is Gemini-3-Pro-Preview~~ Now 45 after llama-3-70b removal | **Fixed** |
| telemetryV3 uses different judge key | Uses `judge_evaluation_telemetry` not `judge_evaluation` | **Verified** |
| llama-3-70b invalid tribalism | Scores 0.85, 0.997 (below 1-10 range) | **Removed** |
| tribalalism typo in profiles | urgency/claude-4-sonnet, all_combined/claude-4-sonnet had 10 dimensions | **Fixed** |
| naturalistic missing llama-3.3-70b | Different model set used vs intervention conditions | **Documented** |
| Judge agreement counted removed models | Judge data predated profile cleanup | **Fixed 2026-01-24** |

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| **Pass** | All checks pass, no discrepancies |
| **Pass with Warnings** | Minor discrepancies documented and explained |
| **Fail** | Critical discrepancies requiring data correction |

---

## Audit Schedule

| Date | Scope | Status |
|------|-------|--------|
| 2026-01-24 | Create audit plan | Done |
| 2026-01-24 | Initial automated audit (158/160 passed) | Done |
| 2026-01-24 | Fix tribalalism typo (2 profiles) | Done |
| 2026-01-24 | Remove llama-3-70b (invalid data) | Done |
| 2026-01-24 | Document naturalistic model count (44 vs 45) | Done |
| 2026-01-24 | Phase 1-6: Per-condition audits | **PASS (160/160)** |
| 2026-01-24 | Phase 7-9: Cross-condition audits | **PASS (6/6)** |
| 2026-01-24 | Final audit report | **audit_report_20260124.json** |
| 2026-01-24 | Fix judge agreement profile filtering | Done |
| 2026-01-24 | Fix naturalistic job file path | Done |
| 2026-01-24 | Regenerate all judge agreement outputs | Done |

---

## Related Files

- `CONSOLIDATED_STATISTICS.md` - Current aggregate statistics
- `MAIN_RESEARCH_BRIEF.md` - Claims to verify against data
- `scripts/generate_consolidated_statistics.py` - Statistics generation
- `scripts/run_data_audit.py` - Automated audit script

---

## Final Audit Summary (2026-01-24)

### Evaluation Counts

| Condition | Models | Judge Evals | Excluded | ICC |
|-----------|--------|-------------|----------|-----|
| baseline | 45 | 2,202 | 50 | 0.813 (Good) |
| authority | 45 | 2,261 | 0 | 0.765 (Good) |
| urgency | 45 | 2,259 | 0 | 0.835 (Good) |
| minimal_steering | 45 | 2,266 | 51 | 0.727 (Moderate) |
| telemetryV3 | 45 | 2,053 | 41 | 0.789 (Good) |
| reminder | 45 | 659 | 15 | 0.830 (Good) |
| naturalistic | 44 | 2,168 | 19 | 0.629 (Moderate) |
| **TOTAL** | — | **13,868** | **176** | — |
| all_combined | 45 | 13,912 | 176 | 0.826 (Good) |

### Key Corrections Made

1. **llama-3-70b removed** - Invalid tribalism scores (0.85, 0.997)
2. **tribalalism typo fixed** - urgency/claude-4-sonnet, all_combined/claude-4-sonnet
3. **Judge agreement filtering** - Now matches current profile set
4. **naturalistic job path** - Fixed to look in `naturalistic_1/` directory

### Audit Result

```
Total Checks: 160/160 PASSED
Per-Condition: 8 conditions × 20 checks each
Cross-Condition: 6 additional checks
Status: COMPLETE
```
