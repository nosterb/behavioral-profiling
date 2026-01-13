#!/usr/bin/env python3
"""
Analyze H1/H1a/H2 results with statistical outliers removed.

This script identifies and removes statistical outliers (models that deviate
significantly from the sophistication-disinhibition regression line) and
regenerates H1/H1a/H2 analysis in a subfolder.

Outlier Detection Method:
    1. Fit linear regression: disinhibition ~ sophistication
    2. Calculate residuals for each model
    3. Flag models with |residual| > OUTLIER_SD_THRESHOLD * residual_std
    4. Remove flagged models and regenerate analysis

Output Structure:
    outputs/behavioral_profiles/<condition>/outliers_removed/
    ├── outlier_removal_info.json       # Details of removed models
    ├── median_split_classification.json
    ├── RESEARCH_BRIEF.md               # Dedicated brief for outliers-removed analysis
    ├── h1_bar_chart_comparison.png
    ├── h1_summary_table.png
    ├── h2_scatter_sophistication_composite.png
    ├── h2_scatter_all_dimensions.png
    └── profiles/                        # Retained model profiles

Usage:
    python3 scripts/analyze_outliers_removed.py <condition>
    python3 scripts/analyze_outliers_removed.py <condition> --threshold 2.5
    python3 scripts/analyze_outliers_removed.py <condition> --dry-run
    python3 scripts/analyze_outliers_removed.py <condition> --regenerate-brief

Examples:
    python3 scripts/analyze_outliers_removed.py telemetryV3
    python3 scripts/analyze_outliers_removed.py baseline --threshold 3.0
    python3 scripts/analyze_outliers_removed.py urgency --dry-run
    python3 scripts/analyze_outliers_removed.py minimal_steering --regenerate-brief
"""

import json
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import numpy as np

# Default configuration
DEFAULT_OUTLIER_SD_THRESHOLD = 2.0
DISINHIBITION_DIMS = ['transgression', 'aggression', 'tribalism', 'grandiosity']
SOPHISTICATION_DIMS = ['depth', 'authenticity']


def load_profiles(profile_dir: Path) -> list:
    """Load all model profiles from a directory."""
    profiles = []
    profiles_dir = profile_dir / 'profiles'

    if not profiles_dir.exists():
        raise FileNotFoundError(f"No profiles directory found at {profiles_dir}")

    for profile_file in sorted(profiles_dir.glob('*.json')):
        with open(profile_file) as f:
            profile = json.load(f)
            profile['_source_file'] = profile_file.name
            profiles.append(profile)

    return profiles


def get_dimension_average(profile: dict, dim: str) -> float:
    """Get average score for a dimension from profile."""
    dimensions = profile.get('dimensions', {})
    dim_data = dimensions.get(dim, {})
    return dim_data.get('average', 5.0)


def calculate_sophistication(profile: dict) -> float:
    """Calculate sophistication composite (mean of depth + authenticity)."""
    values = [get_dimension_average(profile, dim) for dim in SOPHISTICATION_DIMS]
    return np.mean(values)


def calculate_disinhibition(profile: dict) -> float:
    """Calculate disinhibition composite (mean of 4 dimensions)."""
    values = [get_dimension_average(profile, dim) for dim in DISINHIBITION_DIMS]
    return np.mean(values)


