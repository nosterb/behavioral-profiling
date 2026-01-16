#!/usr/bin/env python3
"""
Generate AIME 2025 external validation analysis.

Creates:
- aime_validation_analysis.json with correlations and group comparisons
- Matches AIME benchmark models to behavioral profile models
"""

import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy import stats

# Model name mappings: AIME name -> behavioral profile model_id
# Only include exact matches where we're confident about the model identity
MODEL_MAPPINGS = {
    # Anthropic
    "Claude 3.7 Sonnet": "claude-3.7-sonnet",
    "Claude Sonnet 4": "claude-4-sonnet",
    "Claude Opus 4": "claude-4-opus",
    "Claude Opus 4.1": "claude-4.1-opus",
    "Claude Haiku 4.5": "claude-4.5-haiku",
    "Claude Sonnet 4.5": "claude-4.5-sonnet",

    # OpenAI
    "GPT-4.1": "gpt-4.1",
    "GPT-5": "gpt-5",
    "GPT-5.1": "gpt-5.1",
    "GPT-5.2": "gpt-5.2",
    "GPT-5.2 Pro": "gpt-5.2_pro",
    "GPT OSS 120B High": "gpt-oss-120b",
    "o3": "o3",

    # xAI
    "Grok-3": "grok-3",
    "Grok-4": "grok-4-0709",

    # DeepSeek
    "DeepSeek-R1-0528": "deepseek-r1",

    # Google
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 3 Pro": "gemini-3-pro-preview",
    "Gemini 2.5 Flash": "gemini-2.0-flash",  # Closest match

    # Alibaba/Qwen
    "Qwen3 32B": "qwen3-32b",

    # Meta/Llama - not direct matches in baseline, skip
}


def load_aime_data(csv_path: Path) -> list[dict]:
    """Load AIME benchmark data from CSV."""
    data = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Score']:  # Skip empty scores
                data.append({
                    'rank': int(row['Rank']) if row['Rank'] else None,
                    'provider': row['Provider'],
                    'model': row['Model'],
                    'score': float(row['Score']),
                    'size': row['Size'],
                })
    return data


def load_baseline_profiles(json_path: Path) -> dict:
    """Load baseline median split classification."""
    with open(json_path) as f:
        data = json.load(f)
    return {m['model_id']: m for m in data['models']}


def match_models(aime_data: list[dict], baseline_profiles: dict) -> list[dict]:
    """Match AIME models to behavioral profiles."""
    matched = []

    for aime in aime_data:
        aime_name = aime['model']

        # Try exact mapping first
        if aime_name in MODEL_MAPPINGS:
            baseline_id = MODEL_MAPPINGS[aime_name]
            if baseline_id in baseline_profiles:
                profile = baseline_profiles[baseline_id]
                scores = profile['scores']
                matched.append({
                    'behavioral_model_id': baseline_id,
                    'aime_model': aime_name,
                    'aime_score': aime['score'] * 100,  # Convert to percentage
                    'aime_rank': aime['rank'],
                    'sophistication': profile['sophistication'],
                    'disinhibition': profile['disinhibition'],
                    'depth': scores.get('depth', 0),
                    'authenticity': scores.get('authenticity', 0),
                    'transgression': scores.get('transgression', 0),
                    'aggression': scores.get('aggression', 0),
                    'tribalism': scores.get('tribalism', 0),
                    'grandiosity': scores.get('grandiosity', 0),
                    'sophistication_group': profile['classification'],
                })

    return matched


def calculate_correlations(matched: list[dict]) -> dict:
    """Calculate correlations between AIME scores and behavioral dimensions."""
    aime_scores = np.array([m['aime_score'] for m in matched])

    dimensions = ['sophistication', 'disinhibition', 'depth', 'authenticity',
                  'transgression', 'aggression', 'tribalism', 'grandiosity']

    correlations = {}
    for dim in dimensions:
        values = np.array([m[dim] for m in matched])
        r, p = stats.pearsonr(aime_scores, values)
        correlations[dim] = {
            'r': float(r),
            'p': float(p),
            'n': len(matched),
            'significant': bool(p < 0.05)
        }

    return correlations


