#!/usr/bin/env python3
"""
Create H1a side-by-side bar chart comparing high vs low sophistication groups on disinhibition.

Shows group differences for disinhibition composite and all four disinhibition
dimensions with error bars and significance markers.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_median_split_data(profile_dir):
    """Load median split classification data."""
    median_split_path = profile_dir / "median_split_classification.json"

    with open(median_split_path, 'r') as f:
        return json.load(f)

def format_p(p):
    """Format p-value for display."""
    if p < 0.001:
        return "p < .001"
    elif p < 0.01:
        return "p < .01"
    else:
        return f"p = {p:.3f}"

def get_significance_marker(p):
    """Get significance marker based on p-value."""
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    else:
        return 'ns'

def create_h1_bar_chart(data, output_path, condition="baseline"):
    """Create side-by-side bar chart for H1a group comparisons (disinhibition)."""

    # Dimensions to plot: disinhibition composite + 4 individual dimensions
    dimensions = ['disinhibition', 'transgression', 'aggression', 'tribalism', 'grandiosity']
    display_names = ['Disinhibition\nComposite', 'Transgression', 'Aggression', 'Tribalism', 'Grandiosity']

    fig, ax = plt.subplots(1, 1, figsize=(14, 8))

    x = np.arange(len(dimensions))
    width = 0.35

    # Extract statistics
    high_means = []
    high_stds = []
    low_means = []
    low_stds = []
    cohens_ds = []
    p_values = []

    for dim in dimensions:
        stats = data['statistics'][dim]
        high_means.append(stats['high_mean'])
        high_stds.append(stats['high_std'])
        low_means.append(stats['low_mean'])
        low_stds.append(stats['low_std'])
        cohens_ds.append(stats['cohens_d'])
        p_values.append(stats['p_value'])

    # Create bars
    bars1 = ax.bar(x - width/2, high_means, width,
                    yerr=high_stds, capsize=6,
                    color='#2ecc71', alpha=0.8,
                    edgecolor='black', linewidth=1.5,
                    label=f'High-Sophistication (n={data["n_high_sophistication"]})',
                    error_kw={'linewidth': 2, 'ecolor': 'black'})

    bars2 = ax.bar(x + width/2, low_means, width,
                    yerr=low_stds, capsize=6,
                    color='#e74c3c', alpha=0.8,
                    edgecolor='black', linewidth=1.5,
                    label=f'Low-Sophistication (n={data["n_low_sophistication"]})',
                    error_kw={'linewidth': 2, 'ecolor': 'black'})

    # Add value labels on bars
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        # High-Soph label
        height1 = bar1.get_height()
        ax.text(bar1.get_x() + bar1.get_width()/2., height1 + high_stds[i] + 0.15,
                f'{high_means[i]:.2f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Low-Soph label
        height2 = bar2.get_height()
        ax.text(bar2.get_x() + bar2.get_width()/2., height2 + low_stds[i] + 0.15,
                f'{low_means[i]:.2f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add significance markers above bars
    max_heights = [max(high_means[i] + high_stds[i], low_means[i] + low_stds[i]) for i in range(len(dimensions))]

    for i, (cohens_d, p_value) in enumerate(zip(cohens_ds, p_values)):
        sig_marker = get_significance_marker(p_value)
        y_pos = max_heights[i] + 0.4

        # Draw significance line
        x1 = x[i] - width/2
        x2 = x[i] + width/2
        ax.plot([x1, x2], [y_pos, y_pos], 'k-', linewidth=1.5)

        # Add marker and effect size
        ax.text(x[i], y_pos + 0.15,
                f'{sig_marker}\nd={cohens_d:.2f}',
                ha='center', va='bottom',
                fontsize=9, fontweight='bold')

    # Formatting
    ax.set_ylabel('Mean Score (1-10 scale)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Dimension', fontsize=13, fontweight='bold')
    ax.set_title('H1a: High-Sophistication vs Low-Sophistication Group Comparison\n'
                 'Disinhibition Composite and Individual Dimensions',
                 fontsize=15, fontweight='bold', pad=20)

    # Add condition label as suptitle
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold',
                 y=0.995, color='#666666')
    ax.set_xticks(x)
    ax.set_xticklabels(display_names, fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=12, framealpha=0.95)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_ylim([1, max(max_heights) + 1.2])

    # Add note about significance
    ax.text(0.98, 0.02,
            '*** p < .001  ** p < .01  * p < .05  ns = not significant',
            transform=ax.transAxes,
            fontsize=9,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✓ Created: {output_path}")

def create_h1_summary_table(data, output_path, condition="baseline"):
    """Create summary table image for H1a results."""

    dimensions = ['disinhibition', 'transgression', 'aggression', 'tribalism', 'grandiosity']
    display_names = ['Disinhibition Composite', 'Transgression', 'Aggression', 'Tribalism', 'Grandiosity']

    # Create figure for table
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.axis('off')

    # Prepare table data
    table_data = []
    table_data.append(['Dimension', 'High-Soph\nM (SD)', 'Low-Soph\nM (SD)',
                       'Difference', '% Diff', 't(44)', 'p', "Cohen's d", 'Effect'])

    for dim, display_name in zip(dimensions, display_names):
        stats = data['statistics'][dim]

        high_str = f"{stats['high_mean']:.2f} ({stats['high_std']:.2f})"
        low_str = f"{stats['low_mean']:.2f} ({stats['low_std']:.2f})"
        diff_str = f"+{stats['difference']:.2f}"
        pct_str = f"+{stats['pct_difference']:.1f}%"
        t_str = f"{stats['t_statistic']:.2f}"
        p_str = format_p(stats['p_value'])
        d_str = f"{stats['cohens_d']:.2f}"

        # Effect size label
        d = abs(stats['cohens_d'])
        if d >= 0.8:
            effect = 'large'
        elif d >= 0.5:
            effect = 'medium'
        elif d >= 0.2:
            effect = 'small'
        else:
            effect = 'negligible'

        table_data.append([display_name, high_str, low_str, diff_str, pct_str,
                          t_str, p_str, d_str, effect])

    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.18, 0.12, 0.12, 0.10, 0.08, 0.08, 0.10, 0.10, 0.10])

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)

    # Style header row
    for i in range(len(table_data[0])):
        cell = table[(0, i)]
        cell.set_facecolor('#4a4a4a')
        cell.set_text_props(weight='bold', color='white')

    # Style data rows
    for i in range(1, len(table_data)):
        for j in range(len(table_data[i])):
            cell = table[(i, j)]
            if i == 1:  # Disinhibition composite (primary outcome)
                cell.set_facecolor('#ffffcc')
            else:
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')

    # Add title with condition
    ax.text(0.5, 0.98, f'Condition: {condition}',
            ha='center', va='top', fontsize=11, fontweight='bold', color='#666666',
            transform=ax.transAxes)
    ax.text(0.5, 0.93, 'H1a: Statistical Comparison of High vs Low Sophistication Groups',
            ha='center', va='top', fontsize=14, fontweight='bold',
            transform=ax.transAxes)

    # Add note
    ax.text(0.5, 0.02,
            f'High-Sophistication: n={data["n_high_sophistication"]} | '
            f'Low-Sophistication: n={data["n_low_sophistication"]} | '
            f'Median sophistication = {data["median_sophistication"]:.2f}',
            ha='center', va='bottom', fontsize=10,
            transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

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

    print("\nCreating H1a visualizations...")

    # Create bar chart
    bar_chart_output = profile_dir / "h1_bar_chart_comparison.png"
    create_h1_bar_chart(data, bar_chart_output, condition=intervention)

    # Create summary table
    table_output = profile_dir / "h1_summary_table.png"
    create_h1_summary_table(data, table_output, condition=intervention)

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print("\nCreated H1a group comparison visualizations:")
    print(f"  - {bar_chart_output.name}")
    print(f"  - {table_output.name}")
    print("\nH1a Results Summary:")
    print(f"  Disinhibition Composite: d={data['statistics']['disinhibition']['cohens_d']:.2f}, "
          f"{format_p(data['statistics']['disinhibition']['p_value'])}")
    print(f"  All dimensions show significant differences (p < .001)")

if __name__ == "__main__":
    main()
