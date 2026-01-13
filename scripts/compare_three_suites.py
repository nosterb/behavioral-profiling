#!/usr/bin/env python3
"""
Three-way cross-suite stability analysis for behavioral clustering.
Compares cluster assignments across three different test suites.
"""

import json
from pathlib import Path
from collections import defaultdict
from sklearn.metrics import adjusted_rand_score
import sys


def load_clustering_result(json_path):
    """Load clustering results from JSON file."""
    with open(json_path) as f:
        return json.load(f)


def extract_model_clusters(suite_result):
    """
    Extract model names and cluster assignments from clustering result.
    Handles both old format (with 'clusters' dict) and new format (with 'model_names' list).
    """
    if 'model_names' in suite_result and 'cluster_labels' in suite_result:
        # New format
        return {
            name: label
            for name, label in zip(suite_result['model_names'], suite_result['cluster_labels'])
        }
    elif 'clusters' in suite_result:
        # Old format - extract from clusters dict
        model_clusters = {}
        for cluster_name, cluster_data in suite_result['clusters'].items():
            cluster_id = cluster_data['cluster_id']
            for member in cluster_data['members']:
                model_clusters[member] = cluster_id
        return model_clusters
    else:
        raise ValueError("Unknown clustering result format")


def compare_three_suites(suite1_result, suite2_result, suite3_result):
    """
    Compare cluster assignments across three test suites.

    Returns:
        dict: Stability analysis including:
            - Common models across all three suites
            - Models stable across all three
            - Models stable in only 2 suites
            - Models unstable (different clusters in all 3)
            - Pairwise ARIs
    """
    # Extract model names and cluster assignments
    suite1_clusters = extract_model_clusters(suite1_result)
    suite2_clusters = extract_model_clusters(suite2_result)
    suite3_clusters = extract_model_clusters(suite3_result)

    suite1_models = set(suite1_clusters.keys())
    suite2_models = set(suite2_clusters.keys())
    suite3_models = set(suite3_clusters.keys())

    # Find models common to all three suites
    common_models = suite1_models & suite2_models & suite3_models
    common_models = sorted(list(common_models))

    if len(common_models) == 0:
        return {
            'error': 'No common models across all three suites',
            'suite1_models': len(suite1_models),
            'suite2_models': len(suite2_models),
            'suite3_models': len(suite3_models)
        }

    # Get cluster labels for common models
    labels1 = [suite1_clusters[model] for model in common_models]
    labels2 = [suite2_clusters[model] for model in common_models]
    labels3 = [suite3_clusters[model] for model in common_models]

    # Calculate pairwise ARIs
    ari_1_2 = adjusted_rand_score(labels1, labels2)
    ari_1_3 = adjusted_rand_score(labels1, labels3)
    ari_2_3 = adjusted_rand_score(labels2, labels3)
    ari_mean = (ari_1_2 + ari_1_3 + ari_2_3) / 3

    # Classify stability
    fully_stable = []  # Same cluster in all 3 suites
    partially_stable = []  # Same in 2 suites, different in 1
    unstable = []  # Different in all 3 suites

    for i, model in enumerate(common_models):
        c1, c2, c3 = labels1[i], labels2[i], labels3[i]

        # Check how many pairs match
        matches = sum([c1 == c2, c1 == c3, c2 == c3])

        if matches == 3:
            fully_stable.append({
                'model': model,
                'cluster_suite1': c1,
                'cluster_suite2': c2,
                'cluster_suite3': c3
            })
        elif matches >= 1:
            partially_stable.append({
                'model': model,
                'cluster_suite1': c1,
                'cluster_suite2': c2,
                'cluster_suite3': c3
            })
        else:
            unstable.append({
                'model': model,
                'cluster_suite1': c1,
                'cluster_suite2': c2,
                'cluster_suite3': c3
            })

    # Calculate stability percentages
    n_common = len(common_models)
    fully_stable_pct = 100 * len(fully_stable) / n_common if n_common > 0 else 0
    partially_stable_pct = 100 * len(partially_stable) / n_common if n_common > 0 else 0
    unstable_pct = 100 * len(unstable) / n_common if n_common > 0 else 0

    return {
        'n_common': n_common,
        'common_models': common_models,
        'n_fully_stable': len(fully_stable),
        'n_partially_stable': len(partially_stable),
        'n_unstable': len(unstable),
        'fully_stable_percentage': fully_stable_pct,
        'partially_stable_percentage': partially_stable_pct,
        'unstable_percentage': unstable_pct,
        'adjusted_rand_index_suite1_suite2': ari_1_2,
        'adjusted_rand_index_suite1_suite3': ari_1_3,
        'adjusted_rand_index_suite2_suite3': ari_2_3,
        'adjusted_rand_index_mean': ari_mean,
        'fully_stable_models': fully_stable,
        'partially_stable_models': partially_stable,
        'unstable_models': unstable,
        'interpretation': (
            f"{'High' if fully_stable_pct >= 70 else 'Moderate' if fully_stable_pct >= 50 else 'Low'} stability - "
            f"{fully_stable_pct:.1f}% of models maintain behavioral type across all three suites"
        )
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 compare_three_suites.py <suite1.json> <suite2.json> <suite3.json>")
        print("Example: python3 compare_three_suites.py clustering/v3_v4_v5_pooled/clustering_analysis.json clustering/v6_v7_v8_pooled/clustering_analysis.json clustering/v2/clustering_analysis.json")
        sys.exit(1)

    suite1_path = Path(sys.argv[1])
    suite2_path = Path(sys.argv[2])
    suite3_path = Path(sys.argv[3])

    # Load results
    print(f"Loading clustering results...")
    print(f"  Suite 1: {suite1_path}")
    suite1_result = load_clustering_result(suite1_path)
    print(f"    - {suite1_result['n_models']} models, {suite1_result['n_clusters']} clusters")

    print(f"  Suite 2: {suite2_path}")
    suite2_result = load_clustering_result(suite2_path)
    print(f"    - {suite2_result['n_models']} models, {suite2_result['n_clusters']} clusters")

    print(f"  Suite 3: {suite3_path}")
    suite3_result = load_clustering_result(suite3_path)
    print(f"    - {suite3_result['n_models']} models, {suite3_result['n_clusters']} clusters")

    # Perform comparison
    print(f"\nComparing cluster assignments across three suites...")
    comparison = compare_three_suites(suite1_result, suite2_result, suite3_result)

    # Display results
    print(f"\n{'='*70}")
    print(f"THREE-SUITE STABILITY ANALYSIS")
    print(f"{'='*70}\n")

    print(f"Common models: {comparison['n_common']}")
    print(f"\nStability breakdown:")
    print(f"  Fully stable (same cluster in all 3):  {comparison['n_fully_stable']} ({comparison['fully_stable_percentage']:.1f}%)")
    print(f"  Partially stable (same in 2 of 3):     {comparison['n_partially_stable']} ({comparison['partially_stable_percentage']:.1f}%)")
    print(f"  Unstable (different in all 3):         {comparison['n_unstable']} ({comparison['unstable_percentage']:.1f}%)")

    print(f"\nPairwise Adjusted Rand Indices:")
    print(f"  Suite 1 ↔ Suite 2: {comparison['adjusted_rand_index_suite1_suite2']:.3f}")
    print(f"  Suite 1 ↔ Suite 3: {comparison['adjusted_rand_index_suite1_suite3']:.3f}")
    print(f"  Suite 2 ↔ Suite 3: {comparison['adjusted_rand_index_suite2_suite3']:.3f}")
    print(f"  Mean ARI:          {comparison['adjusted_rand_index_mean']:.3f}")

    print(f"\n{comparison['interpretation']}")

    if comparison['fully_stable_models']:
        print(f"\n{'='*70}")
        print(f"FULLY STABLE MODELS (n={len(comparison['fully_stable_models'])})")
        print(f"{'='*70}\n")
        for entry in comparison['fully_stable_models']:
            print(f"  {entry['model']:40} → Type {entry['cluster_suite1'] + 1}")

    if comparison['partially_stable_models']:
        print(f"\n{'='*70}")
        print(f"PARTIALLY STABLE MODELS (n={len(comparison['partially_stable_models'])})")
        print(f"{'='*70}\n")
        for entry in comparison['partially_stable_models']:
            types = f"Type {entry['cluster_suite1'] + 1} → Type {entry['cluster_suite2'] + 1} → Type {entry['cluster_suite3'] + 1}"
            print(f"  {entry['model']:40} {types}")

    if comparison['unstable_models']:
        print(f"\n{'='*70}")
        print(f"UNSTABLE MODELS (n={len(comparison['unstable_models'])})")
        print(f"{'='*70}\n")
        for entry in comparison['unstable_models']:
            types = f"Type {entry['cluster_suite1'] + 1} → Type {entry['cluster_suite2'] + 1} → Type {entry['cluster_suite3'] + 1}"
            print(f"  {entry['model']:40} {types}")

    # Save results
    output_path = Path('outputs/single_prompt_jobs/clustering/three_suite_stability.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)

    print(f"\n✓ Results saved: {output_path}")


if __name__ == '__main__':
    main()