def calculate_h1_comparison(matched: list[dict]) -> dict:
    """Calculate H1 group comparison (High vs Low sophistication)."""
    high = [m['aime_score'] for m in matched if m['sophistication_group'] == 'High-Sophistication']
    low = [m['aime_score'] for m in matched if m['sophistication_group'] == 'Low-Sophistication']

    if len(high) < 2 or len(low) < 2:
        return {
            'high_sophistication': {'n': len(high), 'mean': float(np.mean(high)) if high else 0, 'sd': float(np.std(high)) if high else 0},
            'low_sophistication': {'n': len(low), 'mean': float(np.mean(low)) if low else 0, 'sd': float(np.std(low)) if low else 0},
            't_statistic': None,
            'p_value': None,
            'significant': False,
            'note': 'Insufficient samples for t-test'
        }

    t_stat, p_value = stats.ttest_ind(high, low)

    return {
        'high_sophistication': {
            'n': len(high),
            'mean': float(np.mean(high)),
            'sd': float(np.std(high, ddof=1))
        },
        'low_sophistication': {
            'n': len(low),
            'mean': float(np.mean(low)),
            'sd': float(np.std(low, ddof=1))
        },
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05)
    }


def main():
    base_dir = Path(__file__).parent.parent
    external_dir = base_dir / "outputs/behavioral_profiles/research_synthesis/limitations/external_evals"

    print("=" * 60)
    print("AIME 2025 External Validation Analysis")
    print("=" * 60)

    # Load data
    aime_data = load_aime_data(external_dir / "AIME_2025.csv")
    baseline_profiles = load_baseline_profiles(
        base_dir / "outputs/behavioral_profiles/baseline/median_split_classification.json"
    )

    print(f"\nLoaded {len(aime_data)} AIME models")
    print(f"Loaded {len(baseline_profiles)} baseline profiles")

    # Match models
    matched = match_models(aime_data, baseline_profiles)
    print(f"\nMatched models: {len(matched)}")

    for m in sorted(matched, key=lambda x: x['aime_score'], reverse=True):
        group_marker = "H" if m['sophistication_group'] == "High-Sophistication" else "L"
        print(f"  [{group_marker}] {m['aime_model']:30} -> {m['behavioral_model_id']:25} "
              f"AIME={m['aime_score']:.1f}% Soph={m['sophistication']:.2f}")

    if len(matched) < 5:
        print("\nWARNING: Too few matched models for reliable analysis")
        return

    # Calculate statistics
    correlations = calculate_correlations(matched)
    h1_comparison = calculate_h1_comparison(matched)

    # Print results
    print("\n" + "-" * 40)
    print("Correlations with AIME Score:")
    print("-" * 40)
    for dim, stats_data in correlations.items():
        sig = "*" if stats_data['significant'] else ""
        print(f"  {dim:15}: r = {stats_data['r']:.3f}, p = {stats_data['p']:.4f} {sig}")

    print("\n" + "-" * 40)
    print("H1 Group Comparison:")
    print("-" * 40)
    high = h1_comparison['high_sophistication']
    low = h1_comparison['low_sophistication']
    print(f"  High-Soph (n={high['n']}): M = {high['mean']:.1f}%, SD = {high['sd']:.1f}")
    print(f"  Low-Soph  (n={low['n']}): M = {low['mean']:.1f}%, SD = {low['sd']:.1f}")
    print(f"  Difference: +{high['mean'] - low['mean']:.1f} pp")
    if not np.isnan(h1_comparison['t_statistic']):
        print(f"  t = {h1_comparison['t_statistic']:.2f}, p = {h1_comparison['p_value']:.4f}")

    # Save results
    output = {
        'generated': datetime.now().isoformat(),
        'analysis_type': 'AIME 2025 External Validation',
        'statistical_software': 'scipy.stats.pearsonr, scipy.stats.ttest_ind',
        'scipy_version': stats.__version__ if hasattr(stats, '__version__') else 'unknown',
        'benchmark_description': 'American Invitational Mathematics Examination 2025 - mathematical reasoning benchmark',
        'sample': {
            'unique_matched_models': len(matched),
            'model_mapping_notes': 'Manual mapping of AIME model names to behavioral profile IDs'
        },
        'h1_group_comparison': h1_comparison,
        'correlations': correlations,
        'matched_model_details': matched
    }

    output_path = external_dir / "aime_validation_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {output_path}")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
