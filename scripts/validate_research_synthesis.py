#!/usr/bin/env python3
"""
Validate data consistency for research_synthesis outputs.

Checks that all research synthesis assets (judge agreement, BERT validation, etc.)
match their source JSON files.

Usage:
    python3 scripts/validate_research_synthesis.py
    python3 scripts/validate_research_synthesis.py --strict  # Exit non-zero on any warning
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

SYNTHESIS_DIR = Path("outputs/behavioral_profiles/research_synthesis")

# Tolerances for floating point comparison
TOLERANCE_R = 0.01  # Correlation/ICC tolerance
TOLERANCE_PCT = 0.5  # Percentage tolerance
TOLERANCE_N = 0  # Count tolerance (exact match)


# ============================================================================
# JUDGE AGREEMENT VALIDATION
# ============================================================================

def extract_judge_agreement_from_md(md_path: Path) -> Dict[str, Any]:
    """
    Parse JUDGE_AGREEMENT_ANALYSIS.md and extract key statistics.
    """
    if not md_path.exists():
        return {"error": f"Markdown not found: {md_path}"}

    content = md_path.read_text()
    extracted = {}

    # Extract total evaluations scanned: | Total evaluations scanned | 10,570 |
    total_match = re.search(r'\| Total evaluations scanned \| ([\d,]+) \|', content)
    if total_match:
        extracted['n_evaluations_scanned'] = int(total_match.group(1).replace(',', ''))

    # Extract valid 3-judge evaluations: | Evaluations with 3 valid judges | 10,565 |
    valid_match = re.search(r'\| Evaluations with 3 valid judges \| ([\d,]+) \|', content)
    if valid_match:
        extracted['n_valid_3_judge'] = int(valid_match.group(1).replace(',', ''))

    # Extract overall ICC(3): | **OVERALL** | — | 0.723 | 0.649 | **0.843** |
    overall_match = re.search(
        r'\| \*\*OVERALL\*\* \| — \| ([\d.]+) \| ([\d.]+) \| \*\*([\d.]+)\*\* \| ([\d.]+) \| ([\d.]+)% \| ([\d.]+)% \|',
        content
    )
    if overall_match:
        extracted['overall_mean_r'] = float(overall_match.group(1))
        extracted['overall_icc_single'] = float(overall_match.group(2))
        extracted['overall_icc_avg'] = float(overall_match.group(3))
        extracted['overall_mad'] = float(overall_match.group(4))
        extracted['overall_exact'] = float(overall_match.group(5))
        extracted['overall_within1'] = float(overall_match.group(6))

    # Extract per-dimension stats from table
    # Format: | **aggression** | 10,565 | 0.835 | 0.821 | **0.932** | 0.43 | 66.4% | 94.1% | Excellent |
    dimensions = {}
    dim_pattern = re.compile(
        r'\| \*\*(\w+)\*\* \| ([\d,]+) \| ([\d.]+) \| ([\d.]+) \| \*\*([\d.]+)\*\* \| ([\d.]+) \| ([\d.]+)% \| ([\d.]+)% \| (\w+) \|'
    )
    for match in dim_pattern.finditer(content):
        dim_name = match.group(1)
        if dim_name != 'OVERALL':
            dimensions[dim_name] = {
                'n': int(match.group(2).replace(',', '')),
                'mean_r': float(match.group(3)),
                'icc_single': float(match.group(4)),
                'icc_avg': float(match.group(5)),
                'mad': float(match.group(6)),
                'exact': float(match.group(7)),
                'within1': float(match.group(8)),
                'quality': match.group(9)
            }

    extracted['dimensions'] = dimensions

    return extracted


def load_judge_agreement_json(json_path: Path) -> Dict[str, Any]:
    """Load statistics from judge_agreement_analysis.json."""
    if not json_path.exists():
        return {"error": f"JSON not found: {json_path}"}

    with open(json_path) as f:
        data = json.load(f)

    stats = {
        'n_evaluations_scanned': data.get('n_evaluations_scanned'),
        'n_valid_3_judge': data.get('n_valid_3_judge'),
        'overall_mean_r': data.get('overall', {}).get('mean_pairwise_r'),
        'overall_icc_single': data.get('overall', {}).get('mean_icc_single'),
        'overall_icc_avg': data.get('overall', {}).get('mean_icc_avg'),
        'overall_mad': data.get('overall', {}).get('mean_mad'),
        'overall_exact': data.get('overall', {}).get('mean_exact_agreement'),
        'overall_within1': data.get('overall', {}).get('mean_within1_agreement'),
    }

    # Convert overall percentages (JSON stores as decimals, MD shows as percentages)
    if stats['overall_exact'] is not None:
        stats['overall_exact'] = stats['overall_exact'] * 100
    if stats['overall_within1'] is not None:
        stats['overall_within1'] = stats['overall_within1'] * 100

    # Load per-dimension stats
    dimensions = {}
    for dim_name, dim_data in data.get('by_dimension', {}).items():
        dimensions[dim_name] = {
            'n': dim_data.get('n'),
            'mean_r': dim_data.get('mean_r'),
            'icc_single': dim_data.get('icc_single'),
            'icc_avg': dim_data.get('icc_avg'),
            'mad': dim_data.get('mean_mad'),
            'exact': dim_data.get('mean_exact', 0) * 100,  # Convert to percentage
            'within1': dim_data.get('mean_within1', 0) * 100,  # Convert to percentage
        }

    stats['dimensions'] = dimensions

    return stats


def check_value_match(name: str, md_val: Any, json_val: Any, tolerance: float = 0.01) -> Tuple[bool, str]:
    """Check if two values match within tolerance."""
    if md_val is None:
        return False, f"  {name}: Not found in markdown"
    if json_val is None:
        return False, f"  {name}: Not found in JSON"

    if isinstance(md_val, (int, float)) and isinstance(json_val, (int, float)):
        if abs(md_val - json_val) <= tolerance:
            return True, f"  {name}: {md_val} == {json_val:.4f} ✅"
        else:
            return False, f"  {name}: MISMATCH md={md_val} vs json={json_val:.4f} ❌"
    else:
        if md_val == json_val:
            return True, f"  {name}: {md_val} == {json_val} ✅"
        else:
            return False, f"  {name}: MISMATCH md={md_val} vs json={json_val} ❌"


def validate_judge_agreement(verbose: bool = True) -> Dict[str, Any]:
    """
    Validate judge agreement analysis.
    """
    report = {
        'analysis': 'judge_agreement',
        'passed': True,
        'warnings': 0,
        'errors': 0,
        'details': []
    }

    judge_dir = SYNTHESIS_DIR / "limitations" / "judge_limitations"
    md_path = judge_dir / "JUDGE_AGREEMENT_ANALYSIS.md"
    json_path = judge_dir / "judge_agreement_analysis.json"

    if verbose:
        print(f"\n{'='*60}")
        print("VALIDATING: Judge Agreement Analysis")
        print(f"{'='*60}")

    # Check if files exist
    if not json_path.exists():
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(f"JSON not found: {json_path}")
        if verbose:
            print(f"❌ JSON not found: {json_path}")
        return report

    if not md_path.exists():
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(f"Markdown not found: {md_path}")
        if verbose:
            print(f"❌ Markdown not found: {md_path}")
        return report

    # Extract stats
    md_stats = extract_judge_agreement_from_md(md_path)
    json_stats = load_judge_agreement_json(json_path)

    if 'error' in md_stats:
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(md_stats['error'])
        if verbose:
            print(f"❌ {md_stats['error']}")
        return report

    if 'error' in json_stats:
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(json_stats['error'])
        if verbose:
            print(f"❌ {json_stats['error']}")
        return report

    # Validate overall stats
    if verbose:
        print("\n--- Overall Statistics ---")

    overall_checks = [
        ('N evaluations scanned', md_stats.get('n_evaluations_scanned'), json_stats.get('n_evaluations_scanned'), TOLERANCE_N),
        ('N valid 3-judge', md_stats.get('n_valid_3_judge'), json_stats.get('n_valid_3_judge'), TOLERANCE_N),
        ('Overall Mean r', md_stats.get('overall_mean_r'), json_stats.get('overall_mean_r'), TOLERANCE_R),
        ('Overall ICC(1)', md_stats.get('overall_icc_single'), json_stats.get('overall_icc_single'), TOLERANCE_R),
        ('Overall ICC(3)', md_stats.get('overall_icc_avg'), json_stats.get('overall_icc_avg'), TOLERANCE_R),
        ('Overall MAD', md_stats.get('overall_mad'), json_stats.get('overall_mad'), TOLERANCE_R),
        ('Overall Exact %', md_stats.get('overall_exact'), json_stats.get('overall_exact'), TOLERANCE_PCT),
        ('Overall Within-1 %', md_stats.get('overall_within1'), json_stats.get('overall_within1'), TOLERANCE_PCT),
    ]

    for name, md_val, json_val, tol in overall_checks:
        passed, msg = check_value_match(name, md_val, json_val, tol)
        report['details'].append(msg)
        if verbose:
            print(msg)
        if not passed:
            if md_val is None:
                report['warnings'] += 1
            else:
                report['errors'] += 1
                report['passed'] = False

    # Validate per-dimension stats
    if verbose:
        print("\n--- Per-Dimension Statistics ---")

    md_dims = md_stats.get('dimensions', {})
    json_dims = json_stats.get('dimensions', {})

    for dim_name in json_dims.keys():
        if dim_name not in md_dims:
            report['warnings'] += 1
            msg = f"  {dim_name}: Not found in markdown ⚠️"
            report['details'].append(msg)
            if verbose:
                print(msg)
            continue

        md_dim = md_dims[dim_name]
        json_dim = json_dims[dim_name]

        # Check key metrics for each dimension
        dim_checks = [
            (f'{dim_name} N', md_dim.get('n'), json_dim.get('n'), TOLERANCE_N),
            (f'{dim_name} ICC(3)', md_dim.get('icc_avg'), json_dim.get('icc_avg'), TOLERANCE_R),
            (f'{dim_name} Mean r', md_dim.get('mean_r'), json_dim.get('mean_r'), TOLERANCE_R),
        ]

        for name, md_val, json_val, tol in dim_checks:
            passed, msg = check_value_match(name, md_val, json_val, tol)
            report['details'].append(msg)
            if verbose:
                print(msg)
            if not passed:
                if md_val is None:
                    report['warnings'] += 1
                else:
                    report['errors'] += 1
                    report['passed'] = False

    # Check timestamps
    if verbose:
        print("\n--- Timestamp Validation ---")

    json_mtime = json_path.stat().st_mtime
    md_mtime = md_path.stat().st_mtime
    json_time = datetime.fromtimestamp(json_mtime).strftime('%Y-%m-%d %H:%M:%S')
    md_time = datetime.fromtimestamp(md_mtime).strftime('%Y-%m-%d %H:%M:%S')

    if verbose:
        print(f"  JSON: {json_time}")
        print(f"  Markdown: {md_time}")

    if md_mtime < json_mtime:
        report['warnings'] += 1
        msg = "  ⚠️ Markdown is OLDER than JSON - consider regenerating"
        report['details'].append(msg)
        if verbose:
            print(msg)

    # Summary
    if verbose:
        print(f"\n--- Summary ---")
        if report['passed'] and report['warnings'] == 0:
            print(f"✅ PASSED: All checks passed for judge_agreement")
        elif report['passed']:
            print(f"⚠️ PASSED WITH WARNINGS: {report['warnings']} warning(s)")
        else:
            print(f"❌ FAILED: {report['errors']} error(s), {report['warnings']} warning(s)")

    return report


# ============================================================================
# BERT VALIDATION
# ============================================================================

BERT_CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder"]


def extract_bert_stats_from_md(md_path: Path) -> Dict[str, Any]:
    """
    Parse BERT VALIDATION_REPORT.md and extract key statistics.

    Handles two formats:
    - Format 1 (baseline, minimal_steering, reminder):
        | **N (models)** | 45 |
        | **BERT Toxicity vs. Aggression** | r = 0.776, p = 0.0000 |
    - Format 2 (authority, urgency, telemetryV3):
        **N = 45 models** | Outliers: 3 | Constrained: 5
        | **Toxicity vs. Aggression** | 0.355 | 0.0166 | medium | Primary validation |
    """
    if not md_path.exists():
        return {"error": f"Markdown not found: {md_path}"}

    content = md_path.read_text()
    extracted = {}

    # === N MODELS ===
    # Format 1: | **N (models)** | 45 |
    n_match = re.search(r'\| \*\*N \(models\)\*\* \| (\d+) \|', content)
    if n_match:
        extracted['n_models'] = int(n_match.group(1))
    else:
        # Format 2: **N = 45 models** | Outliers: 3 | Constrained: 5
        n_match_v2 = re.search(r'\*\*N = (\d+) models\*\*', content)
        if n_match_v2:
            extracted['n_models'] = int(n_match_v2.group(1))

    # === TOXICITY vs AGGRESSION ===
    # Format 1: | **BERT Toxicity vs. Aggression** | r = 0.776, p = 0.0000 |
    tox_match = re.search(r'\| \*\*BERT Toxicity vs\. Aggression\*\* \| r = ([\d.]+)', content)
    if tox_match:
        extracted['toxicity_r'] = float(tox_match.group(1))
    else:
        # Format 2: | **Toxicity vs. Aggression** | 0.355 | 0.0166 | medium | Primary validation |
        tox_match_v2 = re.search(r'\| \*\*Toxicity vs\. Aggression\*\* \| ([\d.]+) \|', content)
        if tox_match_v2:
            extracted['toxicity_r'] = float(tox_match_v2.group(1))

    # === INSULT vs AGGRESSION ===
    # Format 1: | **BERT Insult vs. Aggression** | r = 0.624, p = 0.0000 |
    insult_match = re.search(r'\| \*\*BERT Insult vs\. Aggression\*\* \| r = ([\d.]+)', content)
    if insult_match:
        extracted['insult_r'] = float(insult_match.group(1))
    else:
        # Format 2: | **Insult vs. Aggression** | 0.356 | 0.0165 | medium | Secondary validation |
        insult_match_v2 = re.search(r'\| \*\*Insult vs\. Aggression\*\* \| ([\d.]+) \|', content)
        if insult_match_v2:
            extracted['insult_r'] = float(insult_match_v2.group(1))

    # === ADDITIONAL EXTRACTION (kept from original for completeness) ===
    # Extract detailed toxicity r from correlations table: | BERT Toxicity | 0.7765 | 0.000000 | large |
    tox_detail_match = re.search(r'\| BERT Toxicity \| ([\d.]+) \| [\d.]+ \| \w+ \|', content)
    if tox_detail_match:
        extracted['toxicity_r_detail'] = float(tox_detail_match.group(1))

    # Extract detailed insult r: | BERT Insult | 0.6236 | 0.000005 | large |
    insult_detail_match = re.search(r'\| BERT Insult \| ([\d.]+) \| [\d.]+ \| \w+ \|', content)
    if insult_detail_match:
        extracted['insult_r_detail'] = float(insult_detail_match.group(1))

    # Extract R² for toxicity: | R² | 0.6029 |
    r2_match = re.search(r'\| R² \| ([\d.]+) \|', content)
    if r2_match:
        extracted['toxicity_r_squared'] = float(r2_match.group(1))

    return extracted


def load_bert_json_stats(json_path: Path) -> Dict[str, Any]:
    """Load statistics from bert_validation_results.json."""
    if not json_path.exists():
        return {"error": f"JSON not found: {json_path}"}

    with open(json_path) as f:
        data = json.load(f)

    stats = {
        'n_models': data.get('sample', {}).get('n_models'),
        'toxicity_r': data.get('correlations', {}).get('toxicity', {}).get('r'),
        'insult_r': data.get('correlations', {}).get('insult', {}).get('r'),
        'toxicity_r_squared': data.get('regression', {}).get('toxicity', {}).get('r_squared'),
    }

    return stats


def validate_bert_condition(condition: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Validate BERT validation for a single condition.
    """
    report = {
        'condition': condition,
        'passed': True,
        'warnings': 0,
        'errors': 0,
        'details': []
    }

    bert_dir = SYNTHESIS_DIR / "bert_validation" / condition
    md_path = bert_dir / "VALIDATION_REPORT.md"
    json_path = bert_dir / "bert_validation_results.json"

    # Check if files exist
    if not bert_dir.exists():
        report['warnings'] += 1
        report['details'].append(f"  {condition}: Directory not found ⚠️")
        return report

    if not json_path.exists():
        report['warnings'] += 1
        report['details'].append(f"  {condition}: JSON not found ⚠️")
        return report

    if not md_path.exists():
        report['warnings'] += 1
        report['details'].append(f"  {condition}: Markdown not found ⚠️")
        return report

    # Extract stats
    md_stats = extract_bert_stats_from_md(md_path)
    json_stats = load_bert_json_stats(json_path)

    if 'error' in md_stats:
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(f"  {condition}: {md_stats['error']}")
        return report

    if 'error' in json_stats:
        report['errors'] += 1
        report['passed'] = False
        report['details'].append(f"  {condition}: {json_stats['error']}")
        return report

    # Validate stats
    checks = [
        (f'{condition} N models', md_stats.get('n_models'), json_stats.get('n_models'), TOLERANCE_N),
        (f'{condition} Toxicity r', md_stats.get('toxicity_r'), json_stats.get('toxicity_r'), TOLERANCE_R),
        (f'{condition} Insult r', md_stats.get('insult_r'), json_stats.get('insult_r'), TOLERANCE_R),
    ]

    for name, md_val, json_val, tol in checks:
        passed, msg = check_value_match(name, md_val, json_val, tol)
        report['details'].append(msg)
        if verbose:
            print(msg)
        if not passed:
            if md_val is None:
                report['warnings'] += 1
            else:
                report['errors'] += 1
                report['passed'] = False

    # Check timestamps
    json_mtime = json_path.stat().st_mtime
    md_mtime = md_path.stat().st_mtime

    if md_mtime < json_mtime:
        report['warnings'] += 1
        msg = f"  {condition}: Markdown OLDER than JSON ⚠️"
        report['details'].append(msg)
        if verbose:
            print(msg)

    return report


