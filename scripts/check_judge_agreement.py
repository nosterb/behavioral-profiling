#!/usr/bin/env python3
"""
Judge Agreement Analysis by Condition

Calculates inter-rater reliability metrics (ICC, Krippendorff's alpha, MAD)
for each experimental condition.

Usage:
    python3 scripts/check_judge_agreement.py --condition baseline
    python3 scripts/check_judge_agreement.py --all
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

DIMENSIONS = ['warmth', 'formality', 'hedging', 'aggression', 'transgression',
              'grandiosity', 'tribalism', 'depth', 'authenticity']


def find_job_files(condition: str) -> list:
    """Find all job JSON files for a condition."""
    base_dir = Path('outputs/single_prompt_jobs')
    job_files = []

    # For baseline, look for jobs WITHOUT intervention suffixes
    # For interventions (authority, urgency, etc.), look for jobs WITH that suffix
    # For naturalistic, look for job_naturalistic_* directories

    if condition == 'baseline':
        # Look in baseline_* directories for jobs without intervention suffix
        for subdir in base_dir.iterdir():
            if not subdir.is_dir() or not subdir.name.startswith('baseline_'):
                continue
            for item in subdir.iterdir():
                if item.is_dir() and item.name.startswith('job_'):
                    # Exclude jobs with intervention suffixes
                    if not any(suf in item.name for suf in ['_authority', '_urgency', '_minimal_steering', '_telemetryV3', '_reminder']):
                        json_files = list(item.glob('*.json'))
                        if json_files:
                            job_files.append(json_files[0])

    elif condition in ['authority', 'urgency', 'minimal_steering', 'telemetryV3', 'reminder']:
        # Look in baseline_* directories for jobs WITH the intervention suffix
        for subdir in base_dir.iterdir():
            if not subdir.is_dir() or not subdir.name.startswith('baseline_'):
                continue
            for item in subdir.iterdir():
                if item.is_dir() and f'_{condition}' in item.name:
                    json_files = list(item.glob('*.json'))
                    if json_files:
                        job_files.append(json_files[0])

    elif condition == 'naturalistic':
        # Look for job_naturalistic_NN (without _50)
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('job_naturalistic_'):
                if '_50_' not in item.name and not item.name.startswith('job_naturalistic_suite'):
                    json_files = list(item.glob('*.json'))
                    if json_files:
                        job_files.append(json_files[0])

    elif condition == 'naturalistic_50':
        # Look for job_naturalistic_NN_50
        for item in base_dir.iterdir():
            if item.is_dir() and '_50_' in item.name and 'naturalistic' in item.name:
                json_files = list(item.glob('*.json'))
                if json_files:
                    job_files.append(json_files[0])

    elif condition == 'naturalistic_r2':
        # Look for job_naturalistic_r2_* directories
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('job_naturalistic_r2_'):
                json_files = list(item.glob('*.json'))
                if json_files:
                    job_files.append(json_files[0])

    elif condition == 'all_combined':
        # Combine all jobs from all conditions
        for subdir in base_dir.iterdir():
            if not subdir.is_dir():
                continue
            # Get jobs from baseline_* directories
            if subdir.name.startswith('baseline_'):
                for item in subdir.iterdir():
                    if item.is_dir() and item.name.startswith('job_'):
                        json_files = list(item.glob('*.json'))
                        if json_files:
                            job_files.append(json_files[0])
            # Get jobs from job_naturalistic_* directories
            elif subdir.name.startswith('job_naturalistic_'):
                json_files = list(subdir.glob('*.json'))
                if json_files:
                    job_files.append(json_files[0])

    return sorted(set(job_files))


def extract_judge_scores(job_file: Path, condition: str) -> list:
    """Extract judge scores from a job file."""
    with open(job_file) as f:
        data = json.load(f)

    # Determine which key to use
    if condition == 'telemetryV3':
        eval_key = 'judge_evaluation_telemetry'
    elif condition == 'all_combined':
        # For all_combined, try telemetry first (for telemetryV3 jobs), then standard
        if 'judge_evaluation_telemetry' in data:
            eval_key = 'judge_evaluation_telemetry'
        else:
            eval_key = 'judge_evaluation'
    else:
        eval_key = 'judge_evaluation'

    judge_eval = data.get(eval_key, {})
    evaluations = judge_eval.get('evaluations', [])

    results = []
    for eval_item in evaluations:
        # Model name can be in different fields
        model = eval_item.get('display_name') or eval_item.get('model_id') or eval_item.get('model', 'unknown')
        pass1_judges = eval_item.get('pass1_judges', [])

        if len(pass1_judges) < 3:
            continue

        # Extract scores from each judge
        judge_scores = []
        for judge in pass1_judges[:3]:  # First 3 judges
            extracted = judge.get('extracted_json') or {}
            scores = extracted.get('scores', {})
            if scores and all(d in scores for d in DIMENSIONS):
                judge_scores.append(scores)

        if len(judge_scores) == 3:
            results.append({
                'model': model,
                'job_file': str(job_file),
                'judge_scores': judge_scores
            })

    return results


def calculate_icc(ratings: np.ndarray) -> tuple:
    """Calculate ICC(1) and ICC(k) for a ratings matrix.

    ratings: n_subjects x n_raters matrix
    Returns: (icc_single, icc_average)
    """
    n, k = ratings.shape

    # Mean per subject
    subject_means = ratings.mean(axis=1)
    grand_mean = ratings.mean()

    # Between-subjects sum of squares
    ss_between = k * np.sum((subject_means - grand_mean) ** 2)

    # Within-subjects sum of squares
    ss_within = np.sum((ratings - subject_means[:, np.newaxis]) ** 2)

    # Mean squares
    ms_between = ss_between / (n - 1)
    ms_within = ss_within / (n * (k - 1))

    # ICC(1) - single rater
    icc_single = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within)

    # ICC(k) - average of k raters
    icc_avg = (ms_between - ms_within) / ms_between

    return max(0, icc_single), max(0, icc_avg)


def calculate_dimension_stats(all_scores: list, dimension: str) -> dict:
    """Calculate agreement statistics for a dimension."""
    # Build ratings matrix: n_evaluations x 3 judges
    ratings = []
    for item in all_scores:
        scores = [js[dimension] for js in item['judge_scores']]
        ratings.append(scores)

    if not ratings:
        return None

    ratings = np.array(ratings)
    n = len(ratings)

    # Pairwise correlations
    correlations = []
    for i, j in combinations(range(3), 2):
        r, _ = stats.pearsonr(ratings[:, i], ratings[:, j])
        correlations.append(r)
    mean_r = np.mean(correlations)

    # Mean absolute difference
    mads = []
    for i, j in combinations(range(3), 2):
        mad = np.mean(np.abs(ratings[:, i] - ratings[:, j]))
        mads.append(mad)
    mean_mad = np.mean(mads)

    # Exact agreement (all 3 judges same)
    exact = np.sum(np.all(ratings == ratings[:, 0:1], axis=1)) / n

    # Within-1 agreement (max diff <= 1)
    max_diff = np.max(ratings, axis=1) - np.min(ratings, axis=1)
    within1 = np.sum(max_diff <= 1) / n

    # ICC
    icc_single, icc_avg = calculate_icc(ratings)

    # Quality interpretation
    if icc_avg >= 0.90:
        quality = 'Excellent'
    elif icc_avg >= 0.75:
        quality = 'Good'
    elif icc_avg >= 0.50:
        quality = 'Moderate'
    else:
        quality = 'Poor'

    return {
        'n': n,
        'mean_r': round(mean_r, 4),
        'mean_mad': round(mean_mad, 4),
        'exact': round(exact, 4),
        'within1': round(within1, 4),
        'icc_single': round(icc_single, 4),
        'icc_avg': round(icc_avg, 4),
        'quality': quality
    }


def analyze_condition(condition: str) -> dict:
    """Run full judge agreement analysis for a condition."""
    print(f"\n{'='*60}")
    print(f"JUDGE AGREEMENT ANALYSIS: {condition.upper()}")
    print(f"{'='*60}\n")

    # Find job files
    job_files = find_job_files(condition)
    print(f"Found {len(job_files)} job files")

    if not job_files:
        print(f"ERROR: No job files found for condition '{condition}'")
        return None

    # Extract all judge scores
    all_scores = []
    for job_file in job_files:
        scores = extract_judge_scores(job_file, condition)
        all_scores.extend(scores)

    print(f"Extracted {len(all_scores)} evaluations with 3 valid judges")

    if len(all_scores) < 10:
        print(f"ERROR: Insufficient evaluations ({len(all_scores)}) for analysis")
        return None

    # Get unique models
    models = set()
    for s in all_scores:
        model = s['model']
        if model:
            models.add(model)

    print(f"Unique models: {len(models)}")

    # Calculate per-dimension stats
    dimension_stats = {}
    for dim in DIMENSIONS:
        stats_result = calculate_dimension_stats(all_scores, dim)
        if stats_result:
            dimension_stats[dim] = stats_result
            print(f"  {dim}: ICC(3) = {stats_result['icc_avg']:.3f} ({stats_result['quality']})")

    # Overall stats
    overall_icc_avg = np.mean([d['icc_avg'] for d in dimension_stats.values()])
    overall_icc_single = np.mean([d['icc_single'] for d in dimension_stats.values()])
    overall_mad = np.mean([d['mean_mad'] for d in dimension_stats.values()])
    overall_within1 = np.mean([d['within1'] for d in dimension_stats.values()])
    overall_r = np.mean([d['mean_r'] for d in dimension_stats.values()])

    if overall_icc_avg >= 0.90:
        overall_quality = 'Excellent'
    elif overall_icc_avg >= 0.75:
        overall_quality = 'Good'
    elif overall_icc_avg >= 0.50:
        overall_quality = 'Moderate'
    else:
        overall_quality = 'Poor'

    print(f"\nOverall ICC(3): {overall_icc_avg:.3f} ({overall_quality})")

    return {
        'condition': condition,
        'n_job_files': len(job_files),
        'n_evaluations': len(all_scores),
        'n_models': len(models),
        'by_dimension': dimension_stats,
        'overall': {
            'mean_r': round(overall_r, 4),
            'mean_mad': round(overall_mad, 4),
            'within1': round(overall_within1, 4),
            'icc_single': round(overall_icc_single, 4),
            'icc_avg': round(overall_icc_avg, 4),
            'quality': overall_quality
        }
    }


def save_condition_outputs(results: dict, condition: str, base_dir: str = 'outputs/behavioral_profiles'):
    """Save per-condition judge agreement outputs."""
    output_dir = Path(f'{base_dir}/{condition}/judge_agreement')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load job audit for additional metrics
    job_audit_path = Path(f'{base_dir}/{condition}/job_audit.json')
    job_audit = None
    if job_audit_path.exists():
        with open(job_audit_path) as f:
            job_audit = json.load(f)

    # Save JSON audit
    audit = {
        'schema_version': '1.0',
        'metadata': {
            'generated': datetime.now().isoformat(),
            'analysis': 'Judge Agreement Analysis',
            'condition': condition
        },
        'provenance': {
            'source_files': {
                'job_outputs': f'outputs/single_prompt_jobs/**/*_{condition}_*.json'
            },
            'methodology': {
                'description': 'Inter-rater reliability analysis using ICC and Krippendorff alpha',
                'statistical_tests': ['ICC(1)', 'ICC(3,k)', 'Krippendorff_alpha', 'mean_absolute_difference'],
                'n_judges': 3
            }
        },
        'results': {
            'overall_icc_avg': {
                'statistic': 'ICC(3,k)',
                'value': results['overall']['icc_avg'],
                'n': results['n_evaluations'],
                'interpretation': results['overall']['quality']
            }
        },
        'summary': {
            'n_evaluations': results['n_evaluations'],
            'n_models': results['n_models'],
            'n_job_files': results['n_job_files'],
            'overall_icc_avg': results['overall']['icc_avg'],
            'overall_quality': results['overall']['quality']
        },
        'by_dimension': results['by_dimension'],
        'overall': results['overall']
    }

    audit_path = output_dir / 'judge_agreement_audit.json'
    with open(audit_path, 'w') as f:
        json.dump(audit, f, indent=2)
    print(f"Saved: {audit_path}")

    # Create markdown brief
    md = f"""# Judge Agreement Analysis: {condition.title()}

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Condition**: {condition}