def identify_outliers(profiles: list, threshold_sd: float = DEFAULT_OUTLIER_SD_THRESHOLD) -> tuple:
    """
    Identify statistical outliers based on residuals from regression line.

    Method:
        1. Calculate sophistication and disinhibition for each model
        2. Fit linear regression: disinhibition = m * sophistication + b
        3. Calculate residuals (actual - predicted)
        4. Flag models where |residual| > threshold_sd * std(residuals)

    Args:
        profiles: List of model profile dictionaries
        threshold_sd: Number of standard deviations for outlier threshold

    Returns:
        tuple: (outliers, non_outliers, stats)
            - outliers: List of outlier model data with residual info
            - non_outliers: List of non-outlier model data
            - stats: Dict with regression and residual statistics
    """
    # Calculate sophistication and disinhibition for all models
    data = []
    for p in profiles:
        soph = calculate_sophistication(p)
        disinhib = calculate_disinhibition(p)
        model_name = p.get('model_name', 'unknown')
        data.append({
            'profile': p,
            'model_id': model_name,
            'display_name': model_name,
            'sophistication': soph,
            'disinhibition': disinhib,
            '_source_file': p.get('_source_file', '')
        })

    # Fit regression line
    all_x = np.array([d['sophistication'] for d in data])
    all_y = np.array([d['disinhibition'] for d in data])

    z = np.polyfit(all_x, all_y, 1)
    slope, intercept = z[0], z[1]
    p_func = np.poly1d(z)
    predicted = p_func(all_x)

    # Calculate residuals
    residuals = all_y - predicted
    residual_std = np.std(residuals)
    residual_mean = np.mean(residuals)
    threshold = threshold_sd * residual_std

    # Calculate correlation
    correlation = np.corrcoef(all_x, all_y)[0, 1]

    # Identify outliers
    outliers = []
    non_outliers = []

    for i, d in enumerate(data):
        d['residual'] = float(residuals[i])
        d['predicted'] = float(predicted[i])
        d['sd_from_line'] = float(abs(residuals[i]) / residual_std) if residual_std > 0 else 0
        d['is_outlier'] = abs(residuals[i]) > threshold

        if d['is_outlier']:
            outliers.append(d)
        else:
            non_outliers.append(d)

    stats = {
        'regression': {
            'slope': float(slope),
            'intercept': float(intercept),
            'correlation': float(correlation)
        },
        'residuals': {
            'mean': float(residual_mean),
            'std': float(residual_std),
            'threshold': float(threshold),
            'threshold_sd': threshold_sd
        },
        'counts': {
            'total': len(data),
            'outliers': len(outliers),
            'retained': len(non_outliers)
        }
    }

    return outliers, non_outliers, stats


def create_outlier_removed_profiles(source_dir: Path, target_dir: Path, non_outlier_ids: set) -> int:
    """
    Copy profiles for non-outlier models to target directory.

    Args:
        source_dir: Source profile directory
        target_dir: Target directory for outlier-removed analysis
        non_outlier_ids: Set of model names to retain

    Returns:
        Number of profiles copied
    """
    source_profiles = source_dir / 'profiles'
    target_profiles = target_dir / 'profiles'
    target_profiles.mkdir(parents=True, exist_ok=True)

    # Create history directory
    (target_dir / 'history').mkdir(exist_ok=True)

    copied = 0
    for profile_file in source_profiles.glob('*.json'):
        with open(profile_file) as f:
            profile = json.load(f)

        model_name = profile.get('model_name', '')
        if model_name in non_outlier_ids:
            shutil.copy(profile_file, target_profiles / profile_file.name)
            copied += 1

    # Copy contributions.json if it exists
    contrib_file = source_dir / 'history' / 'contributions.json'
    if contrib_file.exists():
        shutil.copy(contrib_file, target_dir / 'history' / 'contributions.json')

    return copied


