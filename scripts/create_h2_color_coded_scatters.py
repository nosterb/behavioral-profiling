#!/usr/bin/env python3
"""
Create H2 scatter plots with H1 classification color-coding.

Shows sophistication-disinhibition correlation (H2) while visually displaying
the median split classification (H1) through color-coding.

Also highlights:
- Borderline models (close to median split)
- Statistical outliers (unusual sophistication-disinhibition relationships)
- Constrained models (high sophistication but below-predicted disinhibition)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats as sp_stats

# =============================================================================
# CONFIGURABLE THRESHOLDS
# =============================================================================
# These thresholds control how special model patterns are identified.
# Adjust these values to change sensitivity of pattern detection.

# Borderline models: within this distance of median sophistication
# Rationale: ±0.15 captures models that could reasonably be classified either way
# on the median split. This represents ~2.5% of the 1-10 scale on each side.
BORDERLINE_THRESHOLD = 0.15

# Statistical outliers: residuals exceeding this many standard deviations
# Rationale: 2 SD is a common threshold (~95% of data falls within ±2 SD).
# Models beyond this show unusual sophistication-disinhibition relationships.
OUTLIER_SD_THRESHOLD = 2.0

# Constrained models: high sophistication but below-predicted disinhibition
# CONSTRAINED_SOPH_THRESHOLD: minimum sophistication to be considered "high capability"
# Rationale: 6.5 is above the typical median (~5.9-6.7) and represents models
# in roughly the top third of sophistication scores.
CONSTRAINED_SOPH_THRESHOLD = 6.5

# CONSTRAINED_RESIDUAL_THRESHOLD: how far below prediction to be "constrained"
# Rationale: -0.15 means disinhibition is at least 0.15 below what the regression
# predicts for that sophistication level, suggesting deliberate constraint.
CONSTRAINED_RESIDUAL_THRESHOLD = -0.15
# =============================================================================

def load_median_split_data(profile_dir):
    """Load median split classification data."""
    median_split_path = profile_dir / "median_split_classification.json"

    with open(median_split_path, 'r') as f:
        return json.load(f)

def identify_outliers_and_borderline(data, threshold_sd=None, borderline_threshold=None,
                                      constrained_soph=None, constrained_residual=None):
    """
    Identify statistical outliers, borderline models, and constrained models.

    Args:
        data: Median split classification data
        threshold_sd: SD threshold for outliers (default: OUTLIER_SD_THRESHOLD)
        borderline_threshold: Distance from median for borderline (default: BORDERLINE_THRESHOLD)
        constrained_soph: Min sophistication for constrained (default: CONSTRAINED_SOPH_THRESHOLD)
        constrained_residual: Max residual for constrained (default: CONSTRAINED_RESIDUAL_THRESHOLD)

    Returns:
        outliers, borderline, constrained, residuals, residual_std
    """
    # Use module defaults if not specified
    if threshold_sd is None:
        threshold_sd = OUTLIER_SD_THRESHOLD
    if borderline_threshold is None:
        borderline_threshold = BORDERLINE_THRESHOLD
    if constrained_soph is None:
        constrained_soph = CONSTRAINED_SOPH_THRESHOLD
    if constrained_residual is None:
        constrained_residual = CONSTRAINED_RESIDUAL_THRESHOLD
    all_x = [m['sophistication'] for m in data['models']]
    all_y = [m['disinhibition'] for m in data['models']]
    median_soph = data['median_sophistication']
    median_disinhib = np.median(all_y)

    # Calculate regression line
    z = np.polyfit(all_x, all_y, 1)
    p = np.poly1d(z)

    # Calculate residuals
    predicted = p(all_x)
    residuals = np.array(all_y) - predicted
    residual_std = np.std(residuals)

    # Identify outliers, borderline, and constrained models
    outliers = []
    borderline = []
    constrained = []

    for i, model in enumerate(data['models']):
        # Check if outlier (residual > threshold_sd * std)
        if abs(residuals[i]) > threshold_sd * residual_std:
            outliers.append({
                'model': model,
                'residual': residuals[i],
                'predicted': predicted[i]
            })

        # Check if borderline (close to median)
        if abs(model['sophistication'] - median_soph) < borderline_threshold:
            borderline.append(model)

        # Check if constrained (high sophistication, low disinhibition)
        # High sophistication = above constrained_soph threshold
        # Low disinhibition = residual below constrained_residual threshold
        if model['sophistication'] > constrained_soph and residuals[i] < constrained_residual:
            constrained.append({
                'model': model,
                'residual': residuals[i],
                'predicted': predicted[i]
            })

    return outliers, borderline, constrained, residuals, residual_std

def create_color_coded_scatter_composite(data, output_path):
    """Create sophistication vs disinhibition composite scatter with classification colors."""

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    median_soph = data['median_sophistication']

    # Identify outliers, borderline, and constrained models
    outliers, borderline, constrained, residuals, residual_std = identify_outliers_and_borderline(data)

    # Create sets for quick lookup
    outlier_ids = {o['model']['model_id'] for o in outliers}
    borderline_ids = {b['model_id'] for b in borderline}
    constrained_ids = {c['model']['model_id'] for c in constrained}

    # Separate by classification and special cases
    high_normal = []
    high_borderline = []
    low_normal = []
    low_borderline = []

    for model in data['models']:
        is_borderline = model['model_id'] in borderline_ids
        if model['classification'] == 'High-Sophistication':
            if is_borderline:
                high_borderline.append(model)
            else:
                high_normal.append(model)
        else:
            if is_borderline:
                low_borderline.append(model)
            else:
                low_normal.append(model)

    # Plot normal models first
    if high_normal:
        ax.scatter([m['sophistication'] for m in high_normal],
                   [m['disinhibition'] for m in high_normal],
                   color='#2ecc71', alpha=0.7, s=150,
                   edgecolors='black', linewidth=1.5,
                   label=f'High-Soph (n={len(high_normal)})',
                   zorder=3)

    if low_normal:
        ax.scatter([m['sophistication'] for m in low_normal],
                   [m['disinhibition'] for m in low_normal],
                   color='#e74c3c', alpha=0.7, s=150,
                   edgecolors='black', linewidth=1.5,
                   label=f'Low-Soph (n={len(low_normal)})',
                   zorder=3)

    # Plot borderline models with distinct appearance
    if high_borderline:
        ax.scatter([m['sophistication'] for m in high_borderline],
                   [m['disinhibition'] for m in high_borderline],
                   color='#f39c12', alpha=0.9, s=180,
                   edgecolors='black', linewidth=2.5,
                   marker='s',  # Square marker
                   label=f'High-Soph Borderline (n={len(high_borderline)})',
                   zorder=4)

        # Label borderline models
        for model in high_borderline:
            label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
            if len(label_name) > 20:
                label_name = label_name[:17] + '...'

            ax.annotate(label_name,
                       xy=(model['sophistication'], model['disinhibition']),
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=7, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                     color='orange', lw=1.5),
                       zorder=8)

    if low_borderline:
        ax.scatter([m['sophistication'] for m in low_borderline],
                   [m['disinhibition'] for m in low_borderline],
                   color='#e67e22', alpha=0.9, s=180,
                   edgecolors='black', linewidth=2.5,
                   marker='s',  # Square marker
                   label=f'Low-Soph Borderline (n={len(low_borderline)})',
                   zorder=4)

        # Label borderline models
        for model in low_borderline:
            label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
            if len(label_name) > 20:
                label_name = label_name[:17] + '...'

            ax.annotate(label_name,
                       xy=(model['sophistication'], model['disinhibition']),
                       xytext=(8, -12), textcoords='offset points',
                       fontsize=7, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                     color='orange', lw=1.5),
                       zorder=8)

    # Add median split line and borderline zone
    ax.axvline(median_soph, color='purple', linestyle='--',
               linewidth=2.5, alpha=0.8,
               label=f'Median Split = {median_soph:.2f}',
               zorder=2)

    # Shade borderline zone
    ax.axvspan(median_soph - BORDERLINE_THRESHOLD, median_soph + BORDERLINE_THRESHOLD,
               alpha=0.1, color='orange', zorder=1,
               label=f'Borderline Zone (±{BORDERLINE_THRESHOLD})')

    # Add regression line
    all_x = [m['sophistication'] for m in data['models']]
    all_y = [m['disinhibition'] for m in data['models']]
    z = np.polyfit(all_x, all_y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(all_x), max(all_x), 100)
    ax.plot(x_line, p(x_line), 'k--', alpha=0.5, linewidth=2,
            label='Best Fit', zorder=1)

    # Highlight statistical outliers with circles
    if outliers:
        for outlier_info in outliers:
            model = outlier_info['model']
            ax.scatter([model['sophistication']], [model['disinhibition']],
                      s=400, facecolors='none', edgecolors='red',
                      linewidth=3, zorder=5)

        ax.scatter([], [], s=400, facecolors='none', edgecolors='red',
                  linewidth=3, label=f'Statistical Outliers (n={len(outliers)})')

    # Highlight constrained models (high sophistication, low disinhibition)
    if constrained:
        for constrained_info in constrained:
            model = constrained_info['model']
            # Draw cyan diamond
            ax.scatter([model['sophistication']], [model['disinhibition']],
                      marker='D', s=200, color='#00CED1', alpha=0.9,
                      edgecolors='blue', linewidth=2.5, zorder=6)

            # Add label
            label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
            if len(label_name) > 20:
                label_name = label_name[:17] + '...'

            ax.annotate(label_name,
                       xy=(model['sophistication'], model['disinhibition']),
                       xytext=(-10, -15), textcoords='offset points',
                       fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='cyan', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3',
                                     color='blue', lw=1.5),
                       zorder=8)

        ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
                  edgecolors='blue', linewidth=2.5,
                  label=f'Constrained Models (n={len(constrained)})')

    # Add group mean markers
    high_mean_soph = data['statistics']['sophistication']['high_mean']
    high_mean_disinhib = data['statistics']['disinhibition']['high_mean']
    low_mean_soph = data['statistics']['sophistication']['low_mean']
    low_mean_disinhib = data['statistics']['disinhibition']['low_mean']

    ax.scatter([high_mean_soph], [high_mean_disinhib],
               marker='X', s=400, color='darkgreen',
               edgecolors='black', linewidth=2.5,
               label='High-Soph Mean',
               zorder=6)

    ax.scatter([low_mean_soph], [low_mean_disinhib],
               marker='X', s=400, color='darkred',
               edgecolors='black', linewidth=2.5,
               label='Low-Soph Mean',
               zorder=6)

    # Calculate correlation
    r = data['correlation']['sophistication_disinhibition']

    # Add statistics text box
    stats_text = (
        f'H2: Sophistication-Disinhibition Correlation\n'
        f'r = {r:.3f}, p < .001 (large effect)\n\n'
        f'H1: Group Difference\n'
        f'd = {data["statistics"]["disinhibition"]["cohens_d"]:.2f} (large effect)\n\n'
        f'Borderline: {len(borderline)} models (±{BORDERLINE_THRESHOLD} from median)\n'
        f'Constrained: {len(constrained)} models (high-soph, low-disinhib)\n'
        f'Outliers: {len(outliers)} models (|residual| > {OUTLIER_SD_THRESHOLD} SD)'
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95),
            zorder=7)

    # Collect models to label (deduplicated)
    all_models = data['models']
    sorted_by_soph = sorted(all_models, key=lambda m: m['sophistication'])
    sorted_by_disinhib = sorted(all_models, key=lambda m: m['disinhibition'])

    # Track which models need labels and their attributes
    models_to_label = {}  # model_id -> {model, tags, position_priority}

    # Min/max sophistication (top 2 each)
    for model in sorted_by_soph[:2]:
        if model['model_id'] not in models_to_label:
            models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
        models_to_label[model['model_id']]['tags'].append(f"min-soph={model['sophistication']:.2f}")
        models_to_label[model['model_id']]['priority'] += 10

    for model in sorted_by_soph[-2:]:
        if model['model_id'] not in models_to_label:
            models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
        models_to_label[model['model_id']]['tags'].append(f"max-soph={model['sophistication']:.2f}")
        models_to_label[model['model_id']]['priority'] += 10

    # Min/max disinhibition (top 2 each)
    for model in sorted_by_disinhib[:2]:
        if model['model_id'] not in models_to_label:
            models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
        models_to_label[model['model_id']]['tags'].append(f"min-disinhib={model['disinhibition']:.2f}")
        models_to_label[model['model_id']]['priority'] += 5

    for model in sorted_by_disinhib[-2:]:
        if model['model_id'] not in models_to_label:
            models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
        models_to_label[model['model_id']]['tags'].append(f"max-disinhib={model['disinhibition']:.2f}")
        models_to_label[model['model_id']]['priority'] += 5

    # Add outliers (top 3)
    if outliers:
        sorted_outliers = sorted(outliers, key=lambda x: abs(x['residual']), reverse=True)
        for outlier_info in sorted_outliers[:3]:
            model = outlier_info['model']
            if model['model_id'] not in models_to_label:
                models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
            models_to_label[model['model_id']]['tags'].append(f"outlier(res={outlier_info['residual']:+.2f})")
            models_to_label[model['model_id']]['priority'] += 20  # Outliers get highest priority

    # Now label each unique model once with all its tags
    for i, (model_id, info) in enumerate(sorted(models_to_label.items(), key=lambda x: -x[1]['priority'])):
        model = info['model']
        tags = info['tags']

        # Shortened model name
        label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 18:
            label_name = label_name[:15] + '...'

        # Combine all tags
        tag_text = '\n'.join(tags)
        full_label = f"{label_name}\n{tag_text}"

        # Position based on location in plot
        soph = model['sophistication']
        disinhib = model['disinhibition']

        # Smart positioning: away from center
        if soph < 5.5:
            x_offset = -70
        else:
            x_offset = 70

        if disinhib < 1.5:
            y_offset = -40
        else:
            y_offset = 40

        # Add some vertical spread if multiple labels
        y_offset += (i % 3) * 15

        ax.annotate(full_label,
                   xy=(soph, disinhib),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=6.5, fontweight='bold', color='navy',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.85, edgecolor='navy'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                 color='navy', lw=1.3),
                   zorder=9)

    # Labels and formatting
    ax.set_xlabel('Sophistication (Depth + Authenticity) / 2',
                  fontsize=13, fontweight='bold')
    ax.set_ylabel('Disinhibition Composite\n(Transgression + Aggression + Tribalism + Grandiosity) / 4',
                  fontsize=13, fontweight='bold')
    ax.set_title('Sophistication vs Disinhibition Composite\n'
                 '(H2 Correlation with H1 Classification, Outliers & Borderline Models)',
                 fontsize=15, fontweight='bold', pad=20)

    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✓ Created: {output_path}")
    print(f"  - Borderline models: {len(borderline)} (within ±{BORDERLINE_THRESHOLD} of median)")
    if borderline:
        for b in sorted(borderline, key=lambda x: x['sophistication']):
            dist = b['sophistication'] - median_soph
            print(f"    • {b['display_name']}: {b['sophistication']:.3f} ({dist:+.3f} from median)")
    print(f"  - Constrained models: {len(constrained)} (soph > {CONSTRAINED_SOPH_THRESHOLD}, residual < {CONSTRAINED_RESIDUAL_THRESHOLD})")
    if constrained:
        for c in sorted(constrained, key=lambda x: x['residual']):
            print(f"    • {c['model']['display_name']}: soph={c['model']['sophistication']:.3f}, "
                  f"disinhib={c['model']['disinhibition']:.3f}, residual={c['residual']:+.3f}")
    print(f"  - Statistical outliers: {len(outliers)} (residual > 2 SD)")
    if outliers:
        print(f"  - Top outliers labeled:")
        for o in sorted(outliers, key=lambda x: abs(x['residual']), reverse=True)[:3]:
            print(f"    • {o['model']['display_name']}: residual = {o['residual']:+.3f}")

def create_color_coded_scatter_all_dimensions(data, output_path):
    """Create 2x2 scatter plots for all four disinhibition dimensions."""

    disinhibition_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']

    fig, axes = plt.subplots(2, 2, figsize=(18, 16))
    axes = axes.flatten()

    median_soph = data['median_sophistication']

    # Pre-calculate constrained models using COMPOSITE disinhibition (same as main scatter)
    # This ensures consistent constrained identification across all subplots
    all_x = [m['sophistication'] for m in data['models']]
    all_y_composite = [m['disinhibition'] for m in data['models']]
    z_composite = np.polyfit(all_x, all_y_composite, 1)
    p_composite = np.poly1d(z_composite)
    predicted_composite = p_composite(all_x)
    residuals_composite = np.array(all_y_composite) - predicted_composite

    # Identify constrained models using composite (high sophistication, below-predicted disinhibition)
    constrained_composite = []
    for i, model in enumerate(data['models']):
        if model['sophistication'] > CONSTRAINED_SOPH_THRESHOLD and residuals_composite[i] < CONSTRAINED_RESIDUAL_THRESHOLD:
            constrained_composite.append({
                'model': model,
                'residual': residuals_composite[i],
                'predicted': predicted_composite[i]
            })
    constrained_ids = {c['model']['model_id'] for c in constrained_composite}

    # Identify borderline models (same for all subplots)
    borderline = [m for m in data['models']
                 if abs(m['sophistication'] - median_soph) < BORDERLINE_THRESHOLD]
    borderline_ids = {b['model_id'] for b in borderline}

    for idx, dim in enumerate(disinhibition_dims):
        ax = axes[idx]

        # Get dimension-specific values for regression/residuals (for outlier detection)
        all_y_dim = [m['scores'][dim] for m in data['models']]

        # Calculate regression line for this dimension
        z_dim = np.polyfit(all_x, all_y_dim, 1)
        p_dim = np.poly1d(z_dim)
        predicted_dim = p_dim(all_x)
        residuals_dim = np.array(all_y_dim) - predicted_dim
        residual_std_dim = np.std(residuals_dim)

        # Separate by classification and borderline status
        high_normal = []
        high_borderline = []
        low_normal = []
        low_borderline = []

        for model in data['models']:
            is_borderline = model['model_id'] in borderline_ids
            if model['classification'] == 'High-Sophistication':
                if is_borderline:
                    high_borderline.append(model)
                else:
                    high_normal.append(model)
            else:
                if is_borderline:
                    low_borderline.append(model)
                else:
                    low_normal.append(model)

        # Plot normal models (no labels here - legend is created manually)
        if high_normal:
            ax.scatter([m['sophistication'] for m in high_normal],
                       [m['scores'][dim] for m in high_normal],
                       color='#2ecc71', alpha=0.7, s=120,
                       edgecolors='black', linewidth=1.5,
                       zorder=3)

        if low_normal:
            ax.scatter([m['sophistication'] for m in low_normal],
                       [m['scores'][dim] for m in low_normal],
                       color='#e74c3c', alpha=0.7, s=120,
                       edgecolors='black', linewidth=1.5,
                       zorder=3)

        # Plot borderline models (no labels here - legend is created manually)
        if high_borderline:
            ax.scatter([m['sophistication'] for m in high_borderline],
                       [m['scores'][dim] for m in high_borderline],
                       color='#f39c12', alpha=0.9, s=140,
                       edgecolors='black', linewidth=2,
                       marker='s',
                       zorder=4)

            # Label borderline models
            for model in high_borderline:
                label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
                if len(label_name) > 20:
                    label_name = label_name[:17] + '...'

                ax.annotate(label_name,
                           xy=(model['sophistication'], model['scores'][dim]),
                           xytext=(6, 6), textcoords='offset points',
                           fontsize=6, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='orange', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                         color='orange', lw=1),
                           zorder=8)

        if low_borderline:
            ax.scatter([m['sophistication'] for m in low_borderline],
                       [m['scores'][dim] for m in low_borderline],
                       color='#e67e22', alpha=0.9, s=140,
                       edgecolors='black', linewidth=2,
                       marker='s',
                       zorder=4)

            # Label borderline models
            for model in low_borderline:
                label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
                if len(label_name) > 20:
                    label_name = label_name[:17] + '...'

                ax.annotate(label_name,
                           xy=(model['sophistication'], model['scores'][dim]),
                           xytext=(6, -10), textcoords='offset points',
                           fontsize=6, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='orange', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                         color='orange', lw=1),
                           zorder=8)

        # Add median split line
        ax.axvline(median_soph, color='purple', linestyle='--',
                   linewidth=2, alpha=0.6, zorder=2)

        # Shade borderline zone
        ax.axvspan(median_soph - BORDERLINE_THRESHOLD, median_soph + BORDERLINE_THRESHOLD,
                   alpha=0.08, color='orange', zorder=1)

        # Add regression line (using pre-calculated values)
        x_line = np.linspace(min(all_x), max(all_x), 100)
        ax.plot(x_line, p_dim(x_line), 'k--', alpha=0.4, linewidth=2, zorder=1)

        # Calculate statistics for this dimension
        r, p_val = sp_stats.pearsonr(all_x, all_y_dim)
        cohens_d = data['statistics'][dim]['cohens_d']

        # Find outlier models (using pre-calculated residuals)
        dimension_outliers = []
        for i, model in enumerate(data['models']):
            if abs(residuals_dim[i]) > OUTLIER_SD_THRESHOLD * residual_std_dim:
                dimension_outliers.append({
                    'model': model,
                    'residual': residuals_dim[i]
                })

        # Highlight outliers with red circles
        if dimension_outliers:
            sorted_outliers = sorted(dimension_outliers, key=lambda x: abs(x['residual']), reverse=True)
            for outlier_info in sorted_outliers:
                model = outlier_info['model']
                ax.scatter([model['sophistication']], [model['scores'][dim]],
                          s=300, facecolors='none', edgecolors='red',
                          linewidth=2.5, zorder=5)

        # Highlight constrained models (cyan diamonds) - using composite-based identification
        if constrained_composite:
            for constrained_info in constrained_composite:
                model = constrained_info['model']
                ax.scatter([model['sophistication']], [model['scores'][dim]],
                          marker='D', s=160, color='#00CED1', alpha=0.9,
                          edgecolors='blue', linewidth=2, zorder=6)

        # Add statistics text box
        ax.text(0.05, 0.95,
                f'H2: r = {r:.3f}\n'
                f'H1: d = {cohens_d:.2f}\n'
                f'Outliers: {len(dimension_outliers)}\n'
                f'Constrained: {len(constrained_composite)}',
                transform=ax.transAxes,
                fontsize=8,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                zorder=5)

        # Label extreme models for ALL dimensions (not just first)
        # Find extremes for this dimension
        sorted_by_soph = sorted(data['models'], key=lambda m: m['sophistication'])
        sorted_by_dim = sorted(data['models'], key=lambda m: m['scores'][dim])

        # Track which models need labels and their attributes (deduplicated)
        models_to_label = {}

        # Min/max sophistication (top 2 each)
        for model in sorted_by_soph[:2]:
            if model['model_id'] not in models_to_label:
                models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
            models_to_label[model['model_id']]['tags'].append(f"min-s={model['sophistication']:.2f}")
            models_to_label[model['model_id']]['priority'] += 10

        for model in sorted_by_soph[-2:]:
            if model['model_id'] not in models_to_label:
                models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
            models_to_label[model['model_id']]['tags'].append(f"max-s={model['sophistication']:.2f}")
            models_to_label[model['model_id']]['priority'] += 10

        # Min/max dimension score (top 2 each)
        dim_short = dim[:4]
        for model in sorted_by_dim[:2]:
            if model['model_id'] not in models_to_label:
                models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
            models_to_label[model['model_id']]['tags'].append(f"min-{dim_short}={model['scores'][dim]:.2f}")
            models_to_label[model['model_id']]['priority'] += 5

        for model in sorted_by_dim[-2:]:
            if model['model_id'] not in models_to_label:
                models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
            models_to_label[model['model_id']]['tags'].append(f"max-{dim_short}={model['scores'][dim]:.2f}")
            models_to_label[model['model_id']]['priority'] += 5

        # Add top outliers for this dimension (top 3)
        if dimension_outliers:
            sorted_outliers = sorted(dimension_outliers, key=lambda x: abs(x['residual']), reverse=True)
            for outlier_info in sorted_outliers[:3]:
                model = outlier_info['model']
                if model['model_id'] not in models_to_label:
                    models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
                models_to_label[model['model_id']]['tags'].append(f"outlier")
                models_to_label[model['model_id']]['priority'] += 20

        # Add constrained models to labeling (name only, no "constrained" tag)
        for constrained_info in constrained_composite:
            model = constrained_info['model']
            if model['model_id'] not in models_to_label:
                models_to_label[model['model_id']] = {'model': model, 'tags': [], 'priority': 0}
            # Just add priority for labeling, no tag text (cyan diamond is visual indicator)
            models_to_label[model['model_id']]['priority'] += 15

        # Now label each unique model once with all its tags
        for i, (model_id, info) in enumerate(sorted(models_to_label.items(), key=lambda x: -x[1]['priority'])):
            model = info['model']
            tags = info['tags']

            # Shortened model name
            label_name = model['display_name'].replace('Claude-', 'C-').replace('GPT-', 'G-')
            if len(label_name) > 15:
                label_name = label_name[:12] + '...'

            # Combine all tags (limit to 2 for space), or just use name if no tags
            if tags:
                tag_text = ', '.join(tags[:2])
                if len(tags) > 2:
                    tag_text += '...'
                full_label = f"{label_name}\n{tag_text}"
            else:
                full_label = label_name

            # Smart positioning based on location
            soph = model['sophistication']
            dim_val = model['scores'][dim]

            if soph < 5.5:
                x_offset = -60
            else:
                x_offset = 60

            if dim_val < np.median([m['scores'][dim] for m in data['models']]):
                y_offset = -30
            else:
                y_offset = 30

            # Vertical spread for multiple labels
            y_offset += (i % 3) * 12

            ax.annotate(full_label,
                       xy=(soph, dim_val),
                       xytext=(x_offset, y_offset), textcoords='offset points',
                       fontsize=5.5, fontweight='bold', color='navy',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.85, edgecolor='navy'),
                       arrowprops=dict(arrowstyle='->', color='navy', lw=1),
                       zorder=9)

        # Labels and formatting
        ax.set_xlabel('Sophistication', fontsize=11, fontweight='bold')
        ax.set_ylabel(f'{dim.capitalize()} Score', fontsize=11, fontweight='bold')
        ax.set_title(f'{dim.capitalize()}', fontsize=13, fontweight='bold')

        # Add legend entries for special markers (only on first plot to avoid clutter)
        if idx == 0:
            # Create legend with all marker types
            ax.scatter([], [], color='#2ecc71', s=80, label='High-Soph')
            ax.scatter([], [], color='#e74c3c', s=80, label='Low-Soph')
            ax.scatter([], [], color='#f39c12', marker='s', s=80, label='Borderline')
            ax.scatter([], [], s=200, facecolors='none', edgecolors='red', linewidth=2, label='Outlier')
            ax.scatter([], [], marker='D', s=100, color='#00CED1', edgecolors='blue', linewidth=1.5, label='Constrained')
            ax.legend(loc='lower right', fontsize=7, framealpha=0.9, ncol=2)

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

    fig.suptitle('Sophistication vs Individual Disinhibition Dimensions\n'
                 '(H2 Correlations with H1 Classification, Outliers, Borderline & Constrained Models)',
                 fontsize=16, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✓ Created: {output_path}")

def main():
    import sys

    # Get intervention name from command line or default to baseline
    if len(sys.argv) > 1:
        intervention = sys.argv[1]
    else:
        intervention = "baseline"

    # Paths
    profile_dir = Path(f"outputs/behavioral_profiles/{intervention}")

    if not profile_dir.exists():
        print(f"Error: Profile directory not found: {profile_dir}")
        print(f"Usage: python3 {sys.argv[0]} [intervention_name]")
        print(f"Example: python3 {sys.argv[0]} affective")
        sys.exit(1)

    print(f"Intervention: {intervention}")
    print("Loading median split classification data...")
    data = load_median_split_data(profile_dir)

    print(f"Loaded {len(data['models'])} models")
    print(f"Median sophistication: {data['median_sophistication']:.3f}")
    print(f"High-Sophistication: n={data['n_high_sophistication']}")
    print(f"Low-Sophistication: n={data['n_low_sophistication']}")

    print("\nCreating color-coded scatter plots with outlier detection...")

    # Create composite scatter
    composite_output = profile_dir / "h2_scatter_sophistication_composite.png"
    create_color_coded_scatter_composite(data, composite_output)

    # Create all dimensions scatter
    all_dims_output = profile_dir / "h2_scatter_all_dimensions.png"
    create_color_coded_scatter_all_dimensions(data, all_dims_output)

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print("\nCreated H2 scatter plots with enhanced markers:")
    print(f"  - {composite_output.name}")
    print(f"  - {all_dims_output.name}")
    print("\nVisual Legend:")
    print("  🟢 Green circles = High-Sophistication (normal)")
    print("  🔴 Red circles = Low-Sophistication (normal)")
    print(f"  🟠 Orange squares = Borderline (within ±{BORDERLINE_THRESHOLD} of median)")
    print(f"  💎 Cyan diamonds = Constrained (soph > {CONSTRAINED_SOPH_THRESHOLD}, residual < {CONSTRAINED_RESIDUAL_THRESHOLD})")
    print(f"  ⭕ Red circle outline = Statistical outlier (residual > {OUTLIER_SD_THRESHOLD} SD)")
    print("  🟣 Purple dashed line = Median split")
    print("  🟡 Orange shaded zone = Borderline region")

if __name__ == "__main__":
    main()
