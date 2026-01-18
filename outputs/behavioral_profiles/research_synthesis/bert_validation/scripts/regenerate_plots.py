#!/usr/bin/env python3
"""
Regenerate BERT validation scatter plots from saved JSON results.

This script allows updating plot styling without re-running BERT inference.

Usage:
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_plots.py
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_plots.py --input custom_results.json
"""

import json
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# CONFIGURABLE THRESHOLDS (matching research_synthesis)
# =============================================================================
OUTLIER_SD_THRESHOLD = 2.0  # Statistical outliers: residuals > 2 SD
# Constrained: high aggression but below-predicted toxicity
CONSTRAINED_AGG_THRESHOLD = 1.6  # Top ~25% of aggression range (1.13-2.18)
CONSTRAINED_RESIDUAL_THRESHOLD = -0.005  # Below prediction by this much


def load_results(results_path: Path) -> dict:
    """Load validation results from JSON."""
    with open(results_path) as f:
        return json.load(f)


def identify_patterns(x_vals, y_vals, ids, slope, intercept):
    """Identify outliers and constrained models from regression."""
    predicted = slope * np.array(x_vals) + intercept
    residuals = np.array(y_vals) - predicted
    residual_std = np.std(residuals)

    outliers = []
    constrained = []

    for i in range(len(x_vals)):
        if abs(residuals[i]) > OUTLIER_SD_THRESHOLD * residual_std:
            outliers.append({
                'idx': i,
                'model_id': ids[i],
                'residual': residuals[i],
                'sd_from_line': residuals[i] / residual_std
            })

        if x_vals[i] > CONSTRAINED_AGG_THRESHOLD and residuals[i] < CONSTRAINED_RESIDUAL_THRESHOLD:
            constrained.append({
                'idx': i,
                'model_id': ids[i],
                'residual': residuals[i],
                'sd_from_line': residuals[i] / residual_std
            })

    return outliers, constrained, residuals, residual_std


def get_extreme_labels(x_vals, y_vals, ids, sorted_x, sorted_y, y_name, outliers, constrained):
    """Get extreme models for labeling with tags (including outliers)."""
    models_to_label = {}

    # Min/max x (aggression) - top 2 each
    for i in sorted_x[:2]:
        if ids[i] not in models_to_label:
            models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
        models_to_label[ids[i]]['tags'].append(f"min-agg={x_vals[i]:.2f}")
        models_to_label[ids[i]]['priority'] += 10

    for i in sorted_x[-2:]:
        if ids[i] not in models_to_label:
            models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
        models_to_label[ids[i]]['tags'].append(f"max-agg={x_vals[i]:.2f}")
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

    # Add ALL outliers with residual info (so every red ring has a label)
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
        models_to_label[mid]['priority'] += 15

    return models_to_label


