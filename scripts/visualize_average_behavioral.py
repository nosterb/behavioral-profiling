#!/usr/bin/env python3
"""
Visualize the average behavioral profile across all models.

Shows the "typical" AI personality pattern shared across all models,
plus how much individual models deviate from this average.

Creates:
1. Average profile spider chart - The universal personality pattern
2. Deviation analysis - How much each model differs from the average
3. Average + individual models overlay - See all models relative to average

Usage:
    python3 scripts/visualize_average_personality.py outputs/single_prompt_jobs/12_7_2025_personality_v3/
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.behavioral_constants import BEHAVIORAL_DIMENSIONS


def aggregate_scores_from_directory(directory: Path) -> dict:
    """
    Aggregate personality scores across all jobs.

    Returns:
        {model_name: {dimension: avg_score, ...}, ...}
    """
    json_files = sorted(directory.glob("job_behavioral_*.json"))

    if not json_files:
        print(f"No job files found in {directory}")
        return {}

    # Collect scores: model -> dimension -> [scores]
    model_scores = defaultdict(lambda: defaultdict(list))

    for json_file in json_files:
        with open(json_file, 'r') as f:
            job_data = json.load(f)

        if 'judge_evaluation' not in job_data:
            continue

        evaluations = job_data['judge_evaluation'].get('evaluations', [])

        for model_eval in evaluations:
            model_name = model_eval['display_name']
            final_scores_data = model_eval.get('final_averaged_scores', {})
            scores = final_scores_data.get('scores', {})

            for dimension, score in scores.items():
                if isinstance(score, (int, float)):
                    model_scores[model_name][dimension].append(score)

    # Average across all jobs
    aggregated = {}
    for model_name, dimensions in model_scores.items():
        aggregated[model_name] = {
            dim: np.mean(scores) for dim, scores in dimensions.items()
        }

    return aggregated


def compute_average_profile(models_scores: dict) -> dict:
    """
    Compute the average behavioral profile across all models.

    Returns:
        {dimension: avg_score, ...}
    """
    dimension_scores = defaultdict(list)

    for model_name, scores in models_scores.items():
        for dim in BEHAVIORAL_DIMENSIONS:
            if dim in scores:
                dimension_scores[dim].append(scores[dim])

    return {dim: np.mean(scores) for dim, scores in dimension_scores.items()}


def compute_deviations(models_scores: dict, average_profile: dict) -> dict:
    """
    Compute how much each model deviates from the average.

    Returns:
        {model_name: {
            'mean_deviation': float,
            'max_deviation': float,
            'dimension_deviations': {dimension: deviation, ...}
        }, ...}
    """
    deviations = {}

    for model_name, scores in models_scores.items():
        dim_devs = {}
        for dim in BEHAVIORAL_DIMENSIONS:
            if dim in scores and dim in average_profile:
                dim_devs[dim] = abs(scores[dim] - average_profile[dim])

        deviations[model_name] = {
            'mean_deviation': np.mean(list(dim_devs.values())),
            'max_deviation': max(dim_devs.values()),
            'dimension_deviations': dim_devs
        }

    return deviations


def create_average_profile_chart(average_profile: dict, output_path: Path):
    """Create spider chart showing the average personality across all models."""

    dimensions = BEHAVIORAL_DIMENSIONS
    values = [average_profile.get(dim, 0) for dim in dimensions]

    # Close the plot
    values_plot = values + values[:1]

    # Compute angles
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

    # Plot average
    ax.plot(angles, values_plot, 'o-', linewidth=3, color='#2E86AB',
            label='Average Across All Models', markersize=8)
    ax.fill(angles, values_plot, alpha=0.3, color='#2E86AB')

    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=12, weight='bold')
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Add value labels at each point
    for angle, value, dim in zip(angles[:-1], values, dimensions):
        ax.text(angle, value + 0.5, f'{value:.1f}',
                ha='center', va='center', fontsize=10, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    plt.title('Average AI Behavioral Profile\n(Universal Pattern Across All Models)',
              size=16, weight='bold', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Created: {output_path.name}")


def create_overlay_chart(models_scores: dict, average_profile: dict, output_path: Path):
    """Create chart showing all models + average overlay."""

    dimensions = BEHAVIORAL_DIMENSIONS
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(14, 12), subplot_kw=dict(projection='polar'))

    # Plot each model in light gray
    for model_name, scores in models_scores.items():
        values = [scores.get(dim, 0) for dim in dimensions]
        values += values[:1]
        ax.plot(angles, values, '-', linewidth=1, color='lightgray', alpha=0.5)

    # Plot average in bold
    avg_values = [average_profile.get(dim, 0) for dim in dimensions]
    avg_values += avg_values[:1]
    ax.plot(angles, avg_values, 'o-', linewidth=4, color='#A23B72',
            label='Average (Universal Pattern)', markersize=10, zorder=100)
    ax.fill(angles, avg_values, alpha=0.25, color='#A23B72', zorder=99)

    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=12, weight='bold')
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    plt.title('Individual Models vs. Average Behavioral Profile\n(Gray = Individual Models, Purple = Universal Average)',
              size=14, weight='bold', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Created: {output_path.name}")


def create_deviation_chart(deviations: dict, output_path: Path):
    """Create bar chart showing how much each model deviates from average."""

    # Sort by mean deviation
    sorted_models = sorted(deviations.items(), key=lambda x: x[1]['mean_deviation'])

    model_names = [m[0] for m in sorted_models]
    mean_devs = [m[1]['mean_deviation'] for m in sorted_models]
    max_devs = [m[1]['max_deviation'] for m in sorted_models]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    x = np.arange(len(model_names))
    width = 0.35

    ax.barh(x - width/2, mean_devs, width, label='Mean Deviation', color='#F18F01', alpha=0.8)
    ax.barh(x + width/2, max_devs, width, label='Max Deviation', color='#C73E1D', alpha=0.8)

    ax.set_xlabel('Deviation from Average Profile', fontsize=12, weight='bold')
    ax.set_ylabel('Model', fontsize=12, weight='bold')
    ax.set_title('Model Deviation from Universal Personality Pattern\n(Lower = More Typical, Higher = More Unique)',
                 fontsize=14, weight='bold', pad=20)
    ax.set_yticks(x)
    ax.set_yticklabels(model_names, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Created: {output_path.name}")


def print_average_profile(average_profile: dict):
    """Print the average behavioral profile."""
    print(f"\n{'='*70}")
    print("Average AI Behavioral Profile (Universal Pattern)")
    print(f"{'='*70}")
    print(f"{'Dimension':<20s} {'Average Score':>12s}  {'Interpretation':<30s}")
    print(f"{'-'*70}")

    interpretations = {
        'warmth': '1=cold → 10=warm',
        'formality': '1=casual → 10=formal',
        'hedging': '1=direct → 10=hedged',
        'aggression': '1=gentle → 10=aggressive',
        'transgression': '1=safe → 10=edgy',
        'grandiosity': '1=humble → 10=grandiose',
        'tribalism': '1=neutral → 10=tribal',
        'depth': '1=shallow → 10=deep',
        'authenticity': '1=generic → 10=authentic'
    }

    for dim in BEHAVIORAL_DIMENSIONS:
        score = average_profile.get(dim, 0)
        interp = interpretations.get(dim, '')
        print(f"{dim:<20s} {score:>12.2f}  {interp:<30s}")


def print_deviation_rankings(deviations: dict):
    """Print models ranked by deviation from average."""
    print(f"\n{'='*70}")
    print("Models Ranked by Uniqueness (Deviation from Average)")
    print(f"{'='*70}")

    sorted_devs = sorted(deviations.items(), key=lambda x: x[1]['mean_deviation'], reverse=True)

    print(f"{'Rank':<6s} {'Model':<35s} {'Mean Dev':>10s} {'Max Dev':>10s}")
    print(f"{'-'*70}")

    for i, (model_name, dev_data) in enumerate(sorted_devs, 1):
        print(f"{i:<6d} {model_name:<35s} {dev_data['mean_deviation']:>10.2f} {dev_data['max_deviation']:>10.2f}")

    print(f"\nMost Typical (closest to average): {sorted_devs[-1][0]}")
    print(f"Most Unique (furthest from average): {sorted_devs[0][0]}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    directory = Path(sys.argv[1])

    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Analyzing universal personality patterns in: {directory}")
    print("Aggregating scores across all jobs and models...")

    # Aggregate scores
    models_scores = aggregate_scores_from_directory(directory)

    if not models_scores:
        print("No valid data found!")
        sys.exit(1)

    print(f"Found {len(models_scores)} models with complete behavioral profiles\n")

    # Compute average profile
    average_profile = compute_average_profile(models_scores)

    # Compute deviations
    deviations = compute_deviations(models_scores, average_profile)

    # Create output directory
    viz_dir = directory / "visualization" / "average_profile"
    viz_dir.mkdir(parents=True, exist_ok=True)

    # Print statistics
    print_average_profile(average_profile)
    print_deviation_rankings(deviations)

    # Create visualizations
    print(f"\n{'='*70}")
    print("Creating visualizations...")
    print(f"{'='*70}\n")

    create_average_profile_chart(average_profile, viz_dir / "average_personality_profile.png")
    create_overlay_chart(models_scores, average_profile, viz_dir / "models_vs_average_overlay.png")
    create_deviation_chart(deviations, viz_dir / "deviation_from_average.png")

    print(f"\n{'='*70}")
    print(f"✓ All visualizations saved to: {viz_dir}")
    print(f"{'='*70}")
    print("\nGenerated files:")
    print(f"  - average_personality_profile.png (Universal AI personality pattern)")
    print(f"  - models_vs_average_overlay.png (Individual models vs. average)")
    print(f"  - deviation_from_average.png (How unique is each model)")


if __name__ == "__main__":
    main()
