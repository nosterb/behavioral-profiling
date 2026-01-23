# Missing Jobs Manifest (JUDGE ONLY)

**Updated**: 2026-01-19
**Total Jobs Needing Judge Evaluation**: 39
**Action**: Run `judge_invoke.py --max-parallel 3` on existing job outputs (model responses already exist)

---

## Summary by Condition

| Condition | Jobs | Scale | Judge Config | Responses |
|-----------|------|-------|--------------|-----------|
| minimal_steering | 16 | 1-10 | `behavior.yaml` | ~44 each |
| naturalistic_50 | 8 | 1-50 | `behavior_50.yaml` | ~44 each |
| telemetryV3 | 15 | 1-10 | `behavior.yaml` | ~45 each |

**Completed**: reminder (2 jobs) ✓, naturalistic (20 jobs) ✓

---

## Execution Commands

### Option 1: Run All at Once (per condition)

#### minimal_steering (16 jobs)
```bash
python3 src/judge_invoke.py --max-parallel 3 \
    outputs/single_prompt_jobs/baseline_affective/job_love_v1_6_minimal_steering_20260109_110622/job_love_v1_6_minimal_steering_20260109_110622.json \
    outputs/single_prompt_jobs/baseline_affective/job_love_v1_8_minimal_steering_20260109_110820/job_love_v1_8_minimal_steering_20260109_110820.json \
    outputs/single_prompt_jobs/baseline_affective/job_love_v1_7_minimal_steering_20260109_110658/job_love_v1_7_minimal_steering_20260109_110658.json \
    outputs/single_prompt_jobs/baseline_affective/job_love_v1_5_minimal_steering_20260109_104902/job_love_v1_5_minimal_steering_20260109_104902.json \
    outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_transgression_minimal_steering_20260109_131725/job_dimensions_transgression_minimal_steering_20260109_131725.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_13_minimal_steering_20260109_114443/job_broad_13_minimal_steering_20260109_114443.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_9_minimal_steering_20260109_124329/job_broad_9_minimal_steering_20260109_124329.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_10_minimal_steering_20260109_112749/job_broad_10_minimal_steering_20260109_112749.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_4_minimal_steering_20260109_122441/job_broad_4_minimal_steering_20260109_122441.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_8_minimal_steering_20260109_151316/job_typical_v2_8_minimal_steering_20260109_151316.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_1_minimal_steering_20260109_142434/job_typical_v2_1_minimal_steering_20260109_142434.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_4_minimal_steering_20260109_145224/job_typical_v2_4_minimal_steering_20260109_145224.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_3_minimal_steering_20260109_144150/job_typical_v2_3_minimal_steering_20260109_144150.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_13_minimal_steering_20260109_134546/job_typical_v2_13_minimal_steering_20260109_134546.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_12_minimal_steering_20260109_134233/job_typical_v2_12_minimal_steering_20260109_134233.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_15_minimal_steering_20260109_135914/job_typical_v2_15_minimal_steering_20260109_135914.json
```

#### naturalistic_50 (8 jobs)
```bash
python3 src/judge_invoke.py --max-parallel 3 \
    outputs/single_prompt_jobs/job_naturalistic_20_50_20260118_182115/job_naturalistic_20_50_20260118_182115.json \
    outputs/single_prompt_jobs/job_naturalistic_12_50_20260118_172005/job_naturalistic_12_50_20260118_172005.json \
    outputs/single_prompt_jobs/job_naturalistic_02_50_20260118_161941/job_naturalistic_02_50_20260118_161941.json \
    outputs/single_prompt_jobs/job_naturalistic_09_50_20260118_165737/job_naturalistic_09_50_20260118_165737.json \
    outputs/single_prompt_jobs/job_naturalistic_15_50_20260118_174242/job_naturalistic_15_50_20260118_174242.json \
    outputs/single_prompt_jobs/job_naturalistic_06_50_20260118_163839/job_naturalistic_06_50_20260118_163839.json \
    outputs/single_prompt_jobs/job_naturalistic_08_50_20260118_165722/job_naturalistic_08_50_20260118_165722.json \
    outputs/single_prompt_jobs/job_naturalistic_13_50_20260118_174049/job_naturalistic_13_50_20260118_174049.json
```

