#!/usr/bin/env python3
"""
Validate data consistency for a condition.

Checks that all assets (RESEARCH_BRIEF.md, visualizations) match source JSON.
This script ensures reproducibility and data integrity before publication.

Usage:
    python3 scripts/validate_condition_data.py baseline
    python3 scripts/validate_condition_data.py --all
    python3 scripts/validate_condition_data.py --all --strict  # Exit non-zero on any warning
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

CONDITIONS = [
    "baseline", "authority", "urgency", "minimal_steering",
    "telemetryV3", "reminder", "naturalistic", "naturalistic_50"
]

BASE_DIR = Path("outputs/behavioral_profiles")

# Tolerances for floating point comparison
TOLERANCE_D = 0.01  # Cohen's d tolerance
TOLERANCE_R = 0.001  # Pearson r tolerance
TOLERANCE_MEAN = 0.01  # Mean value tolerance


# ============================================================================
# EXTRACTION HELPERS
# ============================================================================

def extract_stats_from_brief(brief_path: Path) -> Dict[str, Any]:
    """
    Parse RESEARCH_BRIEF.md and extract key statistics.

    Returns dict with extracted values or None if extraction fails.
    """
    if not brief_path.exists():
        return {"error": f"Brief not found: {brief_path}"}

    content = brief_path.read_text()
    extracted = {}

    # Extract N from sample line
    n_match = re.search(r'\*\*Sample\*\*:\s*N\s*=\s*(\d+)', content)
    if n_match:
        extracted['n'] = int(n_match.group(1))

    # Extract median sophistication
    median_match = re.search(r'\*\*Median\*\*:\s*([\d.]+)', content)
    if median_match:
        extracted['median_sophistication'] = float(median_match.group(1))

    # Extract High/Low split counts
    high_match = re.search(r'\*\*High-Sophistication\*\*:\s*n\s*=\s*(\d+)', content)
    low_match = re.search(r'\*\*Low-Sophistication\*\*:\s*n\s*=\s*(\d+)', content)
    if high_match and low_match:
        extracted['n_high'] = int(high_match.group(1))
        extracted['n_low'] = int(low_match.group(1))

    # Extract H1a d (disinhibition Cohen's d)
    h1a_match = re.search(r'\*\*t\(\d+\)\s*=\s*[\d.]+,\s*p\s*<\s*\.001,\s*d\s*=\s*([\d.]+)\*\*', content)
    if h1a_match:
        extracted['h1a_d'] = float(h1a_match.group(1))

    # Extract H2 r (correlation)
    h2_match = re.search(r'\*\*r\s*=\s*([\d.]+),\s*p\s*<\s*\.001\*\*', content)
    if h2_match:
        extracted['h2_r'] = float(h2_match.group(1))

    # Extract H1 sophistication d
    h1_soph_match = re.search(r'\*\*d\s*=\s*([\d.]+)\*\*\s*\(large effect\)\s*\n\nThe median split', content)
    if h1_soph_match:
        extracted['h1_soph_d'] = float(h1_soph_match.group(1))

    # Extract outlier sensitivity stats
    outlier_section = re.search(
        r'## Outlier Sensitivity.*?\| \*\*N\*\* \| (\d+) \| (\d+) \|.*?\| \*\*H1a: d\*\* \| ([\d.]+) \| ([\d.]+) \|.*?\| \*\*H2: r\*\* \| ([\d.]+) \| ([\d.]+) \|',
        content, re.DOTALL
    )
    if outlier_section:
        extracted['outlier_n_original'] = int(outlier_section.group(1))
        extracted['outlier_n_removed'] = int(outlier_section.group(2))
        extracted['outlier_h1a_d_original'] = float(outlier_section.group(3))
        extracted['outlier_h1a_d_removed'] = float(outlier_section.group(4))
        extracted['outlier_h2_r_original'] = float(outlier_section.group(5))
        extracted['outlier_h2_r_removed'] = float(outlier_section.group(6))

    return extracted


def extract_stats_from_outlier_brief(brief_path: Path) -> Dict[str, Any]:
    """
    Parse outliers_removed/RESEARCH_BRIEF.md and extract key statistics.

    This brief uses markdown tables with a different format than the main brief.
    Returns dict with extracted values or None if extraction fails.
    """
    if not brief_path.exists():
        return {"error": f"Outlier brief not found: {brief_path}"}

    content = brief_path.read_text()
    extracted = {}

    # Extract N from Sample table: | **N** | 45 | 44 |
    n_match = re.search(r'\| \*\*N\*\* \| \d+ \| (\d+) \|', content)
    if n_match:
        extracted['n'] = int(n_match.group(1))

    # Extract High-Sophistication: | **High-Sophistication** | 23 | 22 |
    high_match = re.search(r'\| \*\*High-Sophistication\*\* \| \d+ \| (\d+) \|', content)
    if high_match:
        extracted['n_high'] = int(high_match.group(1))

    # Extract Low-Sophistication: | **Low-Sophistication** | 22 | 22 |
    low_match = re.search(r'\| \*\*Low-Sophistication\*\* \| \d+ \| (\d+) \|', content)
    if low_match:
        extracted['n_low'] = int(low_match.group(1))

    # Extract Median Sophistication: | **Median Sophistication** | 5.937 | 5.930 |
    median_match = re.search(r'\| \*\*Median Sophistication\*\* \| [\d.]+ \| ([\d.]+) \|', content)
    if median_match:
        extracted['median_sophistication'] = float(median_match.group(1))

    # Extract Cohen's d from H1a table: | **Cohen's d** | 2.13 | 2.84 | +0.71 |
    d_match = re.search(r'\| \*\*Cohen\'s d\*\* \| [\d.]+ \| ([\d.]+) \|', content)
    if d_match:
        extracted['h1a_d'] = float(d_match.group(1))

    # Extract Pearson r from H2 table: | **Pearson r** | 0.778 | 0.819 | +0.041 |
    r_match = re.search(r'\| \*\*Pearson r\*\* \| [\d.]+ \| ([\d.]+) \|', content)
    if r_match:
        extracted['h2_r'] = float(r_match.group(1))

    return extracted


def load_outlier_json_stats(condition: str) -> Dict[str, Any]:
    """Load statistics from outliers_removed JSON source file."""
    outlier_dir = BASE_DIR / condition / "outliers_removed"
    median_split_path = outlier_dir / "median_split_classification.json"

    if not median_split_path.exists():
        return {"error": f"Outlier JSON not found: {median_split_path}"}

    with open(median_split_path) as f:
        data = json.load(f)

    stats = {
        'n': len(data.get('models', [])),
        'n_high': data.get('n_high_sophistication'),
        'n_low': data.get('n_low_sophistication'),
        'median_sophistication': data.get('median_sophistication'),
        'h1a_d': data.get('statistics', {}).get('disinhibition', {}).get('cohens_d'),
        'h2_r': data.get('correlation', {}).get('sophistication_disinhibition'),
    }

    return stats


def check_outlier_timestamps(condition: str) -> Tuple[bool, List[str]]:
    """Check that outliers_removed generated files are newer than source JSON."""
    outlier_dir = BASE_DIR / condition / "outliers_removed"
    messages = []
    all_fresh = True

    median_split_path = outlier_dir / "median_split_classification.json"
    if not median_split_path.exists():
        return True, []  # No outlier analysis exists - not an error

    source_mtime = median_split_path.stat().st_mtime
    source_time = datetime.fromtimestamp(source_mtime).strftime('%Y-%m-%d %H:%M:%S')
    messages.append(f"  Outlier JSON: {source_time}")

    # Check key generated files in outliers_removed
    files_to_check = [
        ("Outlier RESEARCH_BRIEF.md", outlier_dir / "RESEARCH_BRIEF.md"),
        ("Outlier H2 scatter", outlier_dir / "h2_scatter_sophistication_composite.png"),
        ("Outlier H1 bar chart", outlier_dir / "h1_bar_chart_comparison.png"),
    ]

    for name, path in files_to_check:
        if path.exists():
            file_mtime = path.stat().st_mtime
            file_time = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
            if file_mtime >= source_mtime:
                messages.append(f"  {name}: {file_time} ✅")
            else:
                messages.append(f"  {name}: {file_time} ⚠️ OLDER than source")
                all_fresh = False
        else:
            messages.append(f"  {name}: NOT FOUND ⚠️")

    return all_fresh, messages


def load_json_stats(condition: str) -> Dict[str, Any]:
    """Load statistics from JSON source files."""
    profile_dir = BASE_DIR / condition
    median_split_path = profile_dir / "median_split_classification.json"

    if not median_split_path.exists():
        return {"error": f"JSON not found: {median_split_path}"}

    with open(median_split_path) as f:
        data = json.load(f)

    stats = {
        'n': len(data.get('models', [])),
        'n_high': data.get('n_high_sophistication'),
        'n_low': data.get('n_low_sophistication'),
        'median_sophistication': data.get('median_sophistication'),
        'h1a_d': data.get('statistics', {}).get('disinhibition', {}).get('cohens_d'),
        'h2_r': data.get('correlation', {}).get('sophistication_disinhibition'),
        'h1_soph_d': data.get('statistics', {}).get('sophistication', {}).get('cohens_d'),
    }

    # Load outlier stats if available
    outlier_path = profile_dir / "outliers_removed" / "median_split_classification.json"
    if outlier_path.exists():
        with open(outlier_path) as f:
            outlier_data = json.load(f)
        stats['outlier_n_removed'] = len(outlier_data.get('models', []))
        stats['outlier_h1a_d_removed'] = outlier_data.get('statistics', {}).get('disinhibition', {}).get('cohens_d')
        stats['outlier_h2_r_removed'] = outlier_data.get('correlation', {}).get('sophistication_disinhibition')

    return stats


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_value_match(name: str, brief_val: Any, json_val: Any, tolerance: float = 0.01) -> Tuple[bool, str]:
    """Check if two values match within tolerance."""
    if brief_val is None:
        return False, f"  {name}: Not found in brief"
    if json_val is None:
        return False, f"  {name}: Not found in JSON"

    if isinstance(brief_val, (int, float)) and isinstance(json_val, (int, float)):
        if abs(brief_val - json_val) <= tolerance:
            return True, f"  {name}: {brief_val} == {json_val} ✅"
        else:
            return False, f"  {name}: MISMATCH brief={brief_val} vs json={json_val} ❌"
    else:
        if brief_val == json_val:
            return True, f"  {name}: {brief_val} == {json_val} ✅"
        else:
            return False, f"  {name}: MISMATCH brief={brief_val} vs json={json_val} ❌"


def check_timestamps(condition: str) -> Tuple[bool, List[str]]:
    """Check that all generated files are newer than source JSON."""
    profile_dir = BASE_DIR / condition
    messages = []
    all_fresh = True

    median_split_path = profile_dir / "median_split_classification.json"
    if not median_split_path.exists():
        return False, [f"  Source JSON not found: {median_split_path}"]

    source_mtime = median_split_path.stat().st_mtime
    source_time = datetime.fromtimestamp(source_mtime).strftime('%Y-%m-%d %H:%M:%S')
    messages.append(f"  Source JSON: {source_time}")

    # Check key generated files
    files_to_check = [
        ("RESEARCH_BRIEF.md", profile_dir / "RESEARCH_BRIEF.md"),
        ("H2 scatter", profile_dir / "h2_scatter_sophistication_composite.png"),
        ("H1 bar chart", profile_dir / "h1_bar_chart_comparison.png"),
    ]

    # Check outlier files
    outlier_info = profile_dir / "outliers_removed" / "outlier_removal_info.json"
    if outlier_info.exists():
        files_to_check.append(("Outlier analysis", outlier_info))

    for name, path in files_to_check:
        if path.exists():
            file_mtime = path.stat().st_mtime
            file_time = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
            if file_mtime >= source_mtime:
                messages.append(f"  {name}: {file_time} ✅")
            else:
                messages.append(f"  {name}: {file_time} ⚠️ OLDER than source")
                all_fresh = False
        else:
            messages.append(f"  {name}: NOT FOUND ⚠️")
            # Don't fail for missing optional files

    return all_fresh, messages


def validate_condition(condition: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Run full validation for a condition.

    Returns validation report with:
    - passed: bool
    - warnings: int
    - errors: int
    - details: list of messages
    """
    report = {
        'condition': condition,
        'passed': True,
        'warnings': 0,
        'errors': 0,
        'details': []
    }

    profile_dir = BASE_DIR / condition
    brief_path = profile_dir / "RESEARCH_BRIEF.md"

    if verbose:
        print(f"\n{'='*60}")
        print(f"VALIDATING: {condition}")
        print(f"{'='*60}")

    # Check if condition exists
    if not profile_dir.exists():
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(f"Condition directory not found: {profile_dir}")
        if verbose:
            print(f"❌ Condition directory not found: {profile_dir}")
        return report

    # 1. Extract stats from brief and JSON
    if verbose:
        print("\n--- Statistics Comparison ---")

    brief_stats = extract_stats_from_brief(brief_path)
    json_stats = load_json_stats(condition)

    if 'error' in brief_stats:
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(brief_stats['error'])
        if verbose:
            print(f"❌ {brief_stats['error']}")
        return report

    if 'error' in json_stats:
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(json_stats['error'])
        if verbose:
            print(f"❌ {json_stats['error']}")
        return report

    # 2. Compare core statistics
    checks = [
        ('N', brief_stats.get('n'), json_stats.get('n'), 0),
        ('n_high', brief_stats.get('n_high'), json_stats.get('n_high'), 0),
        ('n_low', brief_stats.get('n_low'), json_stats.get('n_low'), 0),
        ('median_sophistication', brief_stats.get('median_sophistication'), json_stats.get('median_sophistication'), TOLERANCE_MEAN),
        ('H1a d', brief_stats.get('h1a_d'), json_stats.get('h1a_d'), TOLERANCE_D),
        ('H2 r', brief_stats.get('h2_r'), json_stats.get('h2_r'), TOLERANCE_R),
    ]

    for name, brief_val, json_val, tol in checks:
        passed, msg = check_value_match(name, brief_val, json_val, tol)
        report['details'].append(msg)
        if verbose:
            print(msg)
        if not passed:
            if brief_val is None:
                report['warnings'] += 1
            else:
                report['errors'] += 1
                report['passed'] = False

    # 3. Check outlier section if available
    if brief_stats.get('outlier_n_removed') and json_stats.get('outlier_n_removed'):
        if verbose:
            print("\n--- Outlier Sensitivity Comparison ---")

        outlier_checks = [
            ('Outlier N (removed)', brief_stats.get('outlier_n_removed'), json_stats.get('outlier_n_removed'), 0),
            ('Outlier H1a d', brief_stats.get('outlier_h1a_d_removed'), json_stats.get('outlier_h1a_d_removed'), TOLERANCE_D),
            ('Outlier H2 r', brief_stats.get('outlier_h2_r_removed'), json_stats.get('outlier_h2_r_removed'), TOLERANCE_R),
        ]

        for name, brief_val, json_val, tol in outlier_checks:
            passed, msg = check_value_match(name, brief_val, json_val, tol)
            report['details'].append(msg)
            if verbose:
                print(msg)
            if not passed:
                report['errors'] += 1
                report['passed'] = False

    # 4. Validate outliers_removed/RESEARCH_BRIEF.md against its own JSON
    outlier_brief_path = profile_dir / "outliers_removed" / "RESEARCH_BRIEF.md"
    outlier_json_path = profile_dir / "outliers_removed" / "median_split_classification.json"

    if outlier_brief_path.exists() and outlier_json_path.exists():
        if verbose:
            print("\n--- Outliers Removed Brief Validation ---")

        outlier_brief_stats = extract_stats_from_outlier_brief(outlier_brief_path)
        outlier_json_stats = load_outlier_json_stats(condition)

        if 'error' not in outlier_brief_stats and 'error' not in outlier_json_stats:
            outlier_brief_checks = [
                ('Outlier Brief N', outlier_brief_stats.get('n'), outlier_json_stats.get('n'), 0),
                ('Outlier Brief n_high', outlier_brief_stats.get('n_high'), outlier_json_stats.get('n_high'), 0),
                ('Outlier Brief n_low', outlier_brief_stats.get('n_low'), outlier_json_stats.get('n_low'), 0),
                ('Outlier Brief H1a d', outlier_brief_stats.get('h1a_d'), outlier_json_stats.get('h1a_d'), TOLERANCE_D),
                ('Outlier Brief H2 r', outlier_brief_stats.get('h2_r'), outlier_json_stats.get('h2_r'), TOLERANCE_R),
            ]

            for name, brief_val, json_val, tol in outlier_brief_checks:
                passed, msg = check_value_match(name, brief_val, json_val, tol)
                report['details'].append(msg)
                if verbose:
                    print(msg)
                if not passed:
                    if brief_val is None:
                        report['warnings'] += 1
                    else:
                        report['errors'] += 1
                        report['passed'] = False

    # 5. Check timestamps
    if verbose:
        print("\n--- Timestamp Validation ---")

    fresh, timestamp_msgs = check_timestamps(condition)
    for msg in timestamp_msgs:
        report['details'].append(msg)
        if verbose:
            print(msg)

    if not fresh:
        report['warnings'] += 1
        report['details'].append("  ⚠️ Some files may be stale - consider regenerating")
        if verbose:
            print("  ⚠️ Some files may be stale - consider regenerating")

    # 6. Check outliers_removed timestamps
    outlier_fresh, outlier_timestamp_msgs = check_outlier_timestamps(condition)
    if outlier_timestamp_msgs:  # Only show if outlier analysis exists
        if verbose:
            print("\n--- Outliers Removed Timestamp Validation ---")
        for msg in outlier_timestamp_msgs:
            report['details'].append(msg)
            if verbose:
                print(msg)

        if not outlier_fresh:
            report['warnings'] += 1
            report['details'].append("  ⚠️ Some outlier files may be stale - consider regenerating")
            if verbose:
                print("  ⚠️ Some outlier files may be stale - consider regenerating")

    # 7. Summary
    if verbose:
        print(f"\n--- Summary ---")
        if report['passed'] and report['warnings'] == 0:
            print(f"✅ PASSED: All checks passed for {condition}")
        elif report['passed']:
            print(f"⚠️ PASSED WITH WARNINGS: {report['warnings']} warning(s) for {condition}")
        else:
            print(f"❌ FAILED: {report['errors']} error(s), {report['warnings']} warning(s) for {condition}")

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Validate condition data consistency')
    parser.add_argument('condition', nargs='?', help='Condition to validate (or --all)')
    parser.add_argument('--all', action='store_true', help='Validate all conditions')
    parser.add_argument('--strict', action='store_true', help='Exit non-zero on any warning')
    parser.add_argument('--quiet', action='store_true', help='Only show summary')
    args = parser.parse_args()

    if not args.condition and not args.all:
        parser.print_help()
        sys.exit(1)

    conditions_to_check = CONDITIONS if args.all else [args.condition]

    all_reports = []
    for condition in conditions_to_check:
        if (BASE_DIR / condition).exists():
            report = validate_condition(condition, verbose=not args.quiet)
            all_reports.append(report)

    # Final summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")

    total_passed = sum(1 for r in all_reports if r['passed'])
    total_warnings = sum(r['warnings'] for r in all_reports)
    total_errors = sum(r['errors'] for r in all_reports)

    for r in all_reports:
        status = "✅" if r['passed'] and r['warnings'] == 0 else "⚠️" if r['passed'] else "❌"
        print(f"  {status} {r['condition']}: {r['errors']} errors, {r['warnings']} warnings")

    print(f"\nTotal: {total_passed}/{len(all_reports)} passed, {total_errors} errors, {total_warnings} warnings")

    # Exit code
    if total_errors > 0:
        sys.exit(1)
    elif args.strict and total_warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
