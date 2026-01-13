#!/usr/bin/env python3
"""
Behavioral Type Clustering Analysis

Identifies distinct behavioral "types" or archetypes among models using clustering.
Analyzes whether these types hold up across different test suites.

Features:
- Hierarchical clustering with dendrogram visualization
- K-means clustering with optimal K detection
- PCA 2D visualization of behavioral space
- Cross-suite stability analysis
- Archetype profiling

Usage:
    # Single suite analysis
    python3 scripts/cluster_behavioral_types.py outputs/single_prompt_jobs/12_10_2025_behavioral_v7/

    # Multi-suite comparison
    python3 scripts/cluster_behavioral_types.py \
        outputs/single_prompt_jobs/12_10_2025_behavioral_v7/ \
        outputs/single_prompt_jobs/12_2_2025_behavioral_v1/ \
        --compare-suites

    # Specify number of clusters
    python3 scripts/cluster_behavioral_types.py outputs/single_prompt_jobs/12_10_2025_behavioral_v7/ --n-clusters 3
"""

import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.behavioral_constants import BEHAVIORAL_DIMENSIONS


def aggregate_scores_from_directory(directory: Path) -> Dict[str, Dict[str, float]]:
    """
    Aggregate behavioral scores across all jobs in a directory.

    Returns:
        {model_name: {dimension: avg_score, ...}, ...}
    """
    json_files = sorted(directory.rglob("*.json"))

    if not json_files:
        return {}

    model_scores = defaultdict(lambda: defaultdict(list))

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                job_data = json.load(f)

            if 'judge_evaluation' not in job_data:
                continue

            evaluations = job_data['judge_evaluation'].get('evaluations', [])

            for model_eval in evaluations:
                model_name = model_eval.get('display_name')
                final_scores = model_eval.get('final_averaged_scores', {})
                scores = final_scores.get('scores', {})

                if not model_name or not scores:
                    continue

                for dimension, score in scores.items():
                    if isinstance(score, (int, float)):
                        model_scores[model_name][dimension].append(score)

        except Exception as e:
            print(f"Warning: Skipped {json_file.name}: {e}")
            continue

    # Calculate averages
    aggregated = {}
    for model_name, dimensions in model_scores.items():
        aggregated[model_name] = {
            dim: np.mean(scores) for dim, scores in dimensions.items()
        }

    return aggregated


def scores_to_matrix(models_scores: Dict[str, Dict[str, float]]) -> Tuple[np.ndarray, List[str]]:
    """
    Convert scores dict to matrix format.

    Returns:
        (matrix, model_names) where matrix is shape (n_models, n_dimensions)
    """
    model_names = sorted(models_scores.keys())

    matrix = []
    for model_name in model_names:
        vector = [models_scores[model_name].get(dim, 0) for dim in BEHAVIORAL_DIMENSIONS]
        matrix.append(vector)

    return np.array(matrix), model_names


def find_optimal_clusters(X: np.ndarray, max_k: int = 8) -> Tuple[int, List[float], List[float]]:
    """
    Find optimal number of clusters using elbow method and silhouette scores.

    Returns:
        (optimal_k, inertias, silhouette_scores)
    """
    inertias = []
    silhouette_scores_list = []
    k_range = range(2, min(max_k + 1, len(X)))

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        inertias.append(kmeans.inertia_)
        silhouette_scores_list.append(silhouette_score(X, labels))

    # Find elbow using second derivative
    if len(inertias) >= 3:
        second_deriv = np.diff(np.diff(inertias))
        optimal_k_elbow = np.argmax(second_deriv) + 3  # +3 because of 2 diffs and starting at k=2
    else:
        optimal_k_elbow = 2

    # Find best silhouette
    optimal_k_silhouette = silhouette_scores_list.index(max(silhouette_scores_list)) + 2

    # Use silhouette as primary, elbow as fallback
    optimal_k = optimal_k_silhouette

    return optimal_k, inertias, silhouette_scores_list


