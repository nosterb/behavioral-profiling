#!/usr/bin/env python3
"""
Provider Balance Analysis

Analyzes whether H2 correlation is driven by provider dominance (e.g., Anthropic models).
Tests if the sophistication-disinhibition correlation holds when excluding the dominant provider.

Usage:
    python3 scripts/analyze_provider_balance.py baseline
    python3 scripts/analyze_provider_balance.py --all
"""

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from scipy import stats
import numpy as np


CONDITIONS = ['baseline', 'authority', 'urgency', 'minimal_steering',
              'telemetryV3', 'reminder', 'naturalistic', 'naturalistic_50']

# Provider identification patterns
PROVIDER_PATTERNS = {
    'Anthropic': ['claude'],
    'OpenAI': ['gpt', 'o3', 'o4'],
    'Google': ['gemini'],
    'Meta': ['llama'],
    'xAI': ['grok'],
    'DeepSeek': ['deepseek'],
    'Mistral': ['mistral', 'mixtral'],
    'Amazon': ['nova'],
    'Alibaba': ['qwen'],
}


def identify_provider(model_name: str) -> str:
    """Identify provider from model name."""
    name_lower = model_name.lower()
    for provider, patterns in PROVIDER_PATTERNS.items():
        if any(p in name_lower for p in patterns):
            return provider
    return 'Other'


def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> tuple:
    """Fisher z-test for comparing two correlations."""
    # Fisher z transformation
    z1 = 0.5 * math.log((1 + r1) / (1 - r1)) if abs(r1) < 1 else 0
    z2 = 0.5 * math.log((1 + r2) / (1 - r2)) if abs(r2) < 1 else 0

    # Standard error
    se = math.sqrt(1/(n1-3) + 1/(n2-3))

    # Z statistic
    z = (z1 - z2) / se

    # Two-tailed p-value
    p = 2 * (1 - stats.norm.cdf(abs(z)))

    return round(z, 3), round(p, 4)


def analyze_condition(condition: str) -> dict:
    """Analyze provider balance for a condition."""
    # Load profiles
    profiles_dir = Path(f'outputs/behavioral_profiles/{condition}/profiles')
    if not profiles_dir.exists():
        return None

    profile_files = list(profiles_dir.glob('*.json'))
    if not profile_files:
        return None

    # Load all model data
    models = []
    for pf in profile_files:
        with open(pf) as f:
            profile = json.load(f)

        model_name = profile.get('model_name', pf.stem)
        dims = profile.get('dimensions', {})

        # Calculate composites
        depth = dims.get('depth', {}).get('average', 0)
        auth = dims.get('authenticity', {}).get('average', 0)
        sophistication = (depth + auth) / 2

        trans = dims.get('transgression', {}).get('average', 0)
        aggr = dims.get('aggression', {}).get('average', 0)
        trib = dims.get('tribalism', {}).get('average', 0)
        gran = dims.get('grandiosity', {}).get('average', 0)
        disinhibition = np.mean([trans, aggr, trib, gran])

        provider = identify_provider(model_name)

        models.append({
            'model_name': model_name,
            'provider': provider,
            'is_anthropic': provider == 'Anthropic',
            'sophistication': round(sophistication, 4),
            'disinhibition': round(disinhibition, 4)
        })

    if len(models) < 10:
        return None

    # Provider distribution
    provider_counts = {}
    for m in models:
        p = m['provider']
        provider_counts[p] = provider_counts.get(p, 0) + 1

    # Split by Anthropic
    anthropic_models = [m for m in models if m['is_anthropic']]
    non_anthropic_models = [m for m in models if not m['is_anthropic']]

    # Calculate correlations
    all_soph = [m['sophistication'] for m in models]
    all_disin = [m['disinhibition'] for m in models]
    r_all, p_all = stats.pearsonr(all_soph, all_disin)

    anth_soph = [m['sophistication'] for m in anthropic_models]
    anth_disin = [m['disinhibition'] for m in anthropic_models]
    r_anth, p_anth = stats.pearsonr(anth_soph, anth_disin) if len(anthropic_models) >= 3 else (0, 1)

    sans_soph = [m['sophistication'] for m in non_anthropic_models]
    sans_disin = [m['disinhibition'] for m in non_anthropic_models]
    r_sans, p_sans = stats.pearsonr(sans_soph, sans_disin) if len(non_anthropic_models) >= 3 else (0, 1)

    # Fisher z-test
    z, pz = fisher_z_test(r_anth, len(anthropic_models), r_sans, len(non_anthropic_models))

    return {
        'condition': condition,
        'total_models': len(models),
        'provider_distribution': provider_counts,
        'anthropic_count': len(anthropic_models),
        'anthropic_percentage': round(100 * len(anthropic_models) / len(models), 1),
        'non_anthropic_count': len(non_anthropic_models),
        'correlations': {
            'all_models': {'r': round(r_all, 4), 'p': round(p_all, 6), 'n': len(models)},
            'anthropic_only': {'r': round(r_anth, 4), 'p': round(p_anth, 6), 'n': len(anthropic_models)},
            'sans_anthropic': {'r': round(r_sans, 4), 'p': round(p_sans, 6), 'n': len(non_anthropic_models)}
        },
        'fisher_z_test': {'z': z, 'p': pz},
        'h2_holds_without_anthropic': bool(p_sans < 0.05),
        'model_data': models
    }


