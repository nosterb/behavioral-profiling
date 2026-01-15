# Research Brief Pre-Publication Audit Plan

**Created**: 2026-01-14
**Target Document**: `MAIN_RESEARCH_BRIEF.md` (v3.2)

---

## Overview

This audit plan ensures all statistics, interpretations, and manual sections in the research brief are accurate before publication.

---

## Phase 1: Statistical Audit (Auto-Generated)

Verify every number in the brief against source JSON files.

| Section | Statistics to Verify | Source File(s) |
|---------|---------------------|----------------|
| **Header** | N=45, Conditions=6, Total=13,650 | `median_split_classification.json` × 6 |
| **§2 Core Results** | All H1/H1a/H2 values (d, r, p) across 6 conditions | `<condition>/median_split_classification.json` |
| **§3.1 External** | ARC-AGI/GPQA correlations (r, p), group diffs | `external_evals/*.json` |
| **§3.2 Outlier** | Δd, Δr for each condition | `<condition>/outliers_removed/` |
| **§3.3 No-Dims** | Δd, Δr for baseline | `baseline/no_dimensions/` |
| **§4.1 Per-Provider H2** | r, p, N per provider | Calculated from baseline models |
| **§4.2 Provider Constraint** | OpenAI residuals, ANOVA p | `provider_constraint_*.json` |
| **§6.1 Judge Agreement** | ICC, Mean r, Within-1 % | `judge_agreement_analysis.json` |
| **§8 H3 Preliminary** | Variability (N, Mean, SD, CV%), ANOVA F/p/η² | `variability_analysis_*.json`, `repeated_measures_anova_results.json` |
| **Appendix A** | Factor correlations | `factor_structure_baseline.json` |
| **Appendix B** | Stability rate, flipper counts | `classification_stability_analysis.json` |

---

## Phase 2: Interpretation Audit

Verify that claims align with the statistics they reference.

| Claim Location | Claim Type | Verification |
|----------------|------------|--------------|
| Executive Summary bullets 1-5 | Key findings | Match §2 table values |
| §2 "Key Observations" | Effect interpretations | d > 1.0 = "large"? |
| §3.1 "Both benchmarks show large" | Effect size interpretation | r > 0.50 for both? |
| §3.2 "strengthens H1a in 4/6" | Outlier impact | Count Δd > 0.1 |
| §4.1 "H2 significant for 3/5" | Provider significance | Count p < 0.05 |
| §4.2 "6/6 conditions" for OpenAI | Consistency claim | All residuals negative? |
| §4.3 "All consistently constrained = OpenAI" | Provider pattern | Verify model list |
| §6.1 ICC interpretations | Reliability thresholds | ICC > 0.75 = "Good"? |
| Appendix B "76% stability" | Calculation | (17+18)/46 |

---

## Phase 3: Manual Section Audit

Review human-edited sections for accuracy and consistency.

| Section | Content Type | Review Focus |
|---------|--------------|--------------|
| **Executive Summary** | Overview narrative | Claims match findings? Accurate numbers? |
| **§5.1 H1/H2 Relationship** | Confidence-tiered claims | High/Moderate/Low justified? |
| **§5.1 Open Questions** | Research gaps | Still relevant? Addressed elsewhere? |
| **§6.2 Other Methodological** | Limitations list | Complete? Accurate? |
| **§7 Future Directions** | Research roadmap | Achievable? Specific? |
| **§8.4 Preliminary Interpretation** | H3 hypotheses | Consistent with §8.2/8.3 data? |

---

## Phase 4: Cross-Reference Audit

Check internal consistency across sections.

| Cross-Reference | Check |
|-----------------|-------|
| Executive Summary ↔ §2 | Numbers match? |
| §3.1 p-values ↔ §6.1 | Consistent precision? |
| §4.3 constrained models ↔ §4.2 | Same OpenAI models? |
| Appendix B flippers ↔ stability rate | Math correct? |
| All "baseline" references | Condition or suite? |

---

## Phase 5: Report Generation

Generate timestamped audit report with:
- All verified statistics (PASS/FAIL/WARN)
- Discrepancies found
- Recommendations for corrections
- Sign-off checklist

---

## Execution Log

| Phase | Status | Timestamp |
|-------|--------|-----------|
| Phase 1 | **COMPLETE** | 2026-01-14 |
| Phase 2 | **COMPLETE** | 2026-01-14 |
| Phase 3 | **COMPLETE** | 2026-01-14 |
| Phase 4 | **COMPLETE** | 2026-01-14 |
| Phase 5 | **COMPLETE** | 2026-01-14 |

## Final Report

See: `AUDIT_REPORT_2026-01-14.md`
