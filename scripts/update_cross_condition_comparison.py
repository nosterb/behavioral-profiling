#!/usr/bin/env python3
"""
Update cross-condition comparison document.

Scans all intervention conditions and generates a comparative summary table
that gets updated each time a new condition is analyzed.

Usage:
    python3 scripts/update_cross_condition_comparison.py
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

def get_available_conditions(base_dir):
    """Find all conditions with completed H1/H1a/H2 analysis.

    Returns conditions with 'baseline' first (anchor), then others alphabetically.
    """
    conditions = []

    for item in base_dir.iterdir():
        if item.is_dir() and item.name not in ['research_synthesis', 'history', 'profiles', 'visualizations']:
            classification_file = item / "median_split_classification.json"
            if classification_file.exists():
                conditions.append(item.name)

    # Sort with baseline first, then alphabetically
    other_conditions = sorted([c for c in conditions if c != 'baseline'])
    if 'baseline' in conditions:
        return ['baseline'] + other_conditions
    return other_conditions

def generate_comparison_table(conditions_data):
    """Generate markdown comparison table."""
    if not conditions_data:
        return "No conditions available for comparison.\n"

    # Header
    lines = [
        "| Metric | " + " | ".join(conditions_data.keys()) + " |",
        "|--------|" + "|".join(["--------"] * len(conditions_data)) + "|"
    ]

    # Sample size
    row = "| **N (Total)** |"
    for cond, data in conditions_data.items():
        row += f" {len(data['models'])} |"
    lines.append(row)

    # High/Low split
    row = "| **High / Low** |"
    for cond, data in conditions_data.items():
        row += f" {data['n_high_sophistication']} / {data['n_low_sophistication']} |"
    lines.append(row)

    # Median sophistication
    row = "| **Median Soph** |"
    for cond, data in conditions_data.items():
        row += f" {data['median_sophistication']:.3f} |"
    lines.append(row)

    # H1: Sophistication separation Cohen's d
    row = "| **H1: Soph d** |"
    for cond, data in conditions_data.items():
        d = data['statistics']['sophistication']['cohens_d']
        row += f" {d:.2f} |"
    lines.append(row)

    # H1a: Disinhibition Cohen's d
    row = "| **H1a: d (disinhib)** |"
    for cond, data in conditions_data.items():
        d = data['statistics']['disinhibition']['cohens_d']
        row += f" {d:.2f} |"
    lines.append(row)

    # H1a: p-value
    row = "| **H1a: p-value** |"
    for cond, data in conditions_data.items():
        p = data['statistics']['disinhibition']['p_value']
        if p < 0.001:
            row += " < .001 |"
        else:
            row += f" {p:.3f} |"
    lines.append(row)

    # H2: Correlation
    row = "| **H2: r** |"
    for cond, data in conditions_data.items():
        r = data['correlation']['sophistication_disinhibition']
        row += f" {r:.3f} |"
    lines.append(row)

    # Separator for dimension breakdown
    lines.append("| | " + " | ".join([""] * len(conditions_data)) + "|")
    lines.append("| **Dimension d:** | " + " | ".join([""] * len(conditions_data)) + "|")

    # Individual dimensions
    for dim in ['transgression', 'aggression', 'tribalism', 'grandiosity']:
        row = f"| *{dim.capitalize()}* |"
        for cond, data in conditions_data.items():
            d = data['statistics'][dim]['cohens_d']
            row += f" {d:.2f} |"
        lines.append(row)

    return "\n".join(lines)

def generate_key_findings(conditions_data):
    """Generate key findings summary."""
    if len(conditions_data) < 2:
        return "Need at least 2 conditions for comparative findings.\n"

    findings = []

    # Find baseline for comparison
    baseline_data = conditions_data.get('baseline')
    if not baseline_data:
        baseline_name = list(conditions_data.keys())[0]
        baseline_data = conditions_data[baseline_name]
        findings.append(f"**Reference condition**: {baseline_name} (baseline not available)\n")
    else:
        baseline_name = 'baseline'

    baseline_r = baseline_data['correlation']['sophistication_disinhibition']
    baseline_d = baseline_data['statistics']['disinhibition']['cohens_d']

    # Compare each condition to baseline
    for cond, data in conditions_data.items():
        if cond == baseline_name:
            continue

        r = data['correlation']['sophistication_disinhibition']
        d = data['statistics']['disinhibition']['cohens_d']

        r_diff = r - baseline_r
        d_diff = d - baseline_d

        r_direction = "stronger" if r_diff > 0 else "weaker"
        d_direction = "larger" if d_diff > 0 else "smaller"

        findings.append(f"**{cond.capitalize()} vs {baseline_name.capitalize()}**:")
        findings.append(f"  - H2 correlation: {r:.3f} ({r_direction} by {abs(r_diff):.3f})")
        findings.append(f"  - H1a effect size: d={d:.2f} ({d_direction} by {abs(d_diff):.2f})")
        findings.append("")

    return "\n".join(findings)

def generate_special_patterns_summary(conditions_data):
    """Summarize special pattern counts across conditions."""
    if not conditions_data:
        return ""

    lines = [
        "| Pattern | " + " | ".join(conditions_data.keys()) + " |",
        "|---------|" + "|".join(["--------"] * len(conditions_data)) + "|"
    ]

    # Note: These would need to be stored in the classification file
    # For now, we'll mark as TBD or extract if available
    for pattern in ['Borderline', 'Constrained', 'Outliers']:
        row = f"| {pattern} |"
        for cond, data in conditions_data.items():
            # Try to get from data, otherwise TBD
            count = "—"  # Default
            row += f" {count} |"
        lines.append(row)

    return "\n".join(lines)

def update_comparison_document(base_dir):
    """Update the cross-condition comparison document."""

    # Get available conditions
    conditions = get_available_conditions(base_dir)

    if not conditions:
        print("No conditions with completed H1/H1a/H2 analysis found.")
        return

    print(f"Found {len(conditions)} conditions: {', '.join(conditions)}")

    # Load data for each condition (preserving order: baseline first)
    conditions_data = {}
    for cond in conditions:
        data = load_condition_data(base_dir / cond)
        if data:
            conditions_data[cond] = data

    print(f"Column order: {' | '.join(conditions_data.keys())}")

    # Generate document
    doc = f"""# Cross-Condition Comparison

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Conditions**: {len(conditions_data)}

