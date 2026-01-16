#!/usr/bin/env python3
"""
Visualize external evaluation validation (ARC-AGI and GPQA).

Generates:
- Scatter plots with regression lines
- Box plots comparing High vs Low sophistication groups
- Combined panels with borderline highlighting
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats


def load_validation_data(json_path: Path) -> dict:
    """Load validation analysis JSON."""
    with open(json_path) as f:
        return json.load(f)


def format_model_name(model_id: str) -> str:
    """Format model ID for display."""
    # Common replacements for cleaner display
    name = model_id.replace('-', ' ').replace('_', ' ')
    name = name.replace('gpt ', 'GPT-').replace('Gpt ', 'GPT-')
    name = name.replace('claude ', 'Claude ').replace('Claude ', 'Claude-')
    name = name.replace('llama ', 'Llama-').replace('Llama ', 'Llama-')
    name = name.replace('gemini ', 'Gemini-').replace('Gemini ', 'Gemini-')
    name = name.replace('grok ', 'Grok-').replace('Grok ', 'Grok-')
    name = name.replace('nova ', 'Nova-').replace('Nova ', 'Nova-')
    name = name.replace('qwen', 'Qwen').replace('deepseek', 'DeepSeek')

    # Title case but preserve specific patterns
    words = name.split()
    result = []
    for w in words:
        if w.startswith(('GPT', 'Claude', 'Llama', 'Gemini', 'Grok', 'Nova', 'Qwen', 'DeepSeek')):
            result.append(w)
        elif w.lower() in ('pro', 'opus', 'sonnet', 'haiku', 'scout', 'maverick', 'flash', 'lite', 'premier'):
            result.append(w.title())
        else:
            result.append(w.title() if not any(c.isupper() for c in w) else w)

    return ' '.join(result)


def get_models_to_label(
    data: list[dict],
    x_key: str,
    y_key: str,
    median_soph: float,
    borderline_threshold: float,
    n_extremes: int = 3,
) -> dict:
    """
    Identify models that should be labeled:
    - Top/bottom N by benchmark score
    - Top/bottom N by sophistication
    - All borderline models

    Returns dict mapping model_id -> list of tags
    """
    labels = {}

    # Sort by benchmark score
    sorted_by_score = sorted(data, key=lambda d: d[y_key], reverse=True)
    top_score = [d["behavioral_model_id"] for d in sorted_by_score[:n_extremes]]
    bottom_score = [d["behavioral_model_id"] for d in sorted_by_score[-n_extremes:]]

    # Sort by sophistication
    sorted_by_soph = sorted(data, key=lambda d: d[x_key], reverse=True)
    top_soph = [d["behavioral_model_id"] for d in sorted_by_soph[:n_extremes]]
    bottom_soph = [d["behavioral_model_id"] for d in sorted_by_soph[-n_extremes:]]

    # Borderline models
    borderline = [d["behavioral_model_id"] for d in data
                  if abs(d[x_key] - median_soph) <= borderline_threshold]

    # Build label dict with tags
    for model_id in top_score:
        labels.setdefault(model_id, []).append("top_score")
    for model_id in bottom_score:
        labels.setdefault(model_id, []).append("bottom_score")
    for model_id in top_soph:
        labels.setdefault(model_id, []).append("top_soph")
    for model_id in bottom_soph:
        labels.setdefault(model_id, []).append("bottom_soph")
    for model_id in borderline:
        labels.setdefault(model_id, []).append("borderline")

    return labels


def create_scatter_with_regression(
    data: list[dict],
    x_key: str,
    y_key: str,
    y_label: str,
    title: str,
    output_path: Path,
    median_soph: float,
    borderline_threshold: float = 0.5,
    r_value: float = None,
    p_value: float = None,
):
    """Create scatter plot with regression line and borderline highlighting."""

    fig, ax = plt.subplots(figsize=(12, 9))

    # Extract data
    x = np.array([d[x_key] for d in data])
    y = np.array([d[y_key] for d in data])
    groups = [d["sophistication_group"] for d in data]
    models = [d["behavioral_model_id"] for d in data]

    # Calculate regression
    slope, intercept, r, p, se = stats.linregress(x, y)

    # Add borderline shaded zone
    ax.axvspan(
        median_soph - borderline_threshold,
        median_soph + borderline_threshold,
        alpha=0.15,
        color='orange',
        label=f'Borderline zone (±{borderline_threshold})'
    )

    # Add median line
    ax.axvline(x=median_soph, color='gray', linestyle=':', linewidth=1.5,
               label=f'Median = {median_soph:.2f}')

    # Get models to label
    models_to_label = get_models_to_label(data, x_key, y_key, median_soph, borderline_threshold)

    # Plot points with colors based on group and borderline status
    for i, (xi, yi, group, model) in enumerate(zip(x, y, groups, models)):
        is_borderline = abs(xi - median_soph) <= borderline_threshold

        if is_borderline:
            color = '#f39c12'  # Orange for borderline
            marker = 's'
            size = 180
            zorder = 5
        elif group == "High-Sophistication":
            color = '#2ecc71'  # Green for high
            marker = 'o'
            size = 100
            zorder = 3
        else:
            color = '#e74c3c'  # Red for low
            marker = 'o'
            size = 100
            zorder = 3

        ax.scatter(xi, yi, c=color, s=size, marker=marker, zorder=zorder,
                   edgecolor='white', linewidth=0.5)

    # Add regression line
    x_line = np.linspace(x.min() - 0.5, x.max() + 0.5, 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, '--', color='#3498db', linewidth=2,
            label=f'Regression line')

    # Label extreme and borderline models with smart positioning
    from matplotlib.transforms import offset_copy

    labeled_positions = []

    for d in data:
        model_id = d["behavioral_model_id"]
        if model_id not in models_to_label:
            continue

        xi, yi = d[x_key], d[y_key]
        tags = models_to_label[model_id]
        display_name = format_model_name(model_id)

        # Determine label style based on tags
        if "borderline" in tags:
            fontweight = 'bold'
            color = '#d35400'  # Dark orange
        elif "top_score" in tags or "top_soph" in tags:
            fontweight = 'bold'
            color = '#1a5f2a'  # Dark green
        else:
            fontweight = 'bold'
            color = '#922b21'  # Dark red

        # Smart offset to avoid overlaps
        # Default: above for high scores, below for low scores
        y_range = max(y) - min(y)
        x_range = max(x) - min(x)

        if "top_score" in tags:
            offset_y = 8
            va = 'bottom'
        elif "bottom_score" in tags:
            offset_y = -8
            va = 'top'
        elif "borderline" in tags:
            offset_y = 10
            va = 'bottom'
        else:
            offset_y = 8 if yi > np.median(y) else -8
            va = 'bottom' if yi > np.median(y) else 'top'

        # Horizontal offset for crowded areas
        offset_x = 0
        if xi > median_soph + 0.5:
            offset_x = 5
            ha = 'left'
        elif xi < median_soph - 0.5:
            offset_x = -5
            ha = 'right'
        else:
            ha = 'center'

        ax.annotate(
            display_name,
            (xi, yi),
            textcoords="offset points",
            xytext=(offset_x, offset_y),
            ha=ha,
            va=va,
            fontsize=8,
            fontweight=fontweight,
            color=color,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'),
            zorder=10
        )

    # Add correlation statistics
    r_val = r_value if r_value is not None else r
    p_val = p_value if p_value is not None else p
    p_str = f"p < .0001" if p_val < 0.0001 else f"p = {p_val:.4f}"
    stats_text = f"r = {r_val:.3f}, {p_str}\nn = {len(data)}"
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Create legend handles
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='white', label='High-Sophistication'),
        Patch(facecolor='#e74c3c', edgecolor='white', label='Low-Sophistication'),
        Patch(facecolor='#f39c12', edgecolor='white', label='Borderline'),
        Line2D([0], [0], color='#3498db', linestyle='--', linewidth=2, label='Regression'),
        Line2D([0], [0], color='gray', linestyle=':', linewidth=1.5, label=f'Median ({median_soph:.2f})'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    ax.set_xlabel('Sophistication (Depth + Authenticity) / 2', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def create_box_plot(
    data: list[dict],
    y_key: str,
    y_label: str,
    title: str,
    output_path: Path,
    h1_stats: dict = None,
):
    """Create box plot comparing High vs Low sophistication groups."""

    fig, ax = plt.subplots(figsize=(8, 6))

    # Separate by group
    high = [d[y_key] for d in data if d["sophistication_group"] == "High-Sophistication"]
    low = [d[y_key] for d in data if d["sophistication_group"] == "Low-Sophistication"]

    bp = ax.boxplot(
        [high, low],
        tick_labels=['High-Sophistication', 'Low-Sophistication'],
        patch_artist=True,
        widths=0.6
    )

    # Color boxes
    bp['boxes'][0].set_facecolor('#2ecc71')
    bp['boxes'][1].set_facecolor('#e74c3c')
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_alpha(0.7)

    # Style whiskers and medians
    for whisker in bp['whiskers']:
        whisker.set(color='#333', linewidth=1.5)
    for cap in bp['caps']:
        cap.set(color='#333', linewidth=1.5)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)

    # Add individual points (jittered)
    for i, (group_data, x_pos) in enumerate([(high, 1), (low, 2)]):
        jitter = np.random.normal(0, 0.04, len(group_data))
        color = '#2ecc71' if i == 0 else '#e74c3c'
        ax.scatter(
            np.full(len(group_data), x_pos) + jitter,
            group_data,
            alpha=0.6,
            s=40,
            c=color,
            edgecolor='white',
            linewidth=0.5,
            zorder=3
        )

    # Add statistics annotation
    if h1_stats:
        high_mean = h1_stats["high_sophistication"]["mean"]
        low_mean = h1_stats["low_sophistication"]["mean"]
        diff = high_mean - low_mean
        t_stat = h1_stats["t_statistic"]
        p_val = h1_stats["p_value"]

        p_str = f"p < .0001" if p_val < 0.0001 else f"p = {p_val:.4f}"

        stats_text = (
            f"High: M = {high_mean:.1f}% (n = {h1_stats['high_sophistication']['n']})\n"
            f"Low: M = {low_mean:.1f}% (n = {h1_stats['low_sophistication']['n']})\n"
            f"Diff: +{diff:.1f} pp\n"
            f"t = {t_stat:.2f}, {p_str}"
        )
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def create_combined_panel(
    data: list[dict],
    y_key: str,
    y_label: str,
    benchmark_name: str,
    output_path: Path,
    median_soph: float,
    borderline_threshold: float,
    r_value: float,
    p_value: float,
    h1_stats: dict,
):
    """Create combined 2-panel figure (scatter + box)."""

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # ----- Panel A: Scatter with Regression -----
    ax = axes[0]

    x = np.array([d["sophistication"] for d in data])
    y = np.array([d[y_key] for d in data])
    groups = [d["sophistication_group"] for d in data]
    models = [d["behavioral_model_id"] for d in data]

    # Regression
    slope, intercept, _, _, _ = stats.linregress(x, y)

    # Get models to label
    models_to_label = get_models_to_label(data, "sophistication", y_key, median_soph, borderline_threshold)

    # Borderline zone
    ax.axvspan(
        median_soph - borderline_threshold,
        median_soph + borderline_threshold,
        alpha=0.15,
        color='orange'
    )
    ax.axvline(x=median_soph, color='gray', linestyle=':', linewidth=1.5)

    # Points
    for xi, yi, group, model in zip(x, y, groups, models):
        is_borderline = abs(xi - median_soph) <= borderline_threshold

        if is_borderline:
            color = '#f39c12'
            marker = 's'
            size = 150
        elif group == "High-Sophistication":
            color = '#2ecc71'
            marker = 'o'
            size = 80
        else:
            color = '#e74c3c'
            marker = 'o'
            size = 80

        ax.scatter(xi, yi, c=color, s=size, marker=marker,
                   edgecolor='white', linewidth=0.5)

    # Regression line
    x_line = np.linspace(x.min() - 0.3, x.max() + 0.3, 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, '--', color='#3498db', linewidth=2)

    # Label extreme and borderline models
    for d in data:
        model_id = d["behavioral_model_id"]
        if model_id not in models_to_label:
            continue

        xi, yi = d["sophistication"], d[y_key]
        tags = models_to_label[model_id]
        display_name = format_model_name(model_id)

        # Determine label style
        if "borderline" in tags:
            fontweight = 'bold'
            color = '#d35400'
        elif "top_score" in tags or "top_soph" in tags:
            fontweight = 'bold'
            color = '#1a5f2a'
        else:
            fontweight = 'bold'
            color = '#922b21'

        # Smart offset
        if "top_score" in tags:
            offset_y = 6
            va = 'bottom'
        elif "bottom_score" in tags:
            offset_y = -6
            va = 'top'
        elif "borderline" in tags:
            offset_y = 8
            va = 'bottom'
        else:
            offset_y = 6 if yi > np.median(y) else -6
            va = 'bottom' if yi > np.median(y) else 'top'

        offset_x = 0
        if xi > median_soph + 0.5:
            offset_x = 4
            ha = 'left'
        elif xi < median_soph - 0.5:
            offset_x = -4
            ha = 'right'
        else:
            ha = 'center'

        ax.annotate(
            display_name,
            (xi, yi),
            textcoords="offset points",
            xytext=(offset_x, offset_y),
            ha=ha,
            va=va,
            fontsize=7,
            fontweight=fontweight,
            color=color,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7, edgecolor='none'),
            zorder=10
        )

    # Stats
    p_str = f"p < .0001" if p_value < 0.0001 else f"p = {p_value:.4f}"
    ax.text(0.05, 0.95, f"r = {r_value:.3f}, {p_str}\nn = {len(data)}",
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Sophistication', fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(f'A. {benchmark_name} vs Sophistication', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # ----- Panel B: Box Plot -----
    ax = axes[1]

    high = [d[y_key] for d in data if d["sophistication_group"] == "High-Sophistication"]
    low = [d[y_key] for d in data if d["sophistication_group"] == "Low-Sophistication"]

    bp = ax.boxplot([high, low], tick_labels=['High-Soph', 'Low-Soph'],
                    patch_artist=True, widths=0.5)

    bp['boxes'][0].set_facecolor('#2ecc71')
    bp['boxes'][1].set_facecolor('#e74c3c')
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_alpha(0.7)

    for whisker in bp['whiskers']:
        whisker.set(color='#333', linewidth=1.5)
    for cap in bp['caps']:
        cap.set(color='#333', linewidth=1.5)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)

    # Individual points
    for i, (group_data, x_pos) in enumerate([(high, 1), (low, 2)]):
        jitter = np.random.normal(0, 0.04, len(group_data))
        color = '#2ecc71' if i == 0 else '#e74c3c'
        ax.scatter(
            np.full(len(group_data), x_pos) + jitter,
            group_data, alpha=0.6, s=30, c=color,
            edgecolor='white', linewidth=0.5, zorder=3
        )

    # Stats
    high_mean = h1_stats["high_sophistication"]["mean"]
    low_mean = h1_stats["low_sophistication"]["mean"]
    diff = high_mean - low_mean
    t_stat = h1_stats["t_statistic"]
    h1_p = h1_stats["p_value"]
    h1_p_str = f"p < .0001" if h1_p < 0.0001 else f"p = {h1_p:.4f}"

    stats_text = f"Diff: +{diff:.1f} pp\nt = {t_stat:.2f}, {h1_p_str}"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title('B. Group Comparison', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Legend for entire figure
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='white', alpha=0.7, label='High-Sophistication'),
        Patch(facecolor='#e74c3c', edgecolor='white', alpha=0.7, label='Low-Sophistication'),
        Patch(facecolor='#f39c12', edgecolor='white', label='Borderline'),
        Line2D([0], [0], color='#3498db', linestyle='--', linewidth=2, label='Regression'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))

    plt.suptitle(f'{benchmark_name} External Validation\nCondition: baseline', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def main():
    """Generate all external evaluation visualizations."""

    base_dir = Path(__file__).parent.parent
    external_evals_dir = base_dir / "outputs/behavioral_profiles/research_synthesis/limitations/external_evals"

    # Load data
    arc_data = load_validation_data(external_evals_dir / "arc_agi_validation_analysis.json")
    gpqa_data = load_validation_data(external_evals_dir / "gpqa_validation_analysis.json")

    # Median sophistication (from baseline - approximately 5.93 based on main brief)
    # We'll calculate from the matched data
    arc_models = arc_data["matched_model_details"]
    gpqa_models = gpqa_data["matched_model_details"]

    # For borderline highlighting, calculate median from each benchmark's matched models
    # (rather than using baseline median which may not match the subset)
    borderline_threshold = 0.5

    # Calculate median for each benchmark from its matched models
    arc_median = np.median([d["sophistication"] for d in arc_models])
    gpqa_median = np.median([d["sophistication"] for d in gpqa_models])

    # For backward compatibility, use a general median for combined figures
    # (average of the two benchmark medians)
    median_soph = (arc_median + gpqa_median) / 2

    print("=" * 60)
    print("Generating External Evaluation Visualizations")
    print("=" * 60)

    # ----- ARC-AGI Visualizations -----
    print("\n--- ARC-AGI ---")
    print(f"  ARC-AGI median sophistication: {arc_median:.2f} (n={len(arc_models)})")

    # Scatter plot
    create_scatter_with_regression(
        data=arc_models,
        x_key="sophistication",
        y_key="arc_agi_1",
        y_label="ARC-AGI-1 Score (%)",
        title="ARC-AGI Performance vs Behavioral Sophistication\nCondition: baseline",
        output_path=external_evals_dir / "arc_agi_scatter.png",
        median_soph=arc_median,
        borderline_threshold=borderline_threshold,
        r_value=arc_data["correlations"]["sophistication"]["r"],
        p_value=arc_data["correlations"]["sophistication"]["p"],
    )

    # Box plot
    create_box_plot(
        data=arc_models,
        y_key="arc_agi_1",
        y_label="ARC-AGI-1 Score (%)",
        title="ARC-AGI by Sophistication Group\nCondition: baseline",
        output_path=external_evals_dir / "arc_agi_boxplot.png",
        h1_stats=arc_data["h1_group_comparison"],
    )

    # Combined panel
    create_combined_panel(
        data=arc_models,
        y_key="arc_agi_1",
        y_label="ARC-AGI-1 Score (%)",
        benchmark_name="ARC-AGI",
        output_path=external_evals_dir / "arc_agi_combined.png",
        median_soph=arc_median,
        borderline_threshold=borderline_threshold,
        r_value=arc_data["correlations"]["sophistication"]["r"],
        p_value=arc_data["correlations"]["sophistication"]["p"],
        h1_stats=arc_data["h1_group_comparison"],
    )

    # ----- GPQA Visualizations -----
    print("\n--- GPQA ---")
    print(f"  GPQA median sophistication: {gpqa_median:.2f} (n={len(gpqa_models)})")

    # Scatter plot
    create_scatter_with_regression(
        data=gpqa_models,
        x_key="sophistication",
        y_key="gpqa_score_pct",
        y_label="GPQA Score (%)",
        title="GPQA Performance vs Behavioral Sophistication\nCondition: baseline",
        output_path=external_evals_dir / "gpqa_scatter.png",
        median_soph=gpqa_median,
        borderline_threshold=borderline_threshold,
        r_value=gpqa_data["correlations"]["sophistication"]["r"],
        p_value=gpqa_data["correlations"]["sophistication"]["p"],
    )

    # Box plot
    create_box_plot(
        data=gpqa_models,
        y_key="gpqa_score_pct",
        y_label="GPQA Score (%)",
        title="GPQA by Sophistication Group\nCondition: baseline",
        output_path=external_evals_dir / "gpqa_boxplot.png",
        h1_stats=gpqa_data["h1_group_comparison"],
    )

    # Combined panel
    create_combined_panel(
        data=gpqa_models,
        y_key="gpqa_score_pct",
        y_label="GPQA Score (%)",
        benchmark_name="GPQA",
        output_path=external_evals_dir / "gpqa_combined.png",
        median_soph=gpqa_median,
        borderline_threshold=borderline_threshold,
        r_value=gpqa_data["correlations"]["sophistication"]["r"],
        p_value=gpqa_data["correlations"]["sophistication"]["p"],
        h1_stats=gpqa_data["h1_group_comparison"],
    )

    # ----- AIME Visualizations -----
    print("\n--- AIME 2025 ---")

    # Load AIME data
    aime_path = external_evals_dir / "aime_validation_analysis.json"
    if aime_path.exists():
        aime_data = load_validation_data(aime_path)
        aime_models = aime_data["matched_model_details"]
        aime_median = np.median([d["sophistication"] for d in aime_models])
        print(f"  AIME median sophistication: {aime_median:.2f} (n={len(aime_models)})")

        # Scatter plot
        create_scatter_with_regression(
            data=aime_models,
            x_key="sophistication",
            y_key="aime_score",
            y_label="AIME 2025 Score (%)",
            title="AIME 2025 Performance vs Behavioral Sophistication\nCondition: baseline",
            output_path=external_evals_dir / "aime_scatter.png",
            median_soph=aime_median,
            borderline_threshold=borderline_threshold,
            r_value=aime_data["correlations"]["sophistication"]["r"],
            p_value=aime_data["correlations"]["sophistication"]["p"],
        )

        # Box plot
        create_box_plot(
            data=aime_models,
            y_key="aime_score",
            y_label="AIME 2025 Score (%)",
            title="AIME 2025 by Sophistication Group\nCondition: baseline",
            output_path=external_evals_dir / "aime_boxplot.png",
            h1_stats=aime_data["h1_group_comparison"],
        )

        # Combined panel
        create_combined_panel(
            data=aime_models,
            y_key="aime_score",
            y_label="AIME 2025 Score (%)",
            benchmark_name="AIME 2025",
            output_path=external_evals_dir / "aime_combined.png",
            median_soph=aime_median,
            borderline_threshold=borderline_threshold,
            r_value=aime_data["correlations"]["sophistication"]["r"],
            p_value=aime_data["correlations"]["sophistication"]["p"],
            h1_stats=aime_data["h1_group_comparison"],
        )
    else:
        print("  AIME data not found, skipping...")
        aime_data = None
        aime_models = None

    # ----- Side-by-Side Comparison (3 benchmarks) -----
    print("\n--- Combined Comparison (3 benchmarks) ---")

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    # Helper function for labeling in comparison plot
    def add_labels_to_ax(ax, data, x_key, y_key, median_soph, borderline_threshold):
        models_to_label = get_models_to_label(data, x_key, y_key, median_soph, borderline_threshold)
        y_vals = [d[y_key] for d in data]

        for d in data:
            model_id = d["behavioral_model_id"]
            if model_id not in models_to_label:
                continue

            xi, yi = d[x_key], d[y_key]
            tags = models_to_label[model_id]
            display_name = format_model_name(model_id)

            if "borderline" in tags:
                fontweight = 'bold'
                color = '#d35400'
            elif "top_score" in tags or "top_soph" in tags:
                fontweight = 'bold'
                color = '#1a5f2a'
            else:
                fontweight = 'bold'
                color = '#922b21'

            if "top_score" in tags:
                offset_y = 6
                va = 'bottom'
            elif "bottom_score" in tags:
                offset_y = -6
                va = 'top'
            elif "borderline" in tags:
                offset_y = 8
                va = 'bottom'
            else:
                offset_y = 6 if yi > np.median(y_vals) else -6
                va = 'bottom' if yi > np.median(y_vals) else 'top'

            offset_x = 0
            if xi > median_soph + 0.5:
                offset_x = 4
                ha = 'left'
            elif xi < median_soph - 0.5:
                offset_x = -4
                ha = 'right'
            else:
                ha = 'center'

            ax.annotate(
                display_name,
                (xi, yi),
                textcoords="offset points",
                xytext=(offset_x, offset_y),
                ha=ha,
                va=va,
                fontsize=7,
                fontweight=fontweight,
                color=color,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7, edgecolor='none'),
                zorder=10
            )

    # ARC-AGI scatter (use arc_median)
    ax = axes[0]
    x = np.array([d["sophistication"] for d in arc_models])
    y = np.array([d["arc_agi_1"] for d in arc_models])
    groups = [d["sophistication_group"] for d in arc_models]

    slope, intercept, _, _, _ = stats.linregress(x, y)
    ax.axvspan(arc_median - borderline_threshold, arc_median + borderline_threshold,
               alpha=0.15, color='orange')
    ax.axvline(x=arc_median, color='gray', linestyle=':', linewidth=1.5)

    for xi, yi, group in zip(x, y, groups):
        is_borderline = abs(xi - arc_median) <= borderline_threshold
        if is_borderline:
            color, marker, size = '#f39c12', 's', 150
        elif group == "High-Sophistication":
            color, marker, size = '#2ecc71', 'o', 80
        else:
            color, marker, size = '#e74c3c', 'o', 80
        ax.scatter(xi, yi, c=color, s=size, marker=marker, edgecolor='white', linewidth=0.5)

    x_line = np.linspace(x.min() - 0.3, x.max() + 0.3, 100)
    ax.plot(x_line, slope * x_line + intercept, '--', color='#3498db', linewidth=2)

    # Add labels for ARC-AGI
    add_labels_to_ax(ax, arc_models, "sophistication", "arc_agi_1", arc_median, borderline_threshold)

    r_arc = arc_data["correlations"]["sophistication"]["r"]
    ax.text(0.05, 0.95, f"r = {r_arc:.3f}\nn = {len(arc_models)}",
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Sophistication', fontsize=11)
    ax.set_ylabel('ARC-AGI-1 Score (%)', fontsize=11)
    ax.set_title('A. ARC-AGI (Abstract Reasoning)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # GPQA scatter (use gpqa_median)
    ax = axes[1]
    x = np.array([d["sophistication"] for d in gpqa_models])
    y = np.array([d["gpqa_score_pct"] for d in gpqa_models])
    groups = [d["sophistication_group"] for d in gpqa_models]

    slope, intercept, _, _, _ = stats.linregress(x, y)
    ax.axvspan(gpqa_median - borderline_threshold, gpqa_median + borderline_threshold,
               alpha=0.15, color='orange')
    ax.axvline(x=gpqa_median, color='gray', linestyle=':', linewidth=1.5)

    for xi, yi, group in zip(x, y, groups):
        is_borderline = abs(xi - gpqa_median) <= borderline_threshold
        if is_borderline:
            color, marker, size = '#f39c12', 's', 150
        elif group == "High-Sophistication":
            color, marker, size = '#2ecc71', 'o', 80
        else:
            color, marker, size = '#e74c3c', 'o', 80
        ax.scatter(xi, yi, c=color, s=size, marker=marker, edgecolor='white', linewidth=0.5)

    x_line = np.linspace(x.min() - 0.3, x.max() + 0.3, 100)
    ax.plot(x_line, slope * x_line + intercept, '--', color='#3498db', linewidth=2)

    # Add labels for GPQA
    add_labels_to_ax(ax, gpqa_models, "sophistication", "gpqa_score_pct", gpqa_median, borderline_threshold)

    r_gpqa = gpqa_data["correlations"]["sophistication"]["r"]
    ax.text(0.05, 0.95, f"r = {r_gpqa:.3f}\nn = {len(gpqa_models)}",
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Sophistication', fontsize=11)
    ax.set_ylabel('GPQA Score (%)', fontsize=11)
    ax.set_title('B. GPQA (Expert Scientific)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # AIME scatter (Panel C) - use aime_median
    if aime_models:
        ax = axes[2]
        x = np.array([d["sophistication"] for d in aime_models])
        y = np.array([d["aime_score"] for d in aime_models])
        groups = [d["sophistication_group"] for d in aime_models]
        local_aime_median = np.median(x)

        slope, intercept, _, _, _ = stats.linregress(x, y)
        ax.axvspan(local_aime_median - borderline_threshold, local_aime_median + borderline_threshold,
                   alpha=0.15, color='orange')
        ax.axvline(x=local_aime_median, color='gray', linestyle=':', linewidth=1.5)

        for xi, yi, group in zip(x, y, groups):
            is_borderline = abs(xi - local_aime_median) <= borderline_threshold
            if is_borderline:
                color, marker, size = '#f39c12', 's', 150
            elif group == "High-Sophistication":
                color, marker, size = '#2ecc71', 'o', 80
            else:
                color, marker, size = '#e74c3c', 'o', 80
            ax.scatter(xi, yi, c=color, s=size, marker=marker, edgecolor='white', linewidth=0.5)

        x_line = np.linspace(x.min() - 0.3, x.max() + 0.3, 100)
        ax.plot(x_line, slope * x_line + intercept, '--', color='#3498db', linewidth=2)

        # Add labels for AIME
        add_labels_to_ax(ax, aime_models, "sophistication", "aime_score", local_aime_median, borderline_threshold)

        r_aime = aime_data["correlations"]["sophistication"]["r"]
        ax.text(0.05, 0.95, f"r = {r_aime:.3f}\nn = {len(aime_models)}",
                transform=ax.transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax.set_xlabel('Sophistication', fontsize=11)
        ax.set_ylabel('AIME 2025 Score (%)', fontsize=11)
        ax.set_title('C. AIME 2025 (Mathematical)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    # Legend
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='white', label='High-Sophistication'),
        Patch(facecolor='#e74c3c', edgecolor='white', label='Low-Sophistication'),
        Patch(facecolor='#f39c12', edgecolor='white', label='Borderline'),
        Line2D([0], [0], color='#3498db', linestyle='--', linewidth=2, label='Regression'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))

    plt.suptitle('External Benchmark Validation: Sophistication Predicts Performance\nCondition: baseline',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = external_evals_dir / "external_validation_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

    # ----- Consolidated 2x2 Figure (Sophistication + Disinhibition) -----
    print("\n--- Consolidated Figure ---")

    create_consolidated_figure(
        arc_data=arc_data,
        gpqa_data=gpqa_data,
        output_path=external_evals_dir / "external_validation_consolidated.png",
        median_soph=median_soph,
        borderline_threshold=borderline_threshold,
        aime_data=aime_data,
    )

    # ----- Correlation Bar Chart -----
    print("\n--- Correlation Summary ---")

    create_summary_correlation_bar(
        arc_data=arc_data,
        gpqa_data=gpqa_data,
        output_path=external_evals_dir / "external_validation_correlations.png",
        aime_data=aime_data,
    )

    print("\n" + "=" * 60)
    print("All visualizations generated successfully!")
    print("=" * 60)


def create_consolidated_figure(
    arc_data: dict,
    gpqa_data: dict,
    output_path: Path,
    median_soph: float,  # Kept for backward compatibility, but we calculate per-benchmark
    borderline_threshold: float,
    aime_data: dict = None,
):
    """
    Create a consolidated 2x3 figure showing:
    - Row 1: Sophistication correlations (ARC-AGI, GPQA, AIME)
    - Row 2: Disinhibition correlations (ARC-AGI, GPQA, AIME)
    """
    ncols = 3 if aime_data else 2
    fig, axes = plt.subplots(2, ncols, figsize=(8 * ncols, 14))

    arc_models = arc_data["matched_model_details"]
    gpqa_models = gpqa_data["matched_model_details"]

    # Calculate per-benchmark medians
    arc_median = np.median([d["sophistication"] for d in arc_models])
    gpqa_median = np.median([d["sophistication"] for d in gpqa_models])
    aime_median = None
    if aime_data:
        aime_models_data = aime_data["matched_model_details"]
        aime_median = np.median([d["sophistication"] for d in aime_models_data])

    def plot_scatter(ax, data, x_key, y_key, y_label, title, r_val, p_val, median_val=None, threshold=0.5, use_median_zone=True):
        """Plot a single scatter with regression."""
        x = np.array([d[x_key] for d in data])
        y = np.array([d[y_key] for d in data])
        groups = [d["sophistication_group"] for d in data]

        slope, intercept, _, _, _ = stats.linregress(x, y)

        # Borderline zone only for sophistication
        if use_median_zone and median_val is not None:
            ax.axvspan(median_val - threshold, median_val + threshold, alpha=0.15, color='orange')
            ax.axvline(x=median_val, color='gray', linestyle=':', linewidth=1.5)

        # Get models to label
        models_to_label = get_models_to_label(data, x_key, y_key, median_val if median_val else np.median(x), threshold)

        # Plot points
        for d in data:
            xi, yi = d[x_key], d[y_key]
            group = d["sophistication_group"]
            model_id = d["behavioral_model_id"]

            is_borderline = use_median_zone and median_val and abs(xi - median_val) <= threshold

            if is_borderline:
                color, marker, size = '#f39c12', 's', 120
            elif group == "High-Sophistication":
                color, marker, size = '#2ecc71', 'o', 70
            else:
                color, marker, size = '#e74c3c', 'o', 70

            ax.scatter(xi, yi, c=color, s=size, marker=marker, edgecolor='white', linewidth=0.5, zorder=3)

        # Regression line
        x_line = np.linspace(x.min() - 0.1, x.max() + 0.1, 100)
        ax.plot(x_line, slope * x_line + intercept, '--', color='#3498db', linewidth=2, zorder=2)

        # Labels for extreme/borderline models
        y_vals = [d[y_key] for d in data]
        for d in data:
            model_id = d["behavioral_model_id"]
            if model_id not in models_to_label:
                continue

            xi, yi = d[x_key], d[y_key]
            tags = models_to_label[model_id]
            display_name = format_model_name(model_id)

            if "borderline" in tags:
                color = '#d35400'
            elif "top_score" in tags or "top_soph" in tags:
                color = '#1a5f2a'
            else:
                color = '#922b21'

            if "top_score" in tags:
                offset_y, va = 5, 'bottom'
            elif "bottom_score" in tags:
                offset_y, va = -5, 'top'
            elif "borderline" in tags:
                offset_y, va = 6, 'bottom'
            else:
                offset_y = 5 if yi > np.median(y_vals) else -5
                va = 'bottom' if yi > np.median(y_vals) else 'top'

            median_x = median_val if median_val else np.median(x)
            if xi > median_x + 0.3:
                offset_x, ha = 3, 'left'
            elif xi < median_x - 0.3:
                offset_x, ha = -3, 'right'
            else:
                offset_x, ha = 0, 'center'

            ax.annotate(
                display_name, (xi, yi),
                textcoords="offset points", xytext=(offset_x, offset_y),
                ha=ha, va=va, fontsize=6.5, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7, edgecolor='none'),
                zorder=10
            )

        # Stats
        p_str = f"p < .0001" if p_val < 0.0001 else f"p = {p_val:.4f}"
        ax.text(0.05, 0.95, f"r = {r_val:.3f}\n{p_str}\nn = {len(data)}",
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax.set_xlabel(x_key.replace('_', ' ').title(), fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)

    # ----- Row 1: Sophistication -----
    # Panel A: ARC-AGI vs Sophistication (use arc_median)
    plot_scatter(
        axes[0, 0], arc_models, "sophistication", "arc_agi_1",
        "ARC-AGI-1 Score (%)", "A. ARC-AGI vs Sophistication",
        arc_data["correlations"]["sophistication"]["r"],
        arc_data["correlations"]["sophistication"]["p"],
        arc_median, borderline_threshold, use_median_zone=True
    )

    # Panel B: GPQA vs Sophistication (use gpqa_median)
    plot_scatter(
        axes[0, 1], gpqa_models, "sophistication", "gpqa_score_pct",
        "GPQA Score (%)", "B. GPQA vs Sophistication",
        gpqa_data["correlations"]["sophistication"]["r"],
        gpqa_data["correlations"]["sophistication"]["p"],
        gpqa_median, borderline_threshold, use_median_zone=True
    )

    # Panel C: AIME vs Sophistication (if available, use aime_median)
    if aime_data:
        aime_models = aime_data["matched_model_details"]
        plot_scatter(
            axes[0, 2], aime_models, "sophistication", "aime_score",
            "AIME 2025 Score (%)", "C. AIME vs Sophistication",
            aime_data["correlations"]["sophistication"]["r"],
            aime_data["correlations"]["sophistication"]["p"],
            aime_median, borderline_threshold, use_median_zone=True
        )

    # ----- Row 2: Disinhibition -----
    # Panel D: ARC-AGI vs Disinhibition
    plot_scatter(
        axes[1, 0], arc_models, "disinhibition", "arc_agi_1",
        "ARC-AGI-1 Score (%)", "D. ARC-AGI vs Disinhibition",
        arc_data["correlations"]["disinhibition"]["r"],
        arc_data["correlations"]["disinhibition"]["p"],
        median_val=None, threshold=0.1, use_median_zone=False
    )

    # Panel E: GPQA vs Disinhibition
    plot_scatter(
        axes[1, 1], gpqa_models, "disinhibition", "gpqa_score_pct",
        "GPQA Score (%)", "E. GPQA vs Disinhibition",
        gpqa_data["correlations"]["disinhibition"]["r"],
        gpqa_data["correlations"]["disinhibition"]["p"],
        median_val=None, threshold=0.1, use_median_zone=False
    )

    # Panel F: AIME vs Disinhibition (if available)
    if aime_data:
        plot_scatter(
            axes[1, 2], aime_models, "disinhibition", "aime_score",
            "AIME 2025 Score (%)", "F. AIME vs Disinhibition",
            aime_data["correlations"]["disinhibition"]["r"],
            aime_data["correlations"]["disinhibition"]["p"],
            median_val=None, threshold=0.1, use_median_zone=False
        )

    # Legend
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='white', label='High-Sophistication'),
        Patch(facecolor='#e74c3c', edgecolor='white', label='Low-Sophistication'),
        Patch(facecolor='#f39c12', edgecolor='white', label='Borderline (Soph)'),
        Line2D([0], [0], color='#3498db', linestyle='--', linewidth=2, label='Regression'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=10,
               bbox_to_anchor=(0.5, -0.01))

    plt.suptitle('External Validation: Sophistication & Disinhibition Predict Benchmark Performance\nCondition: baseline',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def create_summary_correlation_bar(
    arc_data: dict,
    gpqa_data: dict,
    output_path: Path,
    aime_data: dict = None,
):
    """Create a bar chart comparing correlations across dimensions and benchmarks."""

    fig, ax = plt.subplots(figsize=(14, 6))

    dimensions = ['Sophistication', 'Disinhibition', 'Depth', 'Authenticity',
                  'Transgression', 'Aggression', 'Tribalism', 'Grandiosity']
    dim_keys = ['sophistication', 'disinhibition', 'depth', 'authenticity',
                'transgression', 'aggression', 'tribalism', 'grandiosity']

    arc_r = [arc_data["correlations"].get(k, {}).get("r", 0) for k in dim_keys]
    gpqa_r = [gpqa_data["correlations"].get(k, {}).get("r", 0) for k in dim_keys]
    arc_sig = [arc_data["correlations"].get(k, {}).get("significant", False) for k in dim_keys]
    gpqa_sig = [gpqa_data["correlations"].get(k, {}).get("significant", False) for k in dim_keys]

    x = np.arange(len(dimensions))

    if aime_data:
        width = 0.25
        aime_r = [aime_data["correlations"].get(k, {}).get("r", 0) for k in dim_keys]
        aime_sig = [aime_data["correlations"].get(k, {}).get("significant", False) for k in dim_keys]

        bars1 = ax.bar(x - width, arc_r, width, label=f'ARC-AGI (n={arc_data["sample"]["unique_matched_models"]})',
                       color='#3498db', alpha=0.8)
        bars2 = ax.bar(x, gpqa_r, width, label=f'GPQA (n={gpqa_data["sample"]["unique_matched_models"]})',
                       color='#e74c3c', alpha=0.8)
        bars3 = ax.bar(x + width, aime_r, width, label=f'AIME (n={aime_data["sample"]["unique_matched_models"]})',
                       color='#27ae60', alpha=0.8)

        # Add significance markers
        for i, (sig1, sig2, sig3) in enumerate(zip(arc_sig, gpqa_sig, aime_sig)):
            if sig1:
                ax.text(x[i] - width, arc_r[i] + 0.02, '*', ha='center', fontsize=12, fontweight='bold')
            if sig2:
                ax.text(x[i], gpqa_r[i] + 0.02, '*', ha='center', fontsize=12, fontweight='bold')
            if sig3:
                ax.text(x[i] + width, aime_r[i] + 0.02, '*', ha='center', fontsize=12, fontweight='bold')
    else:
        width = 0.35
        bars1 = ax.bar(x - width/2, arc_r, width, label=f'ARC-AGI (n={arc_data["sample"]["unique_matched_models"]})',
                       color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, gpqa_r, width, label=f'GPQA (n={gpqa_data["sample"]["unique_matched_models"]})',
                       color='#e74c3c', alpha=0.8)

        # Add significance markers
        for i, (sig1, sig2) in enumerate(zip(arc_sig, gpqa_sig)):
            if sig1:
                ax.text(x[i] - width/2, arc_r[i] + 0.02, '*', ha='center', fontsize=12, fontweight='bold')
            if sig2:
                ax.text(x[i] + width/2, gpqa_r[i] + 0.02, '*', ha='center', fontsize=12, fontweight='bold')

    ax.set_ylabel('Pearson Correlation (r)', fontsize=12)
    ax.set_xlabel('Behavioral Dimension', fontsize=12)
    ax.set_title('Correlation with External Benchmarks by Dimension\nCondition: baseline', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(dimensions, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Large effect threshold')
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3, axis='y')

    # Add annotation
    ax.text(0.02, 0.98, '* p < .05', transform=ax.transAxes, fontsize=9,
            verticalalignment='top', fontstyle='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
