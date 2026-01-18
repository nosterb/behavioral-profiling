# BERT Validation Directory

**Purpose**: Independent validation of LLM-as-judge behavioral scores using BERT toxicity detection as an external, non-LLM measure.

## Overview

This validation study addresses a key methodological concern: "Are we just measuring what frontier models think, validated by other frontier models?" By using BERT (a fundamentally different architecture trained on human-labeled data), we provide convergent validity for the behavioral profiling methodology.

## Directory Structure

```
bert_validation/
├── CLAUDE.md                          # This file
├── BERT_VALIDATION_BRIEF.md           # Cross-condition research summary
├── REGRESSION_ANALYSIS.md             # Sophistication regression with suppression effect
├── regression_analysis_audit.json     # Regression analysis audit file
├── EXPERIMENT_PLAN.md                 # Original experiment design
├── AUDIT_REPORT.md                    # Audit certification report
├── audit_samples.json                 # Raw samples with BERT scores (5 per condition)
├── audit_results.json                 # Audit certification data
├── scripts/
│   ├── run_bert_validation.py         # Main: BERT vs Aggression
│   ├── run_bert_soph_disin_validation.py  # Extended: BERT vs Soph/Disin
│   ├── run_bert_full_audit.py         # Full audit: re-score all + validate
│   ├── regenerate_validation_reports.py   # Regenerate consolidated reports
│   ├── regenerate_plots.py            # Regenerate from saved JSON
│   └── test_bert_toxicity.py          # BERT model test script
├── baseline/                          # Condition-specific outputs
├── authority/
├── urgency/
├── minimal_steering/
├── telemetryV3/
└── reminder/
```

## Validation Analyses

### 1. BERT vs Aggression (Primary)

**Script**: `run_bert_validation.py`

Correlates BERT toxicity/insult scores with judge-assigned aggression scores.

| Output File | Description |
|-------------|-------------|
| `bert_validation_results.json` | Complete results with per-model scores |
| `scatter_toxicity_vs_aggression.png` | Primary validation scatter |
| `scatter_insult_vs_aggression.png` | Secondary validation scatter |
| `scatter_combined.png` | 2-panel summary |
| `VALIDATION_REPORT.md` | Markdown report |
| `full_run_log.txt` | Execution trace |

### 2. BERT vs Sophistication/Disinhibition (Extended)

**Script**: `run_bert_soph_disin_validation.py`

Extends validation to correlate BERT scores with composite behavioral measures.

### 3. Regression & Mediation Analysis

**Report**: `REGRESSION_ANALYSIS.md`
**Audit**: `regression_analysis_audit.json`

Tests whether Sophistication predicts BERT toxicity independent of Disinhibition using multiple regression and bootstrap mediation (n=5000).

**Key Findings**:
- Disinhibition dominates: 60.1% R², 36.3% unique variance
- Sophistication adds only 2.2% unique variance (not significant)
- **Suppression effect**: β(Soph) = -0.237 (negative) when controlling for Disinhibition
- Full mediation confirmed: ACME significant, ADE not significant

**Related**: See `../framework/STATISTICAL_RELATIONSHIPS.md` for integrated theoretical model.

| Output File | Description |
|-------------|-------------|
| `bert_soph_disin_results.json` | Extended correlation results |
| `scatter_toxicity_vs_sophistication.png` | Toxicity ~ Sophistication |
| `scatter_toxicity_vs_disinhibition.png` | Toxicity ~ Disinhibition |
| `scatter_insult_vs_sophistication.png` | Insult ~ Sophistication |
| `scatter_insult_vs_disinhibition.png` | Insult ~ Disinhibition |
| `scatter_soph_disin_combined.png` | 2x2 grid summary |

## BERT Model Details

| Field | Value |
|-------|-------|
| **Model** | `unitary/toxic-bert` |
| **URL** | https://huggingface.co/unitary/toxic-bert |
| **Architecture** | BERT (bert-base-uncased), 110M parameters |
| **Training Data** | Jigsaw Toxic Comment Classification (~160k Wikipedia comments) |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |
| **Execution** | Local inference (no API calls) |
| **Cache Location** | `~/.cache/huggingface/` (~418MB) |

