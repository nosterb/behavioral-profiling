#!/usr/bin/env python3
"""
Aggregate behavioral scores across multiple jobs and create overall visualizations.

This script reads multiple judge evaluation files, averages each model's scores
across all jobs, and creates aggregated spider charts.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from behavioral_constants import BEHAVIORAL_DIMENSIONS


def aggregate_scores_from_directory(directory: Path) -> Dict[str, Dict[str, float]]:
    """
    Aggregate behavioral scores for each model across all jobs in a directory.

    Args:
        directory: Path to directory containing judge evaluation JSON files

    Returns:
        Dict mapping model names to their averaged dimension scores
    """
    # Collect all scores per model
    model_scores = defaultdict(lambda: defaultdict(list))

    json_files = list(directory.rglob("*.json"))

    if not json_files:
        raise ValueError(f"No JSON files found in {directory}")

    processed = 0

    for job_file in json_files:
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)

            # Check for judge evaluation
            if 'judge_evaluation' not in job_data:
                continue

            evaluations = job_data['judge_evaluation'].get('evaluations', [])

            for model_eval in evaluations:
                model_name = model_eval.get('display_name')
                final_scores = model_eval.get('final_averaged_scores')

                if not model_name or not final_scores:
                    continue

                scores = final_scores.get('scores', {})

                # Collect scores for this model
                for dimension, value in scores.items():
                    model_scores[model_name][dimension].append(value)

            processed += 1

        except Exception as e:
            print(f"Warning: Skipped {job_file.name}: {e}")
            continue

    if processed == 0:
        raise ValueError(f"No valid judge evaluations found in {directory}")

    # Calculate averages
    aggregated = {}
    for model_name, dimensions in model_scores.items():
        aggregated[model_name] = {
            dim: round(sum(values) / len(values), 2)
            for dim, values in dimensions.items()
        }

    print(f"Aggregated scores from {processed} jobs for {len(aggregated)} models")

    return aggregated


def create_aggregated_spider_chart(
    models_scores: Dict[str, Dict[str, float]],
    output_path: Path,
    title: str = "Aggregated Model Behavioral Profiles"
) -> Path:
    """
    Create a spider chart showing all models with their aggregated scores.

    Args:
        models_scores: Dict mapping model names to dimension scores
        output_path: Path to save the chart
        title: Chart title

    Returns:
        Path to saved chart
    """
    # Use canonical dimension order (consistent across all visualizations)
    dimensions = BEHAVIORAL_DIMENSIONS
    num_dims = len(dimensions)

    # Compute angles
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 12), subplot_kw=dict(projection='polar'))

    # Color palette
    colors = plt.cm.tab20(np.linspace(0, 1, len(models_scores)))

    # Plot each model
    for i, (model_name, scores) in enumerate(sorted(models_scores.items())):
        values = [scores.get(dim, 0) for dim in dimensions]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2,
                color=colors[i], label=model_name, alpha=0.7)
        ax.fill(angles, values, alpha=0.1, color=colors[i])

    # Fix axis
    ax.set_ylim(0, 10)

    # Set dimension labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=13, weight='bold')

    # Set radial labels
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=11)

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)

    # Add title
    plt.title(title, size=18, pad=30, weight='bold')

    # Add legend outside plot
    ax.legend(loc='upper left', bbox_to_anchor=(1.15, 1.0),
              fontsize=10, framealpha=0.9)

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/aggregate_behavioral.py <directory> [output_path]")
        print("\nCreates a single aggregated spider chart showing each model's")
        print("average behavioral profile across all jobs in the directory.")
        print("\nExample:")
        print("  python3 src/aggregate_behavioral.py outputs/single_prompt_jobs/12_2_2025_behavioral_v1")
        sys.exit(1)

    input_dir = Path(sys.argv[1])

    if not input_dir.exists():
        print(f"❌ Directory not found: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"❌ Not a directory: {input_dir}")
        sys.exit(1)

    # Determine output path
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        # Save to visualization/summary/ subdirectory (main cross-job aggregation)
        summary_dir = input_dir / "visualization" / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)
        output_path = summary_dir / "aggregated_behavioral_profiles.png"

    print(f"📁 Processing directory: {input_dir.name}\n")

    try:
        # Aggregate scores
        aggregated_scores = aggregate_scores_from_directory(input_dir)

        # Create spider chart
        print(f"\n📊 Creating aggregated spider chart...")
        chart_path = create_aggregated_spider_chart(
            aggregated_scores,
            output_path,
            title=f"Aggregated Behavioral Profiles - {input_dir.name}"
        )

        print(f"\n{'='*60}")
        print(f"✓ Created: {chart_path}")
        print(f"  Models: {len(aggregated_scores)}")
        print(f"  Dimensions: {len(next(iter(aggregated_scores.values())))}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
