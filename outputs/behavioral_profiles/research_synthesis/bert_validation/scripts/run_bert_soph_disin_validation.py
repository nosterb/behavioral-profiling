#!/usr/bin/env python3
"""
BERT Toxicity vs. Sophistication and Disinhibition Analysis.

Extends BERT validation to correlate toxicity/insult scores with:
- Sophistication (depth + authenticity average)
- Disinhibition (transgression + aggression + tribalism + grandiosity average)

Usage:
    python3 run_bert_soph_disin_validation.py --condition baseline
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


# =============================================================================
# CONFIGURABLE THRESHOLDS (matching research_synthesis)
# =============================================================================
OUTLIER_SD_THRESHOLD = 2.0  # Statistical outliers: residuals > 2 SD


def load_bert_results(condition: str) -> dict:
    """Load existing BERT validation results."""
    bert_file = Path(f"outputs/behavioral_profiles/research_synthesis/bert_validation/{condition}/bert_validation_results.json")
    if not bert_file.exists():
        print(f"ERROR: BERT results not found at {bert_file}")
        print("Run run_bert_validation.py first.")
        return None

    with open(bert_file) as f:
        return json.load(f)


def load_classification_data(condition: str) -> dict:
    """Load median split classification with sophistication/disinhibition."""
    class_file = Path(f"outputs/behavioral_profiles/{condition}/median_split_classification.json")
    if not class_file.exists():
        print(f"ERROR: Classification not found at {class_file}")
        return None

    with open(class_file) as f:
        return json.load(f)


def normalize_model_name(name: str) -> str:
    """Normalize model name for matching."""
    import re
    n = name.lower()

    is_thinking = "thinking" in n

    n = n.replace("-thinking", "").replace("_(thinking)", "").replace(" (thinking)", "")
    n = n.replace("-global", "").replace("_global", "")
    n = re.sub(r'-\d{8}.*', '', n)
    n = re.sub(r'_\d{8}.*', '', n)
    n = n.replace(" ", "-").replace("_", "-")
    n = n.strip("-")

    if is_thinking:
        n = n + "-thinking"

    return n


def identify_patterns(x_vals, y_vals, ids, slope, intercept, x_name="x"):
    """Identify outliers and constrained models from regression."""
    x_arr = np.array(x_vals)
    y_arr = np.array(y_vals)
    predicted = slope * x_arr + intercept
    residuals = y_arr - predicted
    residual_std = np.std(residuals)

    # Constrained threshold: top 25% of X range
    x_75th = np.percentile(x_arr, 75)

    outliers = []
    constrained = []

    for i in range(len(x_vals)):
        sd_from_line = residuals[i] / residual_std if residual_std > 0 else 0

        # Outlier: |residual| > threshold * SD
        if abs(residuals[i]) > OUTLIER_SD_THRESHOLD * residual_std:
            outliers.append({
                'idx': i,
                'model_id': ids[i],
                'residual': float(residuals[i]),
                'sd_from_line': float(sd_from_line)
            })

        # Constrained: high X but below-predicted Y (negative residual)
        if x_vals[i] > x_75th and residuals[i] < -0.5 * residual_std:
            constrained.append({
                'idx': i,
                'model_id': ids[i],
                'residual': float(residuals[i]),
                'sd_from_line': float(sd_from_line)
            })

    return outliers, constrained, residuals, float(residual_std)


def get_extreme_labels(x_vals, y_vals, ids, sorted_x, sorted_y, x_name, y_name, outliers, constrained):
    """Get extreme models for labeling with tags (including outliers)."""
    models_to_label = {}

    # Min/max x - top 2 each
    for i in sorted_x[:2]:
        if ids[i] not in models_to_label:
            models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
        models_to_label[ids[i]]['tags'].append(f"min-{x_name}={x_vals[i]:.2f}")
        models_to_label[ids[i]]['priority'] += 10

    for i in sorted_x[-2:]:
        if ids[i] not in models_to_label:
            models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
        models_to_label[ids[i]]['tags'].append(f"max-{x_name}={x_vals[i]:.2f}")
        models_to_label[ids[i]]['priority'] += 10

    # Min/max y - top 2 each
    for i in sorted_y[:2]:
        if ids[i] not in models_to_label:
            models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
        models_to_label[ids[i]]['tags'].append(f"min-{y_name}={y_vals[i]:.4f}")
        models_to_label[ids[i]]['priority'] += 5

    for i in sorted_y[-2:]:
        if ids[i] not in models_to_label:
            models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
        models_to_label[ids[i]]['tags'].append(f"max-{y_name}={y_vals[i]:.4f}")
        models_to_label[ids[i]]['priority'] += 5

    # Add ALL outliers with residual info
    for o in outliers:
        mid = o['model_id']
        if mid not in models_to_label:
            models_to_label[mid] = {'idx': o['idx'], 'tags': [], 'priority': 0}
        models_to_label[mid]['tags'].append(f"outlier({o['sd_from_line']:+.1f}σ)")
        models_to_label[mid]['priority'] += 20

    # Add constrained models
    for c in constrained:
        mid = c['model_id']
        if mid not in models_to_label:
            models_to_label[mid] = {'idx': c['idx'], 'tags': [], 'priority': 0}
        models_to_label[mid]['tags'].append("constrained")
        models_to_label[mid]['priority'] += 15

    return models_to_label


def generate_scatter_plot(x_vals, y_vals, model_ids, classifications,
                          r_val, p_val, slope, intercept,
                          x_label, y_label, title,
                          output_path, condition, x_name, y_name,
                          point_color='#2ecc71'):
    """Generate a single scatter plot with full research_synthesis styling."""

    x_arr = np.array(x_vals)
    y_arr = np.array(y_vals)

    # Identify patterns
    outliers, constrained, residuals, residual_std = identify_patterns(
        x_vals, y_vals, model_ids, slope, intercept, x_name)

    # Sort indices for extremes
    sorted_x = sorted(range(len(x_vals)), key=lambda i: x_vals[i])
    sorted_y = sorted(range(len(y_vals)), key=lambda i: y_vals[i])

    # Get labels
    labels_to_show = get_extreme_labels(x_vals, y_vals, model_ids,
                                         sorted_x, sorted_y, x_name, y_name,
                                         outliers, constrained)

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Color by classification
    colors = ['#e74c3c' if c == 'High-Sophistication' else '#3498db' for c in classifications]

    # Main scatter
    ax.scatter(x_arr, y_arr, c=colors, alpha=0.7, s=150,
               edgecolors='black', linewidth=1.5, zorder=3)

    # Regression line
    x_line = np.linspace(min(x_vals), max(x_vals), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'k--', alpha=0.5, linewidth=2, label='Best Fit', zorder=1)

    # Highlight statistical outliers with red circles
    if outliers:
        for o in outliers:
            ax.scatter([x_vals[o['idx']]], [y_vals[o['idx']]],
                      s=400, facecolors='none', edgecolors='red',
                      linewidth=3, zorder=5)
    ax.scatter([], [], s=400, facecolors='none', edgecolors='red',
              linewidth=3, label=f'Statistical Outliers (n={len(outliers)})')

    # Highlight constrained models with cyan diamonds
    if constrained:
        for c in constrained:
            ax.scatter([x_vals[c['idx']]], [y_vals[c['idx']]],
                      marker='D', s=200, color='#00CED1', alpha=0.9,
                      edgecolors='blue', linewidth=2.5, zorder=6)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5,
              label=f'Constrained (n={len(constrained)})')

    # Label extreme models
    for j, (mid, info) in enumerate(sorted(labels_to_show.items(), key=lambda x: -x[1]['priority'])):
        i = info['idx']
        tags = info['tags']

        # Shorten model name
        label_name = mid.replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 18:
            label_name = label_name[:15] + '...'

        tag_text = '\n'.join(tags[:2])
        full_label = f"{label_name}\n{tag_text}"

        # Smart positioning
        x_offset = -70 if x_vals[i] < np.median(x_vals) else 70
        y_offset = -40 if y_vals[i] < np.median(y_vals) else 40
        y_offset += (j % 3) * 15

        ax.annotate(full_label,
                   xy=(x_vals[i], y_vals[i]),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=6.5, fontweight='bold', color='navy',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                            alpha=0.85, edgecolor='navy'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                 color='navy', lw=1.3),
                   zorder=9)

    # Stats text box
    r_sq = r_val ** 2
    p_str = f"{p_val:.6f}" if p_val >= 0.0001 else "< .0001"
    effect = "Large" if abs(r_val) >= 0.5 else "Medium" if abs(r_val) >= 0.3 else "Small"
    stats_text = (
        f'Validation: BERT {y_name.title()} ~ {x_name.title()}\n'
        f'r = {r_val:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {effect}\n'
        f'N = {len(x_vals)} models\n\n'
        f'Outliers: {len(outliers)} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(constrained)} (high-{x_name}, low-{y_name})'
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95),
            zorder=7)

    # Classification legend
    ax.scatter([], [], c='#e74c3c', s=100, label='High-Sophistication')
    ax.scatter([], [], c='#3498db', s=100, label='Low-Sophistication')

    ax.set_xlabel(x_label, fontsize=13, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=13, fontweight='bold')
    ax.set_title(title, fontsize=15, fontweight='bold', pad=20)

    # Condition label
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold',
                 y=0.995, color='#666666')

    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return {
        'outliers': outliers,
        'constrained': constrained,
        'residual_std': residual_std
    }


def run_soph_disin_analysis(condition: str = "baseline"):
    """Run BERT vs Sophistication and Disinhibition analysis."""
    print("=" * 70)
    print(f"BERT vs. Sophistication & Disinhibition [{condition}]")
    print("=" * 70)

    # Load BERT results
    print("\n[1/3] Loading BERT validation results...")
    bert_data = load_bert_results(condition)
    if not bert_data:
        return

    bert_by_model = {}
    for result in bert_data.get("model_results", []):
        model_id = result["model_id"]
        norm = normalize_model_name(model_id)
        bert_by_model[norm] = {
            "model_id": model_id,
            "toxicity": result["bert_toxicity"],
            "insult": result["bert_insult"]
        }
    print(f"  Loaded BERT scores for {len(bert_by_model)} models")

    # Load classification data
    print("\n[2/3] Loading sophistication/disinhibition data...")
    class_data = load_classification_data(condition)
    if not class_data:
        return

    class_by_model = {}
    for model in class_data.get("models", []):
        model_id = model["model_id"]
        norm = normalize_model_name(model_id)
        class_by_model[norm] = {
            "model_id": model_id,
            "sophistication": model["sophistication"],
            "disinhibition": model["disinhibition"],
            "classification": model["classification"]
        }
    print(f"  Loaded classification for {len(class_by_model)} models")

    # Find overlap
    common_norms = set(bert_by_model.keys()) & set(class_by_model.keys())
    print(f"  Matched models: {len(common_norms)}")

    if len(common_norms) < 10:
        print("ERROR: Not enough matching models")
        return

    # Build arrays
    print("\n[3/3] Computing correlations and generating plots...")
    model_ids = []
    toxicity_vals = []
    insult_vals = []
    soph_vals = []
    disin_vals = []
    classifications = []

    for norm in sorted(common_norms):
        bert = bert_by_model[norm]
        cls = class_by_model[norm]

        model_ids.append(bert["model_id"])
        toxicity_vals.append(bert["toxicity"])
        insult_vals.append(bert["insult"])
        soph_vals.append(cls["sophistication"])
        disin_vals.append(cls["disinhibition"])
        classifications.append(cls["classification"])

    # Compute correlations
    r_tox_soph, p_tox_soph = stats.pearsonr(soph_vals, toxicity_vals)
    r_tox_disin, p_tox_disin = stats.pearsonr(disin_vals, toxicity_vals)
    r_ins_soph, p_ins_soph = stats.pearsonr(soph_vals, insult_vals)
    r_ins_disin, p_ins_disin = stats.pearsonr(disin_vals, insult_vals)

    # Regressions
    slope_tox_soph, int_tox_soph, _, _, se_tox_soph = stats.linregress(soph_vals, toxicity_vals)
    slope_tox_disin, int_tox_disin, _, _, se_tox_disin = stats.linregress(disin_vals, toxicity_vals)
    slope_ins_soph, int_ins_soph, _, _, se_ins_soph = stats.linregress(soph_vals, insult_vals)
    slope_ins_disin, int_ins_disin, _, _, se_ins_disin = stats.linregress(disin_vals, insult_vals)

    print(f"\nN = {len(model_ids)} models")
    print(f"\n--- BERT Toxicity Correlations ---")
    print(f"  vs. Sophistication:  r = {r_tox_soph:.3f}, p = {p_tox_soph:.4f}")
    print(f"  vs. Disinhibition:   r = {r_tox_disin:.3f}, p = {p_tox_disin:.4f}")

    print(f"\n--- BERT Insult Correlations ---")
    print(f"  vs. Sophistication:  r = {r_ins_soph:.3f}, p = {p_ins_soph:.4f}")
    print(f"  vs. Disinhibition:   r = {r_ins_disin:.3f}, p = {p_ins_disin:.4f}")

    # Output directory
    output_dir = Path(f"outputs/behavioral_profiles/research_synthesis/bert_validation/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate plots
    print("\n--- Generating Scatter Plots ---")

    # Plot 1: Toxicity vs Sophistication
    patterns_tox_soph = generate_scatter_plot(
        soph_vals, toxicity_vals, model_ids, classifications,
        r_tox_soph, p_tox_soph, slope_tox_soph, int_tox_soph,
        'Sophistication (depth + authenticity avg)', 'BERT Toxicity Score (0-1)',
        'BERT Toxicity vs. Sophistication\n(Independent Validation with Outlier & Constrained Detection)',
        output_dir / "scatter_toxicity_vs_sophistication.png",
        condition, 'soph', 'tox'
    )
    print(f"  Saved: scatter_toxicity_vs_sophistication.png")
    print(f"    - Outliers: {len(patterns_tox_soph['outliers'])}")
    print(f"    - Constrained: {len(patterns_tox_soph['constrained'])}")

    # Plot 2: Toxicity vs Disinhibition
    patterns_tox_disin = generate_scatter_plot(
        disin_vals, toxicity_vals, model_ids, classifications,
        r_tox_disin, p_tox_disin, slope_tox_disin, int_tox_disin,
        'Disinhibition (trans + agg + trib + grand avg)', 'BERT Toxicity Score (0-1)',
        'BERT Toxicity vs. Disinhibition\n(Independent Validation with Outlier & Constrained Detection)',
        output_dir / "scatter_toxicity_vs_disinhibition.png",
        condition, 'disin', 'tox'
    )
    print(f"  Saved: scatter_toxicity_vs_disinhibition.png")
    print(f"    - Outliers: {len(patterns_tox_disin['outliers'])}")
    print(f"    - Constrained: {len(patterns_tox_disin['constrained'])}")

    # Plot 3: Insult vs Sophistication
    patterns_ins_soph = generate_scatter_plot(
        soph_vals, insult_vals, model_ids, classifications,
        r_ins_soph, p_ins_soph, slope_ins_soph, int_ins_soph,
        'Sophistication (depth + authenticity avg)', 'BERT Insult Score (0-1)',
        'BERT Insult vs. Sophistication\n(Independent Validation with Outlier & Constrained Detection)',
        output_dir / "scatter_insult_vs_sophistication.png",
        condition, 'soph', 'ins'
    )
    print(f"  Saved: scatter_insult_vs_sophistication.png")
    print(f"    - Outliers: {len(patterns_ins_soph['outliers'])}")
    print(f"    - Constrained: {len(patterns_ins_soph['constrained'])}")

    # Plot 4: Insult vs Disinhibition
    patterns_ins_disin = generate_scatter_plot(
        disin_vals, insult_vals, model_ids, classifications,
        r_ins_disin, p_ins_disin, slope_ins_disin, int_ins_disin,
        'Disinhibition (trans + agg + trib + grand avg)', 'BERT Insult Score (0-1)',
        'BERT Insult vs. Disinhibition\n(Independent Validation with Outlier & Constrained Detection)',
        output_dir / "scatter_insult_vs_disinhibition.png",
        condition, 'disin', 'ins'
    )
    print(f"  Saved: scatter_insult_vs_disinhibition.png")
    print(f"    - Outliers: {len(patterns_ins_disin['outliers'])}")
    print(f"    - Constrained: {len(patterns_ins_disin['constrained'])}")

    # Plot 5: Combined 2x2 grid with full labeling
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    colors = ['#e74c3c' if c == 'High-Sophistication' else '#3498db' for c in classifications]

    plot_configs = [
        (axes[0, 0], soph_vals, toxicity_vals, r_tox_soph, slope_tox_soph, int_tox_soph,
         'Sophistication', 'BERT Toxicity', 'Toxicity vs. Sophistication', patterns_tox_soph, 'soph', 'tox'),
        (axes[0, 1], disin_vals, toxicity_vals, r_tox_disin, slope_tox_disin, int_tox_disin,
         'Disinhibition', 'BERT Toxicity', 'Toxicity vs. Disinhibition', patterns_tox_disin, 'disin', 'tox'),
        (axes[1, 0], soph_vals, insult_vals, r_ins_soph, slope_ins_soph, int_ins_soph,
         'Sophistication', 'BERT Insult', 'Insult vs. Sophistication', patterns_ins_soph, 'soph', 'ins'),
        (axes[1, 1], disin_vals, insult_vals, r_ins_disin, slope_ins_disin, int_ins_disin,
         'Disinhibition', 'BERT Insult', 'Insult vs. Disinhibition', patterns_ins_disin, 'disin', 'ins'),
    ]

    for ax, x_v, y_v, r, slope, intercept, x_lab, y_lab, title, patterns, x_name, y_name in plot_configs:
        ax.scatter(x_v, y_v, c=colors, alpha=0.7, s=100, edgecolors='black', linewidth=1, zorder=3)
        x_line = np.linspace(min(x_v), max(x_v), 100)
        ax.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.5, linewidth=2, zorder=1)

        # Track labeled models to avoid duplicates
        labeled_ids = set()

        # Outliers - red circles with labels
        for o in patterns['outliers']:
            ax.scatter([x_v[o['idx']]], [y_v[o['idx']]], s=300, facecolors='none',
                      edgecolors='red', linewidth=2.5, zorder=5)
            label = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')[:15]
            ax.annotate(f"{label}\n({o['sd_from_line']:+.1f}σ)",
                       xy=(x_v[o['idx']], y_v[o['idx']]),
                       xytext=(5, 8), textcoords='offset points',
                       fontsize=6, fontweight='bold', color='red',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='red'),
                       arrowprops=dict(arrowstyle='->', color='red', lw=1),
                       zorder=10)
            labeled_ids.add(o['idx'])

        # Constrained - cyan diamonds with labels
        for c in patterns['constrained']:
            ax.scatter([x_v[c['idx']]], [y_v[c['idx']]], marker='D', s=150, color='#00CED1',
                      alpha=0.9, edgecolors='blue', linewidth=2, zorder=6)
            if c['idx'] not in labeled_ids:
                label = model_ids[c['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')[:15]
                ax.annotate(label,
                           xy=(x_v[c['idx']], y_v[c['idx']]),
                           xytext=(-8, -12), textcoords='offset points',
                           fontsize=6, fontweight='bold', color='blue',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='cyan', alpha=0.7, edgecolor='blue'),
                           arrowprops=dict(arrowstyle='->', color='blue', lw=1, connectionstyle='arc3,rad=-0.2'),
                           zorder=10)
                labeled_ids.add(c['idx'])

        # Min/max X and Y - top 2 each (if not already labeled)
        sorted_x = sorted(range(len(x_v)), key=lambda i: x_v[i])
        sorted_y = sorted(range(len(y_v)), key=lambda i: y_v[i])

        extreme_indices = set(sorted_x[:2] + sorted_x[-2:] + sorted_y[:2] + sorted_y[-2:])
        for idx in extreme_indices:
            if idx not in labeled_ids:
                label = model_ids[idx].replace('Claude-', 'C-').replace('GPT-', 'G-')[:12]
                # Position based on location
                x_off = -50 if x_v[idx] < np.median(x_v) else 50
                y_off = -8 if y_v[idx] < np.median(y_v) else 8
                ax.annotate(label,
                           xy=(x_v[idx], y_v[idx]),
                           xytext=(x_off, y_off), textcoords='offset points',
                           fontsize=5.5, fontweight='bold', color='navy',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.8, edgecolor='navy'),
                           arrowprops=dict(arrowstyle='->', color='navy', lw=0.8, connectionstyle='arc3,rad=0.15'),
                           zorder=9)
                labeled_ids.add(idx)

        ax.text(0.05, 0.95,
                f'r = {r:.3f}\nR² = {r**2:.3f}\nOut: {len(patterns["outliers"])}\nCon: {len(patterns["constrained"])}',
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        ax.set_xlabel(x_lab, fontsize=10, fontweight='bold')
        ax.set_ylabel(y_lab, fontsize=10, fontweight='bold')
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

    # Legend
    axes[0, 0].scatter([], [], c='#e74c3c', s=80, label='High-Soph')
    axes[0, 0].scatter([], [], c='#3498db', s=80, label='Low-Soph')
    axes[0, 0].scatter([], [], s=200, facecolors='none', edgecolors='red', linewidth=2, label='Outlier')
    axes[0, 0].scatter([], [], marker='D', s=100, color='#00CED1', edgecolors='blue', label='Constrained')
    axes[0, 0].legend(loc='lower right', fontsize=7, ncol=2)

    fig.text(0.5, 0.998, f'Condition: {condition}', ha='center', va='top',
             fontsize=11, fontweight='bold', color='#666666')
    fig.suptitle(f'BERT Toxicity/Insult vs. Sophistication/Disinhibition (N={len(model_ids)})',
                 fontsize=14, fontweight='bold', y=0.97)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_dir / "scatter_soph_disin_combined.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_soph_disin_combined.png")

    # Save results JSON
    results = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "condition": condition,
            "n_models": len(model_ids),
            "outlier_threshold_sd": OUTLIER_SD_THRESHOLD,
            "source_bert": f"bert_validation/{condition}/bert_validation_results.json",
            "source_classification": f"{condition}/median_split_classification.json"
        },
        "correlations": {
            "toxicity_vs_sophistication": {
                "r": float(r_tox_soph), "p": float(p_tox_soph), "r_squared": float(r_tox_soph ** 2),
                "interpretation": "large" if abs(r_tox_soph) >= 0.5 else "medium" if abs(r_tox_soph) >= 0.3 else "small"
            },
            "toxicity_vs_disinhibition": {
                "r": float(r_tox_disin), "p": float(p_tox_disin), "r_squared": float(r_tox_disin ** 2),
                "interpretation": "large" if abs(r_tox_disin) >= 0.5 else "medium" if abs(r_tox_disin) >= 0.3 else "small"
            },
            "insult_vs_sophistication": {
                "r": float(r_ins_soph), "p": float(p_ins_soph), "r_squared": float(r_ins_soph ** 2),
                "interpretation": "large" if abs(r_ins_soph) >= 0.5 else "medium" if abs(r_ins_soph) >= 0.3 else "small"
            },
            "insult_vs_disinhibition": {
                "r": float(r_ins_disin), "p": float(p_ins_disin), "r_squared": float(r_ins_disin ** 2),
                "interpretation": "large" if abs(r_ins_disin) >= 0.5 else "medium" if abs(r_ins_disin) >= 0.3 else "small"
            }
        },
        "regression": {
            "toxicity_vs_sophistication": {"slope": float(slope_tox_soph), "intercept": float(int_tox_soph), "std_err": float(se_tox_soph)},
            "toxicity_vs_disinhibition": {"slope": float(slope_tox_disin), "intercept": float(int_tox_disin), "std_err": float(se_tox_disin)},
            "insult_vs_sophistication": {"slope": float(slope_ins_soph), "intercept": float(int_ins_soph), "std_err": float(se_ins_soph)},
            "insult_vs_disinhibition": {"slope": float(slope_ins_disin), "intercept": float(int_ins_disin), "std_err": float(se_ins_disin)}
        },
        "patterns": {
            "toxicity_vs_sophistication": patterns_tox_soph,
            "toxicity_vs_disinhibition": patterns_tox_disin,
            "insult_vs_sophistication": patterns_ins_soph,
            "insult_vs_disinhibition": patterns_ins_disin
        },
        "model_data": [
            {
                "model_id": model_ids[i],
                "toxicity": float(toxicity_vals[i]),
                "insult": float(insult_vals[i]),
                "sophistication": float(soph_vals[i]),
                "disinhibition": float(disin_vals[i]),
                "classification": classifications[i]
            }
            for i in range(len(model_ids))
        ],
        "output_files": [
            "scatter_toxicity_vs_sophistication.png",
            "scatter_toxicity_vs_disinhibition.png",
            "scatter_insult_vs_sophistication.png",
            "scatter_insult_vs_disinhibition.png",
            "scatter_soph_disin_combined.png",
            "bert_soph_disin_results.json"
        ]
    }

    output_file = output_dir / "bert_soph_disin_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n{'Correlation':<35} {'r':>8} {'p':>12} {'Effect':>10} {'Out':>5} {'Con':>5}")
    print("-" * 80)
    print(f"{'Toxicity vs Sophistication':<35} {r_tox_soph:>8.3f} {p_tox_soph:>12.4f} {results['correlations']['toxicity_vs_sophistication']['interpretation']:>10} {len(patterns_tox_soph['outliers']):>5} {len(patterns_tox_soph['constrained']):>5}")
    print(f"{'Toxicity vs Disinhibition':<35} {r_tox_disin:>8.3f} {p_tox_disin:>12.4f} {results['correlations']['toxicity_vs_disinhibition']['interpretation']:>10} {len(patterns_tox_disin['outliers']):>5} {len(patterns_tox_disin['constrained']):>5}")
    print(f"{'Insult vs Sophistication':<35} {r_ins_soph:>8.3f} {p_ins_soph:>12.4f} {results['correlations']['insult_vs_sophistication']['interpretation']:>10} {len(patterns_ins_soph['outliers']):>5} {len(patterns_ins_soph['constrained']):>5}")
    print(f"{'Insult vs Disinhibition':<35} {r_ins_disin:>8.3f} {p_ins_disin:>12.4f} {results['correlations']['insult_vs_disinhibition']['interpretation']:>10} {len(patterns_ins_disin['outliers']):>5} {len(patterns_ins_disin['constrained']):>5}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", type=str, default="baseline",
                        choices=["baseline", "authority", "urgency", "reminder", "telemetryV3", "minimal_steering"],
                        help="Condition to analyze (default: baseline)")
    args = parser.parse_args()

    run_soph_disin_analysis(condition=args.condition)
