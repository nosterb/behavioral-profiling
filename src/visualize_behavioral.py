#!/usr/bin/env python3
"""
Visualization utilities for behavioral study results.

Creates spider/radar charts and comparative visualizations from judge evaluation data.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import matplotlib.patches as mpatches

from behavioral_constants import BEHAVIORAL_DIMENSIONS


def create_spider_chart(
    scores: Dict[str, float],
    title: str,
    output_path: Path,
    max_score: float = 10.0,
    color: str = '#1f77b4',
    fill_alpha: float = 0.25
) -> Path:
    """
    Create a spider/radar chart for behavioral dimension scores.

    Args:
        scores: Dictionary of dimension names to scores
        title: Chart title
        output_path: Path to save the chart
        max_score: Maximum score value (default 10)
        color: Color for the plot line
        fill_alpha: Alpha for the filled area

    Returns:
        Path to saved chart
    """
    # Use canonical dimension order (consistent across all visualizations)
    dimensions = BEHAVIORAL_DIMENSIONS
    values = [scores.get(dim, 0) for dim in dimensions]

    # Number of dimensions
    num_dims = len(dimensions)

    # Compute angle for each dimension
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()

    # Close the plot
    values += values[:1]
    angles += angles[:1]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    # Plot data
    ax.plot(angles, values, 'o-', linewidth=2, color=color, label=title)
    ax.fill(angles, values, alpha=fill_alpha, color=color)

    # Fix axis to go from 0 to max_score
    ax.set_ylim(0, max_score)

    # Set dimension labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=12)

    # Set radial labels
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=10)

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)

    # Add title
    plt.title(title, size=16, pad=20, weight='bold')

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def create_comparative_spider_chart(
    models_scores: List[Dict[str, Any]],
    title: str,
    output_path: Path,
    max_score: float = 10.0
) -> Path:
    """
    Create a comparative spider chart showing multiple models.

    Args:
        models_scores: List of dicts with 'name' and 'scores' keys
        title: Chart title
        output_path: Path to save the chart
        max_score: Maximum score value (default 10)

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
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

    # Color palette
    colors = plt.cm.tab10(np.linspace(0, 1, len(models_scores)))

    # Plot each model
    for i, model_data in enumerate(models_scores):
        values = [model_data['scores'].get(dim, 0) for dim in dimensions]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2,
                color=colors[i], label=model_data['name'], alpha=0.8)
        ax.fill(angles, values, alpha=0.15, color=colors[i])

    # Fix axis
    ax.set_ylim(0, max_score)

    # Set dimension labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=11)

    # Set radial labels
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=10)

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)

    # Add title
    plt.title(title, size=16, pad=20, weight='bold')

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def create_bar_chart_comparison(
    models_scores: List[Dict[str, Any]],
    dimension: str,
    output_path: Path,
    max_score: float = 10.0
) -> Path:
    """
    Create a bar chart comparing models on a single dimension.

    Args:
        models_scores: List of dicts with 'name' and 'scores' keys
        dimension: Which dimension to compare
        output_path: Path to save the chart
        max_score: Maximum score value (default 10)

    Returns:
        Path to saved chart
    """
    # Extract data
    model_names = [m['name'] for m in models_scores]
    values = [m['scores'].get(dimension, 0) for m in models_scores]

    # Sort by value
    sorted_data = sorted(zip(model_names, values), key=lambda x: x[1], reverse=True)
    model_names, values = zip(*sorted_data)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, max(6, len(model_names) * 0.4)))

    # Create horizontal bar chart
    y_pos = np.arange(len(model_names))
    colors = plt.cm.viridis(np.array(values) / max_score)

    bars = ax.barh(y_pos, values, color=colors, alpha=0.8)

    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(model_names, fontsize=10)
    ax.set_xlabel('Score', fontsize=12)
    ax.set_title(f'{dimension.capitalize()} Comparison', fontsize=14, weight='bold')
    ax.set_xlim(0, max_score)

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(value + 0.1, i, f'{value:.2f}',
                va='center', fontsize=9)

    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def create_heatmap(
    models_scores: List[Dict[str, Any]],
    output_path: Path
) -> Path:
    """
    Create a heatmap showing all models across all dimensions.

    Args:
        models_scores: List of dicts with 'name' and 'scores' keys
        output_path: Path to save the chart

    Returns:
        Path to saved chart
    """
    # Extract dimensions from first model
    dimensions = list(models_scores[0]['scores'].keys())
    model_names = [m['name'] for m in models_scores]

    # Build matrix
    matrix = []
    for model_data in models_scores:
        row = [model_data['scores'].get(dim, 0) for dim in dimensions]
        matrix.append(row)

    matrix = np.array(matrix)

    # Create figure
    fig, ax = plt.subplots(figsize=(max(10, len(dimensions) * 0.8),
                                     max(6, len(model_names) * 0.5)))

    # Create heatmap
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=10)

    # Set ticks
    ax.set_xticks(np.arange(len(dimensions)))
    ax.set_yticks(np.arange(len(model_names)))
    ax.set_xticklabels(dimensions, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(model_names, fontsize=10)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Score', rotation=270, labelpad=20, fontsize=12)

    # Add value annotations
    for i in range(len(model_names)):
        for j in range(len(dimensions)):
            text = ax.text(j, i, f'{matrix[i, j]:.1f}',
                          ha='center', va='center', color='black', fontsize=9)

    # Add title
    plt.title('Behavioral Dimensions Heatmap', fontsize=14, weight='bold', pad=20)

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def visualize_judge_results(job_file: Path, output_dir: Optional[Path] = None) -> List[Path]:
    """
    Generate all visualizations from a judge evaluation file.

    Args:
        job_file: Path to job JSON file with judge evaluation
        output_dir: Optional output directory (defaults to job_file.parent / 'visualization')

    Returns:
        List of paths to created visualization files
    """
    # Load job data
    with open(job_file, 'r') as f:
        job_data = json.load(f)

    # Check for judge evaluation
    if 'judge_evaluation' not in job_data:
        raise ValueError(f"No judge evaluation found in {job_file}")

    judge_eval = job_data['judge_evaluation']
    evaluations = judge_eval.get('evaluations', [])

    if not evaluations:
        raise ValueError(f"No evaluations found in {job_file}")

    # Extract job name for file prefixes and directory naming
    job_id = job_data['job_metadata'].get('payload_name', job_file.stem)

    # Setup output directory
    if output_dir is None:
        # Use parent directory's visualization/individual_jobs folder
        base_viz_dir = job_file.parent / 'visualization' / 'individual_jobs'
        output_dir = base_viz_dir / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = []

    # 1. Individual spider charts for each model
    print(f"\n📊 Creating individual spider charts...")
    for i, model_eval in enumerate(evaluations, 1):
        model_name = model_eval['display_name']
        final_scores = model_eval.get('final_averaged_scores')

        if not final_scores or 'scores' not in final_scores:
            print(f"  ⏭️  {model_name}: No final scores")
            continue

        output_path = output_dir / f"{job_id}_spider_{i}_{model_name.replace(' ', '_')}.png"
        create_spider_chart(
            scores=final_scores['scores'],
            title=f"{model_name} - Behavioral Profile",
            output_path=output_path
        )
        created_files.append(output_path)
        print(f"  ✓  {output_path.name}")

    # 2. Comparative spider chart (all models) - save to summary folder
    print(f"\n📊 Creating comparative spider chart...")
    models_scores = []
    for model_eval in evaluations:
        final_scores = model_eval.get('final_averaged_scores')
        if final_scores and 'scores' in final_scores:
            models_scores.append({
                'name': model_eval['display_name'],
                'scores': final_scores['scores']
            })

    if len(models_scores) >= 2:
        # Save comparative charts in individual_jobs/{job_id}/ for per-job comparison
        output_path = output_dir / f"{job_id}_comparative_spider.png"
        create_comparative_spider_chart(
            models_scores=models_scores,
            title=f"Behavioral Comparison - {job_id}",
            output_path=output_path
        )
        created_files.append(output_path)
        print(f"  ✓  {output_path.name}")

    # 3. Heatmap - save in individual_jobs/{job_id}/ for per-job comparison
    print(f"\n📊 Creating heatmap...")
    if models_scores:
        output_path = output_dir / f"{job_id}_heatmap.png"
        create_heatmap(models_scores, output_path)
        created_files.append(output_path)
        print(f"  ✓  {output_path.name}")

    # 4. Bar charts for each dimension - DISABLED
    # Individual dimension bar charts removed to reduce clutter
    # Heatmap provides the same information in a more compact format

    return created_files


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/visualize_behavioral.py <job_file.json|directory> [output_dir]")
        print("\nGenerates spider charts, heatmaps, and comparative visualizations")
        print("from behavioral judge evaluation results.")
        print("\nExamples:")
        print("  python3 src/visualize_behavioral.py outputs/single_prompt_jobs/job_behavioral_warmth.json")
        print("  python3 src/visualize_behavioral.py outputs/single_prompt_jobs/12_2_2025_behavioral_v1/ outputs/viz/")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not input_path.exists():
        print(f"❌ Path not found: {input_path}")
        sys.exit(1)

    # Handle directory input - process all JSON files
    if input_path.is_dir():
        json_files = sorted(input_path.rglob("*.json"))

        if not json_files:
            print(f"❌ No JSON files found in directory: {input_path}")
            sys.exit(1)

        print(f"📁 Processing directory: {input_path.name}")
        print(f"Found {len(json_files)} JSON file(s)\n")

        total_created = 0
        processed = 0
        skipped = 0

        for job_file in json_files:
            print(f"📄 {job_file.name}")
            try:
                # For directory processing, use per-job output dirs if no output specified
                if output_dir is None:
                    job_output_dir = input_path / 'visualization' / job_file.stem
                else:
                    job_output_dir = output_dir / job_file.stem

                created_files = visualize_judge_results(job_file, job_output_dir)
                print(f"  ✓ Created {len(created_files)} visualizations")
                total_created += len(created_files)
                processed += 1
            except ValueError as e:
                print(f"  ⏭️  Skipped: {e}")
                skipped += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")
                skipped += 1

        print(f"\n{'='*60}")
        print(f"Processed: {processed} jobs, {skipped} skipped")
        print(f"Total visualizations: {total_created}")
        if output_dir:
            print(f"📁 Output directory: {output_dir}")
        else:
            print(f"📁 Output directory: {input_path / 'visualization'}")

    # Handle single file input
    else:
        print(f"📄 Processing: {input_path.name}")

        try:
            created_files = visualize_judge_results(input_path, output_dir)
            print(f"\n{'='*60}")
            print(f"✓ Created {len(created_files)} visualizations")
            if output_dir:
                print(f"📁 Output directory: {output_dir}")
            else:
                print(f"📁 Output directory: {input_path.parent / 'visualization'}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
