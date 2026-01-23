#!/usr/bin/env python3
"""
Generate outliers_removed analysis for BERT validation.

Removes statistical outliers (|residual| > 2 SD) from the analysis
and regenerates all outputs in an outliers_removed/ subfolder.

Usage:
    python3 generate_outliers_removed.py [--condition CONDITION]
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

BERT_DIR = Path(__file__).parent.parent
OUTLIER_SD_THRESHOLD = 2.0
CONSTRAINED_AGG_THRESHOLD = 1.6


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
                           patterns_tox, patterns_ins, output_dir,
                           condition_label, n_original, outliers_removed_list):
    """Generate scatter plots with research_synthesis styling."""

    # =========================================================================
    # Plot 1: Toxicity vs Aggression
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(aggression, toxicity, alpha=0.7, s=150,
               c='#2ecc71', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})', zorder=3)

    x_line = np.linspace(min(aggression), max(aggression), 100)
    ax.plot(x_line, slope_tox * x_line + intercept_tox, 'k--', alpha=0.5, linewidth=2, zorder=1)

    # Outliers (in the reduced dataset)
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
        f'N = {len(aggression)} models (removed {n_original - len(aggression)})\n\n'
        f'Outliers: {len(patterns_tox["outliers"])} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(patterns_tox["constrained"])} (high-agg, low-tox)'
    )
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95), zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Toxicity Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Toxicity vs. Judge Aggression\n(Outliers Removed)', fontsize=15, fontweight='bold', pad=20)
    fig.suptitle(f'Condition: {condition_label} (outliers removed)', fontsize=11, fontweight='bold', y=0.995, color='#666666')

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
        f'N = {len(aggression)} models (removed {n_original - len(aggression)})\n\n'
        f'Outliers: {len(patterns_ins["outliers"])} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(patterns_ins["constrained"])} (high-agg, low-ins)'
    )
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95), zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Insult Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Insult vs. Judge Aggression\n(Outliers Removed)', fontsize=15, fontweight='bold', pad=20)
    fig.suptitle(f'Condition: {condition_label} (outliers removed)', fontsize=11, fontweight='bold', y=0.995, color='#666666')

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

    axes[0].text(0.05, 0.95,
                f'r = {r_tox:.3f}\nR² = {r_tox**2:.3f}\np < .0001\nN = {len(aggression)}',
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

    axes[1].text(0.05, 0.95,
                f'r = {r_ins:.3f}\nR² = {r_ins**2:.3f}\np < .0001\nN = {len(aggression)}',
                transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    axes[1].set_xlabel('Judge Aggression (1-10)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('BERT Insult (0-1)', fontsize=12, fontweight='bold')
    axes[1].set_title('Insult Validation', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_axisbelow(True)

    fig.text(0.5, 0.998, f'Condition: {condition_label} (outliers removed)', ha='center', va='top',
             fontsize=11, fontweight='bold', color='#666666')
    fig.suptitle(f'BERT Validation: Outliers Removed (N={len(aggression)}, removed {n_original - len(aggression)})',
                 fontsize=15, fontweight='bold', y=0.97)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(output_dir / "scatter_combined.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_combined.png")


def generate_validation_report(data, output_dir, outliers_removed_info):
    """Generate markdown validation report."""
    conditions_list = data['metadata'].get('conditions_included', ['all_combined'])
    conditions_str = ", ".join(conditions_list) if conditions_list else 'all_combined'
    n_conditions = data['metadata'].get('n_conditions', len(conditions_list))
    total_evals = data['metadata'].get('total_evaluations', 'N/A')

    # Format removed outliers
    removed_list = outliers_removed_info['outliers_removed']
    removed_str = "\n".join([f"  - {o['model_id']} ({o['sd_from_line']:+.2f} SD, {o['reason']})" for o in removed_list])

    report = f"""# BERT Toxicity Validation Report (Outliers Removed)

**Generated**: {data['metadata']['date'][:10]}
**Experiment**: Independent validation of LLM-as-judge aggression scores
**Method**: Aggregated from individual condition results, outliers removed

---

## Outlier Removal Summary

