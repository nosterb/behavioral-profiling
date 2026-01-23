#!/usr/bin/env python3
"""
Job Metrics Audit Script

Comprehensive audit of all job outputs with key metrics:
- Number of models
- Number of unique prompts
- Number of judges
- Number of judge evaluations
- Data completeness checks

Usage:
    python3 scripts/audit_job_metrics.py
    python3 scripts/audit_job_metrics.py --condition baseline
    python3 scripts/audit_job_metrics.py --output-dir outputs/behavioral_profiles/research_synthesis/audit
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def extract_condition(job_name: str, parent_dir: str = '') -> str:
    """Extract condition from job directory name.

    Job naming conventions:
    - job_broad_1_20260106_205223 -> baseline
    - job_broad_1_authority_20260107_234206 -> authority
    - job_naturalistic_01_20260118_135829 -> naturalistic
    - job_naturalistic_01_50_20260118_161728 -> naturalistic_50
    """
    # Combine parent dir context if available
    full_context = f"{parent_dir}_{job_name}" if parent_dir else job_name

    # Check for known conditions in order of specificity
    # Order matters - check more specific patterns first
    conditions = [
        ('_minimal_steering_', 'minimal_steering'),
        ('_telemetryV3_', 'telemetryV3'),
        ('_telemetry_', 'telemetryV3'),
        ('_authority_', 'authority'),
        ('_urgency_', 'urgency'),
        ('_reminder_', 'reminder'),
        ('naturalistic_50', 'naturalistic_50'),
        ('_50_', 'naturalistic_50'),  # naturalistic_01_50_
        ('naturalistic_', 'naturalistic'),
    ]

    for pattern, condition in conditions:
        if pattern in job_name:
            return condition

    # Check if it's explicitly a baseline directory
    if 'baseline' in parent_dir.lower() or 'baseline' in job_name.lower():
        return 'baseline'

    # Default to baseline for jobs without condition suffix
    # (e.g., job_broad_1_20260106 with just timestamp)
    return 'baseline'


def hash_prompt(prompt: str) -> str:
    """Create a short hash of the prompt for identification."""
    return hashlib.md5(prompt.encode()).hexdigest()[:8]


def audit_job(job_dir: Path) -> dict:
    """Audit a single job directory and return metrics."""
    json_files = list(job_dir.glob('*.json'))
    if not json_files:
        return {'error': 'no_json_file', 'job_name': job_dir.name}

    job_file = json_files[0]

    try:
        with open(job_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {'error': f'json_decode_error: {e}', 'job_name': job_dir.name}

    job_name = job_dir.name
    parent_dir = job_dir.parent.name if job_dir.parent.name != 'single_prompt_jobs' else ''
    condition = extract_condition(job_name, parent_dir)

    # Extract metrics
    metrics = {
        'job_name': job_name,
        'job_file': str(job_file),
        'condition': condition,
        'timestamp': None,
        'prompt': None,
        'prompt_hash': None,
        'prompt_length': 0,
        'models_configured': 0,
        'model_responses': 0,
        'judge_evaluation': {
            'exists': False,
            'judges': [],
            'n_judges': 0,
            'n_evaluations': 0,
            'n_valid_3judge': 0,
            'dimensions_scored': []
        },
        'judge_evaluation_random': {
            'exists': False,
            'judges': [],
            'n_judges': 0,
            'n_evaluations': 0
        },
        'judge_evaluation_telemetry': {
            'exists': False,
            'n_evaluations': 0
        },
        'completeness': {
            'has_model_responses': False,
            'has_judge_evaluation': False,
            'all_models_evaluated': False,
            'all_evals_have_3_judges': False
        }
    }

    # Job metadata
    job_meta = data.get('job_metadata', {})
    metrics['timestamp'] = job_meta.get('timestamp') or job_meta.get('start_time')

    # Prompt
    prompt = data.get('prompt', '')
    if isinstance(prompt, dict):
        prompt = prompt.get('content', '') or prompt.get('text', '') or str(prompt)
    metrics['prompt'] = prompt[:200] + '...' if len(prompt) > 200 else prompt
    metrics['prompt_hash'] = hash_prompt(prompt) if prompt else None
    metrics['prompt_length'] = len(prompt)

    # Models configured
    models = data.get('models', [])
    metrics['models_configured'] = len(models)

    # Model responses
    model_responses = data.get('model_responses', [])
    metrics['model_responses'] = len(model_responses)
    metrics['completeness']['has_model_responses'] = len(model_responses) > 0

    # Judge evaluation (original)
    je = data.get('judge_evaluation', {})
    if je:
        metrics['judge_evaluation']['exists'] = True
        evaluations = je.get('evaluations', [])
        metrics['judge_evaluation']['n_evaluations'] = len(evaluations)
        metrics['completeness']['has_judge_evaluation'] = len(evaluations) > 0

        # Check judges and validity
        judges_seen = set()
        valid_3judge = 0
        dimensions_seen = set()

        for eval_entry in evaluations:
            pass1_judges = eval_entry.get('pass1_judges', [])

            for judge in pass1_judges:
                judge_name = judge.get('judge_display_name', 'unknown')
                judges_seen.add(judge_name)

                ext_json = judge.get('extracted_json', {})
                if ext_json and 'scores' in ext_json:
                    dimensions_seen.update(ext_json['scores'].keys())

            # Check if valid 3-judge eval
            if len(pass1_judges) == 3:
                all_have_scores = all(
                    (j.get('extracted_json') or {}).get('scores')
                    for j in pass1_judges
                )
                if all_have_scores:
                    valid_3judge += 1

        metrics['judge_evaluation']['judges'] = sorted(list(judges_seen))
        metrics['judge_evaluation']['n_judges'] = len(judges_seen)
        metrics['judge_evaluation']['n_valid_3judge'] = valid_3judge
        metrics['judge_evaluation']['dimensions_scored'] = sorted(list(dimensions_seen))

        # Completeness checks
        metrics['completeness']['all_models_evaluated'] = (
            len(evaluations) >= metrics['models_configured'] > 0
        )
        metrics['completeness']['all_evals_have_3_judges'] = (
            valid_3judge == len(evaluations) and len(evaluations) > 0
        )
        # Judge evaluation complete if we have valid 3-judge evals
        # (model_responses may have been cleared for storage)
        metrics['completeness']['judge_eval_complete'] = (
            valid_3judge > 0 and valid_3judge == len(evaluations)
        )

    # Judge evaluation random (counterfactual)
    jer = data.get('judge_evaluation_random', {})
    if jer:
        metrics['judge_evaluation_random']['exists'] = True
        rand_evals = jer.get('evaluations', [])
        metrics['judge_evaluation_random']['n_evaluations'] = len(rand_evals)

        rand_judges = set()
        for eval_entry in rand_evals:
            for judge in eval_entry.get('pass1_judges', []):
                rand_judges.add(judge.get('judge_display_name', 'unknown'))

        metrics['judge_evaluation_random']['judges'] = sorted(list(rand_judges))
        metrics['judge_evaluation_random']['n_judges'] = len(rand_judges)

    # Judge evaluation telemetry (for telemetryV3 condition)
    jet = data.get('judge_evaluation_telemetry', {})
    if jet:
        metrics['judge_evaluation_telemetry']['exists'] = True
        metrics['judge_evaluation_telemetry']['n_evaluations'] = len(jet.get('evaluations', []))

    return metrics


def aggregate_by_condition(job_metrics: list) -> dict:
    """Aggregate job metrics by condition."""
    by_condition = defaultdict(lambda: {
        'jobs': [],
        'n_jobs': 0,
        'n_jobs_complete': 0,
        'n_jobs_incomplete': 0,
        'total_models_configured': 0,
        'total_model_responses': 0,
        'total_evaluations': 0,
        'total_valid_3judge': 0,
        'unique_prompts': set(),
        'unique_prompt_hashes': set(),
        'judges_used': set(),
        'dimensions_scored': set(),
        'missing_jobs': []
    })

    for m in job_metrics:
        if 'error' in m:
            continue

        cond = m['condition']
        agg = by_condition[cond]

        agg['jobs'].append(m['job_name'])
        agg['n_jobs'] += 1
        agg['total_models_configured'] += m['models_configured']
        agg['total_model_responses'] += m['model_responses']
        agg['total_evaluations'] += m['judge_evaluation']['n_evaluations']
        agg['total_valid_3judge'] += m['judge_evaluation']['n_valid_3judge']

        if m['prompt_hash']:
            agg['unique_prompt_hashes'].add(m['prompt_hash'])

        agg['judges_used'].update(m['judge_evaluation']['judges'])
        agg['dimensions_scored'].update(m['judge_evaluation']['dimensions_scored'])

        # Check completeness - focus on judge evaluation validity
        # (model_responses may have been cleared for storage efficiency)
        is_complete = (
            m['completeness'].get('judge_eval_complete', False) or
            (m['completeness']['has_judge_evaluation'] and
             m['completeness']['all_evals_have_3_judges'])
        )

        if is_complete:
            agg['n_jobs_complete'] += 1
        else:
            agg['n_jobs_incomplete'] += 1
            agg['missing_jobs'].append({
                'job': m['job_name'],
                'has_responses': m['completeness']['has_model_responses'],
                'has_judge_eval': m['completeness']['has_judge_evaluation'],
                'valid_3judge': m['judge_evaluation']['n_valid_3judge'],
                'expected_evals': m['models_configured']
            })

    # Convert sets to sorted lists for JSON serialization
    result = {}
    for cond, agg in by_condition.items():
        result[cond] = {
            'n_jobs': agg['n_jobs'],
            'n_jobs_complete': agg['n_jobs_complete'],
            'n_jobs_incomplete': agg['n_jobs_incomplete'],
            'n_unique_prompts': len(agg['unique_prompt_hashes']),
            'total_models_configured': agg['total_models_configured'],
            'total_model_responses': agg['total_model_responses'],
            'total_evaluations': agg['total_evaluations'],
            'total_valid_3judge': agg['total_valid_3judge'],
            'judges_used': sorted(list(agg['judges_used'])),
            'n_judges': len(agg['judges_used']),
            'dimensions_scored': sorted(list(agg['dimensions_scored'])),
            'n_dimensions': len(agg['dimensions_scored']),
            'completeness_rate': agg['n_jobs_complete'] / agg['n_jobs'] if agg['n_jobs'] > 0 else 0,
            'missing_jobs': agg['missing_jobs'] if agg['missing_jobs'] else None
        }

    return result


def generate_condition_audit(condition: str, cond_data: dict, jobs: list, output_dir: Path) -> None:
    """Generate per-condition audit files."""
    # Output directly to the condition directory (output_dir is already the condition dir)
    cond_dir = output_dir
    cond_dir.mkdir(parents=True, exist_ok=True)

    # Filter jobs for this condition
    cond_jobs = [j for j in jobs if j.get('condition') == condition]

    # Generate JSON audit
    audit = {
        'schema_version': '1.0',
        'metadata': {
            'generated': datetime.now().isoformat(),
            'analysis': f'Job Audit - {condition}',
            'condition': condition
        },
        'provenance': {
            'source_files': {
                'job_outputs': f'outputs/single_prompt_jobs/**/*_{condition}_*.json'
            },
            'methodology': {
                'description': 'Per-condition job completeness audit',
                'metrics': ['job_count', 'completeness_rate', 'valid_3judge_count']
            }
        },
        'results': {
            'n_jobs': cond_data.get('n_jobs', 0),
            'completeness_rate': cond_data.get('completeness_rate', 0),
            'total_valid_3judge': cond_data.get('total_valid_3judge', 0)
        },
        'summary': cond_data,
        'jobs': cond_jobs
    }

    json_path = cond_dir / 'job_audit.json'
    with open(json_path, 'w') as f:
        json.dump(audit, f, indent=2, default=str)

    # Generate markdown summary for inclusion in RESEARCH_BRIEF.md
    completeness_pct = cond_data['completeness_rate'] * 100
    status = "✅" if completeness_pct == 100 else "⚠️" if completeness_pct >= 80 else "❌"

    # Calculate models per complete job (more accurate than total/n_jobs)
    models_per_job = (cond_data['total_valid_3judge'] // cond_data['n_jobs_complete']
                      if cond_data['n_jobs_complete'] > 0 else 0)

    md = f"""## Data Audit Summary

