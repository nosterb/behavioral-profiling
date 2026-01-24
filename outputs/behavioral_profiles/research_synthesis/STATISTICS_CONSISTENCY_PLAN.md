# Statistics Consistency Plan

**Purpose**: Ensure all statistics in `CONSOLIDATED_STATISTICS.md` and `MAIN_RESEARCH_BRIEF.md` are consistent and traceable to source JSON files.

---

## 1. Document Relationship

| Document | Purpose | Update Mode |
|----------|---------|-------------|
| `CONSOLIDATED_STATISTICS.md` | **Authoritative reference** for all computed statistics | Manual / Script |
| `MAIN_RESEARCH_BRIEF.md` | **Publication document** with AUTO-blocks pulling from sources | `regenerate_main_brief_v2.py` |

**Single Source of Truth**: Both documents should derive statistics from the same JSON source files, NOT from each other.

---

## 2. Statistics Overlap Map

### 2.1 H1/H2 Core (Must Match)

| Statistic | CONSOLIDATED §1 | MAIN_BRIEF §2 (AUTO) | Source File |
|-----------|-----------------|----------------------|-------------|
| N per condition | ✓ | ✓ | `<cond>/median_split_classification.json` |
| Median Soph | ✓ | ✓ | Same |
| N_High / N_Low | ✓ | ✓ | Same |
| H1a d | ✓ | ✓ | Same |
| H1a p | ✓ | ✓ | Same |
| H2 r | ✓ | ✓ | Same |
| Per-dimension d | ✓ (§7) | ✓ | Same |

### 2.2 Outliers Removed (Must Match)

| Statistic | CONSOLIDATED §2 | MAIN_BRIEF §3.2 | Source File |
|-----------|-----------------|-----------------|-------------|
| N_Removed | ✓ | ✓ (Δ only) | `<cond>/outliers_removed/outlier_removal_info.json` |
| H1a d (outliers removed) | ✓ | ✓ (Δ only) | `<cond>/outliers_removed/median_split_classification.json` |
| H2 r (outliers removed) | ✓ | ✓ (Δ only) | Same |

### 2.3 BERT Validation (Must Match)

| Statistic | CONSOLIDATED | MAIN_BRIEF | Source File |
|-----------|--------------|------------|-------------|
| r_tox vs Aggression | §3 | §3.5 bert_primary_table | `bert_validation/<cond>/bert_validation_results.json` |
| r_tox vs Soph | §5 | §3.5 bert_extended_table | `bert_validation/<cond>/bert_soph_disin_results.json` |
| r_tox vs Disin | §5 | §3.5 bert_extended_table | Same |
| BERT outliers removed | §4, §6 | NOT IN BRIEF | `<cond>/outliers_removed/bert_*_audit.json` |

**Gap**: MAIN_BRIEF §3.5 doesn't include BERT outliers-removed stats (§4, §6 in CONSOLIDATED).

### 2.4 External Validation (Must Match)

| Statistic | CONSOLIDATED §10 | MAIN_BRIEF §3.1 | Source File |
|-----------|------------------|-----------------|-------------|
| r(BM→Soph) | ✓ | ✓ | `limitations/external_evals/{gpqa,aime,arc_agi}_validation_analysis.json` |
| r(BM→Disin) | ✓ | ✓ | Same |
| Group diff | ✗ | ✓ | Same |

### 2.5 Judge Agreement (Must Match)

| Statistic | CONSOLIDATED §7 | MAIN_BRIEF §6.1 | Source File |
|-----------|-----------------|-----------------|-------------|
| ICC(3) per dimension | ✓ | ✓ | `<cond>/judge_agreement/judge_agreement_audit.json` |
| Overall ICC | ✓ | ✓ | Same |
| N_Evals | ✓ | ✓ | Same |

### 2.6 Provider Analysis (Must Match)

| Statistic | CONSOLIDATED | MAIN_BRIEF | Source File |
|-----------|--------------|------------|-------------|
| Provider H2 r | Not in CONSOL | §4.1 | `<cond>/provider_comparison_stats.json` |
| Provider ANOVA | §11 | Not explicit | Same |
| Provider Means | §12 | Not explicit | `<cond>/comprehensive_stats.json` |
| Provider Constraint | Not in CONSOL | §4.2 | `limitations/provider_constraint/provider_constraint_*.json` |

### 2.7 H3/Variability (Must Match)

| Statistic | CONSOLIDATED | MAIN_BRIEF §8 | Source File |
|-----------|--------------|---------------|-------------|
| CV%, SD, Mean | Not in CONSOL | ✓ | `cross_condition/variability_analysis_disinhibition.json` |
| ANOVA F, p, η² | Not in CONSOL | ✓ | `cross_condition/repeated_measures_anova_results.json` |

---

## 3. Known Discrepancies to Check

### 3.1 Evaluation Counts

| Source | CONSOLIDATED §0 | MAIN_BRIEF header |
|--------|-----------------|-------------------|
| Total Judge Evaluations | 13,868 | 14,088 |
| Total BERT Evaluations | 14,203 | 14,203 |

**Action**: Verify count methodology and reconcile.

### 3.2 Appendix C Duplicates

MAIN_BRIEF Appendix C (§C.1-C.7) duplicates CONSOLIDATED statistics. These MUST match exactly.

| Appendix C Section | CONSOLIDATED Section |
|--------------------|----------------------|
| C.1 H1/H2 Core | §1 |
| C.2 Outliers-Removed | §2 |
| C.3 BERT External | §3 |
| C.4 Judge Agreement | §7 |
| C.5 Per-Dimension d | §7 (duplicate number) |
| C.6 External Benchmark | §10 |
| C.7 Provider ANOVA | §11 |