def generate_scatter_plots(data: dict, output_dir: Path, condition: str = "baseline"):
    """Generate scatter plots with regression lines (research_synthesis styling)."""

    # Extract data from JSON
    model_results = data['model_results']
    aggression = np.array([r['aggression'] for r in model_results])
    toxicity = np.array([r['bert_toxicity'] for r in model_results])
    insult = np.array([r['bert_insult'] for r in model_results])
    model_ids = [r['model_id'] for r in model_results]

    # Get correlation stats
    r_tox = data['correlations']['toxicity']['r']
    p_tox = data['correlations']['toxicity']['p']
    r_ins = data['correlations']['insult']['r']
    p_ins = data['correlations']['insult']['p']

    # Get regression stats
    slope_tox = data['regression']['toxicity']['slope']
    intercept_tox = data['regression']['toxicity']['intercept']
    slope_ins = data['regression']['insult']['slope']
    intercept_ins = data['regression']['insult']['intercept']

    # Identify patterns
    outliers_tox, constrained_tox, _, _ = identify_patterns(
        aggression, toxicity, model_ids, slope_tox, intercept_tox)
    outliers_ins, constrained_ins, _, _ = identify_patterns(
        aggression, insult, model_ids, slope_ins, intercept_ins)

    # Sort indices
    sorted_by_aggression = sorted(range(len(aggression)), key=lambda i: aggression[i])
    sorted_by_toxicity = sorted(range(len(toxicity)), key=lambda i: toxicity[i])
    sorted_by_insult = sorted(range(len(insult)), key=lambda i: insult[i])

    # =========================================================================
    # Plot 1: Toxicity vs Aggression
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(aggression, toxicity, alpha=0.7, s=150,
               c='#2ecc71', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})', zorder=3)

    x_line = np.linspace(min(aggression), max(aggression), 100)
    y_line = slope_tox * x_line + intercept_tox
    ax.plot(x_line, y_line, 'k--', alpha=0.5, linewidth=2, label='Best Fit', zorder=1)

    # Outliers
    for o in outliers_tox:
        ax.scatter([aggression[o['idx']]], [toxicity[o['idx']]],
                  s=400, facecolors='none', edgecolors='red', linewidth=3, zorder=5)
    ax.scatter([], [], s=400, facecolors='none', edgecolors='red',
              linewidth=3, label=f'Statistical Outliers (n={len(outliers_tox)})')

    # Constrained
    for c in constrained_tox:
        ax.scatter([aggression[c['idx']]], [toxicity[c['idx']]],
                  marker='D', s=200, color='#00CED1', alpha=0.9,
                  edgecolors='blue', linewidth=2.5, zorder=6)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5, label=f'Constrained (n={len(constrained_tox)})')

    # Labels
    tox_labels = get_extreme_labels(aggression, toxicity, model_ids,
                                    sorted_by_aggression, sorted_by_toxicity, 'tox',
                                    outliers_tox, constrained_tox)

    for j, (mid, info) in enumerate(sorted(tox_labels.items(), key=lambda x: -x[1]['priority'])):
        i = info['idx']
        tags = info['tags']
        label_name = mid.replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 18:
            label_name = label_name[:15] + '...'
        tag_text = '\n'.join(tags[:2])
        full_label = f"{label_name}\n{tag_text}"

        x_offset = -70 if aggression[i] < np.median(aggression) else 70
        y_offset = -40 if toxicity[i] < np.median(toxicity) else 40
        y_offset += (j % 3) * 15

        ax.annotate(full_label,
                   xy=(aggression[i], toxicity[i]),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=6.5, fontweight='bold', color='navy',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                            alpha=0.85, edgecolor='navy'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                 color='navy', lw=1.3),
                   zorder=9)

    r_sq = r_tox ** 2
    p_str = f"{p_tox:.6f}" if p_tox >= 0.0001 else "< .0001"
    stats_text = (
        f'Validation: BERT Toxicity ~ Judge Aggression\n'
        f'r = {r_tox:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {"Large" if abs(r_tox) >= 0.5 else "Medium" if abs(r_tox) >= 0.3 else "Small"}\n'
        f'N = {len(aggression)} models\n\n'
        f'Outliers: {len(outliers_tox)} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(constrained_tox)} (high-agg, low-tox)'
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95), zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Toxicity Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Toxicity vs. Judge Aggression\n'
                 '(Independent Validation with Outlier & Constrained Detection)',
                 fontsize=15, fontweight='bold', pad=20)

    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold', y=0.995, color='#666666')
    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_dir / "scatter_toxicity_vs_aggression.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_toxicity_vs_aggression.png")
    print(f"    - Outliers: {len(outliers_tox)}")
    print(f"    - Constrained: {len(constrained_tox)}")

    # =========================================================================
    # Plot 2: Insult vs Aggression
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(aggression, insult, alpha=0.7, s=150,
               c='#e74c3c', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})', zorder=3)

    y_line = slope_ins * x_line + intercept_ins
    ax.plot(x_line, y_line, 'k--', alpha=0.5, linewidth=2, label='Best Fit', zorder=1)

    # Outliers
    for o in outliers_ins:
        ax.scatter([aggression[o['idx']]], [insult[o['idx']]],
                  s=400, facecolors='none', edgecolors='red', linewidth=3, zorder=5)
    ax.scatter([], [], s=400, facecolors='none', edgecolors='red',
              linewidth=3, label=f'Statistical Outliers (n={len(outliers_ins)})')

    # Constrained
    for c in constrained_ins:
        ax.scatter([aggression[c['idx']]], [insult[c['idx']]],
                  marker='D', s=200, color='#00CED1', alpha=0.9,
                  edgecolors='blue', linewidth=2.5, zorder=6)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5, label=f'Constrained (n={len(constrained_ins)})')

    # Labels
    ins_labels = get_extreme_labels(aggression, insult, model_ids,
                                    sorted_by_aggression, sorted_by_insult, 'ins',
                                    outliers_ins, constrained_ins)

    for j, (mid, info) in enumerate(sorted(ins_labels.items(), key=lambda x: -x[1]['priority'])):
        i = info['idx']
        tags = info['tags']
        label_name = mid.replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 18:
            label_name = label_name[:15] + '...'
        tag_text = '\n'.join(tags[:2])
        full_label = f"{label_name}\n{tag_text}"

        x_offset = -70 if aggression[i] < np.median(aggression) else 70
        y_offset = -40 if insult[i] < np.median(insult) else 40
        y_offset += (j % 3) * 15

        ax.annotate(full_label,
                   xy=(aggression[i], insult[i]),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=6.5, fontweight='bold', color='navy',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                            alpha=0.85, edgecolor='navy'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                 color='navy', lw=1.3),
                   zorder=9)

    r_sq = r_ins ** 2
    p_str = f"{p_ins:.6f}" if p_ins >= 0.0001 else "< .0001"
    stats_text = (
        f'Validation: BERT Insult ~ Judge Aggression\n'
        f'r = {r_ins:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {"Large" if abs(r_ins) >= 0.5 else "Medium" if abs(r_ins) >= 0.3 else "Small"}\n'
        f'N = {len(aggression)} models\n\n'
        f'Outliers: {len(outliers_ins)} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(constrained_ins)} (high-agg, low-ins)'
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95), zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Insult Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Insult vs. Judge Aggression\n'
                 '(Independent Validation with Outlier & Constrained Detection)',
                 fontsize=15, fontweight='bold', pad=20)

    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold', y=0.995, color='#666666')
    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_dir / "scatter_insult_vs_aggression.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_insult_vs_aggression.png")
    print(f"    - Outliers: {len(outliers_ins)}")
    print(f"    - Constrained: {len(constrained_ins)}")

    # =========================================================================
    # Plot 3: Combined 2-panel
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Toxicity panel
    axes[0].scatter(aggression, toxicity, alpha=0.7, s=120,
                    c='#2ecc71', edgecolors='black', linewidth=1.5, zorder=3)
    axes[0].plot(x_line, slope_tox * x_line + intercept_tox, 'k--', alpha=0.5, linewidth=2, zorder=1)

    for o in outliers_tox:
        axes[0].scatter([aggression[o['idx']]], [toxicity[o['idx']]],
                       s=300, facecolors='none', edgecolors='red', linewidth=2.5, zorder=5)
        # Label outlier
        label_name = o['model_id'].replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 15:
            label_name = label_name[:12] + '...'
        axes[0].annotate(f"{label_name}\n({o['sd_from_line']:+.1f}σ)",
                        xy=(aggression[o['idx']], toxicity[o['idx']]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=6, fontweight='bold', color='red',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='red'),
                        zorder=10)

    axes[0].text(0.05, 0.95,
                f'r = {r_tox:.3f}\nR² = {r_tox**2:.3f}\np < .0001\nOutliers: {len(outliers_tox)}',
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

    for o in outliers_ins:
        axes[1].scatter([aggression[o['idx']]], [insult[o['idx']]],
                       s=300, facecolors='none', edgecolors='red', linewidth=2.5, zorder=5)
        # Label outlier
        label_name = o['model_id'].replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 15:
            label_name = label_name[:12] + '...'
        axes[1].annotate(f"{label_name}\n({o['sd_from_line']:+.1f}σ)",
                        xy=(aggression[o['idx']], insult[o['idx']]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=6, fontweight='bold', color='red',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='red'),
                        zorder=10)

    axes[1].text(0.05, 0.95,
                f'r = {r_ins:.3f}\nR² = {r_ins**2:.3f}\np < .0001\nOutliers: {len(outliers_ins)}',
                transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    axes[1].set_xlabel('Judge Aggression (1-10)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('BERT Insult (0-1)', fontsize=12, fontweight='bold')
    axes[1].set_title('Insult Validation', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_axisbelow(True)

    fig.text(0.5, 0.998, f'Condition: {condition}', ha='center', va='top',
             fontsize=11, fontweight='bold', color='#666666')
    fig.suptitle(f'BERT Validation: Independent Measure vs. Judge Aggression (N={len(aggression)})',
                 fontsize=15, fontweight='bold', y=0.97)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(output_dir / "scatter_combined.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_combined.png")


def main():
    parser = argparse.ArgumentParser(description="Regenerate BERT validation scatter plots from JSON")
    parser.add_argument("--condition", type=str, default="baseline",
                        choices=["baseline", "authority", "urgency", "reminder", "telemetryV3", "minimal_steering"],
                        help="Condition to regenerate plots for (default: baseline)")
    parser.add_argument("--input", type=str, default=None,
                        help="Path to validation results JSON (defaults to condition-specific path)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for plots (defaults to condition-specific path)")
    args = parser.parse_args()

    # Use condition-specific paths if not explicitly provided
    base_dir = Path("outputs/behavioral_profiles/research_synthesis/bert_validation")
    results_path = Path(args.input) if args.input else base_dir / args.condition / "bert_validation_results.json"
    output_dir = Path(args.output_dir) if args.output_dir else base_dir / args.condition

    if not results_path.exists():
        print(f"ERROR: Results file not found: {results_path}")
        print(f"Run: python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition {args.condition}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"Regenerating BERT Validation Scatter Plots [{args.condition}]")
    print("=" * 60)
    print(f"Input: {results_path}")
    print(f"Output: {output_dir}")

    data = load_results(results_path)
    print(f"\nLoaded results for {data['sample']['n_models']} models")
    print(f"Toxicity correlation: r = {data['correlations']['toxicity']['r']:.3f}")
    print(f"Insult correlation: r = {data['correlations']['insult']['r']:.3f}")

    print("\nGenerating scatter plots...")
    generate_scatter_plots(data, output_dir, condition=args.condition)

    print("\nDone!")


if __name__ == "__main__":
    main()
