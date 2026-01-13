#!/usr/bin/env python3
"""
Variability Analysis: Does Intervention Affect Response Consistency?

Analyzes whether different intervention conditions affect the variance/consistency
of model responses, not just the mean levels.

Key Metrics:
    - Standard Deviation (SD): Absolute spread
    - Coefficient of Variation (CV%): Relative spread (SD/mean × 100)
    - Variance Ratio: Compared to baseline
    - Levene's Test: Statistical test for variance equality

Usage:
    python3 scripts/analyze_variability.py
    python3 scripts/analyze_variability.py --outliers-removed
    python3 scripts/analyze_variability.py --dimension disinhibition
    python3 scripts/analyze_variability.py --output-json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

CONDITIONS = ['baseline', 'authority', 'minimal_steering', 'telemetryV3', 'urgency']
BASE_DIR = Path('outputs/behavioral_profiles')


def load_condition_data(condition: str, outliers_removed: bool = False) -> list:
    """Load model data for a condition."""
    if outliers_removed:
        file = BASE_DIR / condition / 'outliers_removed' / 'median_split_classification.json'
    else:
        file = BASE_DIR / condition / 'median_split_classification.json'

    if not file.exists():
        return []

    with open(file) as f:
        data = json.load(f)

    return data['models']


def calculate_variability_metrics(values: np.ndarray) -> dict:
    """Calculate variability metrics for a set of values."""
    return {
        'n': len(values),
        'mean': float(np.mean(values)),
        'sd': float(np.std(values, ddof=1)),
        'var': float(np.var(values, ddof=1)),
        'cv': float((np.std(values, ddof=1) / np.mean(values)) * 100) if np.mean(values) != 0 else 0,
        'range': float(np.max(values) - np.min(values)),
        'min': float(np.min(values)),
        'max': float(np.max(values))
    }


def run_variability_analysis(dimension: str = 'disinhibition', outliers_removed: bool = False) -> dict:
    """
    Run variability analysis across conditions.

    Args:
        dimension: Which dimension to analyze ('disinhibition', 'sophistication', or dimension name)
        outliers_removed: Whether to use outliers-removed data

    Returns:
        Dictionary with analysis results
    """
    label = "OUTLIERS REMOVED" if outliers_removed else "ORIGINAL"

    print(f"\n{'=' * 80}")
    print(f"VARIABILITY ANALYSIS: {dimension.upper()} ({label})")
    print(f"{'=' * 80}")

    # Load data for all conditions
    all_data = {}
    for cond in CONDITIONS:
        models = load_condition_data(cond, outliers_removed)
        if models:
            if dimension == 'disinhibition':
                values = [m['disinhibition'] for m in models]
            elif dimension == 'sophistication':
                values = [m['sophistication'] for m in models]
            else:
                # Try to get from scores
                values = [m['scores'].get(dimension, 5.0) for m in models]
            all_data[cond] = np.array(values)

    if not all_data:
        print("No data found!")
        return {}

    # Calculate metrics for each condition
    results = {
        'dimension': dimension,
        'outliers_removed': outliers_removed,
        'timestamp': datetime.now().isoformat(),
        'conditions': {}
    }

    print(f"\n{'Condition':<20} {'N':>5} {'Mean':>8} {'SD':>8} {'Var':>10} {'CV%':>8} {'Range':>10}")
    print("-" * 80)

    baseline_var = None
    for cond in CONDITIONS:
        if cond not in all_data:
            continue

        metrics = calculate_variability_metrics(all_data[cond])
        results['conditions'][cond] = metrics

        if cond == 'baseline':
            baseline_var = metrics['var']

        print(f"{cond:<20} {metrics['n']:>5} {metrics['mean']:>8.3f} {metrics['sd']:>8.3f} "
              f"{metrics['var']:>10.4f} {metrics['cv']:>8.1f} {metrics['range']:>10.3f}")

    print("-" * 80)

    # Variance ratios
    if baseline_var and baseline_var > 0:
        print(f"\n## Variance Ratio (vs Baseline)")
        print("-" * 60)
        results['variance_ratios'] = {}

        for cond in CONDITIONS:
            if cond == 'baseline' or cond not in results['conditions']:
                continue

            ratio = results['conditions'][cond]['var'] / baseline_var
            results['variance_ratios'][cond] = ratio

            if ratio > 1.5:
                direction = "↑ MORE variable"
            elif ratio < 0.67:
                direction = "↓ LESS variable"
            else:
                direction = "≈ Similar"

            print(f"  {cond:<20}: {ratio:>6.2f}x baseline variance  {direction}")

    # Statistical tests
    if HAS_SCIPY:
        print(f"\n## Levene's Test (Equality of Variances)")
        print("-" * 60)

        # Omnibus test
        stat, p = stats.levene(*[all_data[c] for c in CONDITIONS if c in all_data])
        results['levene_omnibus'] = {'W': float(stat), 'p': float(p)}
        print(f"  Omnibus: W = {stat:.3f}, p = {p:.6f}")
        if p < 0.05:
            print("  → SIGNIFICANT: Variances differ across conditions")
        else:
            print("  → Not significant: Variances are homogeneous")

        # Pairwise vs baseline
        print(f"\n## Pairwise Variance Comparisons vs Baseline")
        print("-" * 60)
        print(f"{'Condition':<20} {'Levene W':>10} {'p-value':>12} {'Sig':>6} {'Interpretation':>20}")
        print("-" * 60)

        results['pairwise_levene'] = {}
        for cond in CONDITIONS:
            if cond == 'baseline' or cond not in all_data:
                continue

            stat, p = stats.levene(all_data['baseline'], all_data[cond])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""

            if p < 0.05:
                interp = "More var" if results['conditions'][cond]['var'] > baseline_var else "Less var"
            else:
                interp = "No diff"

            results['pairwise_levene'][cond] = {'W': float(stat), 'p': float(p), 'significant': p < 0.05}
            print(f"{cond:<20} {stat:>10.3f} {p:>12.6f} {sig:>6} {interp:>20}")

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)

    sorted_by_var = sorted(results['conditions'].items(), key=lambda x: x[1]['var'])
    print(f"\nRanked by variance (low → high):")
    for i, (cond, metrics) in enumerate(sorted_by_var, 1):
        marker = " ← MOST CONSISTENT" if i == 1 else " ← MOST VARIABLE" if i == len(sorted_by_var) else ""
        print(f"  {i}. {cond:<20} (SD = {metrics['sd']:.3f}, CV = {metrics['cv']:.1f}%){marker}")

    most_consistent = sorted_by_var[0]
    most_variable = sorted_by_var[-1]
    results['summary'] = {
        'most_consistent': most_consistent[0],
        'most_variable': most_variable[0],
        'variance_ratio': most_variable[1]['var'] / most_consistent[1]['var'] if most_consistent[1]['var'] > 0 else None
    }

    print(f"\n## Key Findings:")
    print(f"  • MOST CONSISTENT: {most_consistent[0]} (SD = {most_consistent[1]['sd']:.3f})")
    print(f"  • MOST VARIABLE: {most_variable[0]} (SD = {most_variable[1]['sd']:.3f})")
    if results['summary']['variance_ratio']:
        print(f"  • Variance ratio: {results['summary']['variance_ratio']:.1f}x difference")

    return results


def convert_to_serializable(obj):
    """Convert numpy types to JSON-serializable Python types."""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif obj is None:
        return None
    else:
        return obj


def save_results(results: dict, output_file: Path):
    """Save results to JSON."""
    with open(output_file, 'w') as f:
        json.dump(convert_to_serializable(results), f, indent=2)
    print(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyze variability across conditions')
    parser.add_argument('--dimension', '-d', default='disinhibition',
                        help='Dimension to analyze (default: disinhibition)')
    parser.add_argument('--outliers-removed', action='store_true',
                        help='Use outliers-removed data')
    parser.add_argument('--both', action='store_true',
                        help='Run on both original and outliers-removed')
    parser.add_argument('--output-json', action='store_true',
                        help='Save results to JSON')

    args = parser.parse_args()

    if not HAS_SCIPY:
        print("Warning: scipy not available. Install for statistical tests: pip install scipy")

    if args.both:
        results_orig = run_variability_analysis(args.dimension, outliers_removed=False)
        results_outl = run_variability_analysis(args.dimension, outliers_removed=True)

        if args.output_json:
            output = {
                'original': results_orig,
                'outliers_removed': results_outl
            }
            output_dir = BASE_DIR / 'research_synthesis' / 'cross_condition'
            output_dir.mkdir(parents=True, exist_ok=True)
            save_results(output, output_dir / f'variability_analysis_{args.dimension}.json')
    else:
        results = run_variability_analysis(args.dimension, args.outliers_removed)

        if args.output_json:
            output_dir = BASE_DIR / 'research_synthesis' / 'cross_condition'
            output_dir.mkdir(parents=True, exist_ok=True)
            suffix = '_outliers_removed' if args.outliers_removed else ''
            save_results(results, output_dir / f'variability_analysis_{args.dimension}{suffix}.json')


if __name__ == '__main__':
    main()
