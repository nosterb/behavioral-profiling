#!/usr/bin/env python3
"""
Analyze statistical similarity/distance between model behavioral profiles.

Computes multiple distance metrics and creates visualization heatmaps to show
which models have similar or different personalities.

Metrics computed:
- Euclidean distance: Straight-line distance in 9D space
- Cosine similarity: Angle between profile vectors (0=orthogonal, 1=identical)
- Manhattan distance: Sum of absolute differences across dimensions
- Correlation: Pearson correlation between profiles

Usage:
    python3 scripts/analyze_profile_similarity.py outputs/single_prompt_jobs/12_7_2025_behavioral_v3/
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


def euclidean_distance(v1, v2):
    """Calculate Euclidean distance between two vectors."""
    return np.sqrt(np.sum((np.array(v1) - np.array(v2)) ** 2))


def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors."""
    v1, v2 = np.array(v1), np.array(v2)
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    return dot_product / norm_product if norm_product > 0 else 0


def manhattan_distance(v1, v2):
    """Calculate Manhattan (L1) distance between two vectors."""
    return np.sum(np.abs(np.array(v1) - np.array(v2)))


def pearson_correlation(v1, v2):
    """Calculate Pearson correlation coefficient between two vectors."""
    v1, v2 = np.array(v1), np.array(v2)
    v1_mean, v2_mean = np.mean(v1), np.mean(v2)
    v1_centered = v1 - v1_mean
    v2_centered = v2 - v2_mean
    numerator = np.sum(v1_centered * v2_centered)
    denominator = np.sqrt(np.sum(v1_centered ** 2) * np.sum(v2_centered ** 2))
    return numerator / denominator if denominator > 0 else 0


def aggregate_scores_from_directory(directory: Path) -> dict:
    """
    Aggregate behavioral scores across all jobs.

    Returns:
        {model_name: {dimension: avg_score, ...}, ...}
    """
    json_files = sorted(directory.rglob("job_*.json"))

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


def normalize_to_similarity(value, metric, min_val, max_val):
    """
    Normalize a distance/similarity value to 0-1 scale where 1 = most similar.

    Args:
        value: The raw metric value
        metric: Type of metric
        min_val: Minimum value in the matrix
        max_val: Maximum value in the matrix
    """
    if metric in ['cosine', 'correlation']:
        # Already similarity metrics (higher = more similar)
        # Normalize from [min, max] to [0, 1]
        if max_val == min_val:
            return 1.0
        return (value - min_val) / (max_val - min_val)
    else:
        # Distance metrics (lower = more similar)
        # Invert and normalize: 1 - (value - min) / (max - min)
        if max_val == min_val:
            return 1.0
        return 1.0 - ((value - min_val) / (max_val - min_val))


def compute_composite_similarity(models_scores: dict) -> tuple:
    """
    Compute a composite similarity score combining multiple metrics.

    Returns normalized similarity scores (0-1) where 1 = most similar.

    Args:
        models_scores: {model_name: {dimension: score, ...}, ...}

    Returns:
        (composite_matrix, model_names)
    """
    # Compute all four metrics
    metrics = ['euclidean', 'cosine', 'manhattan', 'correlation']
    matrices = {}

    for metric in metrics:
        matrix, model_names = compute_distance_matrix(models_scores, metric)
        matrices[metric] = matrix

    n_models = len(model_names)

    # Normalize each metric to 0-1 similarity scale
    normalized_matrices = {}

    for metric, matrix in matrices.items():
        normalized = np.zeros_like(matrix)

        # Get min/max excluding diagonal
        mask = ~np.eye(n_models, dtype=bool)
        min_val = matrix[mask].min()
        max_val = matrix[mask].max()

        for i in range(n_models):
            for j in range(n_models):
                if i == j:
                    normalized[i, j] = 1.0  # Perfect similarity with self
                else:
                    normalized[i, j] = normalize_to_similarity(
                        matrix[i, j], metric, min_val, max_val
                    )

        normalized_matrices[metric] = normalized

    # Compute composite as average of normalized scores
    composite = np.mean([normalized_matrices[m] for m in metrics], axis=0)

    return composite, model_names


