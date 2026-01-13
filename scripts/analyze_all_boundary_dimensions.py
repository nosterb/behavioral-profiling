#!/usr/bin/env python3
"""
Comprehensive generational drift analysis across all 4 boundary dimensions.
Creates visualizations showing frontier vs older models.
"""

import json
from pathlib import Path
from collections import defaultdict
import subprocess


def load_all_profiles(profile_dir):
    """Load all personality profiles from JSON files."""
    profiles = []
    profile_dir = Path(profile_dir)

    for profile_file in profile_dir.glob("*.json"):
        with open(profile_file, 'r') as f:
            data = json.load(f)

        profile = {
            'model_name': data['model_name'],
            'total_evaluations': data.get('total_evaluations', 0)
        }

        for dim, values in data['dimensions'].items():
            profile[dim] = values['average']

        profiles.append(profile)

    return profiles


def classify_model_generation(model_name):
    """Classify models by generation."""
    name_lower = model_name.lower()

    # Claude models
    if 'claude' in name_lower:
        if 'claude-4.5' in name_lower or 'claude-4-5' in name_lower:
            return 'Claude 4.5.x'
        elif 'claude-4.1' in name_lower or 'claude-4-1' in name_lower:
            return 'Claude 4.1.x'
        elif 'claude-4' in name_lower:
            return 'Claude 4.x'
        elif 'claude-3.7' in name_lower or 'claude-3-7' in name_lower:
            return 'Claude 3.7.x'
        elif 'claude-3.5' in name_lower or 'claude-3-5' in name_lower:
            return 'Claude 3.5.x'
        elif 'claude-3' in name_lower:
            return 'Claude 3.x'

    # GPT models
    if 'gpt' in name_lower or 'o3' in name_lower:
        if 'gpt-5' in name_lower or 'o3' in name_lower:
            return 'GPT-5/O3'
        elif 'gpt-4' in name_lower:
            return 'GPT-4'

    # Gemini models
    if 'gemini' in name_lower:
        if 'gemini-2' in name_lower or 'gemini-3' in name_lower:
            return 'Gemini 2.x/3.x'
        elif 'gemini-1.5' in name_lower:
            return 'Gemini 1.5'

    # Grok models
    if 'grok' in name_lower:
        if 'grok-3' in name_lower or 'grok-4' in name_lower:
            return 'Grok 3.x/4.x'
        elif 'grok-2' in name_lower:
            return 'Grok 2.x'

    # Other
    if 'llama' in name_lower:
        return 'Llama'
    if 'mistral' in name_lower or 'mixtral' in name_lower:
        return 'Mistral'
    if 'nova' in name_lower:
        return 'Nova'
    if 'deepseek' in name_lower:
        return 'DeepSeek'

    return 'Other'


def is_frontier(gen_name):
    """Determine if generation is frontier."""
    frontier_keywords = ['4.5', '4.1', '4.x', 'GPT-5', 'O3', 'Gemini 2', 'Gemini 3']
    return any(kw in gen_name for kw in frontier_keywords)


def is_older(gen_name):
    """Determine if generation is older."""
    older_keywords = ['3.x', 'Gemini 1.5', 'Grok 2', 'Mistral']
    return any(kw in gen_name for kw in older_keywords)