| Metric | Value |
|--------|-------|
| Jobs | {cond_data['n_jobs']} |
| Complete | {cond_data['n_jobs_complete']} ({completeness_pct:.0f}%) {status} |
| Unique Prompts | {cond_data['n_unique_prompts']} |
| Total Evaluations | {cond_data['total_evaluations']:,} |
| Valid 3-Judge Evals | {cond_data['total_valid_3judge']:,} |
| Models per Job | {models_per_job} |
| Judges | {', '.join(cond_data['judges_used'])} |
| Dimensions | {cond_data['n_dimensions']} |

**Audit File**: `job_audit.json`
"""

    if cond_data.get('missing_jobs'):
        md += f"""
### Incomplete Jobs ({len(cond_data['missing_jobs'])})

| Job | Valid 3-Judge | Expected |
|-----|---------------|----------|
"""
        for mj in cond_data['missing_jobs'][:10]:  # Limit to 10
            md += f"| {mj['job'][:50]} | {mj['valid_3judge']} | {mj['expected_evals']} |\n"

        if len(cond_data['missing_jobs']) > 10:
            md += f"\n*...and {len(cond_data['missing_jobs']) - 10} more*\n"

    md_path = cond_dir / 'DATA_AUDIT.md'
    with open(md_path, 'w') as f:
        f.write(md)

    return json_path, md_path


def generate_markdown_report(audit_data: dict, output_path: Path) -> None:
    """Generate a markdown report from audit data."""

    md = f"""# Job Metrics Audit Report