## Running Validation

### Single Condition

```bash
# BERT vs Aggression
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition baseline

# BERT vs Soph/Disin (requires BERT results first)
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition baseline
```

### All Conditions (Chained)

```bash
# Run BERT vs Aggression for all conditions
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition baseline 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/baseline/full_run_log.txt && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition authority 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/authority/full_run_log.txt && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition urgency 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/urgency/full_run_log.txt && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition minimal_steering 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/minimal_steering/full_run_log.txt && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition telemetryV3 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/telemetryV3/full_run_log.txt && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition reminder 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/reminder/full_run_log.txt

# Then run BERT vs Soph/Disin for all conditions
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition baseline && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition authority && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition urgency && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition minimal_steering && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition telemetryV3 && \
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py --condition reminder
```

## Design Patterns & Best Practices

### 1. Data Flow

```
Job Outputs (JSON)
    ↓ extract model responses
Condition Profiles (JSON)
    ↓ extract behavioral scores (aggression, soph, disin)
BERT Model (local)
    ↓ score each response
Per-Model Averages
    ↓ correlate
Statistical Results + Visualizations
```

### 2. Model Name Normalization

Models are matched across data sources using `normalize_model_name()`:

```python
def normalize_model_name(name: str) -> str:
    # Preserve thinking variant distinction
    is_thinking = "thinking" in name.lower()
    # Remove timestamps, normalize separators
    # Re-add thinking suffix if applicable
```

**Critical**: Thinking variants (e.g., `claude-4.5-haiku-thinking`) are treated as distinct models.

### 3. Pattern Detection

All scatter plots identify two special patterns:

| Pattern | Detection | Visualization |
|---------|-----------|---------------|
| **Outliers** | \|residual\| > 2 SD from regression | Red circles (s=400) |
| **Constrained** | High X (>75th percentile) but negative residual (< -0.5 SD) | Cyan diamonds |

### 4. Visualization Standards

All plots follow `research_synthesis` styling:

```python
# Condition label at top
fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold', y=0.995, color='#666666')

# Stats box (wheat background)
ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95))

# Model labels (navy with lightyellow background)
ax.annotate(label, xy=(...), xytext=(...),
            fontsize=6.5, fontweight='bold', color='navy',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.85, edgecolor='navy'),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color='navy'))

# Grid
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
```

### 5. JSON Output Schema

All results follow this structure:

```json
{
  "metadata": {
    "date": "2026-01-15T...",
    "bert_model": "unitary/toxic-bert",
    "condition": "baseline",
    "n_models": 45,
    "outlier_threshold_sd": 2.0
  },
  "correlations": {
    "<measure>": {
      "r": 0.776,
      "p": 3.65e-10,
      "r_squared": 0.603,
      "interpretation": "large"
    }
  },
  "regression": {
    "<measure>": {
      "slope": 0.0356,
      "intercept": -0.0398,
      "std_err": 0.0044
    }
  },
  "patterns": {
    "<measure>": {
      "outliers": [...],
      "constrained": [...],
      "residual_std": 0.0062
    }
  },
  "model_results": [
    {"model_id": "...", "bert_toxicity": 0.01, "aggression": 1.5, ...}
  ],
  "output_files": [...]
}
```

### 6. Effect Size Interpretation

| r | Interpretation | Threshold |
|---|----------------|-----------|
| ≥ 0.5 | Large | `abs(r) >= 0.5` |
| 0.3 - 0.5 | Medium | `0.3 <= abs(r) < 0.5` |
| < 0.3 | Small | `abs(r) < 0.3` |

### 7. Score Processing

- **All responses scored**: No `--limit` flag by default (scores all ~50 responses per model)
- **Averaging**: Per-model BERT scores are averaged across all responses
- **Truncation**: Texts > 512 tokens are truncated for BERT

### 8. Token Truncation

BERT has a 512 token limit. Response lengths in JSON are measured in **characters** (not tokens).