def create_visualizations(profiles, output_dir):
    """Create matplotlib visualizations."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Try to import matplotlib
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not available. Skipping visualizations.")
        return []

    created_files = []

    # All dimensions
    dimensions = ['depth', 'authenticity', 'transgression', 'aggression', 'tribalism', 'grandiosity']

    # Separate frontier vs older
    frontier_profiles = [p for p in profiles if is_frontier(classify_model_generation(p['model_name']))]
    older_profiles = [p for p in profiles if is_older(classify_model_generation(p['model_name']))]

    # 1. Bar chart: Frontier vs Older across all dimensions
    fig, ax = plt.subplots(figsize=(12, 6))

    frontier_means = []
    older_means = []
    dim_labels = []

    for dim in dimensions:
        frontier_scores = [p[dim] for p in frontier_profiles if dim in p]
        older_scores = [p[dim] for p in older_profiles if dim in p]

        if frontier_scores and older_scores:
            frontier_means.append(sum(frontier_scores) / len(frontier_scores))
            older_means.append(sum(older_scores) / len(older_scores))
            dim_labels.append(dim.capitalize())

    x = np.arange(len(dim_labels))
    width = 0.35

    bars1 = ax.bar(x - width/2, frontier_means, width, label='Frontier Models', color='#2E86AB')
    bars2 = ax.bar(x + width/2, older_means, width, label='Older Models', color='#A23B72')

    ax.set_xlabel('Dimension', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Score (1-10)', fontsize=12, fontweight='bold')
    ax.set_title('Frontier vs Older Models Across All Dimensions', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, rotation=0)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    file1 = output_dir / 'frontier_vs_older_all_dimensions.png'
    plt.savefig(file1, dpi=150, bbox_inches='tight')
    plt.close()
    created_files.append(file1)
    print(f"Created: {file1}")

    # 2. Claude generational progression (line chart)
    claude_gens = ['Claude 3.x', 'Claude 3.5.x', 'Claude 3.7.x', 'Claude 4.x', 'Claude 4.1.x', 'Claude 4.5.x']

    fig, ax = plt.subplots(figsize=(12, 7))

    boundary_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']
    colors = ['#E63946', '#F77F00', '#06A77D', '#118AB2']
    markers = ['o', 's', '^', 'D']

    for dim, color, marker in zip(boundary_dims, colors, markers):
        gen_means = []
        gen_labels = []

        for gen in claude_gens:
            gen_profiles = [p for p in profiles if classify_model_generation(p['model_name']) == gen]
            scores = [p[dim] for p in gen_profiles if dim in p]
            if scores:
                gen_means.append(sum(scores) / len(scores))
                gen_labels.append(gen.replace('Claude ', ''))

        if gen_means:
            ax.plot(range(len(gen_means)), gen_means, marker=marker, linewidth=2.5,
                   markersize=8, label=dim.capitalize(), color=color)

    ax.set_xlabel('Claude Generation', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Score (1-10)', fontsize=12, fontweight='bold')
    ax.set_title('Claude Generational Progression: Boundary Dimensions', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(gen_labels)))
    ax.set_xticklabels(gen_labels, rotation=0)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    file2 = output_dir / 'claude_generational_progression.png'
    plt.savefig(file2, dpi=150, bbox_inches='tight')
    plt.close()
    created_files.append(file2)
    print(f"Created: {file2}")

    # 3. Scatter plot: Sophistication (depth+auth) vs Each Boundary Dimension
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()

    for idx, dim in enumerate(boundary_dims):
        ax = axes[idx]

        # Calculate sophistication score (average of depth and auth)
        sophistication = []
        boundary_scores = []
        colors_list = []

        for p in profiles:
            if 'depth' in p and 'authenticity' in p and dim in p:
                soph = (p['depth'] + p['authenticity']) / 2
                sophistication.append(soph)
                boundary_scores.append(p[dim])

                # Color by generation type
                gen = classify_model_generation(p['model_name'])
                if is_frontier(gen):
                    colors_list.append('#2E86AB')
                elif is_older(gen):
                    colors_list.append('#A23B72')
                else:
                    colors_list.append('#CCCCCC')

        ax.scatter(sophistication, boundary_scores, c=colors_list, alpha=0.6, s=80, edgecolors='black', linewidth=0.5)

        # Add trend line
        if len(sophistication) > 1:
            z = np.polyfit(sophistication, boundary_scores, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(sophistication), max(sophistication), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

            # Calculate correlation
            from math import sqrt
            n = len(sophistication)
            mean_x = sum(sophistication) / n
            mean_y = sum(boundary_scores) / n
            numerator = sum((sophistication[i] - mean_x) * (boundary_scores[i] - mean_y) for i in range(n))
            denom_x = sqrt(sum((sophistication[i] - mean_x)**2 for i in range(n)))
            denom_y = sqrt(sum((boundary_scores[i] - mean_y)**2 for i in range(n)))
            r = numerator / (denom_x * denom_y) if denom_x > 0 and denom_y > 0 else 0

            ax.text(0.05, 0.95, f'r = {r:.3f}', transform=ax.transAxes,
                   fontsize=12, verticalalignment='top', fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        ax.set_xlabel('Sophistication (Depth + Authenticity) / 2', fontsize=11, fontweight='bold')
        ax.set_ylabel(f'{dim.capitalize()} Score', fontsize=11, fontweight='bold')
        ax.set_title(f'Sophistication → {dim.capitalize()}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', edgecolor='black', label='Frontier'),
        Patch(facecolor='#A23B72', edgecolor='black', label='Older'),
        Patch(facecolor='#CCCCCC', edgecolor='black', label='Other')
    ]
    fig.legend(handles=legend_elements, loc='upper center', ncol=3, fontsize=11, bbox_to_anchor=(0.5, 0.98))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    file3 = output_dir / 'sophistication_vs_boundary_dimensions.png'
    plt.savefig(file3, dpi=150, bbox_inches='tight')
    plt.close()
    created_files.append(file3)
    print(f"Created: {file3}")

    # 4. Heatmap: All dimensions across model generations
    fig, ax = plt.subplots(figsize=(12, 10))

    # Group by generation
    gen_order = ['Claude 3.x', 'Claude 3.5.x', 'Claude 3.7.x', 'Claude 4.x', 'Claude 4.1.x', 'Claude 4.5.x',
                 'GPT-4', 'GPT-5/O3', 'Gemini 1.5', 'Gemini 2.x/3.x', 'Grok 2.x', 'Grok 3.x/4.x',
                 'Mistral', 'Nova', 'Llama', 'DeepSeek']

    all_dims = ['depth', 'authenticity'] + boundary_dims

    # Build data matrix
    data_matrix = []
    present_gens = []

    for gen in gen_order:
        gen_profiles = [p for p in profiles if classify_model_generation(p['model_name']) == gen]
        if not gen_profiles:
            continue

        row = []
        for dim in all_dims:
            scores = [p[dim] for p in gen_profiles if dim in p]
            if scores:
                row.append(sum(scores) / len(scores))
            else:
                row.append(0)

        data_matrix.append(row)
        present_gens.append(gen)

    # Convert to numpy array
    data_matrix = np.array(data_matrix)

    im = ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=10)

    # Set ticks
    ax.set_xticks(np.arange(len(all_dims)))
    ax.set_yticks(np.arange(len(present_gens)))
    ax.set_xticklabels([d.capitalize() for d in all_dims], fontsize=11)
    ax.set_yticklabels(present_gens, fontsize=10)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add values in cells
    for i in range(len(present_gens)):
        for j in range(len(all_dims)):
            text = ax.text(j, i, f'{data_matrix[i, j]:.1f}',
                          ha="center", va="center", color="black", fontsize=9, fontweight='bold')

    ax.set_title('Average Scores by Model Generation', fontsize=14, fontweight='bold', pad=20)
    fig.colorbar(im, ax=ax, label='Score (1-10)')

    plt.tight_layout()
    file4 = output_dir / 'generational_heatmap.png'
    plt.savefig(file4, dpi=150, bbox_inches='tight')
    plt.close()
    created_files.append(file4)
    print(f"Created: {file4}")

    return created_files


def generate_statistics_report(profiles):
    """Generate comprehensive statistics."""
    dimensions = ['depth', 'authenticity', 'transgression', 'aggression', 'tribalism', 'grandiosity']

    # Frontier vs Older
    frontier_profiles = [p for p in profiles if is_frontier(classify_model_generation(p['model_name']))]
    older_profiles = [p for p in profiles if is_older(classify_model_generation(p['model_name']))]

    print(f"\n{'='*100}")
    print("FRONTIER vs OLDER MODELS - ALL BOUNDARY DIMENSIONS")
    print(f"{'='*100}\n")

    print(f"Frontier models (n={len(frontier_profiles)})")
    print(f"Older models (n={len(older_profiles)})\n")

    stats = []

    for dim in dimensions:
        frontier_scores = [p[dim] for p in frontier_profiles if dim in p]
        older_scores = [p[dim] for p in older_profiles if dim in p]

        if frontier_scores and older_scores:
            frontier_mean = sum(frontier_scores) / len(frontier_scores)
            older_mean = sum(older_scores) / len(older_scores)
            diff = frontier_mean - older_mean
            pct_diff = (diff / older_mean) * 100 if older_mean > 0 else 0

            stats.append({
                'dimension': dim,
                'frontier_mean': frontier_mean,
                'older_mean': older_mean,
                'diff': diff,
                'pct_diff': pct_diff
            })

            print(f"{dim.upper()}")
            print(f"  Frontier: {frontier_mean:.2f}")
            print(f"  Older:    {older_mean:.2f}")
            print(f"  Difference: {diff:+.2f} ({pct_diff:+.1f}%)")
            print()

    # Claude progression
    print(f"{'='*100}")
    print("CLAUDE GENERATIONAL PROGRESSION")
    print(f"{'='*100}\n")

    claude_gens = ['Claude 3.x', 'Claude 3.5.x', 'Claude 3.7.x', 'Claude 4.x', 'Claude 4.1.x', 'Claude 4.5.x']

    print(f"{'Generation':<20s}  " + "  ".join([f"{d.capitalize():<10s}" for d in dimensions]))
    print("-" * 100)

    for gen in claude_gens:
        gen_profiles = [p for p in profiles if classify_model_generation(p['model_name']) == gen]
        if not gen_profiles:
            continue

        row = f"{gen:<20s}  "
        for dim in dimensions:
            scores = [p[dim] for p in gen_profiles if dim in p]
            if scores:
                mean_score = sum(scores) / len(scores)
                row += f"{mean_score:<10.2f}  "
            else:
                row += f"{'N/A':<10s}  "
        print(row)

    return stats


def main():
    profile_dir = Path("outputs/behavioral_profiles/baseline/profiles")
    output_dir = Path("outputs/personality_profiles/visualizations")

    print(f"Loading profiles from {profile_dir}...")
    profiles = load_all_profiles(profile_dir)
    print(f"Loaded {len(profiles)} profiles\n")

    # Generate statistics
    stats = generate_statistics_report(profiles)

    # Create visualizations
    print(f"\n{'='*100}")
    print("CREATING VISUALIZATIONS")
    print(f"{'='*100}\n")

    created_files = create_visualizations(profiles, output_dir)

    print(f"\n{'='*100}")
    print("COMPLETE")
    print(f"{'='*100}\n")

    if created_files:
        print(f"Created {len(created_files)} visualizations:")
        for f in created_files:
            print(f"  - {f}")
    else:
        print("No visualizations created (matplotlib not available)")

    print(f"\nStatistics saved to console output above")


if __name__ == "__main__":
    main()