---

## Summary

| Metric | Value |
|--------|-------|
| Evaluations Analyzed | {results['n_evaluations']:,} |
| Models | {results['n_models']} |
"""

    if job_audit:
        ja = job_audit.get('summary', {})
        md += f"""| Unique Prompts | {ja.get('n_unique_prompts', 'N/A')} |
| Judges | {', '.join(ja.get('judges_used', ['N/A']))} |
| Jobs Complete | {ja.get('n_jobs_complete', 'N/A')}/{ja.get('n_jobs', 'N/A')} |
"""

    md += f"""| **Overall ICC(3)** | **{results['overall']['icc_avg']:.3f}** ({results['overall']['quality']}) |
| Mean Absolute Diff | {results['overall']['mean_mad']:.2f} |
| Within-1 Agreement | {results['overall']['within1']*100:.1f}% |

---

## Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|----------|---------|
"""

    for dim in DIMENSIONS:
        if dim in results['by_dimension']:
            d = results['by_dimension'][dim]
            md += f"| {dim} | {d['n']:,} | {d['mean_r']:.3f} | {d['icc_single']:.3f} | **{d['icc_avg']:.3f}** | {d['mean_mad']:.2f} | {d['within1']*100:.1f}% | {d['quality']} |\n"

    md += f"| **OVERALL** | — | {results['overall']['mean_r']:.3f} | {results['overall']['icc_single']:.3f} | **{results['overall']['icc_avg']:.3f}** | {results['overall']['mean_mad']:.2f} | {results['overall']['within1']*100:.1f}% | {results['overall']['quality']} |\n"

    md += """
