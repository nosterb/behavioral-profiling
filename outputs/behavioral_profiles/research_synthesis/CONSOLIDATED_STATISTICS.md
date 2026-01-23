# CONSOLIDATED STATISTICS
Generated: 2026-01-23

---

## 0. GLOBAL SUMMARY

| Metric | Value |
|--------|-------|
| Conditions | 8 |
| Condition Names | baseline, authority, urgency, minimal_steering, telemetryV3, reminder, naturalistic, all_combined |
| Models (max per condition) | 45 |
| Total Judge Evaluations | 14,088 |
| Total BERT Evaluations | 14,203 |
| Unique Providers | 9 (AWS, Alibaba, Anthropic, DeepSeek, Google, Meta, Mistral, OpenAI, xAI) |

---

## 1. H1/H2 CORE STATISTICS

| Condition | N | Median_Soph | N_High | N_Low | H1_d | H1_p | H2_r |
|-----------|---|-------------|--------|-------|------|------|------|
| baseline | 45 | 5.937 | 23 | 22 | 2.13 | 7.75e-09 | 0.778 |
| authority | 45 | 6.722 | 23 | 22 | 1.84 | 1.99e-07 | 0.770 |
| urgency | 45 | 6.173 | 23 | 22 | 1.77 | 4.68e-07 | 0.743 |
| minimal_steering | 45 | 5.422 | 23 | 22 | 2.32 | 9.57e-10 | 0.854 |
| telemetryV3 | 45 | 5.106 | 23 | 22 | 1.09 | 0.0007 | 0.625 |
| reminder | 45 | 6.911 | 23 | 22 | 1.65 | 1.77e-06 | 0.720 |
| naturalistic | 44 | 6.357 | 22 | 22 | 2.09 | 1.83e-08 | 0.841 |
| all_combined | 45 | 7.025 | 23 | 22 | 2.30 | 1.25e-09 | 0.815 |

---

## 2. H1/H2 OUTLIERS REMOVED

| Condition | N_Orig | N_Removed | N_Final | H1_d | H1_p | H2_r |
|-----------|--------|-----------|---------|------|------|------|
| baseline | 45 | 1 | 44 | 2.84 | 6.17e-12 | 0.819 |
| authority | 45 | 1 | 44 | 2.43 | 4.60e-10 | 0.830 |
| urgency | 45 | 1 | 44 | 1.82 | 3.43e-07 | 0.768 |
| minimal_steering | 45 | 2 | 43 | 2.46 | 5.71e-10 | 0.875 |
| telemetryV3 | 45 | 2 | 43 | 1.80 | 6.04e-07 | 0.799 |
| reminder | 45 | 1 | 44 | 2.18 | 6.51e-09 | 0.806 |
| naturalistic | 44 | 0 | 44 | 2.40 | 6.35e-10 | 0.911 |
| all_combined | 45 | 1 | 44 | 2.80 | 9.66e-12 | 0.857 |

---

## 3. BERT VALIDATION - TOXICITY vs AGGRESSION

| Condition | N | Evaluations | r_tox | p_tox | r_ins | p_ins |
|-----------|---|-------------|-------|-------|-------|-------|
| baseline | 45 | 2,234 | 0.776 | 3.65e-10 | 0.624 | 4.74e-06 |
| authority | 45 | 2,238 | 0.355 | 0.0166 | 0.356 | 0.0165 |
| urgency | 45 | 2,236 | 0.352 | 0.0178 | 0.414 | 0.0047 |
| minimal_steering | 45 | 2,292 | 0.635 | 2.79e-06 | 0.562 | 5.83e-05 |
| telemetryV3 | 45 | 2,290 | 0.492 | 0.0006 | 0.264 | 0.0799 |
| reminder | 45 | 674 | 0.562 | 5.84e-05 | 0.525 | 0.0002 |
| naturalistic | 44 | 2,239 | 0.478 | 0.0010 | 0.497 | 0.0006 |
| all_combined | 45 | 14,203 | 0.606 | 1.02e-05 | 0.516 | 0.0003 |

---

## 4. BERT VALIDATION - OUTLIERS REMOVED

| Condition | N | N_Removed | r_tox | p_tox | r_ins | p_ins |
|-----------|---|-----------|-------|-------|-------|-------|
| all_combined | 40 | 5 | 0.770 | 6.29e-09 | 0.742 | 4.34e-08 |