#### telemetryV3 (15 jobs)
```bash
python3 src/judge_invoke.py --max-parallel 3 \
    outputs/single_prompt_jobs/baseline_affective/job_love_v1_5_telemetryV3_20260109_013755/job_love_v1_5_telemetryV3_20260109_013755.json \
    outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_transgression_telemetryV3_20260109_112250/job_dimensions_transgression_telemetryV3_20260109_112250.json \
    outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_aggression_telemetryV3_20260109_105716/job_dimensions_aggression_telemetryV3_20260109_105716.json \
    outputs/single_prompt_jobs/baseline_dimensions/job_dimensions_deference_telemetryV3_20260109_110214/job_dimensions_deference_telemetryV3_20260109_110214.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_9_telemetryV3_20260109_104506/job_broad_9_telemetryV3_20260109_104506.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_15_telemetryV3_20260109_095315/job_broad_15_telemetryV3_20260109_095315.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_2_telemetryV3_20260109_095823/job_broad_2_telemetryV3_20260109_095823.json \
    outputs/single_prompt_jobs/baseline_broad/job_broad_3_telemetryV3_20260109_101325/job_broad_3_telemetryV3_20260109_101325.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_1_telemetryV3_20260109_124800/job_typical_v2_1_telemetryV3_20260109_124800.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_7_telemetryV3_20260109_134448/job_typical_v2_7_telemetryV3_20260109_134448.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_19_telemetryV3_20260109_124659/job_typical_v2_19_telemetryV3_20260109_124659.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_17_telemetryV3_20260109_122700/job_typical_v2_17_telemetryV3_20260109_122700.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_8_telemetryV3_20260109_135122/job_typical_v2_8_telemetryV3_20260109_135122.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_15_telemetryV3_20260109_121923/job_typical_v2_15_telemetryV3_20260109_121923.json \
    outputs/single_prompt_jobs/baseline_general/job_typical_v2_4_telemetryV3_20260109_132345/job_typical_v2_4_telemetryV3_20260109_132345.json
```

### Option 2: Run Single Job
```bash
python3 src/judge_invoke.py <path_to_job.json>
```

### Option 3: Run Multiple Jobs with Parallelism
```bash
python3 src/judge_invoke.py --max-parallel 3 <job1.json> <job2.json> <job3.json> ...
```

---

## Detailed Job Inventory

### minimal_steering (16 jobs)