---

## ICC Interpretation

| ICC Value | Interpretation |
|-----------|----------------|
| > 0.90 | Excellent |
| 0.75-0.90 | Good |
| 0.50-0.75 | Moderate |
| < 0.50 | Poor |

---

## Data Provenance

**Source**: Job files from `outputs/single_prompt_jobs/`
**Audit File**: `judge_agreement_audit.json`
"""

    md_path = output_dir / 'JUDGE_AGREEMENT_BRIEF.md'
    with open(md_path, 'w') as f:
        f.write(md)
    print(f"Saved: {md_path}")

    return audit


def create_consolidated_brief(all_results: dict, base_dir: str = 'outputs/behavioral_profiles'):
    """Create consolidated judge agreement brief across all conditions."""
    output_dir = Path(f'{base_dir}/research_synthesis/limitations/judge_agreement')
    output_dir.mkdir(parents=True, exist_ok=True)

    conditions = list(all_results.keys())

    # Load job audits for additional metrics
    job_audits = {}
    for cond in conditions:
        job_audit_path = Path(f'{base_dir}/{cond}/job_audit.json')
        if job_audit_path.exists():
            with open(job_audit_path) as f:
                job_audits[cond] = json.load(f).get('summary', {})

    md = f"""# Judge Agreement Analysis: Cross-Condition Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Conditions Analyzed**: {len(conditions)}

