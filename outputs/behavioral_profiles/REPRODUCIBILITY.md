# Reproducibility Guide

**Purpose**: Instructions for regenerating ALL analysis outputs from raw data.
**Last Updated**: 2026-01-19

---

## Quick Start

```bash
# Regenerate everything (all conditions, all analyses)
./scripts/regenerate_all.sh

# Preview what will be done (no changes)
./scripts/regenerate_all.sh --dry-run

# Regenerate single condition
./scripts/regenerate_all.sh --condition baseline
```

---

## Data Hierarchy

```
Raw Data (immutable)
    ↓
outputs/single_prompt_jobs/           # Job outputs with model responses + judge evaluations
    ↓
Phase 1: Profile Aggregation
    ↓
outputs/behavioral_profiles/<condition>/profiles/   # Aggregated behavioral profiles
    ↓
Phase 2-6: Analysis Pipeline
    ↓
outputs/behavioral_profiles/<condition>/           # H1/H2 visualizations, stats, briefs
outputs/behavioral_profiles/research_synthesis/    # Cross-condition analyses
```

---

## Regeneration Phases

| Phase | Script(s) | Inputs | Outputs |
|-------|-----------|--------|---------|
| **1. Profile Aggregation** | `update_behavioral_profiles.py` | Job JSONs | `profiles/*.json`, `history/` |
| **2. Median Split** | `calculate_median_split.py` | Profiles | `median_split_classification.json` |
| **3. H1/H2 Visualizations** | `create_h1_bar_chart.py`, `create_h2_color_coded_scatters.py` | Median split | `h1_*.png`, `h2_*.png` |
| **4. Research Brief** | `generate_research_brief_v2.py` | Median split + profiles | `RESEARCH_BRIEF.md` |
| **5. Provider Analysis** | `create_provider_summary.py`, etc. | Median split | `provider_*.png`, `comprehensive_stats.json` |
| **6. Statistical Assumptions** | `analyze_statistical_assumptions.py` | Profiles | `statistical_assumptions/` |
| **7. Outlier Sensitivity** | `analyze_outliers_removed.py` | Median split | `outliers_removed/` |
| **8. Cross-Condition** | `update_cross_condition_comparison.py`, etc. | All conditions | `research_synthesis/cross_condition/` |
| **9. BERT Validation** | `run_bert_validation.py` | Job responses + profiles | `bert_validation/<condition>/` |
| **10. Main Brief** | `regenerate_main_brief.py` | All analyses | `MAIN_RESEARCH_BRIEF.md` |

---

## Per-Condition Regeneration

```bash
CONDITION=baseline  # or authority, urgency, minimal_steering, telemetryV3, reminder, naturalistic, naturalistic_50

# Phase 1: Aggregate profiles
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition $CONDITION \
    --profile-dir outputs/behavioral_profiles/$CONDITION

# Phases 2-5: H1/H2 pipeline (one command)
./scripts/run_complete_h1_h2_analysis.sh $CONDITION

# Phase 6: Statistical assumptions
python3 scripts/analyze_statistical_assumptions.py $CONDITION

# Phase 7: Outlier sensitivity
python3 scripts/analyze_outliers_removed.py $CONDITION --force
```

---

## Cross-Condition Regeneration

```bash
# Update comparison tables
python3 scripts/update_cross_condition_comparison.py

# Repeated-measures ANOVA (same models across conditions)
python3 scripts/run_repeated_measures_anova.py --both

# Cross-condition patterns (constrained/outlier models)
python3 scripts/analyze_cross_condition_patterns.py
```

---

## BERT Validation Regeneration

```bash
# Per condition
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition baseline
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition baseline

# Consolidated brief
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_validation_reports.py
```

---

## Main Research Brief Regeneration

```bash
# Regenerate from all condition data
python3 scripts/regenerate_main_brief.py

# Sync to CDN (if publishing)
python3 scripts/sync_research_assets.py --invalidate
```

---

## Audit Verification

After regeneration, verify audit compliance:

```bash
# Quick check
python3 scripts/check_audit_compliance.py

# Full report
python3 scripts/check_audit_compliance.py --full-report

# JSON output for automation
python3 scripts/check_audit_compliance.py --json
```

---

## Prerequisites

### Required Data
- `outputs/single_prompt_jobs/` - Raw job outputs with:
  - Model responses
  - Judge evaluations (`judge_evaluation` or `judge_evaluation_telemetry`)

### Required Packages
```bash
pip install scipy numpy matplotlib pandas
pip install transformers torch  # For BERT validation only
```

### Environment
```bash
# Copy .env.example to .env and set:
AWS_ACCESS_KEY_ID=...          # For model invocation
AWS_SECRET_ACCESS_KEY=...
OPENAI_API_KEY=...             # For OpenAI models
# etc.
```

---

## Determinism Guarantees

All regeneration is **deterministic**:
- No random seeds (or seeds are documented in audit files)
- Same inputs → same outputs
- Floating-point results may vary at ~1e-15 precision

### Non-Deterministic Elements (Documented)
| Element | Location | Documentation |
|---------|----------|---------------|
| Bootstrap CI (if used) | Various | `random_seed` in audit JSON |
| Model responses | Job outputs | Pre-computed, immutable |
| Judge evaluations | Job outputs | Pre-computed, immutable |

---

## Audit Trail Requirements

Every output file should have provenance documented:

### JSON Outputs (`*_audit.json`)
- `schema_version`: "1.0"
- `metadata.generated`: ISO timestamp
- `provenance.source_files`: Input paths
- `provenance.methodology`: Statistical methods
- `results`: Key statistics with n, p, effect sizes

### Markdown Outputs (`*.md`)
Must include section:
```markdown
## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `path/to/source.json` | Description |

### Audit File
| File | Description |
|------|-------------|
| `analysis_audit.json` | Complete provenance data |

### Reproducibility
To regenerate: `python3 scripts/script_name.py args`
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "No profiles found" | Phase 1 not run | Run `update_behavioral_profiles.py` first |
| "Median split failed" | < 2 models per group | Check profile count |
| PNG render fails | No display | Set `MPLBACKEND=Agg` |
| telemetryV3 empty | Wrong key | Uses `judge_evaluation_telemetry` |
| Audit non-compliant | Missing fields | Check `AUDIT_STANDARDS.md` |

---

## File Dependencies

```
Job Outputs (immutable)
    │
    ├──► Profiles ──► Median Split ──► H1/H2 Visualizations
    │                      │                    │
    │                      ├──► Research Brief ◄┘
    │                      │
    │                      └──► Provider Analysis
    │
    ├──► BERT Scores ──► BERT Validation
    │
    └──► (All conditions) ──► Cross-Condition Analysis
                                      │
                                      └──► Main Research Brief
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `CONDITION_BEST_PRACTICES.md` | Per-condition directory structure |
| `REPLICATION_CHECKLIST.md` | Quick verification checklist |
| `research_synthesis/AUDIT_STANDARDS.md` | Audit file requirements |
| `CLAUDE.md` | This directory overview |

---

*This document ensures anyone can regenerate all outputs from raw data with full auditability.*
