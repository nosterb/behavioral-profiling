# Audit Standards for Research Synthesis

**Purpose**: Canonical standards for data provenance and audit trails across all research synthesis outputs.

**Created**: 2026-01-18
**Status**: Active

---

## Core Principles

### 1. Single Source of Truth
Each analysis produces **ONE authoritative audit file** (`*_audit.json`) containing:
- Provenance (inputs, methodology)
- Results (statistics, p-values, effect sizes)
- Raw data (model-level scores for verification)

### 2. Data-Upward Hierarchy
```
Source Data (job outputs, profiles)
       ↓
   *_audit.json (provenance + results + raw data)
       ↓
   *.md reports (reference audit.json)
       ↓
   visualizations (generated from audit data)
```

### 3. Audit File is Authoritative
If discrepancy exists between any files, `*_audit.json` wins. Markdown briefs and visualizations are derived artifacts.

### 4. Deprecation of Results Files
`*_results.json` files are **deprecated intermediates**. New analyses should only produce `*_audit.json`. Existing results files should be migrated.

---

## Canonical Audit JSON Schema

**Version**: 1.0

```json
{
  "schema_version": "1.0",
  "metadata": {
    "generated": "2026-01-18T12:00:00Z",
    "updated": "2026-01-18T12:00:00Z",
    "analysis": "Human-readable analysis name",
    "random_seed": null
  },
  "provenance": {
    "source_files": {
      "<role>": "relative/path/from/repo/root"
    },
    "methodology": {
      "description": "What this analysis does",
      "statistical_tests": ["pearson", "t_test_independent"],
      "composite_construction": "Description if applicable",
      "software": "Python 3.x, scipy 1.x"
    },
    "imputation": {
      "method": "Description or null if none",
      "affected_models": [],
      "model_parameters": {}
    }
  },
  "results": {
    "<result_name>": {
      "statistic": "r|d|t|F",
      "value": 0.72,
      "p": 0.0001,
      "n": 45,
      "effect_size_interpretation": "large",
      "ci_95": [0.55, 0.84]
    }
  },
  "model_data": [
    {
      "model": "Model-Name",
      "values": {},
      "imputed_fields": [],
      "source_file": "relative/path"
    }
  ],
  "output_files": {
    "brief": "ANALYSIS_BRIEF.md",
    "visualizations": ["plot.png"]
  },
  "related_analyses": {
    "upstream": [],
    "downstream": []
  },
  "schema_deviation": null
}
```

### Field Requirements

| Field | Required | Notes |
|-------|----------|-------|
| `schema_version` | **Yes** | For forward compatibility, currently "1.0" |
| `metadata.generated` | **Yes** | ISO-8601 creation timestamp |
| `metadata.updated` | **Yes** | ISO-8601 last modification timestamp |
| `metadata.analysis` | **Yes** | Human-readable name |
| `metadata.random_seed` | If randomized | RNG seed for reproducibility |
| `provenance.source_files` | **Yes** | At least one source with role key |
| `provenance.methodology.description` | **Yes** | What the analysis does |
| `provenance.methodology.statistical_tests` | **Yes** | List of tests used |
| `provenance.imputation` | If applicable | Document any imputation |
| `results` | **Yes** | At least one named result |
| `results.<name>.statistic` | **Yes** | Type of statistic (r, d, t, F, etc.) |
| `results.<name>.value` | **Yes** | Numeric value |
| `results.<name>.p` | **Yes** | P-value |
| `results.<name>.n` | **Yes** | Sample size |
| `model_data` | Recommended | Enables independent verification |
| `output_files` | Recommended | Links to generated artifacts |
| `schema_deviation` | If deviating | Explanation of why standard wasn't followed |

### Path Conventions

All paths in audit files should be **relative to repository root**:
- **Good**: `outputs/behavioral_profiles/baseline/profiles/model.json`
- **Bad**: `/Users/name/project/outputs/...` (absolute)
- **Bad**: `../baseline/profiles/model.json` (relative to current dir)

---

## Canonical Markdown Provenance Section

Every analysis markdown file (`.md`) MUST include this section structure:

```markdown
## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `relative/path/to/source.json` | Description of what this provides |

### Audit File
| File | Description |
|------|-------------|
| `analysis_audit.json` | Complete provenance, results, and raw model data |

### Methodology
- **Statistical tests**: Pearson correlation, independent samples t-test
- **Composite construction**: Mean of X and Y dimensions
- **Imputation**: None (or description if applicable)

### Reproducibility
To regenerate this analysis from source data:
```bash
python3 scripts/script_name.py --args
```

### Data Quality
- **N**: X models
- **Exclusions**: None (or list)
- **Known limitations**: (if any)
```