| Metric | Value |
|--------|-------|
| **Original N** | {outliers_removed_info['n_original']} |
| **Outliers Removed** | {outliers_removed_info['n_removed']} |
| **Final N** | {data['sample']['n_models']} |
| **Threshold** | |residual| > {OUTLIER_SD_THRESHOLD} SD |

### Models Removed

{removed_str}

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

### Comparison with Full Dataset

| Metric | Full Dataset | Outliers Removed | Change |
|--------|--------------|------------------|--------|
| N | {outliers_removed_info['n_original']} | {data['sample']['n_models']} | -{outliers_removed_info['n_removed']} |
| r (Toxicity) | {outliers_removed_info['original_r_tox']:.3f} | {data['correlations']['toxicity']['r']:.3f} | {data['correlations']['toxicity']['r'] - outliers_removed_info['original_r_tox']:+.3f} |
| r (Insult) | {outliers_removed_info['original_r_ins']:.3f} | {data['correlations']['insult']['r']:.3f} | {data['correlations']['insult']['r'] - outliers_removed_info['original_r_ins']:+.3f} |

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

### 2. Source Data

| Field | Value |
|-------|-------|
| **Source** | {data['metadata']['source_condition']}/bert_validation_results.json |
| **Conditions Included** | {conditions_str} |
| **N Conditions** | {n_conditions} |
| **Original Models** | {outliers_removed_info['n_original']} |
| **Models After Removal** | {data['sample']['n_models']} |
| **Total Evaluations** | {total_evals:,} |

### 3. Statistical Results

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

---

## Output Files