def create_dendrogram(X: np.ndarray, model_names: List[str], output_path: Path):
    """Create hierarchical clustering dendrogram."""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Compute linkage
    linkage_matrix = linkage(X, method='ward')

    # Create dendrogram
    dendrogram(
        linkage_matrix,
        labels=model_names,
        ax=ax,
        leaf_font_size=10,
        color_threshold=0.7 * max(linkage_matrix[:, 2])
    )

    ax.set_title('Hierarchical Clustering of Model Personalities', fontsize=14, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Distance (Ward)', fontsize=12)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return linkage_matrix


def create_pca_visualization(X: np.ndarray, model_names: List[str],
                            cluster_labels: np.ndarray, output_path: Path):
    """Create PCA 2D visualization with cluster colors."""
    # Perform PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    # Explained variance
    explained_var = pca.explained_variance_ratio_

    fig, ax = plt.subplots(figsize=(12, 10))

    # Color map
    n_clusters = len(np.unique(cluster_labels))
    colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))

    # Plot each cluster
    for cluster_id in range(n_clusters):
        mask = cluster_labels == cluster_id
        ax.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            c=[colors[cluster_id]],
            s=200,
            alpha=0.6,
            edgecolors='black',
            linewidth=1.5,
            label=f'Type {cluster_id + 1}'
        )

        # Add model labels
        masked_indices = np.where(mask)[0]
        for i, idx in enumerate(masked_indices):
            ax.annotate(
                model_names[idx],
                (X_pca[idx, 0], X_pca[idx, 1]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=9,
                alpha=0.8
            )

    ax.set_xlabel(f'PC1 ({explained_var[0]:.1%} variance)', fontsize=12)
    ax.set_ylabel(f'PC2 ({explained_var[1]:.1%} variance)', fontsize=12)
    ax.set_title('Behavioral Types in 2D Space (PCA)', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return explained_var


def create_elbow_plot(k_range: range, inertias: List[float],
                     silhouette_scores: List[float], optimal_k: int, output_path: Path):
    """Create elbow method and silhouette score plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Elbow plot
    ax1.plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
    ax1.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2, alpha=0.7,
                label=f'Optimal K={optimal_k}')
    ax1.set_xlabel('Number of Clusters (K)', fontsize=12)
    ax1.set_ylabel('Inertia (Within-cluster sum of squares)', fontsize=12)
    ax1.set_title('Elbow Method', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Silhouette plot
    ax2.plot(k_range, silhouette_scores, 'go-', linewidth=2, markersize=8)
    ax2.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2, alpha=0.7,
                label=f'Optimal K={optimal_k}')
    ax2.set_xlabel('Number of Clusters (K)', fontsize=12)
    ax2.set_ylabel('Silhouette Score', fontsize=12)
    ax2.set_title('Silhouette Analysis', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def profile_cluster_archetypes(X: np.ndarray, model_names: List[str],
                               cluster_labels: np.ndarray) -> Dict:
    """
    Profile each cluster to create behavioral archetypes.

    Returns cluster metadata including centroid, member models, and distinctive traits.
    """
    n_clusters = len(np.unique(cluster_labels))
    archetypes = {}

    for cluster_id in range(n_clusters):
        mask = cluster_labels == cluster_id
        cluster_members = np.array(model_names)[mask].tolist()

        # Compute centroid
        centroid = X[mask].mean(axis=0)

        # Find distinctive dimensions (above/below mean)
        overall_mean = X.mean(axis=0)
        deviations = centroid - overall_mean

        # Top distinctive traits
        sorted_dims = np.argsort(np.abs(deviations))[::-1]
        distinctive_traits = [
            {
                'dimension': BEHAVIORAL_DIMENSIONS[i],
                'centroid_score': float(centroid[i]),
                'deviation_from_mean': float(deviations[i]),
                'direction': 'high' if deviations[i] > 0 else 'low'
            }
            for i in sorted_dims[:3]  # Top 3 distinctive dimensions
        ]

        archetypes[f'Type {cluster_id + 1}'] = {
            'cluster_id': cluster_id,
            'n_members': len(cluster_members),
            'members': cluster_members,
            'centroid': {dim: float(centroid[i]) for i, dim in enumerate(BEHAVIORAL_DIMENSIONS)},
            'distinctive_traits': distinctive_traits
        }

    return archetypes


def analyze_suite(directory: Path, n_clusters: int = None) -> Dict:
    """
    Perform complete clustering analysis on a single suite.

    Returns dict with all analysis results.
    """
    suite_name = directory.name
    print(f"\n{'='*70}")
    print(f"Analyzing Suite: {suite_name}")
    print(f"{'='*70}")

    # Load data
    print(f"Loading behavioral data...")
    models_scores = aggregate_scores_from_directory(directory)

    if not models_scores:
        print(f"✗ No behavioral data found in {directory}")
        return {}

    print(f"✓ Loaded {len(models_scores)} models")

    # Convert to matrix
    X, model_names = scores_to_matrix(models_scores)

    # Create output directory
    viz_dir = directory / "visualization" / "clustering"
    viz_dir.mkdir(parents=True, exist_ok=True)

    # Find optimal clusters if not specified
    if n_clusters is None:
        print(f"\nFinding optimal number of clusters...")
        optimal_k, inertias, silhouette_scores = find_optimal_clusters(X)
        print(f"✓ Optimal K = {optimal_k} (via silhouette score)")

        # Create elbow plot
        k_range = range(2, len(inertias) + 2)
        create_elbow_plot(k_range, inertias, silhouette_scores, optimal_k,
                         viz_dir / "optimal_k_analysis.png")
        print(f"  → {viz_dir / 'optimal_k_analysis.png'}")
    else:
        optimal_k = n_clusters
        print(f"\nUsing specified K = {optimal_k}")

    # K-means clustering
    print(f"\nPerforming K-means clustering (K={optimal_k})...")
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X)
    silhouette = silhouette_score(X, cluster_labels)
    print(f"✓ Silhouette score: {silhouette:.3f}")

    # Hierarchical clustering dendrogram
    print(f"\nCreating dendrogram...")
    linkage_matrix = create_dendrogram(X, model_names, viz_dir / "dendrogram.png")
    print(f"  → {viz_dir / 'dendrogram.png'}")

    # PCA visualization
    print(f"\nCreating PCA visualization...")
    explained_var = create_pca_visualization(X, model_names, cluster_labels,
                                            viz_dir / "pca_clusters.png")
    print(f"  → {viz_dir / 'pca_clusters.png'}")
    print(f"  PC1+PC2 explain {sum(explained_var):.1%} of variance")

    # Profile archetypes
    print(f"\nProfiling behavioral archetypes...")
    archetypes = profile_cluster_archetypes(X, model_names, cluster_labels)

    for archetype_name, data in archetypes.items():
        print(f"\n  {archetype_name} (n={data['n_members']}):")
        print(f"    Members: {', '.join(data['members'])}")
        print(f"    Distinctive traits:")
        for trait in data['distinctive_traits']:
            direction_arrow = '↑' if trait['direction'] == 'high' else '↓'
            print(f"      {direction_arrow} {trait['dimension']}: {trait['centroid_score']:.2f} "
                  f"({trait['deviation_from_mean']:+.2f} vs mean)")

    # Save results
    results = {
        'suite_name': suite_name,
        'n_models': len(model_names),
        'n_clusters': optimal_k,
        'silhouette_score': float(silhouette),
        'model_names': model_names,
        'cluster_labels': cluster_labels.tolist(),
        'archetypes': archetypes,
        'pca_explained_variance': explained_var.tolist()
    }

    results_path = viz_dir / "clustering_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved: {results_path}")

    return results


def compare_suites(suite_results: List[Dict]) -> Dict:
    """
    Compare clustering stability across multiple suites.

    Uses Adjusted Rand Index to measure cluster agreement.
    """
    print(f"\n{'='*70}")
    print(f"Cross-Suite Stability Analysis")
    print(f"{'='*70}")

    if len(suite_results) < 2:
        print("Need at least 2 suites for comparison")
        return {}

    # Find common models across all suites
    common_models = set(suite_results[0]['model_names'])
    for result in suite_results[1:]:
        common_models &= set(result['model_names'])

    common_models = sorted(common_models)

    print(f"\nCommon models across all suites: {len(common_models)}")
    print(f"  {', '.join(common_models)}")

    # Extract cluster assignments for common models
    suite_labels = []
    for result in suite_results:
        model_to_label = {
            model: label
            for model, label in zip(result['model_names'], result['cluster_labels'])
        }
        labels = [model_to_label[model] for model in common_models]
        suite_labels.append(labels)

    # Compute pairwise ARI
    print(f"\nPairwise Adjusted Rand Index (1.0 = perfect agreement):")
    ari_matrix = []
    for i, result_i in enumerate(suite_results):
        ari_row = []
        for j, result_j in enumerate(suite_results):
            if i == j:
                ari = 1.0
            else:
                ari = adjusted_rand_score(suite_labels[i], suite_labels[j])
            ari_row.append(ari)
            if i < j:
                print(f"  {result_i['suite_name']} vs {result_j['suite_name']}: {ari:.3f}")
        ari_matrix.append(ari_row)

    # Overall stability
    mean_ari = np.mean([ari_matrix[i][j] for i in range(len(suite_results))
                       for j in range(i+1, len(suite_results))])
    print(f"\nMean ARI across all pairs: {mean_ari:.3f}")

    if mean_ari > 0.7:
        print("  → High stability: Behavioral types are consistent across suites")
    elif mean_ari > 0.4:
        print("  → Moderate stability: Some types persist, some shift")
    else:
        print("  → Low stability: Behavioral types are suite-dependent")

    return {
        'common_models': common_models,
        'ari_matrix': ari_matrix,
        'mean_ari': float(mean_ari),
        'suite_names': [r['suite_name'] for r in suite_results]
    }


def main():
    parser = argparse.ArgumentParser(
        description='Cluster behavioral types and analyze cross-suite stability',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'directories',
        type=Path,
        nargs='+',
        help='One or more suite directories to analyze'
    )
    parser.add_argument(
        '--n-clusters',
        type=int,
        help='Number of clusters (if not specified, optimal K will be determined automatically)'
    )
    parser.add_argument(
        '--compare-suites',
        action='store_true',
        help='Perform cross-suite stability analysis (requires 2+ directories)'
    )

    args = parser.parse_args()

    # Analyze each suite
    suite_results = []
    for directory in args.directories:
        if not directory.exists():
            print(f"✗ Directory not found: {directory}")
            continue

        result = analyze_suite(directory, n_clusters=args.n_clusters)
        if result:
            suite_results.append(result)

    # Cross-suite comparison
    if args.compare_suites and len(suite_results) >= 2:
        comparison = compare_suites(suite_results)

        # Save comparison results
        output_dir = Path('outputs/behavioral_clustering')
        output_dir.mkdir(parents=True, exist_ok=True)
        comparison_path = output_dir / "cross_suite_comparison.json"

        with open(comparison_path, 'w') as f:
            json.dump({
                'suites': suite_results,
                'comparison': comparison
            }, f, indent=2)

        print(f"\n✓ Cross-suite comparison saved: {comparison_path}")

    print(f"\n{'='*70}")
    print(f"Analysis Complete")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