**Current Issue**: CONSOLIDATED §7 is duplicated (JUDGE AGREEMENT and PER-DIMENSION both labeled §7).

---

## 4. Consistency Audit Script

Create `scripts/audit_statistics_consistency.py` to:

1. **Load all source JSON files**
2. **Parse CONSOLIDATED_STATISTICS.md tables**
3. **Parse MAIN_RESEARCH_BRIEF.md AUTO blocks**
4. **Compare values** with tolerance (0.001 for r, p; 0.01 for d)
5. **Report discrepancies**

### Audit Output Format

```json
{
  "audit_date": "2026-01-24",
  "files_checked": {
    "consolidated": "CONSOLIDATED_STATISTICS.md",
    "brief": "MAIN_RESEARCH_BRIEF.md",
    "source_jsons": [...]
  },
  "discrepancies": [
    {
      "statistic": "H2_r_baseline",
      "consolidated_value": 0.778,
      "brief_value": 0.778,
      "source_value": 0.778,
      "status": "MATCH"
    }
  ],
  "summary": {
    "total_checks": 150,
    "matches": 148,
    "discrepancies": 2
  }
}
```

---

## 5. Regeneration Workflow

### Current State

```
Source JSON Files
       │
       ├──> regenerate_main_brief_v2.py ──> MAIN_RESEARCH_BRIEF.md
       │
       └──> (manual) ──> CONSOLIDATED_STATISTICS.md
```

### Proposed State

```
Source JSON Files
       │
       ├──> generate_consolidated_statistics.py ──> CONSOLIDATED_STATISTICS.md
       │
       └──> regenerate_main_brief_v2.py ──> MAIN_RESEARCH_BRIEF.md

       audit_statistics_consistency.py ──> Verify both match sources
```

### Regeneration Commands

```bash
# 1. Regenerate CONSOLIDATED from source JSONs
python3 scripts/generate_consolidated_statistics.py

# 2. Regenerate MAIN_BRIEF from source JSONs
python3 scripts/regenerate_main_brief_v2.py

# 3. Audit consistency
python3 scripts/audit_statistics_consistency.py --output audit_report.json

# 4. Full workflow (all three)
./scripts/regenerate_and_audit.sh
```

---

## 6. Implementation Tasks

### Phase 1: Fix Existing Issues

- [x] Fix CONSOLIDATED §7 duplicate numbering (JUDGE AGREEMENT vs PER-DIMENSION) ✓ 2026-01-24
- [x] Reconcile Total Evaluations count discrepancy (13,868 vs 14,088) ✓ 2026-01-24
- [x] Update MAIN_BRIEF Appendix C to match CONSOLIDATED exactly ✓ 2026-01-24 (added AUTO blocks C.1-C.7)

### Phase 2: Create Audit Infrastructure

- [x] Create `scripts/audit_statistics_consistency.py` ✓ 2026-01-24
- [x] Define tolerance thresholds for numerical comparisons ✓ 2026-01-24
- [x] Generate initial audit report ✓ 2026-01-24

### Phase 3: Create Generation Script

- [x] Create `scripts/generate_consolidated_statistics.py` ✓ 2026-01-24
- [x] Ensure it reads from same sources as `regenerate_main_brief_v2.py` ✓ 2026-01-24
- [x] Add section-by-section generation matching current format ✓ 2026-01-24

### Phase 4: Establish Workflow

- [x] Create `scripts/regenerate_and_audit.sh` master script ✓ 2026-01-24
- [ ] Add pre-commit hook option for consistency check (future)
- [ ] Document workflow in CLAUDE.md (future)

---

## 7. Source File Registry

| Statistic Category | Source File Pattern |
|--------------------|---------------------|
| H1/H2 Core | `<condition>/median_split_classification.json` |
| H1/H2 Outliers Removed | `<condition>/outliers_removed/median_split_classification.json` |
| Outlier Info | `<condition>/outliers_removed/outlier_removal_info.json` |
| BERT vs Aggression | `bert_validation/<condition>/bert_validation_results.json` |
| BERT vs Soph/Disin | `bert_validation/<condition>/bert_soph_disin_results.json` |
| BERT Outliers Removed | `<condition>/outliers_removed/bert_*_audit.json` |
| External Validation | `limitations/external_evals/{gpqa,aime,arc_agi}_validation_analysis.json` |
| Judge Agreement | `<condition>/judge_agreement/judge_agreement_audit.json` |
| Provider Stats | `<condition>/provider_comparison_stats.json` |
| Provider Means | `<condition>/comprehensive_stats.json` |
| Provider Constraint | `limitations/provider_constraint/provider_constraint_<condition>.json` |
| H3 Variability | `cross_condition/variability_analysis_disinhibition.json` |
| H3 ANOVA | `cross_condition/repeated_measures_anova_results.json` |

---

## 8. Quick Verification Commands

```bash
# Check a specific statistic from source
python3 -c "import json; d=json.load(open('outputs/behavioral_profiles/baseline/median_split_classification.json')); print('H2_r:', d['statistics']['h2']['correlation'])"

# Verify BERT baseline
python3 -c "import json; d=json.load(open('outputs/behavioral_profiles/research_synthesis/bert_validation/baseline/bert_validation_results.json')); print('r_tox:', d['correlations']['toxicity']['r'])"

# Compare with CONSOLIDATED
grep "baseline" outputs/behavioral_profiles/research_synthesis/CONSOLIDATED_STATISTICS.md | head -5
```

---

**Created**: 2026-01-24
**Status**: Plan ready for implementation