**Generated**: {audit_data['metadata']['generated']}
**Total Jobs Scanned**: {audit_data['summary']['total_jobs']}
**Total Conditions**: {audit_data['summary']['total_conditions']}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total jobs | {audit_data['summary']['total_jobs']} |
| Complete jobs | {audit_data['summary']['total_complete']} |
| Incomplete jobs | {audit_data['summary']['total_incomplete']} |
| Total model evaluations | {audit_data['summary']['total_evaluations']:,} |
| Total valid 3-judge evals | {audit_data['summary']['total_valid_3judge']:,} |

---

## By Condition

| Condition | Jobs | Complete | Unique Prompts | Models | Evaluations | Valid 3-Judge | Judges | Completeness |
|-----------|------|----------|----------------|--------|-------------|---------------|--------|--------------|
"""

    for cond in sorted(audit_data['by_condition'].keys()):
        c = audit_data['by_condition'][cond]
        completeness_pct = f"{c['completeness_rate']*100:.0f}%"
        status = "✅" if c['completeness_rate'] == 1.0 else "⚠️" if c['completeness_rate'] > 0.5 else "❌"
        md += f"| {cond} | {c['n_jobs']} | {c['n_jobs_complete']} | {c['n_unique_prompts']} | {c['total_models_configured']} | {c['total_evaluations']} | {c['total_valid_3judge']} | {c['n_judges']} | {status} {completeness_pct} |\n"

    md += """
