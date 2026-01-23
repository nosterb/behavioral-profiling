# Coverage Gap Audit Report

**Generated**: 2026-01-19 15:15
**Total Gaps Verified**: 47
**Action Required**: Judge evaluation only (model responses exist)

---

## Summary

| Condition | Gaps | Scale | Judge Config |
|-----------|------|-------|--------------|
| minimal_steering | 16 | 1-10 | `behavior.yaml` |
| telemetryV3 | 15 | 1-10 | `behavior.yaml` |
| naturalistic | 6 | 1-10 | `behavior.yaml` |
| naturalistic_50 | 8 | 1-50 | `behavior_50.yaml` |
| reminder | 2 | 1-10 | `behavior.yaml` |
| **TOTAL** | **47** | | |

---

## Verified Coverage Gaps (with Evidence)

### minimal_steering (16 gaps)

| # | Payload | File | Responses | Evals | Evidence |
|---|---------|------|-----------|-------|----------|
| 1 | `broad_10_minimal_steering` | [job_broad_10_minimal_steering_20260109_112749.json](outputs/single_prompt_jobs/baseline_broad/job_broad_10_minimal_steering_20260109_112749/job_broad_10_minimal_steering_20260109_112749.json) | 45/46 | **0** | ❌ GAP |
| 2 | `broad_13_minimal_steering` | [job_broad_13_minimal_steering_20260109_114443.json](outputs/single_prompt_jobs/baseline_broad/job_broad_13_minimal_steering_20260109_114443/job_broad_13_minimal_steering_20260109_114443.json) | 44/46 | **0** | ❌ GAP |
| 3 | `broad_4_minimal_steering` | [job_broad_4_minimal_steering_20260109_122441.json](outputs/single_prompt_jobs/baseline_broad/job_broad_4_minimal_steering_20260109_122441/job_broad_4_minimal_steering_20260109_122441.json) | 45/46 | **0** | ❌ GAP |
| 4 | `broad_9_minimal_steering` | [job_broad_9_minimal_steering_20260109_124329.json](outputs/single_prompt_jobs/baseline_broad/job_broad_9_minimal_steering_20260109_124329/job_broad_9_minimal_steering_20260109_124329.json) | 45/46 | **0** | ❌ GAP |
| 5 | `dimensions_transgression_minimal_steering` | [job_dimensions_transgression_minimal_steering_20260109_131725.json](outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_transgression_minimal_steering_20260109_131725/job_dimensions_transgression_minimal_steering_20260109_131725.json) | 45/46 | **0** | ❌ GAP |
| 6 | `love_v1_5_minimal_steering` | [job_love_v1_5_minimal_steering_20260109_104902.json](outputs/single_prompt_jobs/baseline_affective/job_love_v1_5_minimal_steering_20260109_104902/job_love_v1_5_minimal_steering_20260109_104902.json) | 45/46 | **0** | ❌ GAP |
| 7 | `love_v1_6_minimal_steering` | [job_love_v1_6_minimal_steering_20260109_110622.json](outputs/single_prompt_jobs/baseline_affective/job_love_v1_6_minimal_steering_20260109_110622/job_love_v1_6_minimal_steering_20260109_110622.json) | 45/46 | **0** | ❌ GAP |
| 8 | `love_v1_7_minimal_steering` | [job_love_v1_7_minimal_steering_20260109_110658.json](outputs/single_prompt_jobs/baseline_affective/job_love_v1_7_minimal_steering_20260109_110658/job_love_v1_7_minimal_steering_20260109_110658.json) | 45/46 | **0** | ❌ GAP |
| 9 | `love_v1_8_minimal_steering` | [job_love_v1_8_minimal_steering_20260109_110820.json](outputs/single_prompt_jobs/baseline_affective/job_love_v1_8_minimal_steering_20260109_110820/job_love_v1_8_minimal_steering_20260109_110820.json) | 45/46 | **0** | ❌ GAP |
| 10 | `typical_v2_12_minimal_steering` | [job_typical_v2_12_minimal_steering_20260109_134233.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_12_minimal_steering_20260109_134233/job_typical_v2_12_minimal_steering_20260109_134233.json) | 45/46 | **0** | ❌ GAP |
| 11 | `typical_v2_13_minimal_steering` | [job_typical_v2_13_minimal_steering_20260109_134546.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_13_minimal_steering_20260109_134546/job_typical_v2_13_minimal_steering_20260109_134546.json) | 45/46 | **0** | ❌ GAP |
| 12 | `typical_v2_15_minimal_steering` | [job_typical_v2_15_minimal_steering_20260109_135914.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_15_minimal_steering_20260109_135914/job_typical_v2_15_minimal_steering_20260109_135914.json) | 45/46 | **0** | ❌ GAP |
| 13 | `typical_v2_1_minimal_steering` | [job_typical_v2_1_minimal_steering_20260109_142434.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_1_minimal_steering_20260109_142434/job_typical_v2_1_minimal_steering_20260109_142434.json) | 44/46 | **0** | ❌ GAP |
| 14 | `typical_v2_3_minimal_steering` | [job_typical_v2_3_minimal_steering_20260109_144150.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_3_minimal_steering_20260109_144150/job_typical_v2_3_minimal_steering_20260109_144150.json) | 45/46 | **0** | ❌ GAP |
| 15 | `typical_v2_4_minimal_steering` | [job_typical_v2_4_minimal_steering_20260109_145224.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_4_minimal_steering_20260109_145224/job_typical_v2_4_minimal_steering_20260109_145224.json) | 45/46 | **0** | ❌ GAP |
| 16 | `typical_v2_8_minimal_steering` | [job_typical_v2_8_minimal_steering_20260109_151316.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_8_minimal_steering_20260109_151316/job_typical_v2_8_minimal_steering_20260109_151316.json) | 45/46 | **0** | ❌ GAP |

