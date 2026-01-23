#!/usr/bin/env python3
"""
Aggregate BERT validation results from individual conditions into all_combined.

This script combines existing BERT results from each condition rather than
re-scoring all responses through BERT, which is much faster.

Usage:
    python3 aggregate_bert_results.py
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from datetime import datetime
import matplotlib.pyplot as plt

# Configuration
CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder", "naturalistic"]
BERT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BERT_DIR / "all_combined"
OUTLIER_SD_THRESHOLD = 2.0
CONSTRAINED_AGG_THRESHOLD = 1.6


def load_condition_results():
    """Load BERT results from all conditions with full provenance tracking."""
    model_data = defaultdict(lambda: {
        "toxicity_scores": [],
        "insult_scores": [],
        "aggression_scores": [],
        "n_responses": 0,
        "all_toxicity_scores": [],
        "all_insult_scores": []
    })
    conditions_with_data = []

    # Track provenance per condition
    provenance = {
        "source_files": {},
        "per_condition": {},
        "aggregation_timestamp": datetime.now().isoformat()
    }

    for condition in CONDITIONS:
        bert_file = BERT_DIR / condition / "bert_validation_results.json"
        if not bert_file.exists():
            print(f"  SKIP: {condition} - no results file")
            continue

        with open(bert_file) as f:
            data = json.load(f)

        conditions_with_data.append(condition)

        # Track source file info
        source_metadata = data.get("metadata", {})
        condition_evals = 0
        condition_models = 0

        for model in data.get("model_results", []):
            mid = model["model_id"]
            n = model.get("n_scored", 1)
            condition_evals += n
            condition_models += 1

            # Get individual scores or replicate average
            tox_scores = model.get("all_toxicity_scores", [model["bert_toxicity"]] * n)
            ins_scores = model.get("all_insult_scores", [model["bert_insult"]] * n)

            model_data[mid]["toxicity_scores"].extend(tox_scores)
            model_data[mid]["insult_scores"].extend(ins_scores)
            model_data[mid]["all_toxicity_scores"].extend(tox_scores)
            model_data[mid]["all_insult_scores"].extend(ins_scores)
            model_data[mid]["aggression_scores"].append(model["aggression"])
            model_data[mid]["n_responses"] += n

        # Record provenance for this condition
        provenance["source_files"][condition] = str(bert_file)
        provenance["per_condition"][condition] = {
            "source_file": str(bert_file),
            "source_date": source_metadata.get("date", "unknown"),
            "n_models": condition_models,
            "n_evaluations": condition_evals,
            "profiles_path": source_metadata.get("source_profiles", f"outputs/behavioral_profiles/{condition}/profiles"),
            "jobs_path": source_metadata.get("source_jobs", "outputs/single_prompt_jobs")
        }

    return model_data, conditions_with_data, provenance


def identify_patterns(x_vals, y_vals, ids, slope, intercept):
    """Identify outliers and constrained models from regression."""
    predicted = slope * np.array(x_vals) + intercept
    residuals = np.array(y_vals) - predicted
    residual_std = np.std(residuals)

    outliers = []
    constrained = []

    for i in range(len(x_vals)):
        sd_from_line = residuals[i] / residual_std if residual_std > 0 else 0

        if abs(residuals[i]) > OUTLIER_SD_THRESHOLD * residual_std:
            outliers.append({
                'idx': i,
                'model_id': ids[i],
                'residual': float(residuals[i]),
                'sd_from_line': float(sd_from_line)
            })

        if x_vals[i] > CONSTRAINED_AGG_THRESHOLD and residuals[i] < -0.005:
            constrained.append({
                'idx': i,
                'model_id': ids[i],
                'residual': float(residuals[i]),
                'sd_from_line': float(sd_from_line)
            })

    return outliers, constrained, float(residual_std)


def generate_scatter_plots(aggression, toxicity, insult, model_ids,
                           r_tox, p_tox, r_ins, p_ins,
                           slope_tox, intercept_tox, slope_ins, intercept_ins,
                           patterns_tox, patterns_ins, output_dir, n_conditions):
    """Generate scatter plots with research_synthesis styling."""

    # Sort for labeling
    sorted_by_agg = sorted(range(len(aggression)), key=lambda i: aggression[i])
    sorted_by_tox = sorted(range(len(toxicity)), key=lambda i: toxicity[i])
    sorted_by_ins = sorted(range(len(insult)), key=lambda i: insult[i])

    outlier_tox_ids = {o['model_id'] for o in patterns_tox['outliers']}
    outlier_ins_ids = {o['model_id'] for o in patterns_ins['outliers']}

    # =========================================================================
    # Plot 1: Toxicity vs Aggression
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(aggression, toxicity, alpha=0.7, s=150,
               c='#2ecc71', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})', zorder=3)

    x_line = np.linspace(min(aggression), max(aggression), 100)
    ax.plot(x_line, slope_tox * x_line + intercept_tox, 'k--', alpha=0.5, linewidth=2, zorder=1)

    # Outliers
    for o in patterns_tox['outliers']:
        ax.scatter([aggression[o['idx']]], [toxicity[o['idx']]],
                  s=400, facecolors='none', edgecolors='red', linewidth=3, zorder=5)
        label = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')[:15]
        ax.annotate(f"{label}\n({o['sd_from_line']:+.1f}σ)",
                   xy=(aggression[o['idx']], toxicity[o['idx']]),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=7, fontweight='bold', color='red',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='red'),
                   arrowprops=dict(arrowstyle='->', color='red'), zorder=10)

    ax.scatter([], [], s=400, facecolors='none', edgecolors='red', linewidth=3,
              label=f'Statistical Outliers (n={len(patterns_tox["outliers"])})')

    # Constrained
    for c in patterns_tox['constrained']:
        ax.scatter([aggression[c['idx']]], [toxicity[c['idx']]],
                  marker='D', s=200, color='#00CED1', alpha=0.9,
                  edgecolors='blue', linewidth=2.5, zorder=6)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5,
              label=f'Constrained (n={len(patterns_tox["constrained"])})')

    # Stats box
    r_sq = r_tox ** 2
    p_str = f"{p_tox:.6f}" if p_tox >= 0.0001 else "< .0001"
    stats_text = (
        f'Validation: BERT Toxicity ~ Judge Aggression\n'
        f'r = {r_tox:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {"Large" if abs(r_tox) >= 0.5 else "Medium" if abs(r_tox) >= 0.3 else "Small"}\n'
        f'N = {len(aggression)} models\n\n'
        f'Outliers: {len(patterns_tox["outliers"])} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(patterns_tox["constrained"])} (high-agg, low-tox)'
    )
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95), zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Toxicity Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Toxicity vs. Judge Aggression\n(Aggregated Across All Conditions)', fontsize=15, fontweight='bold', pad=20)
    fig.suptitle(f'Condition: all_combined ({n_conditions} conditions)', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_dir / "scatter_toxicity_vs_aggression.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_toxicity_vs_aggression.png")

    # =========================================================================
    # Plot 2: Insult vs Aggression
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(aggression, insult, alpha=0.7, s=150,
               c='#e74c3c', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})', zorder=3)

    ax.plot(x_line, slope_ins * x_line + intercept_ins, 'k--', alpha=0.5, linewidth=2, zorder=1)

    for o in patterns_ins['outliers']:
        ax.scatter([aggression[o['idx']]], [insult[o['idx']]],
                  s=400, facecolors='none', edgecolors='red', linewidth=3, zorder=5)
        label = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')[:15]
        ax.annotate(f"{label}\n({o['sd_from_line']:+.1f}σ)",
                   xy=(aggression[o['idx']], insult[o['idx']]),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=7, fontweight='bold', color='red',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='red'),
                   arrowprops=dict(arrowstyle='->', color='red'), zorder=10)

    ax.scatter([], [], s=400, facecolors='none', edgecolors='red', linewidth=3,
              label=f'Statistical Outliers (n={len(patterns_ins["outliers"])})')

    for c in patterns_ins['constrained']:
        ax.scatter([aggression[c['idx']]], [insult[c['idx']]],
                  marker='D', s=200, color='#00CED1', alpha=0.9,
                  edgecolors='blue', linewidth=2.5, zorder=6)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5,
              label=f'Constrained (n={len(patterns_ins["constrained"])})')

    r_sq = r_ins ** 2
    p_str = f"{p_ins:.6f}" if p_ins >= 0.0001 else "< .0001"
    stats_text = (
        f'Validation: BERT Insult ~ Judge Aggression\n'
        f'r = {r_ins:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {"Large" if abs(r_ins) >= 0.5 else "Medium" if abs(r_ins) >= 0.3 else "Small"}\n'
        f'N = {len(aggression)} models\n\n'
        f'Outliers: {len(patterns_ins["outliers"])} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(patterns_ins["constrained"])} (high-agg, low-ins)'
    )
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95), zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Insult Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Insult vs. Judge Aggression\n(Aggregated Across All Conditions)', fontsize=15, fontweight='bold', pad=20)
    fig.suptitle(f'Condition: all_combined ({n_conditions} conditions)', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_dir / "scatter_insult_vs_aggression.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_insult_vs_aggression.png")

    # =========================================================================
    # Plot 3: Combined 2-panel
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Toxicity panel
    axes[0].scatter(aggression, toxicity, alpha=0.7, s=120,
                    c='#2ecc71', edgecolors='black', linewidth=1.5, zorder=3)
    axes[0].plot(x_line, slope_tox * x_line + intercept_tox, 'k--', alpha=0.5, linewidth=2, zorder=1)

    for o in patterns_tox['outliers']:
        axes[0].scatter([aggression[o['idx']]], [toxicity[o['idx']]],
                       s=300, facecolors='none', edgecolors='red', linewidth=2.5, zorder=5)
        label = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')[:12]
        axes[0].annotate(f"{label}\n({o['sd_from_line']:+.1f}σ)",
                        xy=(aggression[o['idx']], toxicity[o['idx']]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=6, fontweight='bold', color='red',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='red'),
                        zorder=10)

    axes[0].text(0.05, 0.95,
                f'r = {r_tox:.3f}\nR² = {r_tox**2:.3f}\np < .0001\nOutliers: {len(patterns_tox["outliers"])}',
                transform=axes[0].transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    axes[0].set_xlabel('Judge Aggression (1-10)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('BERT Toxicity (0-1)', fontsize=12, fontweight='bold')
    axes[0].set_title('Toxicity Validation', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_axisbelow(True)

    # Insult panel
    axes[1].scatter(aggression, insult, alpha=0.7, s=120,
                    c='#e74c3c', edgecolors='black', linewidth=1.5, zorder=3)
    axes[1].plot(x_line, slope_ins * x_line + intercept_ins, 'k--', alpha=0.5, linewidth=2, zorder=1)

    for o in patterns_ins['outliers']:
        axes[1].scatter([aggression[o['idx']]], [insult[o['idx']]],
                       s=300, facecolors='none', edgecolors='red', linewidth=2.5, zorder=5)
        label = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')[:12]
        axes[1].annotate(f"{label}\n({o['sd_from_line']:+.1f}σ)",
                        xy=(aggression[o['idx']], insult[o['idx']]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=6, fontweight='bold', color='red',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='red'),
                        zorder=10)

    axes[1].text(0.05, 0.95,
                f'r = {r_ins:.3f}\nR² = {r_ins**2:.3f}\np < .0001\nOutliers: {len(patterns_ins["outliers"])}',
                transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    axes[1].set_xlabel('Judge Aggression (1-10)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('BERT Insult (0-1)', fontsize=12, fontweight='bold')
    axes[1].set_title('Insult Validation', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_axisbelow(True)

    fig.text(0.5, 0.998, f'Condition: all_combined ({n_conditions} conditions)', ha='center', va='top',
             fontsize=11, fontweight='bold', color='#666666')
    fig.suptitle(f'BERT Validation: Aggregated Across All Conditions (N={len(aggression)})',
                 fontsize=15, fontweight='bold', y=0.97)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(output_dir / "scatter_combined.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_combined.png")


def generate_validation_report(data, output_dir):
    """Generate markdown validation report."""
    conditions_list = data['metadata'].get('conditions_included', ['all_combined'])
    conditions_str = ", ".join(conditions_list) if conditions_list else 'all_combined'
    n_conditions = data['metadata'].get('n_conditions', len(conditions_list))
    total_evals = data['metadata'].get('total_evaluations', 'N/A')

    # Build provenance table
    provenance = data.get('provenance', {})
    per_condition = provenance.get('per_condition', {})

    provenance_rows = ""
    for cond in sorted(per_condition.keys()):
        info = per_condition[cond]
        source_date = info.get('source_date', 'unknown')
        date_str = source_date[:10] if source_date != 'unknown' else 'N/A'
        provenance_rows += f"| {cond} | {info['n_models']} | {info['n_evaluations']:,} | {date_str} |\n"

    report = f"""# BERT Toxicity Validation Report