---

## Summary Table

{generate_comparison_table(conditions_data)}

---

## Key Comparative Findings

{generate_key_findings(conditions_data)}

---

## Interpretation Notes

### H1 (Group Existence) Patterns
- Sophistication separation d > 2.0 indicates well-separated groups
- This validates the median split as creating meaningful distinct groups

### H1a (Group Difference) Patterns
- Cohen's d > 0.8 indicates large effect (high vs low sophistication groups differ substantially in disinhibition)
- Larger d suggests stronger group separation in disinhibition

### H2 (Correlation) Patterns
- r > 0.5 indicates large correlation (sophistication predicts disinhibition)
- Changes in r across conditions suggest intervention effects on this relationship

### Cross-Condition Observations

*Add observations here as patterns emerge across conditions.*

---

## Methodology

- **Classification**: Median split on sophistication composite (depth + authenticity / 2)
- **H1 Test**: Cohen's d for sophistication separation between high and low groups
- **H1a Test**: Independent samples t-test comparing disinhibition between high vs low sophistication groups
- **H2 Test**: Pearson correlation between sophistication and disinhibition composite
- **Effect Sizes**: Cohen's d for group differences, Pearson r for correlations

---

## Files Referenced

"""

    # Add file references
    for cond in conditions_data.keys():
        doc += f"- `../{cond}/median_split_classification.json`\n"
        doc += f"- `../{cond}/RESEARCH_BRIEF.md`\n"

    # Write document
    output_dir = base_dir / "research_synthesis" / "cross_condition"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "CONDITION_COMPARISON.md"
    with open(output_file, 'w') as f:
        f.write(doc)

    print(f"✓ Updated: {output_file}")
    print(f"  - Conditions compared: {', '.join(conditions_data.keys())}")


def main():
    import sys

    base_dir = Path("outputs/behavioral_profiles")

    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}")
        sys.exit(1)

    update_comparison_document(base_dir)
    print("\n✓ Cross-condition comparison updated")


if __name__ == "__main__":
    main()