def compute_distance_matrix(models_scores: dict, metric: str = 'euclidean') -> tuple:
    """
    Compute pairwise distances between all models.

    Args:
        models_scores: {model_name: {dimension: score, ...}, ...}
        metric: 'euclidean', 'cosine', 'manhattan', or 'correlation'

    Returns:
        (distance_matrix, model_names)
    """
    model_names = list(models_scores.keys())
    n_models = len(model_names)

    # Create vectors in canonical dimension order
    vectors = []
    for model_name in model_names:
        vector = [models_scores[model_name].get(dim, 0) for dim in BEHAVIORAL_DIMENSIONS]
        vectors.append(vector)

    vectors = np.array(vectors)

    # Compute distance matrix
    distance_matrix = np.zeros((n_models, n_models))

    for i in range(n_models):
        for j in range(n_models):
            if i == j:
                if metric == 'correlation':
                    distance_matrix[i, j] = 1.0  # Perfect correlation with self
                else:
                    distance_matrix[i, j] = 0.0
            else:
                if metric == 'euclidean':
                    distance_matrix[i, j] = euclidean_distance(vectors[i], vectors[j])
                elif metric == 'cosine':
                    # Store similarity directly (not distance)
                    distance_matrix[i, j] = cosine_similarity(vectors[i], vectors[j])
                elif metric == 'manhattan':
                    distance_matrix[i, j] = manhattan_distance(vectors[i], vectors[j])
                elif metric == 'correlation':
                    distance_matrix[i, j] = pearson_correlation(vectors[i], vectors[j])

    return distance_matrix, model_names


