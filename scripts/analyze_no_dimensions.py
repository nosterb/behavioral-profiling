#!/usr/bin/env python3
"""
Analyze H1/H1a/H2 results with dimensions suite prompts removed.

This script performs sensitivity analysis by excluding prompts that directly
probe for the 9 behavioral dimensions, testing whether the sophistication-
disinhibition relationship holds without dimension-specific probing.

Output Structure:
    outputs/behavioral_profiles/<condition>/no_dimensions/
    ├── sensitivity_analysis_info.json    # Analysis configuration and comparison
    ├── median_split_classification.json
    ├── RESEARCH_BRIEF.md                 # Dedicated brief for no_dimensions analysis
    ├── h1_bar_chart_comparison.png
    ├── h1_summary_table.png
    ├── h2_scatter_sophistication_composite.png
    ├── h2_scatter_all_dimensions.png
    └── profiles/                          # Model profiles without dimensions suite

Usage:
    python3 scripts/analyze_no_dimensions.py <condition> --regenerate-brief

Examples:
    python3 scripts/analyze_no_dimensions.py baseline --regenerate-brief
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


def generate_no_dimensions_brief(output_dir: Path, condition: str, sensitivity_info: dict,
                                  orig_data: dict, new_data: dict):
    """Generate RESEARCH_BRIEF.md for the no_dimensions subfolder."""

    # Extract comparison data
    full_stats = sensitivity_info.get('statistics', {}).get('full_dataset', {})
    no_dim_stats = sensitivity_info.get('statistics', {}).get('no_dimensions', {})
    change = sensitivity_info.get('change', {})
    config = sensitivity_info.get('config', {})

    # Calculate changes from classification data
    orig_d = orig_data['statistics']['disinhibition']['cohens_d']
    new_d = new_data['statistics']['disinhibition']['cohens_d']
    d_change = new_d - orig_d

    orig_r = orig_data['correlation']['sophistication_disinhibition']
    new_r = new_data['correlation']['sophistication_disinhibition']
    r_change = new_r - orig_r

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

    excluded = ', '.join(config.get('excluded_suites', ['dimensions']))
    included = ', '.join(config.get('included_suites', []))

    brief = f"""# Research Brief: {condition_display} (No Dimensions Suite)

**Status**: Sensitivity Analysis
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Parent Condition**: {condition}
**Analysis Type**: Prompt suite exclusion robustness check

---

## Overview

This analysis removes prompts from the **dimensions suite** (which directly probe for the 9 behavioral dimensions) to test whether the sophistication-disinhibition relationship holds without dimension-specific probing.

**Excluded Suites**: {excluded}
**Included Suites**: {included}

**Rationale**: The dimensions suite contains prompts that explicitly ask models to demonstrate specific behavioral traits. Removing these tests whether the H1a/H2 effects are artifacts of direct probing or emerge naturally from general conversation scenarios.

---

## Sample

| Metric | Full Dataset | No Dimensions |
|--------|--------------|---------------|
| **N (models)** | {n_orig} | {n_new} |
| **High-Sophistication** | {orig_data['n_high_sophistication']} | {new_data['n_high_sophistication']} |
| **Low-Sophistication** | {orig_data['n_low_sophistication']} | {new_data['n_low_sophistication']} |
| **Median Sophistication** | {orig_data['median_sophistication']:.3f} | {new_data['median_sophistication']:.3f} |

---

## Results Comparison

### H1a: Group Comparison

| Metric | Full Dataset | No Dimensions | Change |
|--------|--------------|---------------|--------|
| **Cohen's d** | {orig_d:.2f} | {new_d:.2f} | {d_change:+.2f} |
| **Effect Size** | {format_d(orig_d)} | {format_d(new_d)} | — |
| **p-value** | {format_p(orig_data['statistics']['disinhibition']['p_value'])} | {format_p(new_data['statistics']['disinhibition']['p_value'])} | — |

### H2: Correlation

| Metric | Full Dataset | No Dimensions | Change |
|--------|--------------|---------------|--------|
| **Pearson r** | {orig_r:.3f} | {new_r:.3f} | {r_change:+.3f} |

### Per-Dimension H1a Effects