| File | Description |
|------|-------------|
| `bert_validation_results.json` | Complete results with per-model scores |
| `outlier_removal_info.json` | Details of removed models |
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
# Regenerate outliers_removed analysis
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/generate_outliers_removed.py --condition all_combined
```
"""

    report_file = output_dir / "VALIDATION_REPORT.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"  Saved: VALIDATION_REPORT.md")


def main(condition: str = "all_combined"):
    print("=" * 70)
    print(f"Generating Outliers Removed Analysis: {condition}")
    print("=" * 70)

    # Load source results
    source_file = BERT_DIR / condition / "bert_validation_results.json"
    if not source_file.exists():
        print(f"ERROR: Source file not found: {source_file}")
        return

    print(f"\n[1/5] Loading source results from {condition}...")
    with open(source_file) as f:
        source_data = json.load(f)

    model_results = source_data.get("model_results", [])
    n_original = len(model_results)
    print(f"  Loaded {n_original} models")

    # Get original correlations
    original_r_tox = source_data['correlations']['toxicity']['r']
    original_r_ins = source_data['correlations']['insult']['r']

    # Identify outliers (union of toxicity and insult outliers)
    print(f"\n[2/5] Identifying outliers...")
    tox_outliers = {o['model_id'] for o in source_data['patterns']['toxicity']['outliers']}
    ins_outliers = {o['model_id'] for o in source_data['patterns']['insult']['outliers']}
    all_outliers = tox_outliers | ins_outliers

    print(f"  Toxicity outliers: {len(tox_outliers)} - {tox_outliers}")
    print(f"  Insult outliers: {len(ins_outliers)} - {ins_outliers}")
    print(f"  Union (to remove): {len(all_outliers)} - {all_outliers}")

    # Build removal info
    outliers_removed_list = []
    for o in source_data['patterns']['toxicity']['outliers']:
        reason = "toxicity outlier"
        if o['model_id'] in ins_outliers:
            reason = "toxicity + insult outlier"
        outliers_removed_list.append({
            "model_id": o['model_id'],
            "sd_from_line": o['sd_from_line'],
            "reason": reason
        })
    for o in source_data['patterns']['insult']['outliers']:
        if o['model_id'] not in tox_outliers:
            outliers_removed_list.append({
                "model_id": o['model_id'],
                "sd_from_line": o['sd_from_line'],
                "reason": "insult outlier"
            })

    # Filter models
    print(f"\n[3/5] Filtering models...")
    filtered_results = [m for m in model_results if m['model_id'] not in all_outliers]
    n_filtered = len(filtered_results)
    print(f"  Retained {n_filtered} models (removed {n_original - n_filtered})")

    # Recalculate statistics
    print(f"\n[4/5] Recalculating statistics...")
    aggression = [r["aggression"] for r in filtered_results]
    toxicity = [r["bert_toxicity"] for r in filtered_results]
    insult = [r["bert_insult"] for r in filtered_results]
    model_ids = [r["model_id"] for r in filtered_results]

    # Recalculate total evaluations
    total_evaluations = sum(r.get("n_scored", 0) for r in filtered_results)

    r_tox, p_tox = stats.pearsonr(aggression, toxicity)
    r_ins, p_ins = stats.pearsonr(aggression, insult)

    slope_tox, intercept_tox, _, _, std_err_tox = stats.linregress(aggression, toxicity)
    slope_ins, intercept_ins, _, _, std_err_ins = stats.linregress(aggression, insult)

    print(f"  BERT Toxicity vs Aggression: r = {r_tox:.3f}, p = {p_tox:.6f} (was {original_r_tox:.3f})")
    print(f"  BERT Insult vs Aggression:   r = {r_ins:.3f}, p = {p_ins:.6f} (was {original_r_ins:.3f})")

    # Identify patterns in filtered data
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

    # Generate outputs
    print(f"\n[5/5] Generating outputs...")
    output_dir = BERT_DIR / condition / "outliers_removed"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate plots
    generate_scatter_plots(
        aggression, toxicity, insult, model_ids,
        r_tox, p_tox, r_ins, p_ins,
        slope_tox, intercept_tox, slope_ins, intercept_ins,
        patterns_tox, patterns_ins, output_dir,
        condition, n_original, outliers_removed_list
    )

    # Build output JSON
    output = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "bert_model": source_data['metadata']['bert_model'],
            "bert_model_url": source_data['metadata']['bert_model_url'],
            "training_data": source_data['metadata']['training_data'],
            "training_data_url": source_data['metadata']['training_data_url'],
            "source_condition": condition,
            "analysis_type": "outliers_removed",
            "conditions_included": source_data['metadata'].get('conditions_included', [condition]),
            "n_conditions": source_data['metadata'].get('n_conditions', 1),
            "total_evaluations": total_evaluations,
            "outlier_threshold_sd": OUTLIER_SD_THRESHOLD
        },
        "sample": {
            "n_models": n_filtered,
            "n_original": n_original,
            "n_removed": n_original - n_filtered,
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
        "model_results": filtered_results,
        "output_files": {
            "results_json": "bert_validation_results.json",
            "outlier_info": "outlier_removal_info.json",
            "scatter_toxicity": "scatter_toxicity_vs_aggression.png",
            "scatter_insult": "scatter_insult_vs_aggression.png",
            "scatter_combined": "scatter_combined.png",
            "report": "VALIDATION_REPORT.md"
        }
    }

    # Save JSON
    output_file = output_dir / "bert_validation_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Saved: bert_validation_results.json")

    # Save outlier removal info
    outlier_info = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "source_condition": condition,
            "threshold_sd": OUTLIER_SD_THRESHOLD
        },
        "n_original": n_original,
        "n_removed": n_original - n_filtered,
        "n_final": n_filtered,
        "original_r_tox": original_r_tox,
        "original_r_ins": original_r_ins,
        "final_r_tox": float(r_tox),
        "final_r_ins": float(r_ins),
        "outliers_removed": outliers_removed_list
    }
    outlier_file = output_dir / "outlier_removal_info.json"
    with open(outlier_file, "w") as f:
        json.dump(outlier_info, f, indent=2)
    print(f"  Saved: outlier_removal_info.json")

    # Generate report
    generate_validation_report(output, output_dir, outlier_info)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nOriginal: {n_original} models")
    print(f"Removed: {n_original - n_filtered} outliers")
    print(f"Final: {n_filtered} models")
    print(f"\nBERT Toxicity vs Aggression: r = {r_tox:.3f} (was {original_r_tox:.3f}, Δ = {r_tox - original_r_tox:+.3f})")
    print(f"BERT Insult vs Aggression:   r = {r_ins:.3f} (was {original_r_ins:.3f}, Δ = {r_ins - original_r_ins:+.3f})")
    print(f"\nOutput: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", type=str, default="all_combined",
                        help="Condition to process (default: all_combined)")
    args = parser.parse_args()

    main(condition=args.condition)