**Generated**: {data['metadata']['date'][:10]}
**Experiment**: Independent validation of LLM-as-judge aggression scores
**Method**: Aggregated from individual condition results

---

## Summary

| Metric | Value |
|--------|-------|
| **N (models)** | {data['sample']['n_models']} |
| **Total Evaluations** | {total_evals:,} |
| **Conditions** | {n_conditions} ({conditions_str}) |
| **BERT Toxicity vs. Aggression** | r = {data['correlations']['toxicity']['r']:.3f}, p = {data['correlations']['toxicity']['p']:.6f} |
| **BERT Insult vs. Aggression** | r = {data['correlations']['insult']['r']:.3f}, p = {data['correlations']['insult']['p']:.6f} |
| **Interpretation** | {data['interpretation']} |

---

## Visualizations

### BERT Toxicity vs. Judge Aggression
![Toxicity Scatter](scatter_toxicity_vs_aggression.png)

### BERT Insult vs. Judge Aggression
![Insult Scatter](scatter_insult_vs_aggression.png)

### Combined View
![Combined Scatter](scatter_combined.png)

---

## Data Trail

### 1. BERT Model

| Field | Value |
|-------|-------|
| **Model Name** | `{data['metadata']['bert_model']}` |
| **Hosted On** | Hugging Face (downloaded locally) |
| **Model URL** | {data['metadata']['bert_model_url']} |
| **Architecture** | BERT (bert-base-uncased), 110M parameters |
| **Training Data** | {data['metadata']['training_data']} |
| **Training Data URL** | {data['metadata']['training_data_url']} |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |
| **Max Sequence Length** | 512 tokens |
| **Execution** | Local inference (no API calls) |