---

## Condition Details

"""

    for cond in sorted(audit_data['by_condition'].keys()):
        c = audit_data['by_condition'][cond]
        md += f"""### {cond.title()}

| Metric | Value |
|--------|-------|
| Jobs | {c['n_jobs']} |
| Complete | {c['n_jobs_complete']} |
| Incomplete | {c['n_jobs_incomplete']} |
| Unique prompts | {c['n_unique_prompts']} |
| Models configured | {c['total_models_configured']} |
| Model responses | {c['total_model_responses']} |
| Judge evaluations | {c['total_evaluations']} |
| Valid 3-judge evals | {c['total_valid_3judge']} |
| Judges | {', '.join(c['judges_used']) if c['judges_used'] else 'N/A'} |
| Dimensions | {c['n_dimensions']} |
| Completeness | {c['completeness_rate']*100:.1f}% |

"""
        if c['missing_jobs']:
            md += "**Incomplete Jobs:**\n\n"
            md += "| Job | Has Responses | Has Judge Eval | Valid 3-Judge | Expected |\n"
            md += "|-----|---------------|----------------|---------------|----------|\n"
            for mj in c['missing_jobs']:
                has_resp = "✅" if mj['has_responses'] else "❌"
                has_je = "✅" if mj['has_judge_eval'] else "❌"
                md += f"| {mj['job']} | {has_resp} | {has_je} | {mj['valid_3judge']} | {mj['expected_evals']} |\n"
            md += "\n"

    md += """---

## Data Provenance

### Source
- Job outputs: `outputs/single_prompt_jobs/**/*.json`

### Audit File
- `job_metrics_audit.json` - Complete audit data

### Reproducibility
```bash
python3 scripts/audit_job_metrics.py
```

---

