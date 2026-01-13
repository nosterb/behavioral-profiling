#!/usr/bin/env python3
"""
Repeated-Measures ANOVA for Cross-Condition Analysis.

Tests whether condition (intervention) significantly affects disinhibition,
accounting for the repeated-measures design (same models across conditions).

Research Questions:
    1. Main effect of condition: Does disinhibition differ across conditions?
    2. Condition × Sophistication interaction: Does the slope change by condition?

Usage:
    python3 scripts/run_repeated_measures_anova.py
    python3 scripts/run_repeated_measures_anova.py --outliers-removed
    python3 scripts/run_repeated_measures_anova.py --both
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np

# Optional imports - check availability
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import pingouin as pg
    HAS_PINGOUIN = True
except ImportError:
    HAS_PINGOUIN = False


CONDITIONS = ['baseline', 'authority', 'minimal_steering', 'telemetryV3', 'urgency']
BASE_DIR = Path('outputs/behavioral_profiles')


def load_condition_data(condition: str, outliers_removed: bool = False) -> dict:
    """Load model data for a condition."""
    if outliers_removed:
        file = BASE_DIR / condition / 'outliers_removed' / 'median_split_classification.json'
    else:
        file = BASE_DIR / condition / 'median_split_classification.json'

    if not file.exists():
        return {}

    with open(file) as f:
        data = json.load(f)

    # Return dict keyed by model_id
    return {m['model_id']: m for m in data['models']}


def build_matched_dataset(outliers_removed: bool = False) -> tuple:
    """
    Build dataset with only models present in ALL conditions.

    Returns:
        tuple: (data_dict, matched_model_ids)
            data_dict: {condition: {model_id: model_data}}
            matched_model_ids: set of model IDs present in all conditions
    """
    all_data = {}
    model_sets = []

    for cond in CONDITIONS:
        data = load_condition_data(cond, outliers_removed)
        all_data[cond] = data
        model_sets.append(set(data.keys()))

    # Find models present in ALL conditions
    matched = set.intersection(*model_sets) if model_sets else set()

    return all_data, matched


def run_repeated_measures_anova(outliers_removed: bool = False) -> dict:
    """
    Run repeated-measures ANOVA on disinhibition across conditions.

    Uses pingouin if available, otherwise falls back to manual F-test.
    """
    label = "OUTLIERS REMOVED" if outliers_removed else "ORIGINAL (WITH OUTLIERS)"

    print(f"\n{'=' * 80}")
    print(f"REPEATED-MEASURES ANOVA: {label}")
    print(f"{'=' * 80}")

    # Build matched dataset
    all_data, matched_models = build_matched_dataset(outliers_removed)
    n_matched = len(matched_models)

    print(f"\nDataset: {'outliers_removed' if outliers_removed else 'original'}")
    print(f"Conditions: {len(CONDITIONS)}")
    print(f"Models matched across ALL conditions: {n_matched}")

    if n_matched < 20:
        print(f"⚠ Warning: Low sample size (n={n_matched}). Results may be unreliable.")

    # Build data matrix
    # Rows = models, Columns = conditions
    model_list = sorted(matched_models)

    # Create long-format data for pingouin
    long_data = []
    for model_id in model_list:
        for cond in CONDITIONS:
            model = all_data[cond][model_id]
            long_data.append({
                'model_id': model_id,
                'condition': cond,
                'disinhibition': model['disinhibition'],
                'sophistication': model['sophistication']
            })

    results = {
        'label': label,
        'n_models': n_matched,
        'n_conditions': len(CONDITIONS),
        'outliers_removed': outliers_removed
    }

    if HAS_PANDAS and HAS_PINGOUIN:
        df = pd.DataFrame(long_data)

        # Run repeated-measures ANOVA
        print("\n## Repeated-Measures ANOVA: Disinhibition ~ Condition")
        print("-" * 60)

        aov = pg.rm_anova(data=df, dv='disinhibition', within='condition', subject='model_id')
        print(aov.to_string())

        results['rm_anova'] = {
            'F': float(aov['F'].values[0]),
            'df1': int(aov['ddof1'].values[0]),
            'df2': int(aov['ddof2'].values[0]),
            'p_value': float(aov['p-unc'].values[0]),
            'eta_squared': float(aov['ng2'].values[0]),  # generalized eta-squared
            'sphericity': aov['sphericity'].values[0] if 'sphericity' in aov.columns else None,
            'epsilon': float(aov['eps'].values[0]) if 'eps' in aov.columns else None,
            'p_gg_corrected': float(aov['p-GG-corr'].values[0]) if 'p-GG-corr' in aov.columns else None
        }

        # Effect size interpretation
        eta_sq = results['rm_anova']['eta_squared']
        if eta_sq < 0.01:
            effect_label = "negligible"
        elif eta_sq < 0.06:
            effect_label = "small"
        elif eta_sq < 0.14:
            effect_label = "medium"
        else:
            effect_label = "large"

        print(f"\nEffect size: η²p = {eta_sq:.3f} ({effect_label})")

        # Post-hoc pairwise comparisons
        print("\n## Post-Hoc Pairwise Comparisons (Bonferroni corrected)")
        print("-" * 60)

        posthoc = pg.pairwise_tests(data=df, dv='disinhibition', within='condition',
                                     subject='model_id', padjust='bonf')

        # Filter to show comparisons with baseline and significant ones
        print("\nAll pairwise comparisons:")
        print(posthoc[['A', 'B', 'T', 'dof', 'p-unc', 'p-corr', 'hedges']].to_string())

        results['posthoc'] = []
        for _, row in posthoc.iterrows():
            results['posthoc'].append({
                'comparison': f"{row['A']} vs {row['B']}",
                't': float(row['T']),
                'df': int(row['dof']),
                'p_uncorrected': float(row['p-unc']),
                'p_corrected': float(row['p-corr']),
                'hedges_g': float(row['hedges'])
            })

        # Condition means
        print("\n## Condition Means")
        print("-" * 60)
        cond_means = df.groupby('condition')['disinhibition'].agg(['mean', 'std', 'count'])
        cond_means = cond_means.reindex(CONDITIONS)
        print(cond_means.to_string())

        results['condition_means'] = {}
        for cond in CONDITIONS:
            cond_data = df[df['condition'] == cond]['disinhibition']
            results['condition_means'][cond] = {
                'mean': float(cond_data.mean()),
                'std': float(cond_data.std()),
                'n': int(len(cond_data))
            }

        # Test for Condition × Sophistication interaction using mixed ANOVA
        print("\n## Mixed Model: Condition × Sophistication Interaction")
        print("-" * 60)

        # Median split sophistication within the matched dataset
        median_soph = df.groupby('model_id')['sophistication'].mean().median()
        df['soph_group'] = df['sophistication'].apply(lambda x: 'High' if x >= median_soph else 'Low')

        # Mixed ANOVA: condition (within) × soph_group (between)
        try:
            mixed_aov = pg.mixed_anova(data=df, dv='disinhibition', within='condition',
                                        between='soph_group', subject='model_id')
            print(mixed_aov.to_string())

            # Extract interaction
            interaction_row = mixed_aov[mixed_aov['Source'] == 'condition * soph_group']
            if len(interaction_row) > 0:
                row = interaction_row.iloc[0]
                results['interaction'] = {
                    'F': float(row['F']) if pd.notna(row['F']) else None,
                    'df1': int(row['DF1']) if 'DF1' in row and pd.notna(row['DF1']) else None,
                    'df2': int(row['DF2']) if 'DF2' in row and pd.notna(row['DF2']) else None,
                    'p_value': float(row['p-unc']) if pd.notna(row['p-unc']) else None,
                    'eta_squared': float(row['ng2']) if 'ng2' in row and pd.notna(row['ng2']) else None
                }

                int_p = results['interaction']['p_value']
                int_eta = results['interaction']['eta_squared']
                print(f"\nInteraction effect: F = {results['interaction']['F']:.2f}, p = {int_p:.4f}, η²p = {int_eta:.3f}")
                if int_p < 0.05:
                    print("  → Significant interaction: The condition effect differs by sophistication level")
                else:
                    print("  → No significant interaction: Condition effect is consistent across sophistication levels")
        except Exception as e:
            print(f"  Could not run mixed ANOVA: {e}")
            results['interaction'] = None

    elif HAS_PANDAS and HAS_SCIPY:
        # Fallback: Manual F-test using scipy
        df = pd.DataFrame(long_data)

        print("\n## One-Way Repeated Measures (Manual Calculation)")
        print("-" * 60)
        print("(pingouin not available, using scipy fallback)")

        # Group data by condition
        groups = [df[df['condition'] == c]['disinhibition'].values for c in CONDITIONS]

        # Friedman test (non-parametric alternative)
        stat, p = stats.friedmanchisquare(*groups)
        print(f"\nFriedman χ² = {stat:.3f}, p = {p:.6f}")

        results['friedman'] = {
            'chi_square': float(stat),
            'p_value': float(p)
        }

        # Condition means
        print("\n## Condition Means")
        for cond in CONDITIONS:
            vals = df[df['condition'] == cond]['disinhibition']
            print(f"  {cond}: M = {vals.mean():.3f}, SD = {vals.std():.3f}")

    else:
        print("\n⚠ Required packages not available.")
        print("  Install with: pip install pandas scipy pingouin")
        return results

    return results


def print_summary(original_results: dict, outliers_results: dict):
    """Print comparison summary."""
    print("\n" + "=" * 80)
    print("SUMMARY: REPEATED-MEASURES ANOVA COMPARISON")
    print("=" * 80)

    print(f"\n{'Metric':<35} {'Original':>20} {'Outliers Removed':>20}")
    print("-" * 80)

    # Sample size
    print(f"{'N (matched models)':<35} {original_results['n_models']:>20} {outliers_results['n_models']:>20}")

    if 'rm_anova' in original_results and 'rm_anova' in outliers_results:
        orig = original_results['rm_anova']
        outl = outliers_results['rm_anova']

        print(f"{'F statistic':<35} {orig['F']:>20.2f} {outl['F']:>20.2f}")
        print(f"{'p-value':<35} {orig['p_value']:>20.6f} {outl['p_value']:>20.6f}")
        print(f"{'η²p (effect size)':<35} {orig['eta_squared']:>20.3f} {outl['eta_squared']:>20.3f}")

        # Significance
        orig_sig = "Yes" if orig['p_value'] < 0.05 else "No"
        outl_sig = "Yes" if outl['p_value'] < 0.05 else "No"
        print(f"{'Significant (p < .05)?':<35} {orig_sig:>20} {outl_sig:>20}")

    if 'interaction' in original_results and original_results['interaction']:
        if 'interaction' in outliers_results and outliers_results['interaction']:
            orig_int = original_results['interaction']
            outl_int = outliers_results['interaction']
            print(f"\n{'Condition × Sophistication Interaction:':<35}")
            print(f"{'  F statistic':<35} {orig_int['F']:>20.2f} {outl_int['F']:>20.2f}")
            print(f"{'  p-value':<35} {orig_int['p_value']:>20.6f} {outl_int['p_value']:>20.6f}")

    # Interpretation
    print("\n" + "-" * 80)
    print("INTERPRETATION:")
    print("-" * 80)

    if 'rm_anova' in original_results:
        orig_p = original_results['rm_anova']['p_value']
        orig_eta = original_results['rm_anova']['eta_squared']

        if orig_p < 0.001:
            print(f"\n✓ SIGNIFICANT main effect of condition (p < .001)")
            print(f"  Disinhibition differs significantly across intervention conditions.")
        elif orig_p < 0.05:
            print(f"\n✓ SIGNIFICANT main effect of condition (p = {orig_p:.4f})")
        else:
            print(f"\n✗ NO significant main effect of condition (p = {orig_p:.4f})")

        # Effect size interpretation
        if orig_eta >= 0.14:
            print(f"  Effect size is LARGE (η²p = {orig_eta:.3f})")
        elif orig_eta >= 0.06:
            print(f"  Effect size is MEDIUM (η²p = {orig_eta:.3f})")
        else:
            print(f"  Effect size is SMALL (η²p = {orig_eta:.3f})")

    # Robustness check
    if 'rm_anova' in original_results and 'rm_anova' in outliers_results:
        orig_sig = original_results['rm_anova']['p_value'] < 0.05
        outl_sig = outliers_results['rm_anova']['p_value'] < 0.05

        if orig_sig == outl_sig:
            print(f"\n✓ ROBUST: Conclusions hold with and without outliers")
        else:
            print(f"\n⚠ SENSITIVE: Conclusions change when outliers are removed")


def convert_to_serializable(obj):
    """Convert numpy/pandas types to JSON-serializable Python types."""
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


def save_results(original_results: dict, outliers_results: dict):
    """Save results to JSON."""
    output = {
        'timestamp': datetime.now().isoformat(),
        'analysis': 'repeated_measures_anova',
        'conditions': CONDITIONS,
        'original': convert_to_serializable(original_results),
        'outliers_removed': convert_to_serializable(outliers_results)
    }

    output_dir = BASE_DIR / 'research_synthesis' / 'cross_condition'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'repeated_measures_anova_results.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Run repeated-measures ANOVA')
    parser.add_argument('--outliers-removed', action='store_true',
                        help='Run on outliers-removed data only')
    parser.add_argument('--both', action='store_true',
                        help='Run on both original and outliers-removed (default)')
    args = parser.parse_args()

    # Check dependencies
    if not HAS_PANDAS:
        print("Error: pandas is required. Install with: pip install pandas")
        return
    if not HAS_SCIPY:
        print("Error: scipy is required. Install with: pip install scipy")
        return
    if not HAS_PINGOUIN:
        print("Warning: pingouin not available. Install for full analysis: pip install pingouin")
        print("Falling back to basic analysis.\n")

    print("=" * 80)
    print("REPEATED-MEASURES ANOVA: Cross-Condition Analysis")
    print("=" * 80)
    print(f"\nResearch Questions:")
    print("  1. Does disinhibition significantly differ across conditions?")
    print("  2. Does the condition effect interact with sophistication level?")

    if args.outliers_removed:
        outliers_results = run_repeated_measures_anova(outliers_removed=True)
    else:
        # Default: run both
        original_results = run_repeated_measures_anova(outliers_removed=False)
        outliers_results = run_repeated_measures_anova(outliers_removed=True)

        print_summary(original_results, outliers_results)
        save_results(original_results, outliers_results)


if __name__ == '__main__':
    main()