| Dimension | Full Dataset d | No Dimensions d | Change |
|-----------|----------------|-----------------|--------|
"""

    for dim in ['transgression', 'aggression', 'tribalism', 'grandiosity']:
        orig_dim_d = orig_data['statistics'][dim]['cohens_d']
        new_dim_d = new_data['statistics'][dim]['cohens_d']
        dim_change = new_dim_d - orig_dim_d
        brief += f"| {dim.capitalize()} | {orig_dim_d:.2f} | {new_dim_d:.2f} | {dim_change:+.2f} |\n"

    # Interpretation
    if d_change > 0.1:
        d_interp = "Removing dimensions suite **strengthens** the H1a effect, suggesting direct probing was adding noise."
    elif d_change < -0.1:
        d_interp = "Removing dimensions suite **weakens** the H1a effect, suggesting direct probing contributed to the observed effect."
    else:
        d_interp = "H1a effect is **robust** to dimensions suite removal."

    if r_change > 0.02:
        r_interp = "H2 correlation strengthens without dimensions suite, suggesting cleaner signal from natural scenarios."
    elif r_change < -0.02:
        r_interp = "H2 correlation weakens slightly without dimensions suite."
    else:
        r_interp = "H2 correlation is stable regardless of dimensions suite inclusion."

    brief += f"""
---

## Interpretation

{d_interp}

{r_interp}

**Conclusion**: The core findings {'are robust and' if abs(d_change) <= 0.2 else 'should be interpreted with caution as they are'} {'not ' if abs(d_change) <= 0.2 else ''}{'primarily ' if abs(d_change) > 0.2 else ''}driven by dimension-specific probing. The sophistication-disinhibition relationship {'emerges naturally from general conversation scenarios' if r_change >= 0 else 'may be partially dependent on explicit trait probing'}.

---

## Files in This Directory

- `sensitivity_analysis_info.json` - Analysis configuration and comparison statistics
- `median_split_classification.json` - Classification data without dimensions suite
- `h1_bar_chart_comparison.png` - H1a group comparison visualization
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - H2 scatter with regression
- `h2_scatter_all_dimensions.png` - Per-dimension H2 scatters
- `profiles/` - Model profiles (n={n_new})

---

**Parent Analysis**: `../{condition}/RESEARCH_BRIEF.md`
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    output_path = output_dir / 'RESEARCH_BRIEF.md'
    with open(output_path, 'w') as f:
        f.write(brief)

    print(f"  ✓ Generated RESEARCH_BRIEF.md for no_dimensions")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Analyze H1/H1a/H2 results with dimensions suite removed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s baseline --regenerate-brief    # Regenerate brief for existing analysis

Output:
  Updates: outputs/behavioral_profiles/<condition>/no_dimensions/RESEARCH_BRIEF.md
        """
    )

    parser.add_argument(
        'condition',
        help='Condition name (e.g., baseline)'
    )
    parser.add_argument(
        '--regenerate-brief',
        action='store_true',
        help='Regenerate RESEARCH_BRIEF.md for existing no_dimensions directory'
    )

    args = parser.parse_args()

    condition = args.condition
    profile_dir = Path(f'outputs/behavioral_profiles/{condition}')
    output_dir = profile_dir / 'no_dimensions'

    if not profile_dir.exists():
        print(f"Error: Profile directory not found: {profile_dir}")
        sys.exit(1)

    if not output_dir.exists():
        print(f"Error: No existing no_dimensions directory at {output_dir}")
        print("The no_dimensions analysis must be created first.")
        sys.exit(1)

    if args.regenerate_brief:
        print("=" * 80)
        print(f"REGENERATE BRIEF: {condition}/no_dimensions")
        print("=" * 80)

        # Load existing data
        sensitivity_info_path = output_dir / 'sensitivity_analysis_info.json'
        orig_class_path = profile_dir / 'median_split_classification.json'
        new_class_path = output_dir / 'median_split_classification.json'

        required_files = [sensitivity_info_path, orig_class_path, new_class_path]
        if not all(p.exists() for p in required_files):
            print("Error: Missing required files for brief regeneration:")
            for p in required_files:
                status = "✓" if p.exists() else "✗"
                print(f"  {status} {p}")
            sys.exit(1)

        with open(sensitivity_info_path) as f:
            sensitivity_info = json.load(f)
        with open(orig_class_path) as f:
            orig_data = json.load(f)
        with open(new_class_path) as f:
            new_data = json.load(f)

        generate_no_dimensions_brief(output_dir, condition, sensitivity_info, orig_data, new_data)
        print(f"\nRegenerated: {output_dir}/RESEARCH_BRIEF.md")
    else:
        print("Error: Currently only --regenerate-brief is supported.")
        print("The no_dimensions analysis must be created through the profile aggregation pipeline.")
        sys.exit(1)


if __name__ == '__main__':
    main()