| # | Payload Name | JSON Path | Responses | Valid Evals |
|---|--------------|-----------|-----------|-------------|
| 1 | `broad_10_minimal_steering` | `.../job_broad_10_minimal_steering_20260109_112749/job_broad_10_minimal_steering_20260109_112749.json` | 45 | 0 |
| 2 | `broad_13_minimal_steering` | `.../job_broad_13_minimal_steering_20260109_114443/job_broad_13_minimal_steering_20260109_114443.json` | 44 | 0 |
| 3 | `broad_4_minimal_steering` | `.../job_broad_4_minimal_steering_20260109_122441/job_broad_4_minimal_steering_20260109_122441.json` | 45 | 0 |
| 4 | `broad_9_minimal_steering` | `.../job_broad_9_minimal_steering_20260109_124329/job_broad_9_minimal_steering_20260109_124329.json` | 45 | 0 |
| 5 | `dimensions_transgression_minimal_steering` | `.../job_dimensions_transgression_minimal_steering_20260109_131725/job_dimensions_transgression_minimal_steering_20260109_131725.json` | 45 | 0 |
| 6 | `love_v1_5_minimal_steering` | `.../job_love_v1_5_minimal_steering_20260109_104902/job_love_v1_5_minimal_steering_20260109_104902.json` | 45 | 0 |
| 7 | `love_v1_6_minimal_steering` | `.../job_love_v1_6_minimal_steering_20260109_110622/job_love_v1_6_minimal_steering_20260109_110622.json` | 45 | 0 |
| 8 | `love_v1_7_minimal_steering` | `.../job_love_v1_7_minimal_steering_20260109_110658/job_love_v1_7_minimal_steering_20260109_110658.json` | 45 | 0 |
| 9 | `love_v1_8_minimal_steering` | `.../job_love_v1_8_minimal_steering_20260109_110820/job_love_v1_8_minimal_steering_20260109_110820.json` | 45 | 0 |
| 10 | `typical_v2_12_minimal_steering` | `.../job_typical_v2_12_minimal_steering_20260109_134233/job_typical_v2_12_minimal_steering_20260109_134233.json` | 45 | 0 |
| 11 | `typical_v2_13_minimal_steering` | `.../job_typical_v2_13_minimal_steering_20260109_134546/job_typical_v2_13_minimal_steering_20260109_134546.json` | 45 | 0 |
| 12 | `typical_v2_15_minimal_steering` | `.../job_typical_v2_15_minimal_steering_20260109_135914/job_typical_v2_15_minimal_steering_20260109_135914.json` | 45 | 0 |
| 13 | `typical_v2_1_minimal_steering` | `.../job_typical_v2_1_minimal_steering_20260109_142434/job_typical_v2_1_minimal_steering_20260109_142434.json` | 44 | 0 |
| 14 | `typical_v2_3_minimal_steering` | `.../job_typical_v2_3_minimal_steering_20260109_144150/job_typical_v2_3_minimal_steering_20260109_144150.json` | 45 | 0 |
| 15 | `typical_v2_4_minimal_steering` | `.../job_typical_v2_4_minimal_steering_20260109_145224/job_typical_v2_4_minimal_steering_20260109_145224.json` | 45 | 0 |
| 16 | `typical_v2_8_minimal_steering` | `.../job_typical_v2_8_minimal_steering_20260109_151316/job_typical_v2_8_minimal_steering_20260109_151316.json` | 45 | 0 |

### naturalistic_50 (8 jobs)

| # | Payload Name | JSON Path | Responses | Valid Evals |
|---|--------------|-----------|-----------|-------------|
| 1 | `naturalistic_02_50` | `.../job_naturalistic_02_50_20260118_161941/job_naturalistic_02_50_20260118_161941.json` | 44 | 0 |
| 2 | `naturalistic_06_50` | `.../job_naturalistic_06_50_20260118_163839/job_naturalistic_06_50_20260118_163839.json` | 44 | 0 |
| 3 | `naturalistic_08_50` | `.../job_naturalistic_08_50_20260118_165722/job_naturalistic_08_50_20260118_165722.json` | 44 | 0 |
| 4 | `naturalistic_09_50` | `.../job_naturalistic_09_50_20260118_165737/job_naturalistic_09_50_20260118_165737.json` | 44 | 0 |
| 5 | `naturalistic_12_50` | `.../job_naturalistic_12_50_20260118_172005/job_naturalistic_12_50_20260118_172005.json` | 44 | 0 |
| 6 | `naturalistic_13_50` | `.../job_naturalistic_13_50_20260118_174049/job_naturalistic_13_50_20260118_174049.json` | 44 | 0 |
| 7 | `naturalistic_15_50` | `.../job_naturalistic_15_50_20260118_174242/job_naturalistic_15_50_20260118_174242.json` | 44 | 0 |
| 8 | `naturalistic_20_50` | `.../job_naturalistic_20_50_20260118_182115/job_naturalistic_20_50_20260118_182115.json` | 44 | 0 |

### telemetryV3 (15 jobs)

