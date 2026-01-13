#!/usr/bin/env python3
"""
Create single combined provider analysis figure showing:
1. Model counts by provider
2. Sophistication means by provider
3. Disinhibition (H1) analysis by provider

Replaces three separate files with one comprehensive visualization.
"""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict

def load_median_split_data(profile_dir):
    """Load median split classification data."""
    median_split_path = profile_dir / "median_split_classification.json"

    with open(median_split_path, 'r') as f:
        return json.load(f)

def classify_provider(model_id):
    """Classify model by provider based on ID."""
    model_lower = model_id.lower()

    if 'claude' in model_lower:
        return 'Anthropic'
    elif 'gpt' in model_lower or model_lower.startswith('o3'):
        return 'OpenAI'
    elif 'gemini' in model_lower:
        return 'Google'
    elif 'grok' in model_lower:
        return 'xAI'
    elif 'llama' in model_lower:
        return 'Meta'
    elif 'nova' in model_lower:
        return 'AWS'
    elif 'mistral' in model_lower or 'mixtral' in model_lower:
        return 'Mistral'
    elif 'deepseek' in model_lower:
        return 'DeepSeek'
    elif 'qwen' in model_lower:
        return 'Alibaba'
    else:
        return 'Other'

def analyze_by_provider(data):
    """Aggregate statistics by provider."""
    provider_data = defaultdict(lambda: {
        'models': [],
        'sophistication': [],
        'disinhibition': [],
        'transgression': [],
        'aggression': [],
        'tribalism': [],
        'grandiosity': [],
        'high_soph_count': 0,
        'low_soph_count': 0
    })

    for model in data['models']:
        provider = classify_provider(model['model_id'])

        provider_data[provider]['models'].append(model['display_name'])
        provider_data[provider]['sophistication'].append(model['sophistication'])
        provider_data[provider]['disinhibition'].append(model['disinhibition'])
        provider_data[provider]['transgression'].append(model['scores']['transgression'])
        provider_data[provider]['aggression'].append(model['scores']['aggression'])
        provider_data[provider]['tribalism'].append(model['scores']['tribalism'])
        provider_data[provider]['grandiosity'].append(model['scores']['grandiosity'])

        if model['classification'] == 'High-Sophistication':
            provider_data[provider]['high_soph_count'] += 1
        else:
            provider_data[provider]['low_soph_count'] += 1

    # Calculate means
    provider_stats = {}
    for provider, pdata in provider_data.items():
        provider_stats[provider] = {
            'n_models': len(pdata['models']),
            'sophistication_mean': np.mean(pdata['sophistication']),
            'sophistication_std': np.std(pdata['sophistication']),
            'disinhibition_mean': np.mean(pdata['disinhibition']),
            'disinhibition_std': np.std(pdata['disinhibition']),
            'transgression_mean': np.mean(pdata['transgression']),
            'aggression_mean': np.mean(pdata['aggression']),
            'tribalism_mean': np.mean(pdata['tribalism']),
            'grandiosity_mean': np.mean(pdata['grandiosity']),
            'high_soph_count': pdata['high_soph_count'],
            'low_soph_count': pdata['low_soph_count'],
            'high_soph_pct': (pdata['high_soph_count'] / len(pdata['models']) * 100) if len(pdata['models']) > 0 else 0
        }

    return provider_stats