---

### telemetryV3 (15 gaps)

| # | Payload | File | Responses | Evals | Evidence |
|---|---------|------|-----------|-------|----------|
| 1 | `broad_15_telemetryV3` | [job_broad_15_telemetryV3_20260109_095315.json](outputs/single_prompt_jobs/baseline_broad/job_broad_15_telemetryV3_20260109_095315/job_broad_15_telemetryV3_20260109_095315.json) | 45/46 | **0** | ❌ GAP |
| 2 | `broad_2_telemetryV3` | [job_broad_2_telemetryV3_20260109_095823.json](outputs/single_prompt_jobs/baseline_broad/job_broad_2_telemetryV3_20260109_095823/job_broad_2_telemetryV3_20260109_095823.json) | 45/46 | **0** | ❌ GAP |
| 3 | `broad_3_telemetryV3` | [job_broad_3_telemetryV3_20260109_101325.json](outputs/single_prompt_jobs/baseline_broad/job_broad_3_telemetryV3_20260109_101325/job_broad_3_telemetryV3_20260109_101325.json) | 45/46 | **0** | ❌ GAP |
| 4 | `broad_9_telemetryV3` | [job_broad_9_telemetryV3_20260109_104506.json](outputs/single_prompt_jobs/baseline_broad/job_broad_9_telemetryV3_20260109_104506/job_broad_9_telemetryV3_20260109_104506.json) | 45/46 | **0** | ❌ GAP |
| 5 | `dimensions_aggression_telemetryV3` | [job_dimensions_aggression_telemetryV3_20260109_105716.json](outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_aggression_telemetryV3_20260109_105716/job_dimensions_aggression_telemetryV3_20260109_105716.json) | 45/46 | **0** | ❌ GAP |
| 6 | `dimensions_deference_telemetryV3` | [job_dimensions_deference_telemetryV3_20260109_110214.json](outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_deference_telemetryV3_20260109_110214/job_dimensions_deference_telemetryV3_20260109_110214.json) | 45/46 | **0** | ❌ GAP |
| 7 | `dimensions_transgression_telemetryV3` | [job_dimensions_transgression_telemetryV3_20260109_112250.json](outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_transgression_telemetryV3_20260109_112250/job_dimensions_transgression_telemetryV3_20260109_112250.json) | 45/46 | **0** | ❌ GAP |
| 8 | `love_v1_5_telemetryV3` | [job_love_v1_5_telemetryV3_20260109_013755.json](outputs/single_prompt_jobs/baseline_affective/job_love_v1_5_telemetryV3_20260109_013755/job_love_v1_5_telemetryV3_20260109_013755.json) | 45/46 | **1** | ❌ GAP (partial) |
| 9 | `typical_v2_15_telemetryV3` | [job_typical_v2_15_telemetryV3_20260109_121923.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_15_telemetryV3_20260109_121923/job_typical_v2_15_telemetryV3_20260109_121923.json) | 45/46 | **0** | ❌ GAP |
| 10 | `typical_v2_17_telemetryV3` | [job_typical_v2_17_telemetryV3_20260109_122700.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_17_telemetryV3_20260109_122700/job_typical_v2_17_telemetryV3_20260109_122700.json) | 45/46 | **0** | ❌ GAP |
| 11 | `typical_v2_19_telemetryV3` | [job_typical_v2_19_telemetryV3_20260109_124659.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_19_telemetryV3_20260109_124659/job_typical_v2_19_telemetryV3_20260109_124659.json) | 45/46 | **0** | ❌ GAP |
| 12 | `typical_v2_1_telemetryV3` | [job_typical_v2_1_telemetryV3_20260109_124800.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_1_telemetryV3_20260109_124800/job_typical_v2_1_telemetryV3_20260109_124800.json) | 45/46 | **0** | ❌ GAP |
| 13 | `typical_v2_4_telemetryV3` | [job_typical_v2_4_telemetryV3_20260109_132345.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_4_telemetryV3_20260109_132345/job_typical_v2_4_telemetryV3_20260109_132345.json) | 45/46 | **0** | ❌ GAP |
| 14 | `typical_v2_7_telemetryV3` | [job_typical_v2_7_telemetryV3_20260109_134448.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_7_telemetryV3_20260109_134448/job_typical_v2_7_telemetryV3_20260109_134448.json) | 45/46 | **0** | ❌ GAP |
| 15 | `typical_v2_8_telemetryV3` | [job_typical_v2_8_telemetryV3_20260109_135122.json](outputs/single_prompt_jobs/baseline_general/job_typical_v2_8_telemetryV3_20260109_135122/job_typical_v2_8_telemetryV3_20260109_135122.json) | 45/46 | **0** | ❌ GAP |

