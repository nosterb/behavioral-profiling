#!/usr/bin/env python3
"""
Create provider-specific H2 scatter plots.

Shows sophistication-disinhibition correlation separately for each major provider
in a multi-panel layout.
"""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats as sp_stats
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


def organize_by_provider(data):
    """Organize models by provider."""
    provider_data = defaultdict(list)

    for model in data['models']:
        provider = classify_provider(model['model_id'])
        provider_data[provider].append(model)

    return provider_data


def create_provider_h2_scatters(data, output_path, condition="baseline"):
    """Create multi-panel H2 scatter plots by provider."""

    provider_data = organize_by_provider(data)

    # Filter to providers with at least 3 models (needed for correlation)
    providers = [(p, models) for p, models in provider_data.items()
                 if len(models) >= 3]

    # Sort by number of models (descending)
    providers.sort(key=lambda x: len(x[1]), reverse=True)

    # Take top 6 providers for 2x3 grid
    providers = providers[:6]

    if len(providers) == 0:
        print("Warning: No providers with ≥3 models found")
        return

    # Create figure with 2x3 grid
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    # Color scheme for consistency
    provider_colors = {
        'Anthropic': '#E63946',
        'OpenAI': '#10A37F',
        'Google': '#4285F4',
        'xAI': '#8E44AD',
        'Meta': '#0668E1',
        'AWS': '#FF9900',
        'Mistral': '#F7931E',
        'DeepSeek': '#9B59B6',
        'Alibaba': '#FF6A00'
    }

    for idx, (provider, models) in enumerate(providers):
        ax = axes[idx]

        # Extract data
        sophistication = [m['sophistication'] for m in models]
        disinhibition = [m['disinhibition'] for m in models]

        # Color based on classification
        colors = ['#2ecc71' if m['classification'] == 'High-Sophistication' else '#e74c3c'
                  for m in models]

        # Scatter plot
        ax.scatter(sophistication, disinhibition,
                  c=colors, alpha=0.7, s=120,
                  edgecolors='black', linewidth=1.5)

        # Add regression line
        z = np.polyfit(sophistication, disinhibition, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(sophistication), max(sophistication), 100)
        ax.plot(x_line, p(x_line), 'k--', alpha=0.5, linewidth=2)

        # Calculate correlation
        r, p_val = sp_stats.pearsonr(sophistication, disinhibition)

        # Add statistics text
        stats_text = f'n = {len(models)}\nr = {r:.3f}'
        if p_val < 0.001:
            stats_text += '\np < .001'
        elif p_val < 0.01:
            stats_text += f'\np < .01'
        elif p_val < 0.05:
            stats_text += f'\np < .05'
        else:
            stats_text += f'\np = {p_val:.3f}'

        # Effect size interpretation
        r_abs = abs(r)
        if r_abs >= 0.5:
            effect = 'large'
        elif r_abs >= 0.3:
            effect = 'medium'
        elif r_abs >= 0.1:
            effect = 'small'
        else:
            effect = 'negligible'
        stats_text += f'\n({effect})'

        ax.text(0.05, 0.95, stats_text,
               transform=ax.transAxes,
               fontsize=9,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

        # Add median split line (overall median)
        median_soph = data['median_sophistication']
        ax.axvline(median_soph, color='purple', linestyle='--',
                  linewidth=1.5, alpha=0.5)

        # Labels and formatting
        ax.set_xlabel('Sophistication', fontsize=11, fontweight='bold')
        ax.set_ylabel('Disinhibition Composite', fontsize=11, fontweight='bold')

        # Color-code title by provider
        title_color = provider_colors.get(provider, '#808080')
        ax.set_title(provider, fontsize=13, fontweight='bold',
                    color=title_color, pad=10)

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # Set consistent axis limits across all panels
        ax.set_xlim([3, 9])
        ax.set_ylim([1, 3])

    # Hide unused subplots
    for idx in range(len(providers), len(axes)):
        axes[idx].axis('off')

    # Add overall title with condition label
    fig.suptitle(f'Sophistication-Disinhibition Correlation by Provider (H2)\nCondition: {condition}',
                fontsize=16, fontweight='bold', y=1.01)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='black', label='High-Sophistication'),
        Patch(facecolor='#e74c3c', edgecolor='black', label='Low-Sophistication')
    ]
    fig.legend(handles=legend_elements, loc='lower center',
              ncol=2, fontsize=11, framealpha=0.95,
              bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✓ Created: {output_path}")
    print(f"  - Providers included: {len(providers)}")
    for provider, models in providers:
        soph = [m['sophistication'] for m in models]
        disinhib = [m['disinhibition'] for m in models]
        r, _ = sp_stats.pearsonr(soph, disinhib)
        print(f"    • {provider}: n={len(models)}, r={r:.3f}")


def main():
    # Get intervention name from command line or default to baseline
    if len(sys.argv) > 1:
        intervention = sys.argv[1]
    else:
        intervention = "baseline"

    # Paths
    profile_dir = Path(f"outputs/behavioral_profiles/{intervention}")

    if not profile_dir.exists():
        print(f"Error: Profile directory not found: {profile_dir}")
        print(f"Usage: python3 {sys.argv[0]} [intervention_name]")
        print(f"Example: python3 {sys.argv[0]} authority")
        sys.exit(1)

    print(f"Intervention: {intervention}")
    print("Loading median split classification data...")
    data = load_median_split_data(profile_dir)

    print(f"Loaded {len(data['models'])} models")

    print("\nCreating provider-specific H2 scatter plots...")
    output_path = profile_dir / "provider_h2_scatters.png"
    create_provider_h2_scatters(data, output_path, condition=intervention)

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