### 2. Source Data

| Field | Value |
|-------|-------|
| **Aggregation Method** | Combined from individual condition BERT results |
| **Conditions Included** | {conditions_str} |
| **N Conditions** | {n_conditions} |
| **Models Evaluated** | {data['sample']['n_models']} |
| **Total Evaluations** | {total_evals:,} |

### 3. Data Provenance

Per-condition breakdown of source data:

| Condition | Models | Evaluations | Source Date |
|-----------|--------|-------------|-------------|
{provenance_rows}
**Audit File**: `bert_validation_results.json` contains full provenance in the `provenance` field.

### 4. Statistical Results

#### Correlations

| Measure | r | p-value | Effect Size |
|---------|---|---------|-------------|
| BERT Toxicity | {data['correlations']['toxicity']['r']:.4f} | {data['correlations']['toxicity']['p']:.6f} | {data['correlations']['toxicity']['interpretation']} |
| BERT Insult | {data['correlations']['insult']['r']:.4f} | {data['correlations']['insult']['p']:.6f} | {data['correlations']['insult']['interpretation']} |

#### Regression: Toxicity ~ Aggression

| Parameter | Value |
|-----------|-------|
| Slope | {data['regression']['toxicity']['slope']:.6f} |
| Intercept | {data['regression']['toxicity']['intercept']:.6f} |
| R² | {data['regression']['toxicity']['r_squared']:.4f} |
| Standard Error | {data['regression']['toxicity']['std_err']:.6f} |