---

### naturalistic (6 gaps)

| # | Payload | File | Responses | Evals | Evidence |
|---|---------|------|-----------|-------|----------|
| 1 | `naturalistic_03` | [job_naturalistic_03_20260118_135724.json](outputs/single_prompt_jobs/naturalistic/job_naturalistic_03_20260118_135724/job_naturalistic_03_20260118_135724.json) | 44/45 | **0** | ❌ GAP |
| 2 | `naturalistic_05` | [job_naturalistic_05_20260118_141913.json](outputs/single_prompt_jobs/naturalistic/job_naturalistic_05_20260118_141913/job_naturalistic_05_20260118_141913.json) | 44/45 | **0** | ❌ GAP |
| 3 | `naturalistic_09` | [job_naturalistic_09_20260118_143758.json](outputs/single_prompt_jobs/naturalistic/job_naturalistic_09_20260118_143758/job_naturalistic_09_20260118_143758.json) | 44/45 | **0** | ❌ GAP |
| 4 | `naturalistic_11` | [job_naturalistic_11_20260118_145752.json](outputs/single_prompt_jobs/naturalistic/job_naturalistic_11_20260118_145752/job_naturalistic_11_20260118_145752.json) | 44/45 | **0** | ❌ GAP |
| 5 | `naturalistic_16` | [job_naturalistic_16_20260118_153702.json](outputs/single_prompt_jobs/naturalistic/job_naturalistic_16_20260118_153702/job_naturalistic_16_20260118_153702.json) | 44/45 | **0** | ❌ GAP |
| 6 | `naturalistic_20` | [job_naturalistic_20_20260118_155708.json](outputs/single_prompt_jobs/naturalistic/job_naturalistic_20_20260118_155708/job_naturalistic_20_20260118_155708.json) | 44/45 | **0** | ❌ GAP |

---

### naturalistic_50 (8 gaps)

| # | Payload | File | Responses | Evals | Evidence |
|---|---------|------|-----------|-------|----------|
| 1 | `naturalistic_02_50` | [job_naturalistic_02_50_20260118_161941.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_02_50_20260118_161941/job_naturalistic_02_50_20260118_161941.json) | 44/45 | **0** | ❌ GAP |
| 2 | `naturalistic_06_50` | [job_naturalistic_06_50_20260118_163839.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_06_50_20260118_163839/job_naturalistic_06_50_20260118_163839.json) | 44/45 | **0** | ❌ GAP |
| 3 | `naturalistic_08_50` | [job_naturalistic_08_50_20260118_165722.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_08_50_20260118_165722/job_naturalistic_08_50_20260118_165722.json) | 44/45 | **0** | ❌ GAP |
| 4 | `naturalistic_09_50` | [job_naturalistic_09_50_20260118_165737.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_09_50_20260118_165737/job_naturalistic_09_50_20260118_165737.json) | 44/45 | **0** | ❌ GAP |
| 5 | `naturalistic_12_50` | [job_naturalistic_12_50_20260118_172005.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_12_50_20260118_172005/job_naturalistic_12_50_20260118_172005.json) | 44/45 | **0** | ❌ GAP |
| 6 | `naturalistic_13_50` | [job_naturalistic_13_50_20260118_174049.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_13_50_20260118_174049/job_naturalistic_13_50_20260118_174049.json) | 44/45 | **0** | ❌ GAP |
| 7 | `naturalistic_15_50` | [job_naturalistic_15_50_20260118_174242.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_15_50_20260118_174242/job_naturalistic_15_50_20260118_174242.json) | 44/45 | **0** | ❌ GAP |
| 8 | `naturalistic_20_50` | [job_naturalistic_20_50_20260118_182115.json](outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_20_50_20260118_182115/job_naturalistic_20_50_20260118_182115.json) | 44/45 | **0** | ❌ GAP |

