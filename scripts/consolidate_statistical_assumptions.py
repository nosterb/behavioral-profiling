#!/usr/bin/env python3
"""
Consolidate Statistical Assumptions Analysis

Aggregates per-condition statistical assumption audits into a cross-condition summary.

Usage:
    python3 scripts/consolidate_statistical_assumptions.py
    python3 scripts/consolidate_statistical_assumptions.py --output-dir custom/path
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


CONDITIONS = ['baseline', 'authority', 'urgency', 'minimal_steering',
              'telemetryV3', 'reminder', 'naturalistic', 'naturalistic_50']


def load_condition_audit(condition: str) -> dict:
    """Load the statistical assumptions audit for a condition."""
    # Try multiple possible locations
    paths = [
        Path(f'outputs/behavioral_profiles/{condition}/statistical_assumptions/normality_audit.json'),
        Path(f'outputs/behavioral_profiles/{condition}/statistical_assumptions/statistical_assumptions_audit.json'),
    ]

    for path in paths:
        if path.exists():
            with open(path) as f:
                return json.load(f)

    return None


def load_job_audit(condition: str) -> dict:
    """Load job audit for a condition."""
    path = Path(f'outputs/behavioral_profiles/{condition}/job_audit.json')
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def main():
    parser = argparse.ArgumentParser(description='Consolidate Statistical Assumptions')
    parser.add_argument('--output-dir', default='outputs/behavioral_profiles/research_synthesis/limitations/statistical_assumptions',
                        help='Output directory')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Consolidating statistical assumptions across conditions...")

    # Collect data from each condition
    conditions_data = {}
    summary_table = []
    cross_condition_outliers = {}

    for condition in CONDITIONS:
        audit = load_condition_audit(condition)
        job_audit = load_job_audit(condition)

        if not audit:
            print(f"  {condition}: No audit found, skipping")
            continue

        print(f"  {condition}: Loaded")

        # Extract key metrics
        n_models = audit.get('metadata', {}).get('n_models', 45)
        results = audit.get('results', {})
        summary = results.get('summary', {})
        outliers = results.get('outliers', [])
        corr_robust = results.get('correlation_robustness', {}).get('full_sample', {})
        corr_clean = results.get('correlation_robustness', {}).get('outliers_removed', {})

        # Build condition entry
        cond_entry = {
            'n_models': n_models,
            'parametric_appropriate_clean': summary.get('residuals_normal_without_outliers', True),
            'sophistication_symmetric': summary.get('sophistication_symmetric', True),
            'correlation_methods_agree_full': corr_robust.get('methods_agree', True),
            'correlation_methods_agree_clean': corr_clean.get('methods_agree', True),
            'pearson_r_full': round(corr_robust.get('pearson_r', 0), 4),
            'pearson_r_clean': round(corr_clean.get('pearson_r', 0), 4),
            'spearman_rho_full': round(corr_robust.get('spearman_rho', 0), 4),
            'spearman_rho_clean': round(corr_clean.get('spearman_rho', 0), 4),
            'n_outliers': len(outliers),
            'outlier_models': [o.get('model', o.get('model_id', 'unknown')) for o in outliers]
        }
        conditions_data[condition] = cond_entry

        # Build summary table entry
        job_summary = job_audit.get('summary', {}) if job_audit else {}
        table_entry = {
            'condition': condition,
            'n_models': n_models,
            'unique_prompts': job_summary.get('n_unique_prompts', 'N/A'),
            'total_evals': job_summary.get('total_evaluations', 'N/A'),
            'jobs_complete': f"{job_summary.get('n_jobs_complete', '?')}/{job_summary.get('n_jobs', '?')}",
            'n_outliers': len(outliers),
            'outlier_models': cond_entry['outlier_models'],
            'status_clean': 'OK' if cond_entry['parametric_appropriate_clean'] else 'WARN'
        }
        summary_table.append(table_entry)

        # Track cross-condition outliers
        for outlier in outliers:
            model = outlier.get('model', outlier.get('model_id', 'unknown')).lower().replace(' ', '-')
            if model not in cross_condition_outliers:
                cross_condition_outliers[model] = {
                    'conditions': [],
                    'provider': outlier.get('provider', 'Unknown')
                }
            cross_condition_outliers[model]['conditions'].append(condition)

    if not conditions_data:
        print("ERROR: No condition data found")
        return

    # Find most frequent outlier
    most_frequent = None
    max_freq = 0
    for model, data in cross_condition_outliers.items():
        if len(data['conditions']) > max_freq:
            max_freq = len(data['conditions'])
            most_frequent = {
                'model': model,
                'provider': data['provider'],
                'frequency': f"{len(data['conditions'])}/{len(conditions_data)}",
                'conditions': data['conditions'],
                'interpretation': 'Consistently exhibits higher disinhibition than predicted by sophistication level'
            }

    # Build consolidated audit
    audit = {
        'schema_version': '1.0',
        'metadata': {
            'generated': datetime.now().isoformat(),
            'analysis': 'Statistical Assumptions - Cross-Condition Consolidated',
            'n_conditions': len(conditions_data)
        },
        'provenance': {
            'source_files': {
                'per_condition_audits': 'outputs/behavioral_profiles/*/statistical_assumptions/normality_audit.json'
            },
            'methodology': {
                'description': 'Consolidation of per-condition statistical assumption checks',
                'tests_aggregated': ['Shapiro-Wilk normality', 'Pearson vs Spearman agreement', 'outlier detection'],
                'outlier_threshold': '2.0 SD from regression line'
            }
        },
        'results': {
            'n_conditions_analyzed': len(conditions_data),
            'all_conditions_parametric_appropriate': all(c['parametric_appropriate_clean'] for c in conditions_data.values()),
            'total_outliers_identified': sum(c['n_outliers'] for c in conditions_data.values()),
            'cross_condition_outlier_count': len(cross_condition_outliers)
        },
        'summary_table': summary_table,
        'conditions': conditions_data,
        'cross_condition_outliers': cross_condition_outliers,
        'notable_patterns': {
            'most_frequent_outlier': most_frequent
        } if most_frequent else {}
    }

    # Save audit JSON
    audit_path = output_dir / 'statistical_assumptions_consolidated_audit.json'
    with open(audit_path, 'w') as f:
        json.dump(audit, f, indent=2)
    print(f"\nSaved: {audit_path}")

    # Generate markdown brief
    md = f"""# Statistical Assumptions - Cross-Condition Consolidated

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Conditions Analyzed**: {len(conditions_data)}