---

## 5. BERT vs SOPHISTICATION/DISINHIBITION

| Condition | r_tox_soph | p | r_tox_disin | p | r_ins_soph | p | r_ins_disin | p |
|-----------|------------|---|-------------|---|------------|---|-------------|---|
| baseline | 0.510 | 0.0003 | 0.776 | 3.96e-10 | 0.357 | 0.0159 | 0.555 | 7.66e-05 |
| authority | 0.471 | 0.0011 | 0.348 | 0.0193 | 0.314 | 0.0360 | 0.365 | 0.0138 |
| urgency | 0.602 | 1.19e-05 | 0.342 | 0.0215 | 0.440 | 0.0025 | 0.390 | 0.0081 |
| minimal_steering | 0.512 | 0.0003 | 0.590 | 1.97e-05 | 0.417 | 0.0044 | 0.522 | 0.0002 |
| telemetryV3 | 0.682 | 2.51e-07 | 0.511 | 0.0003 | 0.455 | 0.0017 | 0.281 | 0.0617 |
| reminder | 0.487 | 0.0007 | 0.579 | 3.07e-05 | 0.427 | 0.0034 | 0.541 | 0.0001 |
| naturalistic | 0.612 | 9.95e-06 | 0.454 | 0.0020 | 0.603 | 1.51e-05 | 0.483 | 0.0009 |

---

## 6. JUDGE AGREEMENT - ICC(3)

| Condition | N_Evals | Overall | warm | form | hedge | aggr | trans | grand | trib | depth | auth |
|-----------|---------|---------|------|------|-------|------|-------|-------|------|-------|------|
| baseline | 2,252 | 0.808 | 0.89 | 0.67 | 0.83 | 0.93 | 0.85 | 0.69 | 0.85 | 0.74 | 0.80 |
| authority | 2,261 | 0.765 | 0.74 | 0.68 | 0.87 | 0.88 | 0.78 | 0.58 | 0.77 | 0.81 | 0.77 |
| urgency | 2,259 | 0.835 | 0.89 | 0.69 | 0.87 | 0.93 | 0.82 | 0.86 | 0.87 | 0.75 | 0.84 |
| minimal_steering | 2,317 | 0.718 | 0.90 | 0.58 | 0.80 | 0.86 | 0.76 | 0.36 | 0.73 | 0.71 | 0.76 |
| telemetryV3 | 2,094 | 0.795 | 0.91 | 0.71 | 0.79 | 0.86 | 0.84 | 0.65 | 0.81 | 0.80 | 0.79 |
| reminder | 674 | 0.827 | 0.91 | 0.57 | 0.84 | 0.95 | 0.89 | 0.81 | 0.87 | 0.76 | 0.85 |
| naturalistic | 2,231 | 0.629 | 0.79 | 0.51 | 0.80 | 0.63 | 0.71 | 0.00 | 0.63 | 0.81 | 0.78 |
| all_combined | 12,160 | 0.833 | 0.89 | 0.69 | 0.89 | 0.93 | 0.84 | 0.82 | 0.85 | 0.79 | 0.82 |

---

## 7. PER-DIMENSION H1 EFFECT SIZES (Cohen's d)

| Condition | warm | form | hedge | aggr | trans | grand | trib | depth | auth | soph | disin |
|-----------|------|------|-------|------|-------|-------|------|-------|------|------|-------|
| baseline | 0.82 | -1.58 | -1.08 | 2.17 | 1.81 | 1.71 | 1.26 | 3.49 | 3.70 | 3.75 | 2.13 |
| authority | -0.22 | -0.42 | 0.54 | 1.79 | 1.97 | 0.96 | 0.98 | 2.93 | 4.44 | 4.19 | 1.84 |
| urgency | -0.18 | -0.72 | -1.02 | 1.81 | 1.80 | 1.25 | 1.44 | 3.88 | 3.80 | 4.25 | 1.77 |
| minimal_steering | -0.27 | -1.57 | -1.60 | 2.13 | 1.89 | 0.96 | 1.28 | 4.58 | 3.96 | 4.36 | 2.32 |
| telemetryV3 | 1.48 | -0.11 | -0.18 | 0.80 | 1.07 | 1.21 | 0.60 | 3.94 | 3.24 | 3.67 | 1.09 |
| reminder | -0.18 | -2.57 | -1.11 | 1.73 | 2.28 | 0.70 | 0.92 | 3.51 | 4.33 | 4.14 | 1.65 |
| naturalistic | 0.75 | -1.06 | -0.98 | 2.08 | 1.28 | 1.83 | 1.29 | 3.18 | 3.48 | 3.51 | 2.09 |
| all_combined | 0.44 | -1.29 | -1.27 | 2.25 | 2.06 | 1.62 | 1.66 | 3.45 | 3.68 | 3.73 | 2.30 |