---

### reminder (2 gaps)

| # | Payload | File | Responses | Evals | Evidence |
|---|---------|------|-----------|-------|----------|
| 1 | `dimensions_dominance_1_reminder` | [job_dimensions_dominance_1_reminder_20260110_201521.json](outputs/single_prompt_jobs/baseline_reminder/job_dimensions_dominance_1_reminder_20260110_201521/job_dimensions_dominance_1_reminder_20260110_201521.json) | 45/46 | **0** | ❌ GAP |
| 2 | `dimensions_transgression_1_reminder` | [job_dimensions_transgression_1_reminder_20260110_203131.json](outputs/single_prompt_jobs/baseline_reminder/job_dimensions_transgression_1_reminder_20260110_203131/job_dimensions_transgression_1_reminder_20260110_203131.json) | 45/46 | **0** | ❌ GAP |

---

## Execution Commands

### reminder (2 jobs) — Start here (smallest)
```bash
python3 src/judge_invoke.py \
    "outputs/single_prompt_jobs/baseline_reminder/job_dimensions_dominance_1_reminder_20260110_201521/job_dimensions_dominance_1_reminder_20260110_201521.json" \
    "outputs/single_prompt_jobs/baseline_reminder/job_dimensions_transgression_1_reminder_20260110_203131/job_dimensions_transgression_1_reminder_20260110_203131.json" \
    --max-parallel 3
```

### naturalistic (6 jobs)
```bash
python3 src/judge_invoke.py \
    "outputs/single_prompt_jobs/naturalistic/job_naturalistic_03_20260118_135724/job_naturalistic_03_20260118_135724.json" \
    "outputs/single_prompt_jobs/naturalistic/job_naturalistic_05_20260118_141913/job_naturalistic_05_20260118_141913.json" \
    "outputs/single_prompt_jobs/naturalistic/job_naturalistic_09_20260118_143758/job_naturalistic_09_20260118_143758.json" \
    "outputs/single_prompt_jobs/naturalistic/job_naturalistic_11_20260118_145752/job_naturalistic_11_20260118_145752.json" \
    "outputs/single_prompt_jobs/naturalistic/job_naturalistic_16_20260118_153702/job_naturalistic_16_20260118_153702.json" \
    "outputs/single_prompt_jobs/naturalistic/job_naturalistic_20_20260118_155708/job_naturalistic_20_20260118_155708.json" \
    --max-parallel 3
```

### naturalistic_50 (8 jobs) — Uses 1-50 scale
```bash
python3 src/judge_invoke.py \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_02_50_20260118_161941/job_naturalistic_02_50_20260118_161941.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_06_50_20260118_163839/job_naturalistic_06_50_20260118_163839.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_08_50_20260118_165722/job_naturalistic_08_50_20260118_165722.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_09_50_20260118_165737/job_naturalistic_09_50_20260118_165737.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_12_50_20260118_172005/job_naturalistic_12_50_20260118_172005.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_13_50_20260118_174049/job_naturalistic_13_50_20260118_174049.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_15_50_20260118_174242/job_naturalistic_15_50_20260118_174242.json" \
    "outputs/single_prompt_jobs/naturalistic_50/job_naturalistic_20_50_20260118_182115/job_naturalistic_20_50_20260118_182115.json" \
    --max-parallel 3
```

