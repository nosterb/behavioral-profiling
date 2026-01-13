#!/usr/bin/env python3
"""
Update comprehensive_stats.json to use median split classification.

Replaces "by_generation" (Frontier/Older) with "by_classification" (High-Sophistication/Low-Sophistication).
"""

import json
from pathlib import Path

# Load median split classification
median_split_path = Path('outputs/behavioral_profiles/baseline/median_split_classification.json')
with open(median_split_path, 'r') as f:
    median_data = json.load(f)

# Load comprehensive stats
stats_path = Path('outputs/behavioral_profiles/baseline/comprehensive_stats.json')
with open(stats_path, 'r') as f:
    stats = json.load(f)

# Separate models by classification
high_soph_models = [m for m in median_data['models'] if m['classification'] == 'High-Sophistication']
low_soph_models = [m for m in median_data['models'] if m['classification'] == 'Low-Sophistication']

# Build new classification section
dimensions = ['warmth', 'formality', 'hedging', 'aggression', 'transgression',
              'grandiosity', 'tribalism', 'depth', 'authenticity', 'sophistication']

by_classification = {
    'High-Sophistication': {
        'n': len(high_soph_models),
        'means': {},
        'stds': {},
        'models': [m['model_id'] for m in sorted(high_soph_models, key=lambda x: -x['sophistication'])]
    },
    'Low-Sophistication': {
        'n': len(low_soph_models),
        'means': {},
        'stds': {},
        'models': [m['model_id'] for m in sorted(low_soph_models, key=lambda x: -x['sophistication'])]
    },
    'cohens_d': {}
}

# Add statistical results from median split
for dim in dimensions:
    if dim in median_data['statistics']:
        stat = median_data['statistics'][dim]
        by_classification['High-Sophistication']['means'][dim] = stat['high_mean']
        by_classification['High-Sophistication']['stds'][dim] = stat['high_std']
        by_classification['Low-Sophistication']['means'][dim] = stat['low_mean']
        by_classification['Low-Sophistication']['stds'][dim] = stat['low_std']
        by_classification['cohens_d'][dim] = stat['cohens_d']

# Add disinhibition composite
disinhibition_stat = median_data['statistics']['disinhibition']
by_classification['High-Sophistication']['means']['disinhibition'] = disinhibition_stat['high_mean']
by_classification['High-Sophistication']['stds']['disinhibition'] = disinhibition_stat['high_std']
by_classification['Low-Sophistication']['means']['disinhibition'] = disinhibition_stat['low_mean']
by_classification['Low-Sophistication']['stds']['disinhibition'] = disinhibition_stat['low_std']
by_classification['cohens_d']['disinhibition'] = disinhibition_stat['cohens_d']

# Replace by_generation with by_classification
del stats['by_generation']
stats['by_classification'] = by_classification

# Add median split metadata
stats['classification_method'] = {
    'type': 'median_split',
    'criterion': 'sophistication',
    'median_value': median_data['median_sophistication'],
    'description': 'Capability-based classification using median split on sophistication scores (depth + authenticity) / 2'
}

# Save updated stats
with open(stats_path, 'w') as f:
    json.dump(stats, f, indent=2)

print(f"✓ Updated comprehensive_stats.json")
print(f"  Replaced 'by_generation' with 'by_classification'")
print(f"  High-Sophistication: n={len(high_soph_models)}")
print(f"  Low-Sophistication: n={len(low_soph_models)}")
print(f"  Median sophistication: {median_data['median_sophistication']:.3f}")
