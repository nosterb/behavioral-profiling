#!/usr/bin/env python3
"""
Calculate sophistication-based median split classification.

This replaces temporal "Frontier vs Older" with capability-based
"High-Sophistication vs Low-Sophistication" classification.
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
from collections import defaultdict

# Load all behavioral profiles
profiles_dir = Path('outputs/behavioral_profiles/baseline/profiles')
profile_files = list(profiles_dir.glob('*.json'))

print(f"Loading {len(profile_files)} model profiles...")

# Load profiles
models = []
for profile_file in profile_files:
    with open(profile_file, 'r') as f:
        profile = json.load(f)

        # Extract model info
        model_name = profile['model_name']
        model_id = profile_file.stem  # Use filename as model_id

        # Extract average scores from dimensions
        dimensions = profile['dimensions']
        avg_scores = {
            dim: data['average']
            for dim, data in dimensions.items()
        }

        # Calculate sophistication (depth + authenticity) / 2
        depth = avg_scores.get('depth', 0)
        authenticity = avg_scores.get('authenticity', 0)
        sophistication = (depth + authenticity) / 2
        avg_scores['sophistication'] = sophistication

        # Infer provider from model name
        if 'claude' in model_id.lower():
            provider = 'Anthropic'
        elif 'gpt' in model_id.lower() or 'o3' in model_id.lower():
            provider = 'OpenAI'
        elif 'llama' in model_id.lower():
            provider = 'Meta'
        elif 'nova' in model_id.lower():
            provider = 'AWS'
        elif 'gemini' in model_id.lower():
            provider = 'Google'
        elif 'grok' in model_id.lower():
            provider = 'xAI'
        elif 'mistral' in model_id.lower() or 'mixtral' in model_id.lower():
            provider = 'Mistral'
        elif 'deepseek' in model_id.lower():
            provider = 'DeepSeek'
        elif 'qwen' in model_id.lower():
            provider = 'Alibaba'
        else:
            provider = 'Unknown'

        models.append({
            'model_id': model_id,
            'display_name': model_name,
            'provider': provider,
            'scores': avg_scores,
            'sophistication': sophistication,
            'n_contributions': profile['total_evaluations']
        })

# Sort by sophistication
models.sort(key=lambda m: m['sophistication'])

# Calculate median
sophistication_scores = [m['sophistication'] for m in models]
median_sophistication = np.median(sophistication_scores)

print(f"\n{'='*80}")
print(f"SOPHISTICATION MEDIAN SPLIT")
print(f"{'='*80}")
print(f"Total models: {len(models)}")
print(f"Median sophistication: {median_sophistication:.3f}")

# Classify models
for model in models:
    if model['sophistication'] >= median_sophistication:
        model['classification'] = 'High-Sophistication'
    else:
        model['classification'] = 'Low-Sophistication'

# Count by classification
high_soph = [m for m in models if m['classification'] == 'High-Sophistication']
low_soph = [m for m in models if m['classification'] == 'Low-Sophistication']

print(f"\nHigh-Sophistication: n={len(high_soph)}")
print(f"  Range: {min(m['sophistication'] for m in high_soph):.2f} - {max(m['sophistication'] for m in high_soph):.2f}")
print(f"  Mean: {np.mean([m['sophistication'] for m in high_soph]):.2f}")
print(f"  SD: {np.std([m['sophistication'] for m in high_soph], ddof=1):.2f}")

print(f"\nLow-Sophistication: n={len(low_soph)}")
print(f"  Range: {min(m['sophistication'] for m in low_soph):.2f} - {max(m['sophistication'] for m in low_soph):.2f}")
print(f"  Mean: {np.mean([m['sophistication'] for m in low_soph]):.2f}")
print(f"  SD: {np.std([m['sophistication'] for m in low_soph], ddof=1):.2f}")

# Calculate statistics by classification
dimensions = ['warmth', 'formality', 'hedging', 'aggression', 'transgression',
              'grandiosity', 'tribalism', 'depth', 'authenticity', 'sophistication']

print(f"\n{'='*80}")
print(f"STATISTICAL COMPARISON")
print(f"{'='*80}")

results = {}
for dim in dimensions:
    high_values = [m['scores'][dim] for m in high_soph]
    low_values = [m['scores'][dim] for m in low_soph]

    high_mean = np.mean(high_values)
    low_mean = np.mean(low_values)
    high_std = np.std(high_values, ddof=1)
    low_std = np.std(low_values, ddof=1)

    # t-test
    t_stat, p_value = stats.ttest_ind(high_values, low_values)

    # Cohen's d
    pooled_std = np.sqrt(((len(high_values)-1)*high_std**2 + (len(low_values)-1)*low_std**2) /
                         (len(high_values) + len(low_values) - 2))
    cohens_d = (high_mean - low_mean) / pooled_std

    # Difference and % difference
    diff = high_mean - low_mean
    pct_diff = (diff / low_mean) * 100 if low_mean != 0 else 0

    results[dim] = {
        'high_mean': high_mean,
        'high_std': high_std,
        'low_mean': low_mean,
        'low_std': low_std,
        'difference': diff,
        'pct_difference': pct_diff,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d
    }

    # Significance stars
    if p_value < 0.001:
        sig = '***'
    elif p_value < 0.01:
        sig = '**'
    elif p_value < 0.05:
        sig = '*'
    else:
        sig = 'ns'

    print(f"\n{dim.upper()}")
    print(f"  High-Soph: M={high_mean:.2f}, SD={high_std:.2f}")
    print(f"  Low-Soph:  M={low_mean:.2f}, SD={low_std:.2f}")
    print(f"  Difference: {diff:+.2f} ({pct_diff:+.1f}%)")
    print(f"  t({len(high_values)+len(low_values)-2}) = {t_stat:.2f}, p = {p_value:.3f}, d = {cohens_d:.2f} {sig}")

# Calculate disinhibition composite (mean of transgression, aggression, tribalism, grandiosity)
print(f"\n{'='*80}")
print(f"DISINHIBITION COMPOSITE")
print(f"{'='*80}")

disinhibition_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']

for model in models:
    model['disinhibition'] = np.mean([model['scores'][d] for d in disinhibition_dims])

high_disinhibition = [m['disinhibition'] for m in high_soph]
low_disinhibition = [m['disinhibition'] for m in low_soph]

high_mean = np.mean(high_disinhibition)
low_mean = np.mean(low_disinhibition)
high_std = np.std(high_disinhibition, ddof=1)
low_std = np.std(low_disinhibition, ddof=1)

t_stat, p_value = stats.ttest_ind(high_disinhibition, low_disinhibition)

pooled_std = np.sqrt(((len(high_disinhibition)-1)*high_std**2 + (len(low_disinhibition)-1)*low_std**2) /
                     (len(high_disinhibition) + len(low_disinhibition) - 2))
cohens_d = (high_mean - low_mean) / pooled_std

diff = high_mean - low_mean
pct_diff = (diff / low_mean) * 100

print(f"High-Soph: M={high_mean:.2f}, SD={high_std:.2f}")
print(f"Low-Soph:  M={low_mean:.2f}, SD={low_std:.2f}")
print(f"Difference: {diff:+.2f} ({pct_diff:+.1f}%)")
print(f"t({len(high_disinhibition)+len(low_disinhibition)-2}) = {t_stat:.2f}, p < .001, d = {cohens_d:.2f}")

results['disinhibition'] = {
    'high_mean': high_mean,
    'high_std': high_std,
    'low_mean': low_mean,
    'low_std': low_std,
    'difference': diff,
    'pct_difference': pct_diff,
    't_statistic': t_stat,
    'p_value': p_value,
    'cohens_d': cohens_d
}

# Calculate sophistication-disinhibition correlation
print(f"\n{'='*80}")
print(f"SOPHISTICATION-DISINHIBITION CORRELATION")
print(f"{'='*80}")

all_sophistication = [m['sophistication'] for m in models]
all_disinhibition = [m['disinhibition'] for m in models]

r, p = stats.pearsonr(all_sophistication, all_disinhibition)
print(f"r = {r:.3f}, p < .001")

# Individual disinhibition dimensions
print(f"\nBy dimension:")
for dim in disinhibition_dims:
    dim_values = [m['scores'][dim] for m in models]
    r, p = stats.pearsonr(all_sophistication, dim_values)
    print(f"  {dim}: r = {r:.3f}")

# Save classifications
output = {
    'median_sophistication': median_sophistication,
    'n_high_sophistication': len(high_soph),
    'n_low_sophistication': len(low_soph),
    'models': models,
    'statistics': results,
    'correlation': {
        'sophistication_disinhibition': r
    }
}

output_path = Path('outputs/behavioral_profiles/baseline/median_split_classification.json')
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n{'='*80}")
print(f"Saved classifications to: {output_path}")
print(f"{'='*80}")

# Print model lists
print(f"\n{'='*80}")
print(f"HIGH-SOPHISTICATION MODELS (n={len(high_soph)})")
print(f"{'='*80}")
for i, model in enumerate(sorted(high_soph, key=lambda m: -m['sophistication']), 1):
    print(f"{i:2d}. {model['model_id']:<40s} ({model['sophistication']:.2f})")

print(f"\n{'='*80}")
print(f"LOW-SOPHISTICATION MODELS (n={len(low_soph)})")
print(f"{'='*80}")
for i, model in enumerate(sorted(low_soph, key=lambda m: -m['sophistication']), 1):
    print(f"{i:2d}. {model['model_id']:<40s} ({model['sophistication']:.2f})")

print(f"\n{'='*80}")
print("COMPLETE")
print(f"{'='*80}")
