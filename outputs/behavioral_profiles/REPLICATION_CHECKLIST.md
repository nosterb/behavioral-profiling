# Condition Replication Checklist

Quick reference for creating or auditing a condition directory. See `CONDITION_BEST_PRACTICES.md` for full documentation.

---

## Pre-Requisites

- [ ] Jobs exist in `outputs/single_prompt_jobs/`
- [ ] Jobs have `judge_evaluation` with 3-judge panels (or `judge_evaluation_telemetry` for telemetryV3)
- [ ] At least 40 models with valid evaluations
- [ ] All 9 dimensions scored (warmth, formality, hedging, aggression, transgression, grandiosity, tribalism, depth, authenticity)

---

## Stage-by-Stage Execution (Required)

### Stage 1: Profile Aggregation

```bash
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition <CONDITION> \
    --profile-dir outputs/behavioral_profiles/<CONDITION>
```

**Verify**:
- [ ] `profiles/` directory has ~45 JSON files
- [ ] `history/contributions.json` exists
- [ ] `history/updates_log.json` exists

### Stage 2-5: Core H1/H2 Pipeline

```bash
./scripts/run_complete_h1_h2_analysis.sh <CONDITION>
```

**Verify**:
- [ ] `median_split_classification.json` - Valid JSON, median 4-7, balanced groups
- [ ] `h1_bar_chart_comparison.png` - Renders, shows condition label
- [ ] `h1_summary_table.png` - Shows effect sizes
- [ ] `h2_scatter_sophistication_composite.png` - Shows regression line, r value
- [ ] `h2_scatter_all_dimensions.png` - 4-panel grid
- [ ] `RESEARCH_BRIEF.md` - Complete with all sections
- [ ] `all_models_data.csv` - 45 rows
- [ ] `comprehensive_stats.json` - Provider breakdown

### Stage 6: Statistical Assumptions

```bash
python3 scripts/analyze_statistical_assumptions.py <CONDITION>
```

**Verify** (in `statistical_assumptions/`):
- [ ] `normality_audit.json` - Schema version 1.1, has provenance
- [ ] `STATISTICAL_ASSUMPTIONS_BRIEF.md` - Human-readable summary
- [ ] 5 distribution PNGs exist

### Stage 7: Outlier Sensitivity

```bash
python3 scripts/analyze_outliers_removed.py <CONDITION>
```

**Verify** (in `outliers_removed/`):
- [ ] `outlier_removal_info.json` - Lists removed models
- [ ] `RESEARCH_BRIEF.md` - Sensitivity analysis report
- [ ] Full H1/H2 visualization set
- [ ] `profiles/` and `history/` subdirectories

### Stage 8: Judge Agreement

```bash
python3 scripts/analyze_judge_agreement.py <CONDITION>
```

**Verify** (in `judge_agreement/`):
- [ ] `judge_agreement_audit.json` - ICC, Krippendorff's alpha values
- [ ] `JUDGE_AGREEMENT_BRIEF.md` - Interpretation

---

## Optional Stages

### Qualitative Examples (Optional)

```bash
python3 scripts/extract_qualitative_examples.py <CONDITION>
```

**Verify**:
- [ ] `qualitative_examples.json` - Inventory with categories
- [ ] `qualitative_chats/` - Markdown chat exports

### Job Audit (Optional)

```bash
python3 scripts/audit_condition_jobs.py <CONDITION>
```

**Verify**:
- [ ] `job_audit.json` - All jobs listed with completeness status
- [ ] `DATA_AUDIT.md` - Summary table

---

## Provider Analysis (Stage 4 Details)

```bash
python3 scripts/create_provider_summary.py <CONDITION>
python3 scripts/create_provider_h2_scatters.py <CONDITION>
python3 scripts/analyze_all_models_by_provider.py <CONDITION>
python3 scripts/analyze_provider_comparisons.py <CONDITION>
```

**Verify**:
- [ ] `provider_summary.png` - 4-panel overview
- [ ] `provider_h2_scatters.png` - Provider-colored correlations
- [ ] `all_dimensions_by_provider.png` - 3×3 dimension grid
- [ ] `provider_dimensions_heatmap.png` - Heatmap visualization
- [ ] `provider_comparison_stats.json` - ANOVA results
- [ ] `provider_comparison_summary.png` - Comparison panels
- [ ] `provider_comparison_dimensions.png` - Dimension comparison

---

## File Count Verification

```bash
find outputs/behavioral_profiles/<CONDITION> -type f | wc -l
```

| Metric | Minimum | Expected |
|--------|---------|----------|
| Root files | 15 | 17 |
| profiles/ | 40 | 45 |
| Total files | 100 | ~120 |

---

## Quality Checks

### Statistical Quality
- [ ] Cohen's d reported with interpretation
- [ ] Pearson r with p-value (exact or < .001)
- [ ] All effect sizes have magnitude labels (small/medium/large)
- [ ] Bonferroni correction applied to pairwise comparisons

### Visualization Quality
- [ ] All PNGs have condition label in title
- [ ] Regression lines present with stats box
- [ ] Special patterns highlighted (outliers, constrained, borderline)
- [ ] Model labels readable (no overlap)

### Data Integrity
- [ ] All scores in range [1, 10]
- [ ] No NaN/null values in statistical outputs
- [ ] Contribution counts > 0 for all models
- [ ] Median sophistication between 4-7

---

## Provenance Audit Checklist

For each analysis output, verify:

- [ ] `metadata.generated` - ISO timestamp present
- [ ] `metadata.condition` - Matches directory name
- [ ] `metadata.n_models` - Matches profile count
- [ ] `provenance.source_files` - Paths exist and are valid
- [ ] `provenance.methodology` - Methods documented
- [ ] `output_files` - Listed files actually exist

---

## Troubleshooting Quick Reference

| Symptom | Check | Fix |
|---------|-------|-----|
| Empty profiles/ | Job judge_evaluation | Run judge_invoke.py |
| N < 40 models | Missing jobs | Check job list completeness |
| Median outside 4-7 | Score distribution | Review judge calibration |
| PNG fails | matplotlib backend | Use Agg backend |
| telemetryV3 empty | Wrong key | Use judge_evaluation_telemetry |
| NaN in stats | Missing dimensions | Check profile completeness |

---

## Cross-Condition Updates

After completing a new condition, run:

```bash
# Update cross-condition comparison
python3 scripts/update_cross_condition_comparison.py

# Update aggregate profiles (root-level)
python3 scripts/aggregate_all_conditions.py

# Regenerate main research brief
python3 scripts/regenerate_main_brief.py
```

---

## Reference Commands

```bash
# Full pipeline (new condition)
CONDITION=<name>
python3 scripts/update_behavioral_profiles.py outputs/single_prompt_jobs --recursive --condition $CONDITION --profile-dir outputs/behavioral_profiles/$CONDITION
./scripts/run_complete_h1_h2_analysis.sh $CONDITION
python3 scripts/analyze_statistical_assumptions.py $CONDITION
python3 scripts/analyze_outliers_removed.py $CONDITION
python3 scripts/analyze_judge_agreement.py $CONDITION

# Verify
ls -la outputs/behavioral_profiles/$CONDITION/ | head -30
find outputs/behavioral_profiles/$CONDITION -type f | wc -l
# Expected: ~17 root files, ~120 total files
```