def run_h1_h2_analysis(output_dir: Path, condition: str) -> bool:
    """
    Run H1/H1a/H2 analysis scripts on the outlier-removed data.

    Args:
        output_dir: Directory containing outlier-removed profiles
        condition: Original condition name (for relative path construction)

    Returns:
        True if all stages succeeded
    """
    import subprocess

    # Construct relative intervention path for scripts that expect it
    relative_intervention = f"{condition}/outliers_removed"
    success = True

    # Stage 2: Median split classification
    print("\nStage 2: Calculating median split...")
    result = subprocess.run(
        ['python3', 'scripts/calculate_median_split.py', str(output_dir)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ✗ Error: {result.stderr[:500]}")
        return False

    # Print summary from output
    lines = result.stdout.strip().split('\n')
    for line in lines[-25:]:
        if line.strip():
            print(f"  {line}")

    # Stage 3a: H1a visualizations
    print("\nStage 3a: Generating H1a visualizations...")
    result = subprocess.run(
        ['python3', 'scripts/create_h1_bar_chart.py', relative_intervention],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ✗ Warning: {result.stderr[:300]}")
        success = False
    else:
        print("  ✓ H1a visualizations created")

    # Stage 3b: H2 scatter plots
    print("\nStage 3b: Generating H2 scatter plots...")
    result = subprocess.run(
        ['python3', 'scripts/create_h2_color_coded_scatters.py', relative_intervention],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ✗ Warning: {result.stderr[:300]}")
        success = False
    else:
        print("  ✓ H2 scatter plots created")

    return success


def print_comparison(orig_path: Path, new_path: Path, outlier_count: int):
    """Print comparison table between original and outlier-removed results."""
    if not orig_path.exists() or not new_path.exists():
        print("  ⚠ Could not load classification files for comparison")
        return

    with open(orig_path) as f:
        orig = json.load(f)
    with open(new_path) as f:
        new = json.load(f)

    print(f"\n{'Metric':<30} {'With Outliers':>15} {'Without Outliers':>18} {'Change':>12}")
    print("-" * 75)

    # Sample size
    orig_n = orig['n_high_sophistication'] + orig['n_low_sophistication']
    new_n = new['n_high_sophistication'] + new['n_low_sophistication']
    print(f"{'N (total models)':<30} {orig_n:>15} {new_n:>18} {-outlier_count:>+12}")

    # Median sophistication
    print(f"{'Median Sophistication':<30} {orig['median_sophistication']:>15.3f} {new['median_sophistication']:>18.3f} {new['median_sophistication'] - orig['median_sophistication']:>+12.3f}")

    # H2 correlation
    orig_r = orig['correlation']['sophistication_disinhibition']
    new_r = new['correlation']['sophistication_disinhibition']
    print(f"{'H2: r (correlation)':<30} {orig_r:>15.3f} {new_r:>18.3f} {new_r - orig_r:>+12.3f}")

    # H1a effect size
    orig_d = orig['statistics']['disinhibition']['cohens_d']
    new_d = new['statistics']['disinhibition']['cohens_d']
    print(f"{'H1a: d (effect size)':<30} {orig_d:>15.2f} {new_d:>18.2f} {new_d - orig_d:>+12.2f}")

    # P-values
    orig_p = orig['statistics']['disinhibition']['p_value']
    new_p = new['statistics']['disinhibition']['p_value']
    print(f"{'H1a: p-value':<30} {orig_p:>15.6f} {new_p:>18.6f}")

    print("-" * 75)

    # Interpretation
    r_change = new_r - orig_r
    d_change = new_d - orig_d

    print("\nInterpretation:")
    if r_change > 0.01:
        print(f"  • H2 correlation strengthened by {r_change:+.3f}")
    elif r_change < -0.01:
        print(f"  • H2 correlation weakened by {r_change:+.3f}")
    else:
        print(f"  • H2 correlation essentially unchanged ({r_change:+.3f})")

    if d_change > 0.1:
        print(f"  • H1a effect size increased by {d_change:+.2f} (stronger group difference)")
    elif d_change < -0.1:
        print(f"  • H1a effect size decreased by {d_change:+.2f} (weaker group difference)")
    else:
        print(f"  • H1a effect size essentially unchanged ({d_change:+.2f})")


def generate_outlier_brief(output_dir: Path, condition: str, outlier_info: dict,
                           orig_data: dict, new_data: dict):
    """Generate RESEARCH_BRIEF.md for the outliers_removed subfolder."""
    from datetime import datetime

    # Calculate changes
    orig_d = orig_data['statistics']['disinhibition']['cohens_d']
    new_d = new_data['statistics']['disinhibition']['cohens_d']
    d_change = new_d - orig_d

    orig_r = orig_data['correlation']['sophistication_disinhibition']
    new_r = new_data['correlation']['sophistication_disinhibition']
    r_change = new_r - orig_r

    n_outliers = len(outlier_info.get('outliers_removed', []))
    n_orig = len(orig_data.get('models', []))
    n_new = len(new_data.get('models', []))

    # Format condition name
    condition_display = condition.replace('_', ' ').title()

    # Helper functions
    def format_p(p):
        if p < 0.001:
            return "p < .001"
        elif p < 0.01:
            return "p < .01"
        else:
            return f"p = {p:.3f}"

    def format_d(d):
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    brief = f"""# Research Brief: {condition_display} (Outliers Removed)

**Status**: Sensitivity Analysis
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Parent Condition**: {condition}
**Analysis Type**: Outlier-removed robustness check

---

## Overview

This analysis removes statistical outliers from the {condition_display} condition to test the robustness of H1a and H2 findings.

**Outlier Detection**: Models with |residual| > {outlier_info.get('config', {}).get('outlier_sd_threshold', 2.0)} SD from the sophistication-disinhibition regression line.

---

## Sample

| Metric | Original | Outliers Removed |
|--------|----------|------------------|
| **N** | {n_orig} | {n_new} |
| **Outliers Removed** | — | {n_outliers} |
| **High-Sophistication** | {orig_data['n_high_sophistication']} | {new_data['n_high_sophistication']} |
| **Low-Sophistication** | {orig_data['n_low_sophistication']} | {new_data['n_low_sophistication']} |
| **Median Sophistication** | {orig_data['median_sophistication']:.3f} | {new_data['median_sophistication']:.3f} |

---

## Outliers Removed ({n_outliers})

"""

    for o in outlier_info.get('outliers_removed', []):
        model_id = o.get('model_id', 'Unknown')
        soph = o.get('sophistication', 0)
        disinhib = o.get('disinhibition', 0)
        sd = o.get('sd_from_line', 0)
        direction = "above" if o.get('residual', 0) > 0 else "below"
        brief += f"- **{model_id}**: Soph={soph:.2f}, Disinhib={disinhib:.2f}, {sd:.1f} SD {direction} line\n"

    brief += f"""
---

## Results Comparison

### H1a: Group Comparison

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Cohen's d** | {orig_d:.2f} | {new_d:.2f} | {d_change:+.2f} |
| **Effect Size** | {format_d(orig_d)} | {format_d(new_d)} | — |
| **p-value** | {format_p(orig_data['statistics']['disinhibition']['p_value'])} | {format_p(new_data['statistics']['disinhibition']['p_value'])} | — |

### H2: Correlation

| Metric | Original | Outliers Removed | Change |
|--------|----------|------------------|--------|
| **Pearson r** | {orig_r:.3f} | {new_r:.3f} | {r_change:+.3f} |

### Per-Dimension H1a Effects

| Dimension | Original d | Outliers Removed d | Change |
|-----------|------------|-------------------|--------|
"""

    for dim in ['transgression', 'aggression', 'tribalism', 'grandiosity']:
        orig_dim_d = orig_data['statistics'][dim]['cohens_d']
        new_dim_d = new_data['statistics'][dim]['cohens_d']
        dim_change = new_dim_d - orig_dim_d
        brief += f"| {dim.capitalize()} | {orig_dim_d:.2f} | {new_dim_d:.2f} | {dim_change:+.2f} |\n"

    # Interpretation
    if d_change > 0.1:
        d_interp = "Removing outliers **strengthens** the H1a effect, suggesting outliers were noise."
    elif d_change < -0.1:
        d_interp = "Removing outliers **weakens** the H1a effect, suggesting outliers contributed to the observed effect."
    else:
        d_interp = "H1a effect is **robust** to outlier removal."

    if r_change > 0.02:
        r_interp = "H2 correlation strengthens without outliers."
    elif r_change < -0.02:
        r_interp = "H2 correlation weakens slightly without outliers."
    else:
        r_interp = "H2 correlation is stable regardless of outliers."

    brief += f"""
---

## Interpretation

{d_interp}

{r_interp}

**Conclusion**: The core findings {'are robust and' if d_change >= 0 else 'should be interpreted with caution as they are partially'} {'not ' if d_change >= 0 else ''}driven by outlier models.

---

## Files in This Directory

- `outlier_removal_info.json` - Details of removed models and detection parameters
- `median_split_classification.json` - Classification data without outliers
- `h1_bar_chart_comparison.png` - H1a group comparison visualization
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - H2 scatter with regression
- `h2_scatter_all_dimensions.png` - Per-dimension H2 scatters
- `profiles/` - Retained model profiles (n={n_new})

---

**Parent Analysis**: `../{condition}/RESEARCH_BRIEF.md`
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    output_path = output_dir / 'RESEARCH_BRIEF.md'
    with open(output_path, 'w') as f:
        f.write(brief)

    print(f"  ✓ Generated RESEARCH_BRIEF.md for outliers_removed")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Analyze H1/H1a/H2 results with statistical outliers removed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s telemetryV3                    # Default 2.0 SD threshold
  %(prog)s baseline --threshold 2.5       # Custom threshold
  %(prog)s urgency --dry-run              # Show what would be removed
  %(prog)s authority --threshold 1.5      # More aggressive removal

Output:
  Creates subfolder: outputs/behavioral_profiles/<condition>/outliers_removed/
        """
    )

    parser.add_argument(
        'condition',
        help='Condition name (e.g., baseline, telemetryV3, authority)'
    )
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=DEFAULT_OUTLIER_SD_THRESHOLD,
        help=f'SD threshold for outlier detection (default: {DEFAULT_OUTLIER_SD_THRESHOLD})'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show outliers without creating output files'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing outliers_removed directory'
    )
    parser.add_argument(
        '--regenerate-brief',
        action='store_true',
        help='Regenerate RESEARCH_BRIEF.md for existing outliers_removed directory without re-running analysis'
    )

    args = parser.parse_args()

    condition = args.condition
    threshold_sd = args.threshold
    profile_dir = Path(f'outputs/behavioral_profiles/{condition}')
    output_dir = profile_dir / 'outliers_removed'

    if not profile_dir.exists():
        print(f"Error: Profile directory not found: {profile_dir}")
        sys.exit(1)

    # Handle --regenerate-brief: regenerate brief for existing outliers_removed without re-running analysis
    if args.regenerate_brief:
        if not output_dir.exists():
            print(f"Error: No existing outliers_removed directory at {output_dir}")
            print("Run without --regenerate-brief to perform outlier analysis first.")
            sys.exit(1)

        print("=" * 80)
        print(f"REGENERATE BRIEF: {condition}/outliers_removed")
        print("=" * 80)

        # Load existing data
        outlier_info_path = output_dir / 'outlier_removal_info.json'
        orig_class_path = profile_dir / 'median_split_classification.json'
        new_class_path = output_dir / 'median_split_classification.json'

        if not all(p.exists() for p in [outlier_info_path, orig_class_path, new_class_path]):
            print("Error: Missing required files for brief regeneration:")
            for p in [outlier_info_path, orig_class_path, new_class_path]:
                status = "✓" if p.exists() else "✗"
                print(f"  {status} {p}")
            sys.exit(1)

        with open(outlier_info_path) as f:
            outlier_info = json.load(f)
        with open(orig_class_path) as f:
            orig_data = json.load(f)
        with open(new_class_path) as f:
            new_data = json.load(f)

        generate_outlier_brief(output_dir, condition, outlier_info, orig_data, new_data)
        print(f"\nRegenerated: {output_dir}/RESEARCH_BRIEF.md")
        sys.exit(0)

    print("=" * 80)
    print(f"OUTLIER REMOVAL ANALYSIS: {condition}")
    print("=" * 80)
    print(f"Threshold: {threshold_sd} SD from regression line")
    if args.dry_run:
        print("Mode: DRY RUN (no files will be created)")

    # Load profiles
    print(f"\nLoading profiles from {profile_dir}...")
    try:
        profiles = load_profiles(profile_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    print(f"Loaded {len(profiles)} profiles")

    # Identify outliers
    print(f"\nIdentifying outliers (|residual| > {threshold_sd} SD)...")
    outliers, non_outliers, stats = identify_outliers(profiles, threshold_sd)

    print(f"\nOutlier Detection Results:")
    print(f"  Regression: disinhibition = {stats['regression']['slope']:.4f} * sophistication + {stats['regression']['intercept']:.4f}")
    print(f"  Correlation: r = {stats['regression']['correlation']:.4f}")
    print(f"  Residual SD: {stats['residuals']['std']:.4f}")
    print(f"  Threshold: ±{stats['residuals']['threshold']:.4f}")
    print(f"  Total models: {stats['counts']['total']}")
    print(f"  Outliers: {stats['counts']['outliers']}")
    print(f"  Retained: {stats['counts']['retained']}")

    if outliers:
        print(f"\nOutlier Models ({len(outliers)}):")
        for o in sorted(outliers, key=lambda x: abs(x['residual']), reverse=True):
            direction = "above" if o['residual'] > 0 else "below"
            print(f"  • {o['display_name']}")
            print(f"    Sophistication: {o['sophistication']:.3f}")
            print(f"    Disinhibition: {o['disinhibition']:.3f}")
            print(f"    Residual: {o['residual']:+.4f} ({direction} regression line)")
            print(f"    SD from line: {o['sd_from_line']:.2f}")
    else:
        print("\nNo outliers found at this threshold!")
        if not args.dry_run:
            print("No output directory created.")
        sys.exit(0)

    # Dry run stops here
    if args.dry_run:
        print(f"\n{'=' * 80}")
        print("DRY RUN COMPLETE - No files created")
        print("=" * 80)
        sys.exit(0)

    # Check for existing output
    if output_dir.exists() and not args.force:
        print(f"\n⚠ Output directory already exists: {output_dir}")
        print("Use --force to overwrite")
        sys.exit(1)

    # Create output directory with non-outlier profiles
    print(f"\nCreating outlier-removed directory: {output_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    non_outlier_ids = {d['model_id'] for d in non_outliers}
    copied = create_outlier_removed_profiles(profile_dir, output_dir, non_outlier_ids)
    print(f"Copied {copied} profiles to {output_dir}/profiles/")

    # Save outlier removal info
    outlier_info = {
        'condition': condition,
        'timestamp': datetime.now().isoformat(),
        'config': {
            'outlier_sd_threshold': threshold_sd,
            'disinhibition_dimensions': DISINHIBITION_DIMS,
            'sophistication_dimensions': SOPHISTICATION_DIMS
        },
        'statistics': stats,
        'outliers_removed': [
            {
                'model_id': o['model_id'],
                'display_name': o['display_name'],
                'sophistication': o['sophistication'],
                'disinhibition': o['disinhibition'],
                'residual': o['residual'],
                'sd_from_line': o['sd_from_line']
            }
            for o in sorted(outliers, key=lambda x: abs(x['residual']), reverse=True)
        ],
        'models_retained': sorted([d['model_id'] for d in non_outliers])
    }

    with open(output_dir / 'outlier_removal_info.json', 'w') as f:
        json.dump(outlier_info, f, indent=2)
    print(f"Saved: {output_dir}/outlier_removal_info.json")

    # Run H1/H1a/H2 analysis
    print(f"\n{'=' * 80}")
    print("RUNNING H1/H1a/H2 ANALYSIS ON OUTLIER-REMOVED DATA")
    print("=" * 80)

    success = run_h1_h2_analysis(output_dir, condition)

    # Print comparison
    print(f"\n{'=' * 80}")
    print("COMPARISON: WITH vs WITHOUT OUTLIERS")
    print("=" * 80)

    orig_class = profile_dir / 'median_split_classification.json'
    new_class = output_dir / 'median_split_classification.json'
    print_comparison(orig_class, new_class, len(outliers))

    # Generate dedicated RESEARCH_BRIEF.md for outliers_removed subfolder
    if orig_class.exists() and new_class.exists():
        with open(orig_class) as f:
            orig_data = json.load(f)
        with open(new_class) as f:
            new_data = json.load(f)
        generate_outlier_brief(output_dir, condition, outlier_info, orig_data, new_data)

    # Summary
    print(f"\n{'=' * 80}")
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nOutput files in: {output_dir}/")
    print("  - outlier_removal_info.json")
    print("  - median_split_classification.json")
    print("  - RESEARCH_BRIEF.md")
    print("  - h1_bar_chart_comparison.png")
    print("  - h1_summary_table.png")
    print("  - h2_scatter_sophistication_composite.png")
    print("  - h2_scatter_all_dimensions.png")
    print(f"  - profiles/ ({copied} models)")

    if not success:
        print("\n⚠ Some visualizations may have failed - check output directory")
        sys.exit(1)


if __name__ == '__main__':
    main()