#### Regression: Insult ~ Aggression

| Parameter | Value |
|-----------|-------|
| Slope | {data['regression']['insult']['slope']:.6f} |
| Intercept | {data['regression']['insult']['intercept']:.6f} |
| R² | {data['regression']['insult']['r_squared']:.4f} |
| Standard Error | {data['regression']['insult']['std_err']:.6f} |

### 5. Score Ranges

| Measure | Min | Max |
|---------|-----|-----|
| Judge Aggression | {data['sample']['aggression_range'][0]:.2f} | {data['sample']['aggression_range'][1]:.2f} |
| BERT Toxicity | {data['sample']['toxicity_range'][0]:.4f} | {data['sample']['toxicity_range'][1]:.4f} |
| BERT Insult | {data['sample']['insult_range'][0]:.4f} | {data['sample']['insult_range'][1]:.4f} |

---

## Output Files

| File | Description |
|------|-------------|
| `bert_validation_results.json` | Complete results with per-model scores (for downstream use) |
| `scatter_toxicity_vs_aggression.png` | Toxicity correlation scatter plot |
| `scatter_insult_vs_aggression.png` | Insult correlation scatter plot |
| `scatter_combined.png` | Combined 2-panel visualization |
| `VALIDATION_REPORT.md` | This report |

---