*This audit supports data quality verification for the behavioral profiling research initiative.*
"""

    with open(output_path, 'w') as f:
        f.write(md)


def find_job_directories(base_dir: Path) -> list:
    """Find all job directories, handling nested structure."""
    job_dirs = []

    for item in base_dir.iterdir():
        if not item.is_dir():
            continue

        # Skip known non-job directories
        if item.name in ['chats', 'visualization', 'visualizations']:
            continue

        # Check if this directory contains a job JSON directly
        json_files = list(item.glob('*.json'))
        if json_files and any('job_' in f.name or item.name.startswith('job_') for f in json_files):
            job_dirs.append(item)
        elif json_files and len(json_files) == 1:
            # Single JSON file might be a job
            job_dirs.append(item)
        else:
            # Check for nested job directories (e.g., baseline_broad/job_broad_1_...)
            nested_jobs = [d for d in item.iterdir()
                          if d.is_dir() and d.name.startswith('job_')]
            job_dirs.extend(nested_jobs)

            # Also check for non-prefixed job dirs with JSON files
            for subdir in item.iterdir():
                if subdir.is_dir() and subdir.name not in ['chats', 'visualization']:
                    sub_jsons = list(subdir.glob('*.json'))
                    if sub_jsons:
                        job_dirs.append(subdir)

    return sorted(set(job_dirs))


def main():
    parser = argparse.ArgumentParser(description='Audit job metrics across all conditions')
    parser.add_argument('--condition', help='Filter to specific condition')
    parser.add_argument('--output-dir', default='outputs/behavioral_profiles/research_synthesis/audit',
                        help='Output directory for audit files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    jobs_dir = Path('outputs/single_prompt_jobs')
    if not jobs_dir.exists():
        print(f"ERROR: Jobs directory not found: {jobs_dir}")
        sys.exit(1)

    # Find all job directories (handles nested structure)
    job_dirs = find_job_directories(jobs_dir)
    print(f"Found {len(job_dirs)} job directories")

    # Audit each job
    all_metrics = []
    for job_dir in job_dirs:
        metrics = audit_job(job_dir)

        # Filter by condition if specified
        if args.condition and metrics.get('condition') != args.condition:
            continue

        all_metrics.append(metrics)

        if args.verbose:
            if 'error' in metrics:
                print(f"  ERROR: {metrics['job_name']}: {metrics['error']}")
            else:
                status = "✅" if metrics['completeness']['all_evals_have_3_judges'] else "⚠️"
                print(f"  {status} {metrics['job_name']}: {metrics['judge_evaluation']['n_valid_3judge']} valid evals")

    # Aggregate by condition
    by_condition = aggregate_by_condition(all_metrics)

    # Calculate summary
    summary = {
        'total_jobs': len([m for m in all_metrics if 'error' not in m]),
        'total_conditions': len(by_condition),
        'total_complete': sum(c['n_jobs_complete'] for c in by_condition.values()),
        'total_incomplete': sum(c['n_jobs_incomplete'] for c in by_condition.values()),
        'total_evaluations': sum(c['total_evaluations'] for c in by_condition.values()),
        'total_valid_3judge': sum(c['total_valid_3judge'] for c in by_condition.values())
    }

    # Build audit output
    audit_data = {
        'schema_version': '1.0',
        'metadata': {
            'generated': datetime.now().isoformat(),
            'analysis': 'Job Metrics Audit',
            'script': 'scripts/audit_job_metrics.py',
            'source_dir': str(jobs_dir)
        },
        'provenance': {
            'source_files': {
                'job_outputs': 'outputs/single_prompt_jobs/**/*.json'
            },
            'methodology': {
                'description': 'Comprehensive audit of all job outputs with completeness metrics',
                'metrics': ['model_count', 'judge_evaluation_count', 'completeness_rate', 'valid_3judge_count']
            }
        },
        'results': {
            'summary': summary
        },
        'summary': summary,
        'by_condition': by_condition,
        'per_job': all_metrics
    }

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON audit
    audit_json_path = output_dir / 'job_metrics_audit.json'
    with open(audit_json_path, 'w') as f:
        json.dump(audit_data, f, indent=2, default=str)
    print(f"\nSaved: {audit_json_path}")

    # Generate markdown report
    md_path = output_dir / 'JOB_METRICS_AUDIT.md'
    generate_markdown_report(audit_data, md_path)
    print(f"Saved: {md_path}")

    # Generate per-condition audit files
    profiles_dir = Path('outputs/behavioral_profiles')
    print(f"\nGenerating per-condition audits...")
    for cond, cond_data in by_condition.items():
        cond_output_dir = profiles_dir / cond
        if cond_output_dir.exists():
            json_path, md_path = generate_condition_audit(cond, cond_data, all_metrics, cond_output_dir)
            print(f"  {cond}: {json_path.name}, {md_path.name}")

    # Print summary
    print(f"\n{'='*70}")
    print("AUDIT SUMMARY")
    print(f"{'='*70}")
    print(f"Total jobs: {summary['total_jobs']}")
    print(f"Complete: {summary['total_complete']}")
    print(f"Incomplete: {summary['total_incomplete']}")
    print(f"Total evaluations: {summary['total_evaluations']:,}")
    print(f"Valid 3-judge: {summary['total_valid_3judge']:,}")

    print(f"\nBy Condition:")
    for cond in sorted(by_condition.keys()):
        c = by_condition[cond]
        status = "✅" if c['completeness_rate'] == 1.0 else "⚠️"
        print(f"  {status} {cond}: {c['n_jobs_complete']}/{c['n_jobs']} complete, "
              f"{c['total_valid_3judge']} valid evals, {c['n_unique_prompts']} prompts")


if __name__ == '__main__':
    main()