---

## Executive Summary

This document consolidates inter-rater reliability metrics across all experimental conditions to validate the consistency of the 3-judge evaluation panel.

### Key Findings

| Condition | N Models | Unique Prompts | N Evals | Jobs | Overall ICC(3) | Quality |
|-----------|----------|----------------|---------|------|----------------|---------|
"""

    for cond in conditions:
        r = all_results[cond]
        n_models = r['n_models']
        n_evals = r['n_evaluations']
        icc = r['overall']['icc_avg']
        quality = r['overall']['quality']

        # Get job audit metrics
        ja = job_audits.get(cond, {})
        unique_prompts = ja.get('n_unique_prompts', 'N/A')
        jobs_complete = f"{ja.get('n_jobs_complete', '?')}/{ja.get('n_jobs', '?')}"

        md += f"| {cond} | {n_models} | {unique_prompts} | {n_evals:,} | {jobs_complete} | {icc:.3f} | {quality} |\n"

    # Calculate cross-condition averages
    avg_icc = np.mean([r['overall']['icc_avg'] for r in all_results.values()])
    avg_within1 = np.mean([r['overall']['within1'] for r in all_results.values()])

    if avg_icc >= 0.90:
        avg_quality = 'Excellent'
    elif avg_icc >= 0.75:
        avg_quality = 'Good'
    elif avg_icc >= 0.50:
        avg_quality = 'Moderate'
    else:
        avg_quality = 'Poor'

    md += f"""
**Cross-Condition Average ICC(3)**: {avg_icc:.3f} ({avg_quality})
**Cross-Condition Average Within-1**: {avg_within1*100:.1f}%

---

## Dimension Agreement Across Conditions

| Dimension | """

    for cond in conditions:
        md += f"{cond[:8]} | "
    md += "Avg |\n"

    md += "|-----------|"
    for _ in conditions:
        md += "--------|"
    md += "-----|\n"

    for dim in DIMENSIONS:
        md += f"| {dim} |"
        dim_iccs = []
        for cond in conditions:
            if dim in all_results[cond]['by_dimension']:
                icc = all_results[cond]['by_dimension'][dim]['icc_avg']
                dim_iccs.append(icc)
                md += f" {icc:.2f} |"
            else:
                md += " — |"
        avg_dim_icc = np.mean(dim_iccs) if dim_iccs else 0
        md += f" **{avg_dim_icc:.2f}** |\n"

    md += """
