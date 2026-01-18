# Research Synthesis Directory

**Purpose**: Consolidated research outputs, cross-condition analyses, and external validation studies.

## Directory Structure

```
research_synthesis/
├── CLAUDE.md                          # This file
├── MAIN_RESEARCH_BRIEF.md             # Primary research document (source)
├── MAIN_RESEARCH_BRIEF_PUBLIC.md      # Public version with CDN URLs
├── bert_validation/                   # BERT toxicity validation (see bert_validation/CLAUDE.md)
├── cross_condition/                   # Cross-condition statistical analyses
├── limitations/                       # Methodological limitations & robustness
├── publish_audits/                    # Pre-publication audit reports
└── framework/                            # Statistical models & mediation analyses
```

## Subdirectory Purposes

### `framework/`

Statistical relationship models and mediation analyses (correlational, not causal).

| File | Description |
|------|-------------|
| `STATISTICAL_RELATIONSHIPS.md` | Documentation of capability-disinhibition-toxicity path model |
| `path_diagram.png` | Full 4-variable path model visualization |
| `mediation_diagram.png` | Focused mediation analysis (GPQA → Disinhibition → Toxicity) |
| `generate_path_diagram.py` | Script to regenerate diagrams |
| `statistical_model_audit.json` | Audit file with all statistical relationships |

### `bert_validation/`

Independent validation using BERT toxicity model. See `bert_validation/CLAUDE.md` for detailed documentation.

| Analysis | Description |
|----------|-------------|
| BERT vs Aggression | Validates judge aggression scores with BERT toxicity |
| BERT vs Sophistication | Correlates BERT toxicity with sophistication composite |
| BERT vs Disinhibition | Correlates BERT toxicity with disinhibition composite |

### `cross_condition/`

Aggregate analyses comparing results across all experimental conditions.

| File | Description |
|------|-------------|
| `CONDITION_COMPARISON.md` | Auto-updated H1/H2 comparison table |
| `CROSS_CONDITION_BRIEF.md` | Summary of cross-condition findings |
| `PROVIDER_CONSTRAINT_ANALYSIS.md` | Provider-level constraint patterns |
| `OUTLIERS_REMOVED_COMPARISON.md` | Sensitivity analysis without outliers |
| `repeated_measures_anova_results.json` | Repeated-measures ANOVA (same models across conditions) |
| `variability_analysis_disinhibition.json` | Variance analysis across conditions |
| `cross_condition_patterns.json` | Models that appear as outliers/constrained across conditions |

### `limitations/`

Methodological limitations and robustness analyses organized by topic.

