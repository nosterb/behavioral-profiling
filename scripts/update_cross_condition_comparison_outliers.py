#!/usr/bin/env python3
"""
Update cross-condition comparison document for outliers-removed analysis.

Scans all intervention conditions' outliers_removed subfolders and generates
a comparative summary table alongside the original (with outliers) data.

Usage:
    python3 scripts/update_cross_condition_comparison_outliers.py
"""

import json
from pathlib import Path
from datetime import datetime


def load_condition_data(condition_dir):
    """Load median split classification data for a condition."""
    classification_file = condition_dir / "median_split_classification.json"
    if not classification_file.exists():
        return None

    with open(classification_file, 'r') as f:
        return json.load(f)


def load_outlier_info(condition_dir):
    """Load outlier removal info for a condition."""
    outlier_file = condition_dir / "outliers_removed" / "outlier_removal_info.json"
    if not outlier_file.exists():
        return None

    with open(outlier_file, 'r') as f:
        return json.load(f)


def get_available_conditions(base_dir):
    """Find all conditions with completed outliers_removed analysis.

    Returns conditions with 'baseline' first (anchor), then others alphabetically.
    """
    conditions = []

    for item in base_dir.iterdir():
        if item.is_dir() and item.name not in ['research_synthesis', 'history', 'profiles', 'visualizations']:
            # Check for outliers_removed subfolder with classification
            outliers_classification = item / "outliers_removed" / "median_split_classification.json"
            original_classification = item / "median_split_classification.json"
            if outliers_classification.exists() and original_classification.exists():
                conditions.append(item.name)

    # Sort with baseline first, then alphabetically
    other_conditions = sorted([c for c in conditions if c != 'baseline'])
    if 'baseline' in conditions:
        return ['baseline'] + other_conditions
    return other_conditions


def generate_comparison_table(original_data, outliers_data):
    """Generate markdown comparison table showing both original and outliers-removed."""
    if not original_data:
        return "No conditions available for comparison.\n"

    conditions = list(original_data.keys())

    # Header
    lines = [
        "| Metric | " + " | ".join(conditions) + " |",
        "|--------|" + "|".join(["--------"] * len(conditions)) + "|"
    ]

    # Sample size (original → outliers removed)
    row = "| **N** |"
    for cond in conditions:
        orig_n = len(original_data[cond]['models'])
        outl_n = len(outliers_data[cond]['models'])
        row += f" {orig_n} → {outl_n} |"
    lines.append(row)

    # Median sophistication
    row = "| **Median Soph** |"
    for cond in conditions:
        orig = original_data[cond]['median_sophistication']
        outl = outliers_data[cond]['median_sophistication']
        diff = outl - orig
        sign = "+" if diff >= 0 else ""
        row += f" {orig:.2f} → {outl:.2f} ({sign}{diff:.2f}) |"
    lines.append(row)

    # H1: Disinhibition Cohen's d
    row = "| **H1: d** |"
    for cond in conditions:
        orig = original_data[cond]['statistics']['disinhibition']['cohens_d']
        outl = outliers_data[cond]['statistics']['disinhibition']['cohens_d']
        diff = outl - orig
        sign = "+" if diff >= 0 else ""
        row += f" {orig:.2f} → {outl:.2f} ({sign}{diff:.2f}) |"
    lines.append(row)

    # H2: Correlation
    row = "| **H2: r** |"
    for cond in conditions:
        orig = original_data[cond]['correlation']['sophistication_disinhibition']
        outl = outliers_data[cond]['correlation']['sophistication_disinhibition']
        diff = outl - orig
        sign = "+" if diff >= 0 else ""
        row += f" {orig:.3f} → {outl:.3f} ({sign}{diff:.3f}) |"
    lines.append(row)

    return "\n".join(lines)


def generate_outliers_summary(base_dir, conditions):
    """Generate summary of which models were removed as outliers."""
    lines = [
        "| Condition | Outliers Removed | SD from Line |",
        "|-----------|------------------|--------------|"
    ]

    for cond in conditions:
        info = load_outlier_info(base_dir / cond)
        if not info:
            lines.append(f"| **{cond}** | (no info) | — |")
            continue

        # Handle both formats: 'outliers_removed' (list) or 'outliers' (list)
        outliers = None
        if isinstance(info.get('outliers_removed'), list):
            outliers = info['outliers_removed']
        elif isinstance(info.get('outliers'), list):
            outliers = info['outliers']

        if outliers:
            for i, o in enumerate(outliers):
                model = o.get('display_name', o.get('model_id', 'Unknown'))
                sd = o.get('sd_from_line', 0)
                if i == 0:
                    lines.append(f"| **{cond}** | {model} | {sd:.2f} |")
                else:
                    lines.append(f"| | {model} | {sd:.2f} |")
        else:
            lines.append(f"| **{cond}** | (none) | — |")

    return "\n".join(lines)