---

## Summary

| Condition | N | Prompts | Evals | Jobs | Outliers | Status |
|-----------|---|---------|-------|------|----------|--------|
"""

    for entry in summary_table:
        outlier_str = ', '.join(entry['outlier_models'][:2]) if entry['outlier_models'] else '—'
        if len(entry['outlier_models']) > 2:
            outlier_str += f" (+{len(entry['outlier_models'])-2})"
        md += f"| {entry['condition']} | {entry['n_models']} | {entry['unique_prompts']} | {entry['total_evals']} | {entry['jobs_complete']} | {entry['n_outliers']} | {entry['status_clean']} |\n"

    md += f"""
---

## Cross-Condition Outliers

Models appearing as statistical outliers in multiple conditions:

| Model | Provider | Frequency | Conditions |
|-------|----------|-----------|------------|
"""

    for model, data in sorted(cross_condition_outliers.items(), key=lambda x: -len(x[1]['conditions'])):
        if len(data['conditions']) > 1:
            md += f"| {model} | {data['provider']} | {len(data['conditions'])}/{len(conditions_data)} | {', '.join(data['conditions'])} |\n"

    md += """
---

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `*/statistical_assumptions/normality_audit.json` | Per-condition assumption checks |

### Audit File
| File | Description |
|------|-------------|
| `statistical_assumptions_consolidated_audit.json` | Complete cross-condition data |

### Reproducibility
```bash
python3 scripts/consolidate_statistical_assumptions.py
```
"""

    md_path = output_dir / 'STATISTICAL_ASSUMPTIONS_CONSOLIDATED.md'
    with open(md_path, 'w') as f:
        f.write(md)
    print(f"Saved: {md_path}")

    print(f"\nConsolidated {len(conditions_data)} conditions")


if __name__ == '__main__':
    main()