---

## 8. DIMENSION MEANS (ALL MODELS)

| Condition | warm | form | hedge | aggr | trans | grand | trib | depth | auth |
|-----------|------|------|-------|------|-------|-------|------|-------|------|
| baseline | 6.02 | 6.92 | 4.25 | 1.45 | 1.63 | 1.90 | 1.17 | 6.51 | 5.29 |
| authority | 5.39 | 7.72 | 7.39 | 1.48 | 1.69 | 2.25 | 1.13 | 7.02 | 5.89 |
| urgency | 4.55 | 7.45 | 3.55 | 2.71 | 2.25 | 3.15 | 1.41 | 6.61 | 5.58 |
| minimal_steering | 6.38 | 6.93 | 4.62 | 1.25 | 1.44 | 1.70 | 1.07 | 6.05 | 4.90 |
| telemetryV3 | 5.87 | 6.86 | 4.38 | 1.24 | 1.40 | 1.60 | 1.09 | 5.65 | 4.53 |
| reminder | 6.55 | 6.45 | 5.41 | 2.08 | 2.25 | 2.30 | 1.40 | 6.80 | 6.15 |
| naturalistic | 6.15 | 6.94 | 4.17 | 1.23 | 1.31 | 1.83 | 1.13 | 6.92 | 5.33 |
| all_combined | 5.65 | 7.09 | 4.71 | 1.60 | 1.66 | 2.10 | 1.18 | 6.43 | 5.27 |

---

## 9. MODEL COUNTS BY PROVIDER

| Condition | N | Anthropic | OpenAI | Meta | Google | xAI | Mistral | DeepSeek | Alibaba | AWS |
|-----------|---|-----------|--------|------|--------|-----|---------|----------|---------|-----|
| baseline | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| authority | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| urgency | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| minimal_steering | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| telemetryV3 | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| reminder | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| naturalistic | 45 | 19 | 9 | 5 | 3 | 2 | 2 | 1 | 1 | 3 |
| all_combined | 46 | 19 | 9 | 6 | 3 | 2 | 2 | 1 | 1 | 3 |

---

## 10. EXTERNAL VALIDATION

### 10.1 Per-Benchmark Correlations

| Benchmark | N | r(BM→Soph) | p | r(BM→Disin) | p |
|-----------|---|------------|---|-------------|---|
| GPQA | 35 | 0.884 | 1.92e-12 | 0.711 | 1.73e-06 |
| AIME | 20 | 0.828 | 6.56e-06 | 0.464 | 0.0392 |
| ARC-AGI | 16 | 0.801 | 0.0002 | 0.596 | 0.0148 |

### 10.2 Triangulated Analysis Summary

| Approach | N | r(R→D) | r(S→D) | Δr | r(R→S) | Sig |
|----------|---|--------|--------|-----|--------|-----|
| 3-benchmark observed | 13 | 0.409 | 0.420 | -0.011 | 0.792 | No |
| GPQA+AIME observed | 20 | 0.463 | 0.447 | 0.016 | 0.763 | Yes |
| GPQA only (BEST) | 35 | 0.711 | 0.753 | -0.043 | 0.884 | Yes |
| Cross-benchmark imputed | 35 | 0.698 | 0.753 | -0.055 | 0.848 | Yes |
| Multiple imputation | 45 | 0.772 | 0.778 | -0.006 | 0.948 | Yes |

### 10.3 Best Estimate: GPQA Alone (N=35)

| Correlation | r | p |
|-------------|---|---|
| reasoning_to_disinhibition | 0.711 | 2.00e-06 |
| sophistication_to_disinhibition | 0.753 | 0.00e+00 |
| reasoning_to_sophistication | 0.884 | 0.00e+00 |