def generate_robustness_assessment(original_data, outliers_data):
    """Generate robustness assessment for each condition."""
    lines = []

    for cond in original_data.keys():
        orig_d = original_data[cond]['statistics']['disinhibition']['cohens_d']
        outl_d = outliers_data[cond]['statistics']['disinhibition']['cohens_d']
        orig_r = original_data[cond]['correlation']['sophistication_disinhibition']
        outl_r = outliers_data[cond]['correlation']['sophistication_disinhibition']

        d_change = outl_d - orig_d
        r_change = outl_r - orig_r

        # Assess robustness
        if abs(d_change) < 0.2 and abs(r_change) < 0.05:
            robustness = "**Highly Robust** - Results stable with/without outliers"
        elif abs(d_change) < 0.5 and abs(r_change) < 0.1:
            robustness = "**Moderately Robust** - Minor sensitivity to outliers"
        else:
            robustness = "**Sensitive** - Results substantially affected by outliers"

        lines.append(f"**{cond.capitalize()}**: {robustness}")
        lines.append(f"  - H1 change: d {orig_d:.2f} → {outl_d:.2f} (Δ = {d_change:+.2f})")
        lines.append(f"  - H2 change: r {orig_r:.3f} → {outl_r:.3f} (Δ = {r_change:+.3f})")
        lines.append("")

    return "\n".join(lines)


def update_comparison_document(base_dir):
    """Update the cross-condition comparison document for outliers-removed."""

    # Get available conditions
    conditions = get_available_conditions(base_dir)

    if not conditions:
        print("No conditions with completed outliers_removed analysis found.")
        return

    print(f"Found {len(conditions)} conditions with outliers_removed: {', '.join(conditions)}")

    # Load original and outliers-removed data
    original_data = {}
    outliers_data = {}

    for cond in conditions:
        orig = load_condition_data(base_dir / cond)
        outl = load_condition_data(base_dir / cond / "outliers_removed")
        if orig and outl:
            original_data[cond] = orig
            outliers_data[cond] = outl

    # Generate document
    doc = f"""# Cross-Condition Comparison: Outlier Sensitivity Analysis

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Conditions**: {len(original_data)}
**Threshold**: 2.0 SD from regression line

---

## Summary Table (Original → Outliers Removed)

{generate_comparison_table(original_data, outliers_data)}

---

## Outliers Removed by Condition

{generate_outliers_summary(base_dir, conditions)}

---

## Robustness Assessment

{generate_robustness_assessment(original_data, outliers_data)}

---

## Interpretation

### What This Analysis Shows

This sensitivity analysis tests whether the H1 and H2 findings are robust to the
removal of statistical outliers (models > 2 SD from the sophistication-disinhibition
regression line).

### Key Questions Answered

1. **Are findings robust?** If H1 (d) and H2 (r) remain similar after outlier removal,
   the findings are robust and not driven by a few extreme cases.

2. **Which conditions are most affected?** Large changes indicate sensitivity to
   specific outlier models.

3. **Are outliers consistent across conditions?** The same model appearing as an
   outlier in multiple conditions may indicate systematic measurement issues.

### Robustness Criteria

| Change | H1 (d) | H2 (r) | Interpretation |
|--------|--------|--------|----------------|
| Minimal | < 0.2 | < 0.05 | Highly robust |
| Moderate | 0.2-0.5 | 0.05-0.1 | Moderately robust |
| Large | > 0.5 | > 0.1 | Sensitive to outliers |

---

## Files Referenced

"""

    # Add file references
    for cond in original_data.keys():
        doc += f"- `../{cond}/median_split_classification.json`\n"
        doc += f"- `../{cond}/outliers_removed/median_split_classification.json`\n"
        doc += f"- `../{cond}/outliers_removed/outlier_removal_info.json`\n"

    # Write document
    output_dir = base_dir / "research_synthesis" / "cross_condition"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "OUTLIERS_REMOVED_COMPARISON.md"
    with open(output_file, 'w') as f:
        f.write(doc)

    print(f"✓ Updated: {output_file}")


def main():
    import sys

    base_dir = Path("outputs/behavioral_profiles")

    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}")
        sys.exit(1)

    update_comparison_document(base_dir)
    print("\n✓ Outliers-removed cross-condition comparison updated")


if __name__ == "__main__":
    main()