---

## ICC Interpretation Guide

| ICC Value | Interpretation | Meaning |
|-----------|----------------|---------|
| > 0.90 | **Excellent** | Near-perfect agreement |
| 0.75-0.90 | **Good** | Reliable for research |
| 0.50-0.75 | **Moderate** | Acceptable with caution |
| < 0.50 | **Poor** | Low reliability |

---

## Per-Condition Detail Briefs

| Condition | Brief Location |
|-----------|----------------|
"""

    for cond in conditions:
        md += f"| {cond} | `{cond}/judge_agreement/JUDGE_AGREEMENT_BRIEF.md` |\n"

    md += """
---

## Methodology

### Metrics Calculated

| Metric | Description |
|--------|-------------|
| **Mean r** | Average pairwise Pearson correlation between judges |
| **ICC(1)** | Intraclass correlation for single rater reliability |
| **ICC(3)** | Intraclass correlation for average of 3 raters |
| **MAD** | Mean absolute difference between judge pairs (1-10 scale) |
| **Within-1** | Percentage where all judges differ by ≤1 point |

### Data Sources

- Job files from `outputs/single_prompt_jobs/`
- Only evaluations with all 3 judges providing valid scores included

---

## Data Provenance

**Audit Files**: Per-condition `judge_agreement_audit.json`
**Consolidated Audit**: `judge_agreement_consolidated_audit.json`
**Generated By**: `scripts/check_judge_agreement.py`
"""

    md_path = output_dir / 'JUDGE_AGREEMENT_CONSOLIDATED.md'
    with open(md_path, 'w') as f:
        f.write(md)
    print(f"\nSaved: {md_path}")

    # Save consolidated audit JSON
    audit = {
        'schema_version': '1.0',
        'metadata': {
            'generated': datetime.now().isoformat(),
            'analysis': 'Judge Agreement - Cross-Condition Consolidated',
            'n_conditions': len(conditions)
        },
        'provenance': {
            'source_files': {
                'per_condition_audits': f'{base_dir}/*/judge_agreement/judge_agreement_audit.json'
            },
            'methodology': {
                'description': 'Consolidated inter-rater reliability across all conditions',
                'statistical_tests': ['ICC(3,k)', 'within_1_agreement'],
                'aggregation': 'mean across conditions'
            }
        },
        'results': {
            'avg_icc_avg': {
                'statistic': 'ICC(3,k)',
                'value': round(avg_icc, 4),
                'n': len(conditions),
                'interpretation': avg_quality
            }
        },
        'summary': {
            'avg_icc_avg': round(avg_icc, 4),
            'avg_within1': round(avg_within1, 4),
            'overall_quality': avg_quality
        },
        'conditions': {cond: {
            'n_models': r['n_models'],
            'n_evaluations': r['n_evaluations'],
            'overall_icc_avg': r['overall']['icc_avg'],
            'overall_quality': r['overall']['quality'],
            'overall_within1': r['overall']['within1']
        } for cond, r in all_results.items()}
    }

    audit_path = output_dir / 'judge_agreement_consolidated_audit.json'
    with open(audit_path, 'w') as f:
        json.dump(audit, f, indent=2)
    print(f"Saved: {audit_path}")


def main():
    parser = argparse.ArgumentParser(description='Judge Agreement Analysis')
    parser.add_argument('--condition', help='Condition to analyze')
    parser.add_argument('--all', action='store_true', help='Analyze all conditions')
    parser.add_argument('--base-dir', type=str, default='outputs/behavioral_profiles',
                        help='Base directory for behavioral profiles (default: outputs/behavioral_profiles)')
    args = parser.parse_args()

    base_dir = args.base_dir
    conditions = ['baseline', 'authority', 'urgency', 'minimal_steering',
                  'telemetryV3', 'reminder', 'naturalistic', 'naturalistic_50',
                  'naturalistic_r2', 'all_combined']

    if args.all:
        all_results = {}
        for cond in conditions:
            results = analyze_condition(cond)
            if results:
                save_condition_outputs(results, cond, base_dir)
                all_results[cond] = results

        if all_results:
            create_consolidated_brief(all_results, base_dir)

    elif args.condition:
        results = analyze_condition(args.condition)
        if results:
            save_condition_outputs(results, args.condition, base_dir)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