def create_similarity_heatmap(
    distance_matrix: np.ndarray,
    model_names: list,
    metric: str,
    output_path: Path
):
    """Create a heatmap visualization of model similarities/distances."""

    # Configure based on metric type
    if metric == 'euclidean':
        title = 'Model Behavioral Profile Distances (Euclidean)'
        cmap = 'YlOrRd'  # Yellow to Red (low to high distance)
        cbar_label = 'Euclidean Distance'
        fmt = '.2f'
        vmin, vmax = None, None
    elif metric == 'cosine':
        title = 'Model Behavioral Profile Similarity (Cosine)'
        cmap = 'RdYlGn'  # Red to Green (dissimilar to similar)
        cbar_label = 'Cosine Similarity'
        fmt = '.3f'
        vmin, vmax = 0, 1
    elif metric == 'manhattan':
        title = 'Model Behavioral Profile Distances (Manhattan)'
        cmap = 'YlOrRd'
        cbar_label = 'Manhattan Distance (L1)'
        fmt = '.2f'
        vmin, vmax = None, None
    elif metric == 'correlation':
        title = 'Model Behavioral Profile Correlation'
        cmap = 'RdYlGn'
        cbar_label = 'Pearson Correlation'
        fmt = '.3f'
        vmin, vmax = -1, 1

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 12))

    # Create heatmap
    im = ax.imshow(distance_matrix, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(cbar_label, rotation=270, labelpad=20, fontsize=11)

    # Set ticks and labels
    ax.set_xticks(np.arange(len(model_names)))
    ax.set_yticks(np.arange(len(model_names)))
    ax.set_xticklabels(model_names, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(model_names, fontsize=9)

    # Add values to cells
    for i in range(len(model_names)):
        for j in range(len(model_names)):
            text = ax.text(j, i, format(distance_matrix[i, j], fmt),
                          ha="center", va="center", color="black", fontsize=8)

    # Title and layout
    ax.set_title(title, fontsize=14, weight='bold', pad=20)
    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Created: {output_path.name}")


def print_most_similar_pairs(distance_matrix: np.ndarray, model_names: list, metric: str, top_n: int = 10):
    """Print the most similar model pairs."""

    pairs = []
    n = len(model_names)

    for i in range(n):
        for j in range(i + 1, n):  # Only upper triangle
            pairs.append((model_names[i], model_names[j], distance_matrix[i, j]))

    # Sort based on metric
    if metric in ['cosine', 'correlation', 'composite']:
        # Higher is more similar
        pairs.sort(key=lambda x: x[2], reverse=True)
        label = "similar"
    else:
        # Lower distance is more similar
        pairs.sort(key=lambda x: x[2])
        label = "similar (lowest distance)"

    print(f"\n{'='*70}")
    print(f"Top {top_n} Most Similar Model Pairs ({metric})")
    print(f"{'='*70}")

    for i, (model1, model2, value) in enumerate(pairs[:top_n], 1):
        print(f"{i:2d}. {model1:30s} ↔ {model2:30s}  {value:7.3f}")


def print_most_different_pairs(distance_matrix: np.ndarray, model_names: list, metric: str, top_n: int = 10):
    """Print the most different model pairs."""

    pairs = []
    n = len(model_names)

    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((model_names[i], model_names[j], distance_matrix[i, j]))

    # Sort based on metric
    if metric in ['cosine', 'correlation', 'composite']:
        # Lower is more different
        pairs.sort(key=lambda x: x[2])
        label = "different"
    else:
        # Higher distance is more different
        pairs.sort(key=lambda x: x[2], reverse=True)
        label = "different (highest distance)"

    print(f"\n{'='*70}")
    print(f"Top {top_n} Most Different Model Pairs ({metric})")
    print(f"{'='*70}")

    for i, (model1, model2, value) in enumerate(pairs[:top_n], 1):
        print(f"{i:2d}. {model1:30s} ↔ {model2:30s}  {value:7.3f}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    directory = Path(sys.argv[1])

    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Analyzing behavioral profile similarities in: {directory}")
    print("Aggregating scores across all jobs...")

    # Aggregate scores
    models_scores = aggregate_scores_from_directory(directory)

    if not models_scores:
        print("No valid data found!")
        sys.exit(1)

    print(f"Found {len(models_scores)} models with complete behavioral profiles\n")

    # Create output directory
    viz_dir = directory / "visualization" / "similarity_analysis"
    viz_dir.mkdir(parents=True, exist_ok=True)

    # First, compute and visualize composite similarity
    print(f"\n{'='*70}")
    print(f"Computing Composite Similarity (combines all metrics)...")
    print(f"{'='*70}")

    composite_matrix, model_names = compute_composite_similarity(models_scores)

    # Create composite heatmap
    output_path = viz_dir / "similarity_composite.png"

    # Use custom visualization for composite
    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(composite_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Composite Similarity Score', rotation=270, labelpad=20, fontsize=11)
    ax.set_xticks(np.arange(len(model_names)))
    ax.set_yticks(np.arange(len(model_names)))
    ax.set_xticklabels(model_names, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(model_names, fontsize=9)

    # Add values to cells
    for i in range(len(model_names)):
        for j in range(len(model_names)):
            text = ax.text(j, i, format(composite_matrix[i, j], '.3f'),
                          ha="center", va="center", color="black", fontsize=8)

    ax.set_title('Composite Behavioral Profile Similarity\n(Average of Euclidean, Cosine, Manhattan, and Correlation)',
                 fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Created: {output_path.name}")

    # Print composite rankings
    print_most_similar_pairs(composite_matrix, model_names, 'composite', top_n=10)
    print_most_different_pairs(composite_matrix, model_names, 'composite', top_n=10)

    # Then compute and visualize each individual metric
    metrics = [
        ('euclidean', 'Euclidean Distance'),
        ('cosine', 'Cosine Similarity'),
        ('manhattan', 'Manhattan Distance'),
        ('correlation', 'Pearson Correlation')
    ]

    for metric_key, metric_name in metrics:
        print(f"\n{'='*70}")
        print(f"Computing {metric_name}...")
        print(f"{'='*70}")

        # Compute distance matrix
        distance_matrix, model_names = compute_distance_matrix(models_scores, metric_key)

        # Create heatmap
        output_path = viz_dir / f"similarity_{metric_key}.png"
        create_similarity_heatmap(distance_matrix, model_names, metric_key, output_path)

        # Print statistics
        print_most_similar_pairs(distance_matrix, model_names, metric_key, top_n=5)
        print_most_different_pairs(distance_matrix, model_names, metric_key, top_n=5)

    print(f"\n{'='*70}")
    print(f"✓ All similarity analyses saved to: {viz_dir}")
    print(f"{'='*70}")
    print("\nGenerated files:")
    print(f"  - similarity_composite.png (⭐ RECOMMENDED - combines all metrics)")
    for metric_key, _ in metrics:
        print(f"  - similarity_{metric_key}.png")


if __name__ == "__main__":
    main()
