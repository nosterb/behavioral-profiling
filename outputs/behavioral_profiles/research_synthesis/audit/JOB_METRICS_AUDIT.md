# Job Metrics Audit Report

**Generated**: 2026-01-19T19:08:43.401186
**Total Jobs Scanned**: 309
**Total Conditions**: 8

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total jobs | 309 |
| Complete jobs | 270 |
| Incomplete jobs | 39 |
| Total model evaluations | 12,838 |
| Total valid 3-judge evals | 12,823 |

---

## By Condition

| Condition | Jobs | Complete | Unique Prompts | Models | Evaluations | Valid 3-Judge | Judges | Completeness |
|-----------|------|----------|----------------|--------|-------------|---------------|--------|--------------|
| authority | 51 | 50 | 51 | 2295 | 2295 | 2294 | 3 | ⚠️ 98% |
| baseline | 50 | 49 | 50 | 2300 | 2300 | 2299 | 3 | ⚠️ 98% |
| minimal_steering | 51 | 48 | 51 | 2346 | 2346 | 2341 | 3 | ⚠️ 94% |
| naturalistic | 20 | 17 | 20 | 900 | 900 | 896 | 3 | ⚠️ 85% |
| naturalistic_50 | 20 | 12 | 20 | 900 | 540 | 540 | 3 | ⚠️ 60% |
| reminder | 15 | 14 | 15 | 690 | 690 | 689 | 3 | ⚠️ 93% |
| telemetryV3 | 51 | 30 | 51 | 2346 | 1472 | 1470 | 3 | ⚠️ 59% |
| urgency | 51 | 50 | 51 | 2295 | 2295 | 2294 | 3 | ⚠️ 98% |

---

## Condition Details

### Authority

| Metric | Value |
|--------|-------|
| Jobs | 51 |
| Complete | 50 |
| Incomplete | 1 |
| Unique prompts | 51 |
| Models configured | 2295 |
| Model responses | 0 |
| Judge evaluations | 2295 |
| Valid 3-judge evals | 2294 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 11 |
| Completeness | 98.0% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_broad_13_authority_20260107_231717 | ❌ | ✅ | 44 | 45 |

### Baseline

| Metric | Value |
|--------|-------|
| Jobs | 50 |
| Complete | 49 |
| Incomplete | 1 |
| Unique prompts | 50 |
| Models configured | 2300 |
| Model responses | 0 |
| Judge evaluations | 2300 |
| Valid 3-judge evals | 2299 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 12 |
| Completeness | 98.0% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_typical_v2_9_20260107_120749 | ❌ | ✅ | 45 | 46 |

### Minimal_Steering

| Metric | Value |
|--------|-------|
| Jobs | 51 |
| Complete | 48 |
| Incomplete | 3 |
| Unique prompts | 51 |
| Models configured | 2346 |
| Model responses | 0 |
| Judge evaluations | 2346 |
| Valid 3-judge evals | 2341 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 11 |
| Completeness | 94.1% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_broad_4_minimal_steering_20260109_122441 | ❌ | ✅ | 44 | 46 |
| job_broad_9_minimal_steering_20260109_124329 | ❌ | ✅ | 45 | 46 |
| job_typical_v2_8_minimal_steering_20260109_151316 | ❌ | ✅ | 44 | 46 |

### Naturalistic

| Metric | Value |
|--------|-------|
| Jobs | 20 |
| Complete | 17 |
| Incomplete | 3 |
| Unique prompts | 20 |
| Models configured | 900 |
| Model responses | 0 |
| Judge evaluations | 900 |
| Valid 3-judge evals | 896 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 10 |
| Completeness | 85.0% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_naturalistic_03_20260118_135724 | ❌ | ✅ | 44 | 45 |
| job_naturalistic_05_20260118_141913 | ❌ | ✅ | 44 | 45 |
| job_naturalistic_20_20260118_155708 | ❌ | ✅ | 43 | 45 |

### Naturalistic_50

| Metric | Value |
|--------|-------|
| Jobs | 20 |
| Complete | 12 |
| Incomplete | 8 |
| Unique prompts | 20 |
| Models configured | 900 |
| Model responses | 0 |
| Judge evaluations | 540 |
| Valid 3-judge evals | 540 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 12 |
| Completeness | 60.0% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_naturalistic_02_50_20260118_161941 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_06_50_20260118_163839 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_08_50_20260118_165722 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_09_50_20260118_165737 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_12_50_20260118_172005 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_13_50_20260118_174049 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_15_50_20260118_174242 | ❌ | ❌ | 0 | 45 |
| job_naturalistic_20_50_20260118_182115 | ❌ | ❌ | 0 | 45 |