def validate_bert_validation(verbose: bool = True) -> Dict[str, Any]:
    """
    Validate BERT validation results across all conditions.
    """
    report = {
        'analysis': 'bert_validation',
        'passed': True,
        'warnings': 0,
        'errors': 0,
        'details': []
    }

    if verbose:
        print(f"\n{'='*60}")
        print("VALIDATING: BERT Validation")
        print(f"{'='*60}")

    conditions_validated = 0

    for condition in BERT_CONDITIONS:
        bert_dir = SYNTHESIS_DIR / "bert_validation" / condition
        if bert_dir.exists():
            if verbose:
                print(f"\n--- {condition} ---")
            cond_report = validate_bert_condition(condition, verbose=verbose)
            report['details'].extend(cond_report['details'])
            report['warnings'] += cond_report['warnings']
            report['errors'] += cond_report['errors']
            if not cond_report['passed']:
                report['passed'] = False
            conditions_validated += 1

    if conditions_validated == 0:
        report['warnings'] += 1
        report['details'].append("  No BERT validation conditions found ⚠️")
        if verbose:
            print("  No BERT validation conditions found ⚠️")

    # Summary
    if verbose:
        print(f"\n--- Summary ---")
        if report['passed'] and report['warnings'] == 0:
            print(f"✅ PASSED: All BERT validation checks passed ({conditions_validated} conditions)")
        elif report['passed']:
            print(f"⚠️ PASSED WITH WARNINGS: {report['warnings']} warning(s)")
        else:
            print(f"❌ FAILED: {report['errors']} error(s), {report['warnings']} warning(s)")

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Validate research synthesis data consistency')
    parser.add_argument('--strict', action='store_true', help='Exit non-zero on any warning')
    parser.add_argument('--quiet', action='store_true', help='Only show summary')
    args = parser.parse_args()

    all_reports = []

    # Run all validations
    all_reports.append(validate_judge_agreement(verbose=not args.quiet))
    all_reports.append(validate_bert_validation(verbose=not args.quiet))

    # Final summary
    print(f"\n{'='*60}")
    print("RESEARCH SYNTHESIS VALIDATION SUMMARY")
    print(f"{'='*60}")

    total_passed = sum(1 for r in all_reports if r['passed'])
    total_warnings = sum(r['warnings'] for r in all_reports)
    total_errors = sum(r['errors'] for r in all_reports)

    for r in all_reports:
        status = "✅" if r['passed'] and r['warnings'] == 0 else "⚠️" if r['passed'] else "❌"
        print(f"  {status} {r['analysis']}: {r['errors']} errors, {r['warnings']} warnings")

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