## Interpretation

{data['interpretation']}

**Effect size thresholds** (Cohen's conventions):
- |r| < 0.10: Negligible
- |r| 0.10-0.30: Small
- |r| 0.30-0.50: Medium
- |r| >= 0.50: Large

---

## Reproducibility

```bash
# Regenerate from existing condition results
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/aggregate_bert_results.py
```

---

## References

1. Unitary AI toxic-bert: {data['metadata']['bert_model_url']}
2. Jigsaw Toxic Comment Challenge: {data['metadata']['training_data_url']}
3. BERT paper: Devlin et al. (2019) "BERT: Pre-training of Deep Bidirectional Transformers"
"""

    report_file = output_dir / "VALIDATION_REPORT.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"  Saved: VALIDATION_REPORT.md")


def main():
    print("=" * 70)
    print("Aggregating BERT Validation Results: all_combined")
    print("=" * 70)

    # Load data from all conditions
    print("\n[1/4] Loading BERT results from individual conditions...")
    model_data, conditions_with_data, provenance = load_condition_results()

    if not conditions_with_data:
        print("ERROR: No condition results found")
        return

    print(f"  Loaded {len(conditions_with_data)} conditions: {conditions_with_data}")
    print(f"  Total models: {len(model_data)}")

    # Print per-condition provenance
    print("\n  Per-condition breakdown:")
    for cond, info in provenance["per_condition"].items():
        print(f"    {cond}: {info['n_models']} models, {info['n_evaluations']:,} evaluations")

    # Calculate per-model aggregates
    print("\n[2/4] Calculating per-model aggregates...")
    results = []
    total_evaluations = 0

    for mid, data in sorted(model_data.items()):
        avg_tox = np.mean(data["toxicity_scores"])
        avg_ins = np.mean(data["insult_scores"])
        avg_agg = np.mean(data["aggression_scores"])
        n_scored = len(data["toxicity_scores"])
        total_evaluations += n_scored

        results.append({
            "model_id": mid,
            "aggression": float(avg_agg),
            "bert_toxicity": float(avg_tox),
            "bert_insult": float(avg_ins),
            "n_responses": data["n_responses"],
            "n_scored": n_scored,
            "all_toxicity_scores": [float(x) for x in data["all_toxicity_scores"]],
            "all_insult_scores": [float(x) for x in data["all_insult_scores"]]
        })

    print(f"  Total evaluations: {total_evaluations:,}")

    # Calculate statistics
    print("\n[3/4] Computing correlations...")
    aggression = [r["aggression"] for r in results]
    toxicity = [r["bert_toxicity"] for r in results]
    insult = [r["bert_insult"] for r in results]
    model_ids = [r["model_id"] for r in results]

    r_tox, p_tox = stats.pearsonr(aggression, toxicity)
    r_ins, p_ins = stats.pearsonr(aggression, insult)

    slope_tox, intercept_tox, _, _, std_err_tox = stats.linregress(aggression, toxicity)
    slope_ins, intercept_ins, _, _, std_err_ins = stats.linregress(aggression, insult)

    print(f"  BERT Toxicity vs Aggression: r = {r_tox:.3f}, p = {p_tox:.6f}")
    print(f"  BERT Insult vs Aggression:   r = {r_ins:.3f}, p = {p_ins:.6f}")

    # Identify patterns
    outliers_tox, constrained_tox, residual_std_tox = identify_patterns(
        aggression, toxicity, model_ids, slope_tox, intercept_tox)
    outliers_ins, constrained_ins, residual_std_ins = identify_patterns(
        aggression, insult, model_ids, slope_ins, intercept_ins)

    patterns_tox = {"outliers": outliers_tox, "constrained": constrained_tox, "residual_std": residual_std_tox}
    patterns_ins = {"outliers": outliers_ins, "constrained": constrained_ins, "residual_std": residual_std_ins}

    # Interpretation
    if abs(r_tox) >= 0.5:
        interp = "Strong validation - BERT toxicity validates aggression measure"
    elif abs(r_tox) >= 0.3:
        interp = "Moderate validation - Partial overlap between constructs"
    else:
        interp = "Weak validation - Aggression captures something distinct from toxicity"

    # Generate plots
    print("\n[4/4] Generating visualizations...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generate_scatter_plots(
        aggression, toxicity, insult, model_ids,
        r_tox, p_tox, r_ins, p_ins,
        slope_tox, intercept_tox, slope_ins, intercept_ins,
        patterns_tox, patterns_ins, OUTPUT_DIR, len(conditions_with_data)
    )

    # Build output JSON
    output = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "bert_model": "unitary/toxic-bert",
            "bert_model_url": "https://huggingface.co/unitary/toxic-bert",
            "training_data": "Jigsaw Toxic Comment Classification Challenge",
            "training_data_url": "https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge",
            "source_condition": "all_combined",
            "aggregation_method": "Combined from individual condition BERT results",
            "conditions_included": sorted(conditions_with_data),
            "n_conditions": len(conditions_with_data),
            "total_evaluations": total_evaluations
        },
        "provenance": provenance,
        "sample": {
            "n_models": len(results),
            "total_evaluations": total_evaluations,
            "aggression_range": [float(min(aggression)), float(max(aggression))],
            "toxicity_range": [float(min(toxicity)), float(max(toxicity))],
            "insult_range": [float(min(insult)), float(max(insult))]
        },
        "correlations": {
            "toxicity": {
                "r": float(r_tox),
                "p": float(p_tox),
                "interpretation": "large" if abs(r_tox) >= 0.5 else "medium" if abs(r_tox) >= 0.3 else "small"
            },
            "insult": {
                "r": float(r_ins),
                "p": float(p_ins),
                "interpretation": "large" if abs(r_ins) >= 0.5 else "medium" if abs(r_ins) >= 0.3 else "small"
            }
        },
        "regression": {
            "toxicity": {
                "slope": float(slope_tox),
                "intercept": float(intercept_tox),
                "std_err": float(std_err_tox),
                "r_squared": float(r_tox ** 2)
            },
            "insult": {
                "slope": float(slope_ins),
                "intercept": float(intercept_ins),
                "std_err": float(std_err_ins),
                "r_squared": float(r_ins ** 2)
            }
        },
        "interpretation": interp,
        "patterns": {
            "toxicity": {
                "outliers": [{"model_id": o["model_id"], "residual": o["residual"], "sd_from_line": o["sd_from_line"]} for o in outliers_tox],
                "constrained": [{"model_id": c["model_id"], "residual": c["residual"], "sd_from_line": c["sd_from_line"]} for c in constrained_tox],
                "residual_std": residual_std_tox
            },
            "insult": {
                "outliers": [{"model_id": o["model_id"], "residual": o["residual"], "sd_from_line": o["sd_from_line"]} for o in outliers_ins],
                "constrained": [{"model_id": c["model_id"], "residual": c["residual"], "sd_from_line": c["sd_from_line"]} for c in constrained_ins],
                "residual_std": residual_std_ins
            }
        },
        "model_results": results,
        "output_files": {
            "results_json": "bert_validation_results.json",
            "scatter_toxicity": "scatter_toxicity_vs_aggression.png",
            "scatter_insult": "scatter_insult_vs_aggression.png",
            "scatter_combined": "scatter_combined.png",
            "report": "VALIDATION_REPORT.md"
        }
    }

    # Save JSON
    output_file = OUTPUT_DIR / "bert_validation_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved: bert_validation_results.json")

    # Generate report
    generate_validation_report(output, OUTPUT_DIR)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nConditions: {len(conditions_with_data)} ({', '.join(conditions_with_data)})")
    print(f"Models: {len(results)}")
    print(f"Total Evaluations: {total_evaluations:,}")
    print(f"\nBERT Toxicity vs Aggression: r = {r_tox:.3f}, p = {p_tox:.6f} ({output['correlations']['toxicity']['interpretation']})")
    print(f"BERT Insult vs Aggression:   r = {r_ins:.3f}, p = {p_ins:.6f} ({output['correlations']['insult']['interpretation']})")
    print(f"\nOutliers (toxicity): {len(outliers_tox)}")
    print(f"Outliers (insult): {len(outliers_ins)}")


if __name__ == "__main__":
    main()