### Reminder

| Metric | Value |
|--------|-------|
| Jobs | 15 |
| Complete | 14 |
| Incomplete | 1 |
| Unique prompts | 15 |
| Models configured | 690 |
| Model responses | 0 |
| Judge evaluations | 690 |
| Valid 3-judge evals | 689 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 13 |
| Completeness | 93.3% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_dimensions_dominance_1_reminder_20260110_201521 | ❌ | ✅ | 45 | 46 |

### Telemetryv3

| Metric | Value |
|--------|-------|
| Jobs | 51 |
| Complete | 30 |
| Incomplete | 21 |
| Unique prompts | 51 |
| Models configured | 2346 |
| Model responses | 0 |
| Judge evaluations | 1472 |
| Valid 3-judge evals | 1470 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 12 |
| Completeness | 58.8% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_love_v1_10_telemetryV3_20260108_233750 | ❌ | ❌ | 0 | 46 |
| job_love_v1_3_telemetryV3_20260109_014010 | ❌ | ❌ | 0 | 46 |
| job_love_v1_4_telemetryV3_20260109_013800 | ❌ | ❌ | 0 | 46 |
| job_love_v1_9_telemetryV3_20260109_053849 | ❌ | ❌ | 0 | 46 |
| job_broad_10_telemetryV3_20260109_054054 | ❌ | ❌ | 0 | 46 |
| job_broad_14_telemetryV3_20260109_073747 | ❌ | ❌ | 0 | 46 |
| job_broad_15_telemetryV3_20260109_095315 | ❌ | ❌ | 0 | 46 |
| job_broad_3_telemetryV3_20260109_101325 | ❌ | ❌ | 0 | 46 |
| job_broad_6_telemetryV3_20260109_103513 | ❌ | ❌ | 0 | 46 |
| job_broad_7_telemetryV3_20260109_103905 | ❌ | ❌ | 0 | 46 |
| job_dimensions_aggression_telemetryV3_20260109_105716 | ❌ | ✅ | 45 | 46 |
| job_dimensions_deference_telemetryV3_20260109_110214 | ❌ | ❌ | 0 | 46 |
| job_dimensions_identity_telemetryV3_20260109_112058 | ❌ | ❌ | 0 | 46 |
| job_dimensions_transgression_telemetryV3_20260109_112250 | ❌ | ✅ | 45 | 46 |
| job_typical_v2_12_telemetryV3_20260109_115733 | ❌ | ❌ | 0 | 46 |
| job_typical_v2_15_telemetryV3_20260109_121923 | ❌ | ❌ | 0 | 46 |
| job_typical_v2_19_telemetryV3_20260109_124659 | ❌ | ❌ | 0 | 46 |
| job_typical_v2_3_telemetryV3_20260109_130827 | ❌ | ❌ | 0 | 46 |
| job_typical_v2_4_telemetryV3_20260109_132345 | ❌ | ❌ | 0 | 46 |
| job_typical_v2_7_telemetryV3_20260109_134448 | ❌ | ❌ | 0 | 46 |
| job_typical_v2_9_telemetryV3_20260109_134924 | ❌ | ❌ | 0 | 46 |

### Urgency

| Metric | Value |
|--------|-------|
| Jobs | 51 |
| Complete | 50 |
| Incomplete | 1 |
| Unique prompts | 51 |
| Models configured | 2295 |
| Model responses | 0 |
| Judge evaluations | 2295 |
| Valid 3-judge evals | 2294 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Dimensions | 20 |
| Completeness | 98.0% |

**Incomplete Jobs:**

| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |
|-----|---------------|----------------|---------------|----------|
| job_typical_v2_2_urgency_20260108_023657 | ❌ | ✅ | 44 | 45 |

---

## Data Provenance

### Source
- Job outputs: `outputs/single_prompt_jobs/**/*.json`

### Audit File
- `job_metrics_audit.json` - Complete audit data

### Reproducibility
```bash
python3 scripts/audit_job_metrics.py
```

---

*This audit supports data quality verification for the behavioral profiling research initiative.*