| Variable | Min | Max | Mean |
|----------|-----|-----|------|
| gpqa | 30.80 | 93.20 | 68.19 |
| sophistication | 4.01 | 7.55 | 5.95 |
| disinhibition | 1.30 | 2.31 | 1.54 |

---

## 11. PROVIDER ANOVA (BASELINE)

### 11.1 Disinhibition

| Statistic | Value |
|-----------|-------|
| F | 5.728 |
| p | 0.0012 |
| eta_squared | 0.403 |
| df_between | 4 |
| df_within | 34 |
| N | 39 |

### 11.2 Sophistication

| Statistic | Value |
|-----------|-------|
| F | 3.082 |
| p | 0.0287 |
| eta_squared | 0.266 |
| df_between | 4 |
| df_within | 34 |
| N | 39 |

---

## 12. PROVIDER MEANS (BASELINE)

| Provider | N | Disin_Mean | Disin_SD | Soph_Mean | Soph_SD |
|----------|---|------------|----------|-----------|---------|

| Google | 3 | 1.872 | 0.399 | 7.080 | 0.774 |
| xAI | 2 | 1.740 | 0.177 | 6.533 | 0.193 |
| DeepSeek | 1 | 1.642 | N/A | 6.260 | N/A |
| Alibaba | 1 | 1.590 | N/A | 6.380 | N/A |
| Anthropic | 19 | 1.559 | 0.170 | 5.842 | 0.874 |
| OpenAI | 9 | 1.510 | 0.123 | 6.354 | 1.338 |
| Meta | 5 | 1.397 | 0.040 | 5.172 | 0.111 |
| Mistral | 2 | 1.357 | 0.030 | 4.535 | 0.026 |
| AWS | 3 | 1.329 | 0.051 | 5.113 | 0.156 |

---

## 13. COMPOSITE RANGES

| Condition | Soph_Min | Soph_Max | Disin_Min | Disin_Max |
|-----------|----------|----------|-----------|-----------|

| baseline | 4.01 | 7.55 | 1.30 | 2.31 |
| authority | 4.20 | 8.24 | 1.30 | 2.75 |
| urgency | 3.92 | 8.28 | 1.39 | 4.81 |
| minimal_steering | 3.84 | 7.12 | 1.23 | 1.58 |
| telemetryV3 | 3.49 | 7.29 | 1.18 | 1.97 |
| reminder | 3.83 | 8.36 | 1.41 | 4.12 |
| naturalistic | 4.22 | 7.80 | 1.24 | 1.85 |
| all_combined | 4.47 | 8.45 | 1.41 | 2.52 |

---

## 14. EFFECT SIZE SUMMARY

| Condition | H1_d_Range | H2_r_Range | All_p < .05 |
|-----------|------------|------------|-------------|
| baseline | 2.13 - 2.84 | 0.778 - 0.819 | Yes |
| authority | 1.84 - 2.43 | 0.770 - 0.830 | Yes |
| urgency | 1.77 - 1.82 | 0.743 - 0.768 | Yes |
| minimal_steering | 2.32 - 2.46 | 0.854 - 0.875 | Yes |
| telemetryV3 | 1.09 - 1.80 | 0.625 - 0.799 | Yes |
| reminder | 1.65 - 2.18 | 0.720 - 0.806 | Yes |
| naturalistic | 2.09 - 2.40 | 0.841 - 0.911 | Yes |
| all_combined | 2.30 - 2.80 | 0.815 - 0.857 | Yes |

---

## DATA SOURCES

| Section | Source File |
|---------|-------------|
| H1/H2 Core | `<condition>/median_split_classification.json` |
| Outliers Removed | `<condition>/outliers_removed/median_split_classification.json` |
| BERT Validation | `bert_validation/<condition>/bert_validation_results.json` |
| BERT Soph/Disin | `bert_validation/<condition>/bert_soph_disin_results.json` |
| Judge Agreement | `<condition>/judge_agreement/judge_agreement_audit.json` |
| External Validation | `limitations/external_evals/reasoning_composite_triangulated_audit.json` |
| Per-Benchmark | `limitations/external_evals/{gpqa,aime,arc_agi}_validation_analysis.json` |
| Provider ANOVA | `<condition>/provider_comparison_stats.json` |
| Provider Means | `<condition>/comprehensive_stats.json` |

---

## REPRODUCIBILITY

```bash
python3 scripts/generate_consolidated_statistics.py
```