| Subfolder | Contents |
|-----------|----------|
| `external_evals/` | Validation against ARC-AGI, GPQA, AIME benchmarks |
| `factor_structure/` | Inter-dimension correlations, composite validity |
| `judge_limitations/` | Inter-judge reliability (Krippendorff's alpha, ICC) |
| `median_split/` | Classification stability analysis |
| `prompt_design/` | Prompt inventories, qualitative pattern analysis |
| `provider_constraint/` | Provider-level sophistication-disinhibition patterns |
| `quadrant_classification/` | 2D visualization of model behavioral space |

### `publish_audits/`

Pre-publication verification documentation.

| File | Description |
|------|-------------|
| `AUDIT_PLAN.md` | 5-phase audit methodology |
| `AUDIT_REPORT_<date>.md` | Timestamped audit reports |

## Main Research Brief

The `MAIN_RESEARCH_BRIEF.md` is the consolidated research document combining all findings.

### Section Structure

| Section | Content | Update Mode |
|---------|---------|-------------|
| Executive Summary | Key findings | **MANUAL** |
| §1 Hypotheses & Methods | H1/H1a/H2 definitions | Auto |
| §2 Core Results | Cross-condition table | Auto |
| §3 Robustness & Validation | External, outlier, no-dims | Auto |
| §4 Provider & Model Patterns | Per-provider H2, constraint analysis | Auto |
| §5 Interpretation | H1/H2 relationship | **MANUAL** |
| §6 Limitations | Judge bias, other | **§6.2 MANUAL** |
| §7 Future Directions | Research roadmap | **MANUAL** |
| §8 H3 Preliminary | Intervention effects | **§8.4 MANUAL** |
| Appendix A | Factor structure | Auto |
| Appendix B | File references | Auto |

### Manual Section Preservation

Sections marked **MANUAL** use preservation markers:

```markdown
### 5.1 H1/H2 Relationship

<!-- MANUAL-START -->
Your manually edited content here...
<!-- MANUAL-END -->
```

Content between markers is preserved when regenerating.

### Regeneration Commands

```bash
# Regenerate from condition data
python3 scripts/regenerate_main_brief.py

# Full workflow: regenerate + sync to CDN
python3 scripts/regenerate_main_brief.py && python3 scripts/sync_research_assets.py --invalidate
```

## Development Patterns

### Naming Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| `<analysis>_<condition>.json` | `provider_constraint_baseline.json` | Condition-specific data |
| `<ANALYSIS>_BRIEF.md` | `BERT_VALIDATION_BRIEF.md` | Human-readable summaries |
| `<analysis>_results.json` | `bert_validation_results.json` | Machine-readable outputs |
| `scatter_<y>_vs_<x>.png` | `scatter_toxicity_vs_aggression.png` | Visualization naming |

### Output File Structure

Each analysis typically produces:

1. **JSON results file** - Machine-readable data with full provenance
2. **Markdown report** - Human-readable summary
3. **Visualizations** - PNG scatter plots, heatmaps
4. **Log file** - Execution trace (optional)

### JSON Results Schema

All results JSONs follow this pattern:

```json
{
  "metadata": {
    "date": "ISO timestamp",
    "condition": "condition name",
    "source_files": ["list of source paths"],
    "n_models": 45
  },
  "correlations": {
    "<metric>": {"r": 0.78, "p": 0.0001, "interpretation": "large"}
  },
  "patterns": {
    "outliers": [...],
    "constrained": [...]
  },
  "model_data": [...],
  "output_files": [...]
}
```

### Visualization Standards

All scatter plots include:

| Element | Implementation |
|---------|----------------|
| **Condition label** | `fig.suptitle(f'Condition: {condition}')` at y=0.995 |
| **Stats box** | Wheat background, top-left, includes r, R², p, N |
| **Outliers** | Red circles (s=400, facecolors='none', edgecolors='red') |
| **Constrained** | Cyan diamonds (marker='D', color='#00CED1', edgecolors='blue') |
| **Regression line** | Black dashed (k--, alpha=0.5) |
| **Model labels** | Navy text with lightyellow bbox, arrows |
| **Grid** | alpha=0.3, linestyle='--' |

### Statistical Thresholds

| Threshold | Value | Usage |
|-----------|-------|-------|
| `OUTLIER_SD_THRESHOLD` | 2.0 | |residual| > 2 SD from regression |
| Effect size (r) | 0.5 | Large effect threshold |
| Effect size (r) | 0.3 | Medium effect threshold |
| p-value display | < .0001 | Format for very small p |

## Data Provenance & Auditability

**REQUIRED**: All analyses in `research_synthesis/` must follow these auditability standards. See root `CLAUDE.md` for full specification.

### Audit File Schema (Extended)

For complex analyses (e.g., triangulated approaches), the audit JSON should include:

```json
{
  "metadata": {
    "generated": "ISO timestamp",
    "updated": "ISO timestamp",
    "analysis": "Human-readable name",
    "random_seed": 42
  },
  "provenance": {
    "source_files": {
      "behavioral_profiles": "path/to/profiles/*.json",
      "external_benchmark": "path/to/benchmark.json"
    },
    "methodology": {
      "composite_construction": "Description of method",
      "imputation_method": "Description if applicable",
      "statistical_tests": ["pearson", "t-test", etc.]
    }
  },
  "approach_1_name": {
    "n": 20,
    "correlations": {...},
    "note": "Why this approach matters"
  },
  "approach_2_name": {...},
  "summary": {
    "key_finding": "One-sentence takeaway",
    "best_estimate": "Most reliable result",
    "caution": "Important caveats"
  }
}
```

### Imputation Documentation

When imputing missing values, ALWAYS document:

| Field | Required | Example |
|-------|----------|---------|
| `*_observed` | Yes | Original value or `null` |
| `*_final` | Yes | Value used in analysis |
| `*_imputed` | Yes | `true` / `false` flag |
| Imputation model | Yes | `{"slope": X, "intercept": Y, "r": Z}` |

### Triangulated Analysis Pattern

For analyses with multiple methodological approaches:

1. **Name approaches clearly**: `approach_1_observed_only`, `approach_2_imputed`, etc.
2. **Document each approach's N**: Sample sizes may differ
3. **Include convergence assessment**: Do approaches agree?
4. **Identify best estimate**: Which approach is most reliable and why?
5. **Flag non-significant results**: Don't bury p > 0.05 findings

### Example: External Validation Audit

```
limitations/external_evals/
├── reasoning_composite_triangulated_audit.json  # Primary audit
├── reasoning_composite_audit.json               # Legacy (single approach)
├── REASONING_COMPOSITE_ANALYSIS.md              # Human-readable report
└── [source validation JSONs]                    # Input data
```

## Cross-Condition Analysis Commands

```bash
# Update condition comparison table
python3 scripts/update_cross_condition_comparison.py

# Run repeated-measures ANOVA
python3 scripts/run_repeated_measures_anova.py --both

# Analyze variability
python3 scripts/analyze_variability.py --both --output-json

# Cross-condition patterns
python3 scripts/analyze_cross_condition_patterns.py
```

## Pre-Publication Workflow

1. **Regenerate brief**: `python3 scripts/regenerate_main_brief.py`
2. **Run audit**: Request "Run a full pre-publication audit of MAIN_RESEARCH_BRIEF.md"
3. **Review audit report**: Check `publish_audits/AUDIT_REPORT_<date>.md`
4. **Sync to CDN**: `python3 scripts/sync_research_assets.py --invalidate`
5. **Export**: Use pandoc for PDF/HTML (see parent CLAUDE.md)

## Related Documentation

- Parent: `outputs/behavioral_profiles/CLAUDE.md` - Condition directories and H1/H2 pipeline
- Root: `CLAUDE.md` - Project overview
- BERT: `bert_validation/CLAUDE.md` - External validation methodology