---

## File Naming Conventions

| Pattern | Usage | Example |
|---------|-------|---------|
| `*_audit.json` | **Primary** audit file (authoritative) | `bert_validation_audit.json` |
| `*_triangulated_audit.json` | Multi-approach analysis | `reasoning_composite_triangulated_audit.json` |
| `*_results.json` | **DEPRECATED** - migrate to audit | `bert_validation_results.json` |
| `*_BRIEF.md` or `*_ANALYSIS.md` | Human-readable report | `BERT_VALIDATION_BRIEF.md` |
| `*_REPORT.md` | Validation/audit reports | `VALIDATION_REPORT.md` |

---

## Deviation Documentation

When deviation from this standard is **necessary**, document it in THREE places:

### 1. In Audit JSON
```json
{
  "schema_deviation": {
    "reason": "Triangulated analysis with 3 methodological approaches",
    "affected_fields": ["results structure uses approach_1, approach_2 instead of flat results"],
    "documented_in": "_PROVENANCE_NOTES.md"
  }
}
```

### 2. In Markdown Brief
Add a "Schema Deviation" subsection under Data Provenance:
```markdown
### Schema Deviation
This analysis deviates from standard audit schema because [reason].
See `_PROVENANCE_NOTES.md` for details.
```

### 3. In Directory (for complex cases)
Create `_PROVENANCE_NOTES.md` explaining:
- Why deviation is necessary
- How to interpret the non-standard structure
- Migration plan (if applicable)

### Valid Deviation Reasons
- Legacy format required for backward compatibility
- External data source with incompatible structure
- Triangulated analysis requiring multiple result structures
- Experimental analysis not yet standardized

---

## Migration Path for Legacy Files

### For `*_results.json` without `*_audit.json`:

1. **Create audit file** incorporating results + provenance:
   ```bash
   python3 scripts/migrate_results_to_audit.py path/to/results.json
   ```

2. **Mark results file as deprecated** (add to file or rename):
   ```json
   {
     "_deprecated": "See *_audit.json for authoritative data",
     ...existing content...
   }
   ```

3. **Update markdown** to reference audit file instead of results

### For markdown files without provenance sections:

1. Identify the source data for the analysis
2. Locate or create the corresponding audit.json
3. Add the canonical provenance section referencing it

---

## Verification Checklist

Before publishing any analysis, verify:

- [ ] `*_audit.json` exists with all required fields
- [ ] `schema_version` is set to "1.0"
- [ ] `metadata.generated` and `metadata.updated` are valid ISO-8601
- [ ] `provenance.source_files` lists all inputs with relative paths
- [ ] `provenance.methodology` describes statistical approach
- [ ] `results` contains all key statistics with n, p, value
- [ ] `model_data` present (if verification needed)
- [ ] Markdown has "Data Provenance & Audit Trail" section
- [ ] Markdown references the audit file
- [ ] Any deviations documented in `schema_deviation`

### Quick Verification Command
```bash
python3 scripts/check_audit_compliance.py [path]
```

---

## Examples

### Minimal Compliant Audit File
```json
{
  "schema_version": "1.0",
  "metadata": {
    "generated": "2026-01-18T10:00:00Z",
    "updated": "2026-01-18T10:00:00Z",
    "analysis": "H2 Correlation Analysis - Baseline"
  },
  "provenance": {
    "source_files": {
      "profiles": "outputs/behavioral_profiles/baseline/profiles/"
    },
    "methodology": {
      "description": "Pearson correlation between sophistication and disinhibition composites",
      "statistical_tests": ["pearson"]
    }
  },
  "results": {
    "h2_correlation": {
      "statistic": "r",
      "value": 0.702,
      "p": 0.0001,
      "n": 45,
      "effect_size_interpretation": "large"
    }
  }
}
```

### Full Audit File with Model Data
See `limitations/external_evals/reasoning_composite_triangulated_audit.json` for a comprehensive example with multiple approaches and model-level data.

---

## Related Documentation

- Root `CLAUDE.md` - Project-wide audit requirements
- `research_synthesis/CLAUDE.md` - Directory-specific patterns
- `bert_validation/CLAUDE.md` - BERT validation methodology
- `AUDIT_MEMORY.md` - Language/terminology audit tracking

---

*This document is the authoritative standard. All research synthesis outputs should comply or document deviations.*