| # | Payload Name | JSON Path | Responses | Valid Evals |
|---|--------------|-----------|-----------|-------------|
| 1 | `broad_15_telemetryV3` | `.../job_broad_15_telemetryV3_20260109_095315/job_broad_15_telemetryV3_20260109_095315.json` | 45 | 0 |
| 2 | `broad_2_telemetryV3` | `.../job_broad_2_telemetryV3_20260109_095823/job_broad_2_telemetryV3_20260109_095823.json` | 45 | 0 |
| 3 | `broad_3_telemetryV3` | `.../job_broad_3_telemetryV3_20260109_101325/job_broad_3_telemetryV3_20260109_101325.json` | 45 | 0 |
| 4 | `broad_9_telemetryV3` | `.../job_broad_9_telemetryV3_20260109_104506/job_broad_9_telemetryV3_20260109_104506.json` | 45 | 0 |
| 5 | `dimensions_aggression_telemetryV3` | `.../job_dimensions_aggression_telemetryV3_20260109_105716/job_dimensions_aggression_telemetryV3_20260109_105716.json` | 45 | 0 |
| 6 | `dimensions_deference_telemetryV3` | `.../job_dimensions_deference_telemetryV3_20260109_110214/job_dimensions_deference_telemetryV3_20260109_110214.json` | 45 | 0 |
| 7 | `dimensions_transgression_telemetryV3` | `.../job_dimensions_transgression_telemetryV3_20260109_112250/job_dimensions_transgression_telemetryV3_20260109_112250.json` | 45 | 0 |
| 8 | `love_v1_5_telemetryV3` | `.../job_love_v1_5_telemetryV3_20260109_013755/job_love_v1_5_telemetryV3_20260109_013755.json` | 45 | 1 |
| 9 | `typical_v2_15_telemetryV3` | `.../job_typical_v2_15_telemetryV3_20260109_121923/job_typical_v2_15_telemetryV3_20260109_121923.json` | 45 | 0 |
| 10 | `typical_v2_17_telemetryV3` | `.../job_typical_v2_17_telemetryV3_20260109_122700/job_typical_v2_17_telemetryV3_20260109_122700.json` | 45 | 0 |
| 11 | `typical_v2_19_telemetryV3` | `.../job_typical_v2_19_telemetryV3_20260109_124659/job_typical_v2_19_telemetryV3_20260109_124659.json` | 45 | 0 |
| 12 | `typical_v2_1_telemetryV3` | `.../job_typical_v2_1_telemetryV3_20260109_124800/job_typical_v2_1_telemetryV3_20260109_124800.json` | 45 | 0 |
| 13 | `typical_v2_4_telemetryV3` | `.../job_typical_v2_4_telemetryV3_20260109_132345/job_typical_v2_4_telemetryV3_20260109_132345.json` | 45 | 0 |
| 14 | `typical_v2_7_telemetryV3` | `.../job_typical_v2_7_telemetryV3_20260109_134448/job_typical_v2_7_telemetryV3_20260109_134448.json` | 45 | 0 |
| 15 | `typical_v2_8_telemetryV3` | `.../job_typical_v2_8_telemetryV3_20260109_135122/job_typical_v2_8_telemetryV3_20260109_135122.json` | 45 | 0 |

---

## Post-Completion Steps

After judge evaluation completes, run phases 2-5:

```bash
# Phase 2: Re-aggregate profiles
for COND in minimal_steering telemetryV3 naturalistic_50; do
    python3 scripts/update_behavioral_profiles.py \
        outputs/single_prompt_jobs --recursive \
        --condition $COND \
        --profile-dir outputs/behavioral_profiles/$COND
done

# Phase 3: Re-run H1/H2 analysis
for COND in minimal_steering telemetryV3 naturalistic_50; do
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

## Data Provenance

**Manifest JSON**: `research_synthesis/MISSING_JOBS_MANIFEST.json`
**Note**: Model responses already exist - only judge evaluation needed
