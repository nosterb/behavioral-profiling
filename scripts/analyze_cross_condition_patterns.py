#!/usr/bin/env python3
"""
Analyze constrained and outlier model patterns across all conditions.

Creates/updates: research_synthesis/cross_condition/cross_condition_patterns.json

Constrained: High sophistication (>6.5) + residual < -0.15 (below regression line)
Outlier: |residual| > 2 SD from regression line
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Thresholds (matching create_h2_color_coded_scatters.py)
CONSTRAINED_SOPH_THRESHOLD = 6.5
CONSTRAINED_RESIDUAL_THRESHOLD = -0.15
OUTLIER_SD_THRESHOLD = 2.0

DISINHIBITION_DIMS = ['transgression', 'aggression', 'tribalism', 'grandiosity']


def load_median_split_data(condition_dir):
    """Load median split classification data for a condition."""
    path = condition_dir / "median_split_classification.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def analyze_condition(data, condition_name):
    """Analyze constrained and outlier models for a single condition."""
    models = data['models']

    # Get sophistication and disinhibition values
    all_x = [m['sophistication'] for m in models]
    all_y = [m['disinhibition'] for m in models]

    # Composite regression
    z = np.polyfit(all_x, all_y, 1)
    p = np.poly1d(z)
    predicted = p(all_x)
    residuals = np.array(all_y) - predicted
    residual_std = np.std(residuals)

    constrained_composite = []
    outlier_composite = []

    for i, model in enumerate(models):
        model_info = {
            'model_id': model['model_id'],
            'display_name': model['display_name'],
            'sophistication': model['sophistication'],
            'disinhibition': model['disinhibition'],
            'residual': float(residuals[i]),
            'sd_from_line': float(residuals[i] / residual_std) if residual_std > 0 else 0
        }

        # Check constrained (composite)
        if model['sophistication'] > CONSTRAINED_SOPH_THRESHOLD and residuals[i] < CONSTRAINED_RESIDUAL_THRESHOLD:
            constrained_composite.append(model_info)

        # Check outlier (composite)
        if abs(residuals[i]) > OUTLIER_SD_THRESHOLD * residual_std:
            outlier_composite.append(model_info)

    # Per-dimension analysis
    constrained_dimensions = defaultdict(list)
    outlier_dimensions = defaultdict(list)

    for dim in DISINHIBITION_DIMS:
        all_y_dim = [m['scores'][dim] for m in models]
        z_dim = np.polyfit(all_x, all_y_dim, 1)
        p_dim = np.poly1d(z_dim)
        predicted_dim = p_dim(all_x)
        residuals_dim = np.array(all_y_dim) - predicted_dim
        residual_std_dim = np.std(residuals_dim)

        for i, model in enumerate(models):
            # Constrained for this dimension
            if model['sophistication'] > CONSTRAINED_SOPH_THRESHOLD and residuals_dim[i] < CONSTRAINED_RESIDUAL_THRESHOLD:
                constrained_dimensions[model['model_id']].append(dim)

            # Outlier for this dimension
            if abs(residuals_dim[i]) > OUTLIER_SD_THRESHOLD * residual_std_dim:
                outlier_dimensions[model['model_id']].append(dim)

    return {
        'condition': condition_name,
        'n_models': len(models),
        'regression': {
            'slope': float(z[0]),
            'intercept': float(z[1]),
            'residual_std': float(residual_std)
        },
        'constrained': {
            'composite': constrained_composite,
            'by_dimension': {mid: dims for mid, dims in constrained_dimensions.items()}
        },
        'outliers': {
            'composite': outlier_composite,
            'by_dimension': {mid: dims for mid, dims in outlier_dimensions.items()}
        }
    }


def normalize_model_name(name):
    """Normalize model name for cross-condition comparison."""
    # Lowercase for comparison, but track original for display
    return name.lower().replace(' ', '-').replace('_(thinking)', '-thinking').replace('(thinking)', '-thinking')


def aggregate_cross_condition(condition_results):
    """Aggregate patterns across all conditions."""
    constrained_counts = defaultdict(lambda: {'composite': 0, 'dimensions': 0, 'conditions': [], 'display_name': ''})
    outlier_counts = defaultdict(lambda: {'composite': 0, 'dimensions': 0, 'conditions': [], 'display_name': ''})

    for result in condition_results:
        condition = result['condition']

        # Constrained composite
        for model in result['constrained']['composite']:
            key = normalize_model_name(model['display_name'])
            constrained_counts[key]['composite'] += 1
            constrained_counts[key]['display_name'] = model['display_name']  # Keep last seen display name
            if condition not in constrained_counts[key]['conditions']:
                constrained_counts[key]['conditions'].append(condition)

        # Constrained dimensions
        for mid, dims in result['constrained']['by_dimension'].items():
            # Find display name from model_id
            display_name = mid
            for model in result['constrained']['composite'] + result['outliers']['composite']:
                if model['model_id'] == mid:
                    display_name = model['display_name']
                    break
            key = normalize_model_name(display_name)
            constrained_counts[key]['dimensions'] += len(dims)
            if not constrained_counts[key]['display_name']:
                constrained_counts[key]['display_name'] = display_name

        # Outlier composite
        for model in result['outliers']['composite']:
            key = normalize_model_name(model['display_name'])
            outlier_counts[key]['composite'] += 1
            outlier_counts[key]['display_name'] = model['display_name']
            if condition not in outlier_counts[key]['conditions']:
                outlier_counts[key]['conditions'].append(condition)

        # Outlier dimensions
        for mid, dims in result['outliers']['by_dimension'].items():
            display_name = mid
            for model in result['constrained']['composite'] + result['outliers']['composite']:
                if model['model_id'] == mid:
                    display_name = model['display_name']
                    break
            key = normalize_model_name(display_name)
            outlier_counts[key]['dimensions'] += len(dims)
            if not outlier_counts[key]['display_name']:
                outlier_counts[key]['display_name'] = display_name

    # Sort by composite count, then dimensions
    constrained_sorted = sorted(
        [(name, data) for name, data in constrained_counts.items() if data['composite'] > 0],
        key=lambda x: (-x[1]['composite'], -x[1]['dimensions'])
    )

    outlier_sorted = sorted(
        [(name, data) for name, data in outlier_counts.items() if data['composite'] > 0],
        key=lambda x: (-x[1]['composite'], -x[1]['dimensions'])
    )

    return {
        'most_constrained': [
            {'model': data['display_name'], 'normalized_key': key,
             'composite': data['composite'], 'dimensions': data['dimensions'],
             'conditions': data['conditions']}
            for key, data in constrained_sorted
        ],
        'most_outlier': [
            {'model': data['display_name'], 'normalized_key': key,
             'composite': data['composite'], 'dimensions': data['dimensions'],
             'conditions': data['conditions']}
            for key, data in outlier_sorted
        ]
    }


def main():
    base_dir = Path("outputs/behavioral_profiles")
    output_dir = base_dir / "research_synthesis" / "cross_condition"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all conditions with median_split_classification.json
    conditions = []
    for d in sorted(base_dir.iterdir()):
        if d.is_dir() and d.name != "research_synthesis":
            if (d / "median_split_classification.json").exists():
                conditions.append(d.name)

    print(f"Found {len(conditions)} conditions: {', '.join(conditions)}")

    # Analyze each condition
    condition_results = []
    for condition in conditions:
        condition_dir = base_dir / condition
        data = load_median_split_data(condition_dir)
        if data:
            result = analyze_condition(data, condition)
            condition_results.append(result)
            print(f"  {condition}: {len(result['constrained']['composite'])} constrained, "
                  f"{len(result['outliers']['composite'])} outliers (composite)")

    # Aggregate cross-condition patterns
    aggregated = aggregate_cross_condition(condition_results)

    # Build output
    output = {
        'generated': datetime.now().isoformat(),
        'thresholds': {
            'constrained_soph_threshold': CONSTRAINED_SOPH_THRESHOLD,
            'constrained_residual_threshold': CONSTRAINED_RESIDUAL_THRESHOLD,
            'outlier_sd_threshold': OUTLIER_SD_THRESHOLD
        },
        'conditions_analyzed': conditions,
        'per_condition': condition_results,
        'cross_condition': aggregated
    }

    # Write output
    output_path = output_dir / "cross_condition_patterns.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nWrote: {output_path}")

    # Print summary
    print("\n" + "="*70)
    print("MOST CONSTRAINED MODELS (composite appearances)")
    print("="*70)
    for item in aggregated['most_constrained'][:10]:
        print(f"  {item['model']:<40} {item['composite']} composite, "
              f"{item['dimensions']} dims, conditions: {', '.join(item['conditions'])}")

    print("\n" + "="*70)
    print("MOST OUTLIER MODELS (composite appearances)")
    print("="*70)
    for item in aggregated['most_outlier'][:10]:
        print(f"  {item['model']:<40} {item['composite']} composite, "
              f"{item['dimensions']} dims, conditions: {', '.join(item['conditions'])}")


if __name__ == "__main__":
    main()