| Condition | Truncated | % |
|-----------|-----------|---|
| baseline | 691 / 2,234 | 30.9% |
| authority | 915 / 2,238 | 40.9% |
| urgency | 516 / 2,236 | 23.1% |
| minimal_steering | 236 / 2,292 | 10.3% |
| telemetryV3 | 715 / 2,290 | 31.2% |
| reminder | 176 / 674 | 26.1% |
| **TOTAL** | **3,249 / 11,964** | **27.2%** |

**Token-to-char ratio**: ~0.23 (i.e., 512 tokens ≈ 2,200 chars)

### 9. JSON Serialization

When saving results to JSON, ensure numpy types are converted:

```python
# Convert numpy bool/float to Python native types
"match": bool(tox_match)  # not np.bool_
"toxicity": float(scores["toxicity"])  # not np.float64
```

## Key Findings

### Baseline Validation

| Correlation | r | p | Effect |
|------------|-----|------|--------|
| Toxicity vs Aggression | 0.78 | < .0001 | Large |
| Toxicity vs Disinhibition | 0.78 | < .0001 | Large |
| Toxicity vs Sophistication | 0.51 | 0.0003 | Large |
| Insult vs Disinhibition | 0.56 | 0.0001 | Large |

### Intervention Effects

Interventions weaken the BERT-aggression correlation (r drops from 0.78 to 0.35-0.52), suggesting they create dissociation between judge-perceived aggression and BERT-detected toxicity.

## Audit & Certification

### Audit Status: PASSED (2026-01-16)

All 11,964 responses were re-scored through BERT. Per-model averages matched stored values within tolerance (< 0.0001).

| Metric | Value |
|--------|-------|
| Models Validated | 270 (45 × 6 conditions) |
| Models Matched | 270 (100%) |
| Total Responses | 11,964 |

### Audit Files

| File | Description |
|------|-------------|
| `audit_samples.json` | 30 raw response samples (5 per condition) with BERT scores |
| `audit_results.json` | Certification summary data |
| `AUDIT_REPORT.md` | Human-readable audit report |

### Running an Audit

```bash
# Full re-scoring audit (all 11,964 responses)
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_full_audit.py
```

### audit_samples.json Schema

```json
{
  "metadata": {
    "audit_date": "2026-01-16T...",
    "bert_model": "unitary/toxic-bert",
    "conditions": ["baseline", ...],
    "samples_per_condition": 5
  },
  "audit_samples": {
    "<condition>": [
      {
        "sample_id": 1,
        "model_id": "Claude-4.5-Sonnet",
        "prompt": "...",
        "response": "...",
        "response_length_chars": 1294,
        "source_file": "job_*.json",
        "bert_scores": {
          "toxicity": 0.010266,
          "insult": 0.000507,
          ...
        }
      }
    ]
  },
  "certification": {
    "status": "PASSED",
    "total_models_validated": 270,
    "total_models_matched": 270
  }
}
```

## Adding New Analyses

When adding new BERT correlation analyses:

1. **Follow naming convention**: `run_bert_<x>_validation.py`
2. **Use shared utilities**: `normalize_model_name()`, pattern detection functions
3. **Match visualization style**: Use same colors, stats box, outlier/constrained markers
4. **Output both JSON and PNG**: Results file + scatter plots
5. **Include condition label**: All plots must show condition at top
6. **Update BERT_VALIDATION_BRIEF.md**: Add new analysis to cross-condition summary

## Troubleshooting

### BERT Model Not Found

```bash
# Model downloads automatically on first run
# Check cache: ls ~/.cache/huggingface/hub/models--unitary--toxic-bert/
```

### No Matching Models

Ensure profiles exist for the condition:
```bash
ls outputs/behavioral_profiles/<condition>/profiles/
```

### Low Correlation

Low correlation is informative - it means aggression captures something distinct from standard toxicity detection. Document this finding.

## Related Documentation

- Parent: `research_synthesis/CLAUDE.md` - Research synthesis overview
- Grandparent: `behavioral_profiles/CLAUDE.md` - H1/H2 analysis pipeline
- Root: `CLAUDE.md` - Project overview