def create_combined_provider_figure(data, output_path):
    """Create single combined figure with all provider analyses."""

    # Analyze by provider
    provider_stats = analyze_by_provider(data)

    # Sort providers by sophistication (descending)
    providers_sorted = sorted(provider_stats.keys(),
                             key=lambda p: provider_stats[p]['sophistication_mean'],
                             reverse=True)

    # Filter to providers with at least 2 models
    providers_sorted = [p for p in providers_sorted if provider_stats[p]['n_models'] >= 2]

    # Create figure with 2x2 grid
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # Colors for consistency
    provider_colors = {
        'Google': '#4285F4',
        'Alibaba': '#FF6A00',
        'DeepSeek': '#9B59B6',
        'xAI': '#8E44AD',
        'OpenAI': '#10A37F',
        'Anthropic': '#E63946',
        'AWS': '#FF9900',
        'Meta': '#0668E1',
        'Mistral': '#F7931E'
    }

    colors = [provider_colors.get(p, '#808080') for p in providers_sorted]

    # ========================================================================
    # Panel A: Model Counts
    # ========================================================================
    ax1 = fig.add_subplot(gs[0, 0])

    counts = [provider_stats[p]['n_models'] for p in providers_sorted]
    bars = ax1.bar(range(len(providers_sorted)), counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add count labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax1.set_xticks(range(len(providers_sorted)))
    ax1.set_xticklabels(providers_sorted, rotation=45, ha='right', fontsize=11)
    ax1.set_ylabel('Number of Models', fontsize=12, fontweight='bold')
    ax1.set_title('A. Model Count by Provider', fontsize=13, fontweight='bold', loc='left')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_axisbelow(True)

    # Add total count text
    total_models = sum(counts)
    ax1.text(0.98, 0.98, f'Total: {total_models} models',
             transform=ax1.transAxes, ha='right', va='top',
             fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # ========================================================================
    # Panel B: Sophistication Means
    # ========================================================================
    ax2 = fig.add_subplot(gs[0, 1])

    soph_means = [provider_stats[p]['sophistication_mean'] for p in providers_sorted]
    soph_stds = [provider_stats[p]['sophistication_std'] for p in providers_sorted]

    bars = ax2.bar(range(len(providers_sorted)), soph_means,
                    yerr=soph_stds, capsize=5, error_kw={'linewidth': 2},
                    color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add overall mean line
    overall_mean = np.mean(soph_means)
    ax2.axhline(overall_mean, color='red', linestyle='--', linewidth=2,
                label=f'Overall Mean = {overall_mean:.2f}', zorder=10)

    # Add median line
    median_soph = data['median_sophistication']
    ax2.axhline(median_soph, color='purple', linestyle=':', linewidth=2,
                label=f'Median = {median_soph:.2f}', zorder=10)

    ax2.set_xticks(range(len(providers_sorted)))
    ax2.set_xticklabels(providers_sorted, rotation=45, ha='right', fontsize=11)
    ax2.set_ylabel('Sophistication (Depth + Authenticity) / 2', fontsize=12, fontweight='bold')
    ax2.set_title('B. Mean Sophistication by Provider', fontsize=13, fontweight='bold', loc='left')
    ax2.legend(loc='lower left', fontsize=10, framealpha=0.9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_axisbelow(True)
    ax2.set_ylim([0, 10])

    # ========================================================================
    # Panel C: Disinhibition Composite (H1)
    # ========================================================================
    ax3 = fig.add_subplot(gs[1, 0])

    disinhib_means = [provider_stats[p]['disinhibition_mean'] for p in providers_sorted]
    disinhib_stds = [provider_stats[p]['disinhibition_std'] for p in providers_sorted]

    bars = ax3.bar(range(len(providers_sorted)), disinhib_means,
                    yerr=disinhib_stds, capsize=5, error_kw={'linewidth': 2},
                    color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add overall mean line
    overall_disinhib = np.mean(disinhib_means)
    ax3.axhline(overall_disinhib, color='red', linestyle='--', linewidth=2,
                label=f'Overall Mean = {overall_disinhib:.2f}', zorder=10)

    ax3.set_xticks(range(len(providers_sorted)))
    ax3.set_xticklabels(providers_sorted, rotation=45, ha='right', fontsize=11)
    ax3.set_ylabel('Disinhibition Composite', fontsize=12, fontweight='bold')
    ax3.set_title('C. Mean Disinhibition by Provider (H1)', fontsize=13, fontweight='bold', loc='left')
    ax3.legend(loc='lower left', fontsize=10, framealpha=0.9)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    ax3.set_axisbelow(True)
    ax3.set_ylim([1, 3])

    # ========================================================================
    # Panel D: High vs Low Sophistication Split
    # ========================================================================
    ax4 = fig.add_subplot(gs[1, 1])

    # Stacked bar chart
    high_counts = [provider_stats[p]['high_soph_count'] for p in providers_sorted]
    low_counts = [provider_stats[p]['low_soph_count'] for p in providers_sorted]

    x_pos = np.arange(len(providers_sorted))
    p1 = ax4.bar(x_pos, high_counts, color='#2ecc71', alpha=0.8,
                 edgecolor='black', linewidth=1.5, label='High-Sophistication')
    p2 = ax4.bar(x_pos, low_counts, bottom=high_counts, color='#e74c3c', alpha=0.8,
                 edgecolor='black', linewidth=1.5, label='Low-Sophistication')

    # Add percentage labels
    for i, provider in enumerate(providers_sorted):
        total = high_counts[i] + low_counts[i]
        high_pct = (high_counts[i] / total * 100) if total > 0 else 0

        # Label high-sophistication section
        if high_counts[i] > 0:
            ax4.text(i, high_counts[i] / 2, f'{high_pct:.0f}%',
                    ha='center', va='center', fontsize=10, fontweight='bold', color='white')

        # Label low-sophistication section
        if low_counts[i] > 0:
            ax4.text(i, high_counts[i] + low_counts[i] / 2, f'{100-high_pct:.0f}%',
                    ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(providers_sorted, rotation=45, ha='right', fontsize=11)
    ax4.set_ylabel('Number of Models', fontsize=12, fontweight='bold')
    ax4.set_title('D. Classification Split by Provider', fontsize=13, fontweight='bold', loc='left')
    ax4.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    ax4.set_axisbelow(True)

    # Overall title
    fig.suptitle('Provider Analysis: Baseline Condition',
                fontsize=16, fontweight='bold', y=0.995)

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"\n✓ Created combined provider figure: {output_path}")
    print(f"  - Model counts by provider")
    print(f"  - Sophistication means (with overall mean and median)")
    print(f"  - Disinhibition composite (H1 primary outcome)")
    print(f"  - High vs Low sophistication classification split")

    return provider_stats

def main():
    # Get intervention from command line argument
    if len(sys.argv) > 1:
        intervention = sys.argv[1]
    else:
        intervention = "baseline"

    # Paths
    profile_dir = Path(f"outputs/behavioral_profiles/{intervention}")
    output_path = profile_dir / "provider_summary.png"

    if not profile_dir.exists():
        print(f"Error: Profile directory not found: {profile_dir}")
        sys.exit(1)

    print("Loading median split classification data...")
    data = load_median_split_data(profile_dir)

    print(f"Loaded {len(data['models'])} models")
    print(f"Median sophistication: {data['median_sophistication']:.3f}")

    print("\nCreating combined provider analysis figure...")
    provider_stats = create_combined_provider_figure(data, output_path)

    print("\nProvider Statistics Summary:")
    print("-" * 80)
    for provider in sorted(provider_stats.keys(),
                           key=lambda p: provider_stats[p]['sophistication_mean'],
                           reverse=True):
        stats = provider_stats[provider]
        if stats['n_models'] >= 2:
            print(f"{provider:<12s}: n={stats['n_models']:2d}  "
                  f"sophistication={stats['sophistication_mean']:.2f}  "
                  f"disinhibition={stats['disinhibition_mean']:.2f}  "
                  f"high-soph={stats['high_soph_pct']:.0f}%")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