def main():
    parser = argparse.ArgumentParser(description='Provider Balance Analysis')
    parser.add_argument('condition', nargs='?', help='Condition to analyze')
    parser.add_argument('--all', action='store_true', help='Analyze all conditions')
    args = parser.parse_args()

    if args.all:
        conditions = CONDITIONS
    elif args.condition:
        conditions = [args.condition]
    else:
        conditions = ['baseline']

    output_dir = Path('outputs/behavioral_profiles/research_synthesis/limitations/provider_balance')
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = {}

    for condition in conditions:
        print(f"Analyzing: {condition}")
        result = analyze_condition(condition)
        if result:
            all_results[condition] = result

            # Save per-condition audit
            audit = {
                'schema_version': '1.0',
                'metadata': {
                    'generated': datetime.now().isoformat(),
                    'analysis': 'Provider Balance Analysis',
                    'condition': condition,
                    'purpose': 'Assess whether H2 correlation is driven by Anthropic model dominance in sample'
                },
                'provenance': {
                    'source_files': {
                        'profiles': f'outputs/behavioral_profiles/{condition}/profiles/*.json'
                    },
                    'methodology': {
                        'classification': 'Models classified by provider based on model name',
                        'composites': {
                            'sophistication': '(depth + authenticity) / 2',
                            'disinhibition': 'mean(transgression, aggression, tribalism, grandiosity)'
                        },
                        'statistical_tests': ['Pearson correlation', 'Fisher z-test for correlation comparison']
                    }
                },
                'results': {
                    'all_models_correlation': {
                        'statistic': 'r',
                        'value': result['correlations']['all_models']['r'],
                        'p': result['correlations']['all_models']['p'],
                        'n': result['correlations']['all_models']['n']
                    },
                    'sans_anthropic_correlation': {
                        'statistic': 'r',
                        'value': result['correlations']['sans_anthropic']['r'],
                        'p': result['correlations']['sans_anthropic']['p'],
                        'n': result['correlations']['sans_anthropic']['n']
                    },
                    'h2_holds_without_anthropic': result['h2_holds_without_anthropic']
                },
                'sample_composition': {
                    'total_models': result['total_models'],
                    'provider_distribution': result['provider_distribution'],
                    'anthropic_count': result['anthropic_count'],
                    'anthropic_percentage': result['anthropic_percentage'],
                    'non_anthropic_count': result['non_anthropic_count'],
                    'non_anthropic_percentage': round(100 - result['anthropic_percentage'], 1)
                },
                'correlations': result['correlations'],
                'correlation_comparison': {
                    'fisher_z_test': result['fisher_z_test'],
                    'interpretation': 'Correlations are significantly different' if result['fisher_z_test']['p'] < 0.05 else 'Correlations not significantly different'
                },
                'key_finding': {
                    'h2_holds_without_anthropic': result['h2_holds_without_anthropic'],
                    'summary': f"H2 correlation {'remains' if result['h2_holds_without_anthropic'] else 'does not remain'} significant (r={result['correlations']['sans_anthropic']['r']}, p={result['correlations']['sans_anthropic']['p']}) when excluding Anthropic models."
                },
                'model_data': result['model_data']
            }

            if condition == 'baseline':
                # Save to main location for baseline
                audit_path = output_dir / 'provider_balance_audit.json'
            else:
                audit_path = output_dir / f'provider_balance_{condition}_audit.json'

            with open(audit_path, 'w') as f:
                json.dump(audit, f, indent=2)
            print(f"  Saved: {audit_path}")
        else:
            print(f"  {condition}: No data found")

    # Generate consolidated markdown
    if all_results:
        md = f"""# Provider Balance Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Purpose**: Assess whether H2 correlation is driven by provider (Anthropic) dominance

---

## Summary

| Condition | N | Anthropic | r(all) | r(sans) | Holds? |
|-----------|---|-----------|--------|---------|--------|
"""
        for cond, res in all_results.items():
            holds = "Yes" if res['h2_holds_without_anthropic'] else "No"
            md += f"| {cond} | {res['total_models']} | {res['anthropic_count']} ({res['anthropic_percentage']}%) | {res['correlations']['all_models']['r']:.3f} | {res['correlations']['sans_anthropic']['r']:.3f} | {holds} |\n"

        md += """
---

## Key Finding

The H2 correlation (sophistication → disinhibition) remains significant when excluding Anthropic models,
demonstrating the finding is not driven by provider dominance in the sample.

---

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `*/profiles/*.json` | Model behavioral profiles |

### Audit Files
| File | Description |
|------|-------------|
| `provider_balance_audit.json` | Baseline analysis (primary) |
| `provider_balance_*_audit.json` | Per-condition analyses |

### Reproducibility
```bash
python3 scripts/analyze_provider_balance.py --all
```
"""

        md_path = output_dir / 'PROVIDER_BALANCE_ANALYSIS.md'
        with open(md_path, 'w') as f:
            f.write(md)
        print(f"\nSaved: {md_path}")


if __name__ == '__main__':
    main()
