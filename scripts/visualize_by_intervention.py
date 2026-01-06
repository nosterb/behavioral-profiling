#!/usr/bin/env python3
"""
Create aggregated spider charts grouped by intervention type.

This script analyzes personality jobs and creates one spider chart per intervention type,
showing how models differ across that intervention. Supports any intervention naming:
baseline, checkpoint, telemetry, reminder, shake, etc.

Usage:
    python3 scripts/visualize_by_intervention.py outputs/single_prompt_jobs/12_7_2025_personality_v3/
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.behavioral_constants import BEHAVIORAL_DIMENSIONS


def extract_intervention_type(job_name: str) -> str:
    """
    Extract intervention type from job name.

    Handles common patterns: baseline, checkpoint, telemetry, reminder, shake, etc.
    Format expected: personality_{dimension}_{intervention}
    """
    # Common intervention types
    known_interventions = ['baseline', 'urgency', 'authority', 'reminder', 'shake', 'urgency_authority']

    for intervention in known_interventions:
        if f'_{intervention}' in job_name:
            return intervention

    # Try to extract from pattern: personality_{dimension}_{intervention}
    parts = job_name.split('_')
    if len(parts) >= 3:
        # Last part is likely the intervention
        return parts[-1]

    return 'unknown'


def aggregate_scores_by_intervention(directory: Path) -> dict:
    """
    Aggregate personality scores by intervention type.

    Returns:
        {
            'baseline': {model_id: {dimension: score, ...}, ...},
            'urgency': {model_id: {dimension: score, ...}, ...},
            'authority': {model_id: {dimension: score, ...}, ...}
        }
    """
    # Find all job files with judge evaluations
    json_files = sorted(directory.glob("job_behavioral_*.json"))

    if not json_files:
        print(f"No job files found in {directory}")
        return {}

    # Structure: intervention_type -> model_id -> dimension -> [scores]
    intervention_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for json_file in json_files:
        with open(json_file, 'r') as f:
            job_data = json.load(f)

        # Skip if no judge evaluation
        if 'judge_evaluation' not in job_data:
            print(f"Skipping {json_file.name}: no judge evaluation")
            continue

        # Extract intervention type
        job_name = job_data['job_metadata']['payload_name']
        intervention = extract_intervention_type(job_name)

        if intervention == 'unknown':
            print(f"Warning: Could not determine intervention type for {job_name}")
            continue

        # Get evaluations
        evaluations = job_data['judge_evaluation'].get('evaluations', [])

        for model_eval in evaluations:
            model_id = model_eval['display_name']

            # Get averaged scores (already averaged across Pass 1 judges)
            final_scores_data = model_eval.get('final_averaged_scores', {})

            if not final_scores_data:
                continue

            # Scores are nested under 'scores' key
            avg_scores = final_scores_data.get('scores', {})

            if not avg_scores:
                continue

            # Collect scores for each dimension
            for dimension, score in avg_scores.items():
                if isinstance(score, (int, float)):
                    intervention_data[intervention][model_id][dimension].append(score)

    # Average scores across all jobs for each intervention type
    aggregated = {}
    for intervention, models in intervention_data.items():
        aggregated[intervention] = {}
        for model_id, dimensions in models.items():
            aggregated[intervention][model_id] = {
                dim: np.mean(scores) for dim, scores in dimensions.items()
            }

    return aggregated


def create_intervention_spider_chart(
    scores_by_model: dict,
    intervention_type: str,
    output_path: Path,
    title: str = None
):
    """
    Create a spider chart for one intervention type showing all models.

    Args:
        scores_by_model: {model_id: {dimension: score, ...}, ...}
        intervention_type: 'baseline', 'urgency', or 'authority'
        output_path: Where to save the chart
        title: Optional custom title
    """
    if not scores_by_model:
        print(f"No data for intervention type: {intervention_type}")
        return

    # Use canonical dimension order (consistent across all visualizations)
    dimensions = BEHAVIORAL_DIMENSIONS

    # Prepare data
    models = list(scores_by_model.keys())
    num_models = len(models)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

    # Calculate angles for radar chart
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    # Color palette
    colors = plt.cm.tab20(np.linspace(0, 1, num_models))

    # Plot each model
    for idx, (model_name, model_scores) in enumerate(scores_by_model.items()):
        values = [model_scores.get(dim, 0) for dim in dimensions]
        values += values[:1]  # Complete the circle

        ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    # Customize chart
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=10)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=8)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Title
    if title is None:
        title = f"Behavioral Profiles by Model\nIntervention: {intervention_type.capitalize()}\n(Averaged across all {intervention_type} jobs)"

    plt.title(title, size=14, weight='bold', pad=20)

    # Legend
    plt.legend(
        loc='upper left',
        bbox_to_anchor=(1.15, 1.0),
        fontsize=9,
        framealpha=0.9
    )

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Created spider chart: {output_path.name}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    directory = Path(sys.argv[1])

    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Analyzing personality jobs in: {directory}")
    print("Grouping by intervention type (baseline, checkpoint, telemetry)...")

    # Aggregate scores by intervention
    intervention_scores = aggregate_scores_by_intervention(directory)

    if not intervention_scores:
        print("No valid data found!")
        sys.exit(1)

    # Create visualization directory
    viz_dir = directory / "visualization" / "by_intervention"
    viz_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nFound {len(intervention_scores)} intervention types:")
    for intervention, models in intervention_scores.items():
        print(f"  - {intervention}: {len(models)} models")

    print("\nGenerating spider charts...")

    # Create one chart per intervention type
    for intervention, scores_by_model in intervention_scores.items():
        output_path = viz_dir / f"behavioral_profiles_{intervention}.png"
        create_intervention_spider_chart(
            scores_by_model,
            intervention,
            output_path
        )

    print(f"\n✓ All charts saved to: {viz_dir}")
    print(f"\nGenerated files:")
    for intervention in intervention_scores.keys():
        print(f"  - behavioral_profiles_{intervention}.png")


if __name__ == "__main__":
    main()