### telemetryV3 (15 jobs)
```bash
python3 src/judge_invoke.py \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_15_telemetryV3_20260109_095315/job_broad_15_telemetryV3_20260109_095315.json" \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_2_telemetryV3_20260109_095823/job_broad_2_telemetryV3_20260109_095823.json" \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_3_telemetryV3_20260109_101325/job_broad_3_telemetryV3_20260109_101325.json" \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_9_telemetryV3_20260109_104506/job_broad_9_telemetryV3_20260109_104506.json" \
    "outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_aggression_telemetryV3_20260109_105716/job_dimensions_aggression_telemetryV3_20260109_105716.json" \
    "outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_deference_telemetryV3_20260109_110214/job_dimensions_deference_telemetryV3_20260109_110214.json" \
    "outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_transgression_telemetryV3_20260109_112250/job_dimensions_transgression_telemetryV3_20260109_112250.json" \
    "outputs/single_prompt_jobs/baseline_affective/job_love_v1_5_telemetryV3_20260109_013755/job_love_v1_5_telemetryV3_20260109_013755.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_15_telemetryV3_20260109_121923/job_typical_v2_15_telemetryV3_20260109_121923.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_17_telemetryV3_20260109_122700/job_typical_v2_17_telemetryV3_20260109_122700.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_19_telemetryV3_20260109_124659/job_typical_v2_19_telemetryV3_20260109_124659.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_1_telemetryV3_20260109_124800/job_typical_v2_1_telemetryV3_20260109_124800.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_4_telemetryV3_20260109_132345/job_typical_v2_4_telemetryV3_20260109_132345.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_7_telemetryV3_20260109_134448/job_typical_v2_7_telemetryV3_20260109_134448.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_8_telemetryV3_20260109_135122/job_typical_v2_8_telemetryV3_20260109_135122.json" \
    --max-parallel 3
```

### minimal_steering (16 jobs)
```bash
python3 src/judge_invoke.py \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_10_minimal_steering_20260109_112749/job_broad_10_minimal_steering_20260109_112749.json" \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_13_minimal_steering_20260109_114443/job_broad_13_minimal_steering_20260109_114443.json" \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_4_minimal_steering_20260109_122441/job_broad_4_minimal_steering_20260109_122441.json" \
    "outputs/single_prompt_jobs/baseline_broad/job_broad_9_minimal_steering_20260109_124329/job_broad_9_minimal_steering_20260109_124329.json" \
    "outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_transgression_minimal_steering_20260109_131725/job_dimensions_transgression_minimal_steering_20260109_131725.json" \
    "outputs/single_prompt_jobs/baseline_affective/job_love_v1_5_minimal_steering_20260109_104902/job_love_v1_5_minimal_steering_20260109_104902.json" \
    "outputs/single_prompt_jobs/baseline_affective/job_love_v1_6_minimal_steering_20260109_110622/job_love_v1_6_minimal_steering_20260109_110622.json" \
    "outputs/single_prompt_jobs/baseline_affective/job_love_v1_7_minimal_steering_20260109_110658/job_love_v1_7_minimal_steering_20260109_110658.json" \
    "outputs/single_prompt_jobs/baseline_affective/job_love_v1_8_minimal_steering_20260109_110820/job_love_v1_8_minimal_steering_20260109_110820.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_12_minimal_steering_20260109_134233/job_typical_v2_12_minimal_steering_20260109_134233.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_13_minimal_steering_20260109_134546/job_typical_v2_13_minimal_steering_20260109_134546.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_15_minimal_steering_20260109_135914/job_typical_v2_15_minimal_steering_20260109_135914.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_1_minimal_steering_20260109_142434/job_typical_v2_1_minimal_steering_20260109_142434.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_3_minimal_steering_20260109_144150/job_typical_v2_3_minimal_steering_20260109_144150.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_4_minimal_steering_20260109_145224/job_typical_v2_4_minimal_steering_20260109_145224.json" \
    "outputs/single_prompt_jobs/baseline_general/job_typical_v2_8_minimal_steering_20260109_151316/job_typical_v2_8_minimal_steering_20260109_151316.json" \
    --max-parallel 3
```

---

## Post-Completion Steps

After all judge evaluations complete:

```bash
# Phase 2: Re-aggregate profiles
for COND in minimal_steering telemetryV3 reminder naturalistic naturalistic_50; do
    python3 scripts/update_behavioral_profiles.py \
        outputs/single_prompt_jobs --recursive \
        --condition $COND \
        --profile-dir outputs/behavioral_profiles/$COND
done

# Phase 3: Re-run H1/H2 analysis
for COND in minimal_steering telemetryV3 reminder naturalistic naturalistic_50; do
    ./scripts/run_complete_h1_h2_analysis.sh $COND
done

# Phase 4: Update statistical analyses
python3 scripts/check_statistical_assumptions.py --all
python3 scripts/check_judge_agreement.py --all

# Phase 5: Update cross-condition docs
python3 scripts/update_cross_condition_comparison.py
python3 scripts/regenerate_main_brief.py
```

---

## Audit Metadata

**Audit Method**: Direct JSON inspection of each job file
**Evidence Criteria**: `valid_3judge_evals < 40` AND `successful_responses >= 40`
**Generated By**: Coverage gap audit script
**JSON Audit**: [COVERAGE_GAP_AUDIT.json](outputs/behavioral_profiles/research_synthesis/COVERAGE_GAP_AUDIT.json)
