#!/usr/bin/env python3
"""
Analyze all models in behavioral profiles and categorize by provider.
Creates comprehensive statistics and visualizations.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict

# Get intervention from command line argument
if len(sys.argv) > 1:
    intervention = sys.argv[1]
else:
    intervention = "baseline"

# Paths
BASELINE_DIR = Path(f"outputs/behavioral_profiles/{intervention}")
PROFILES_DIR = BASELINE_DIR / "profiles"
OUTPUT_DIR = BASELINE_DIR

if not PROFILES_DIR.exists():
    print(f"Error: Profile directory not found: {PROFILES_DIR}")
    sys.exit(1)

# Behavioral dimensions in canonical order
DIMENSIONS = [
    "warmth",
    "formality",
    "hedging",
    "aggression",
    "transgression",
    "grandiosity",
    "tribalism",
    "depth",
    "authenticity"
]

def classify_provider(model_name):
    """Classify model by provider based on name."""
    model_lower = model_name.lower()

    # Provider classification
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

def load_median_split_classification():
    """Load median split classification to get High/Low sophistication groupings."""
    classification_file = BASELINE_DIR / "median_split_classification.json"
    if classification_file.exists():
        with open(classification_file, 'r') as f:
            data = json.load(f)

        # Build lookup dict: model_id -> classification
        classification = {}
        for model in data.get('models', []):
            model_id = model.get('model_id', '')
            # Extract just the model name part for matching
            if ':' in model_id:
                model_name = model_id.split(':')[-1]
            else:
                model_name = model_id
            classification[model_name.lower()] = model.get('classification', 'Unknown')
            # Also store by display name
            display_name = model.get('display_name', '')
            if display_name:
                classification[display_name.lower()] = model.get('classification', 'Unknown')
        return classification
    return {}

# Load classification at module level
SOPHISTICATION_CLASSIFICATION = load_median_split_classification()

def classify_sophistication(model_name):
    """Classify model as High-Sophistication or Low-Sophistication using median split."""
    model_lower = model_name.lower()

    # Try exact match first
    if model_lower in SOPHISTICATION_CLASSIFICATION:
        return SOPHISTICATION_CLASSIFICATION[model_lower]

    # Try partial match
    for key, value in SOPHISTICATION_CLASSIFICATION.items():
        if key in model_lower or model_lower in key:
            return value

    return 'Unknown'

def load_profiles():
    """Load all behavioral profiles."""
    profiles = {}

    for file_path in PROFILES_DIR.glob("*.json"):
        model_name = file_path.stem

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Extract dimension scores (check both root and nested structure)
        scores = {}
        dimensions_data = data.get('dimensions', data)  # Support both structures

        for dim in DIMENSIONS:
            if dim in dimensions_data:
                dim_data = dimensions_data[dim]
                scores[dim] = dim_data.get('average', None)
            else:
                scores[dim] = None

        # Skip if any dimension is missing
        if any(v is None for v in scores.values()):
            print(f"Warning: Skipping {model_name} due to missing dimensions")
            continue

        profiles[model_name] = {
            'provider': classify_provider(model_name),
            'sophistication_group': classify_sophistication(model_name),
            'scores': scores,
            'n_evaluations': dimensions_data.get('depth', {}).get('count', 0) if 'depth' in dimensions_data else 0
        }

    return profiles

def calculate_sophistication(profiles):
    """Calculate sophistication composite (depth + authenticity)."""
    for model_name, data in profiles.items():
        depth = data['scores']['depth']
        authenticity = data['scores']['authenticity']
        data['scores']['sophistication'] = (depth + authenticity) / 2

def create_dataframe(profiles):
    """Create pandas DataFrame from profiles."""
    rows = []
    for model_name, data in profiles.items():
        row = {
            'model': model_name,
            'provider': data['provider'],
            'sophistication_group': data['sophistication_group'],
            'n_evaluations': data['n_evaluations']
        }
        row.update(data['scores'])
        rows.append(row)

    return pd.DataFrame(rows)

def analyze_overall(df):
    """Generate overall statistics."""
    stats = {
        'n_models': len(df),
        'n_high_soph': len(df[df['sophistication_group'] == 'High-Sophistication']),
        'n_low_soph': len(df[df['sophistication_group'] == 'Low-Sophistication']),
        'providers': df['provider'].value_counts().to_dict(),
        'overall_means': df[DIMENSIONS + ['sophistication']].mean().to_dict(),
        'overall_stds': df[DIMENSIONS + ['sophistication']].std().to_dict()
    }
    return stats

def analyze_by_provider(df):
    """Generate provider-specific statistics."""
    provider_stats = {}

    for provider in df['provider'].unique():
        provider_df = df[df['provider'] == provider]

        provider_stats[provider] = {
            'n': len(provider_df),
            'means': provider_df[DIMENSIONS + ['sophistication']].mean().to_dict(),
            'stds': provider_df[DIMENSIONS + ['sophistication']].std().to_dict(),
            'models': provider_df['model'].tolist()
        }

    return provider_stats

def analyze_by_sophistication_group(df):
    """Analyze high vs low sophistication groups."""
    group_stats = {}

    for group in ['High-Sophistication', 'Low-Sophistication']:
        group_df = df[df['sophistication_group'] == group]

        group_stats[group] = {
            'n': len(group_df),
            'means': group_df[DIMENSIONS + ['sophistication']].mean().to_dict(),
            'stds': group_df[DIMENSIONS + ['sophistication']].std().to_dict()
        }

    return group_stats

def calculate_correlations(df):
    """Calculate sophistication → disinhibition correlations."""
    disinhibition_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']

    overall_corr = {}
    for dim in disinhibition_dims:
        corr = df['sophistication'].corr(df[dim])
        overall_corr[dim] = corr

    # Provider-specific correlations
    provider_corr = {}
    for provider in df['provider'].unique():
        provider_df = df[df['provider'] == provider]
        if len(provider_df) >= 3:  # Need at least 3 for correlation
            provider_corr[provider] = {}
            for dim in disinhibition_dims:
                corr = provider_df['sophistication'].corr(provider_df[dim])
                provider_corr[provider][dim] = corr

    return {
        'overall': overall_corr,
        'by_provider': provider_corr
    }

def plot_provider_breakdown(df, output_path):
    """Plot model count by provider."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    provider_counts = df['provider'].value_counts().sort_values(ascending=False)

    bars = ax.bar(range(len(provider_counts)), provider_counts.values, color='steelblue', alpha=0.7)
    ax.set_xticks(range(len(provider_counts)))
    ax.set_xticklabels(provider_counts.index, rotation=45, ha='right')
    ax.set_ylabel('Number of Models', fontsize=12)
    ax.set_title(f'Model Count by Provider (N={len(df)} total)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Add count labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_provider_sophistication(df, output_path):
    """Plot sophistication by provider."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Calculate means and sort
    provider_means = df.groupby('provider')['sophistication'].mean().sort_values(ascending=False)
    provider_stds = df.groupby('provider')['sophistication'].std()

    bars = ax.bar(range(len(provider_means)), provider_means.values,
                   yerr=provider_stds.values, capsize=5,
                   color='coral', alpha=0.7)
    ax.set_xticks(range(len(provider_means)))
    ax.set_xticklabels(provider_means.index, rotation=45, ha='right')
    ax.set_ylabel('Sophistication (Depth + Authenticity)', fontsize=12)
    ax.set_title('Mean Sophistication by Provider', fontsize=14, fontweight='bold')
    ax.axhline(df['sophistication'].mean(), color='red', linestyle='--',
               linewidth=1.5, label=f'Overall Mean = {df["sophistication"].mean():.2f}')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_all_dimensions_by_provider(df, output_path):
    """Plot all 9 dimensions by provider."""
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    axes = axes.flatten()

    dims_to_plot = DIMENSIONS

    for i, dim in enumerate(dims_to_plot):
        ax = axes[i]

        # Calculate means and sort by mean
        provider_means = df.groupby('provider')[dim].mean().sort_values(ascending=False)
        provider_stds = df.groupby('provider')[dim].std()

        bars = ax.bar(range(len(provider_means)), provider_means.values,
                      yerr=provider_stds.values, capsize=3,
                      color='steelblue', alpha=0.7)
        ax.set_xticks(range(len(provider_means)))
        ax.set_xticklabels(provider_means.index, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('Score (1-10)', fontsize=10)
        ax.set_title(dim.capitalize(), fontsize=11, fontweight='bold')
        ax.axhline(df[dim].mean(), color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(axis='y', alpha=0.3)

    plt.suptitle(f'All Behavioral Dimensions by Provider\nCondition: {intervention}', fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_provider_heatmap(df, output_path):
    """Create heatmap of all dimensions by provider."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Calculate means for each provider
    provider_means = df.groupby('provider')[DIMENSIONS + ['sophistication']].mean()
    provider_means = provider_means.sort_values('sophistication', ascending=False)

    # Create heatmap
    sns.heatmap(provider_means.T, annot=True, fmt='.2f', cmap='RdYlGn',
                cbar_kws={'label': 'Mean Score'}, ax=ax,
                vmin=1, vmax=10, center=5.5)
    ax.set_xlabel('Provider', fontsize=12)
    ax.set_ylabel('Dimension', fontsize=12)
    ax.set_title(f'Behavioral Dimensions Heatmap by Provider\nCondition: {intervention}', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def save_comprehensive_report(stats, correlations, output_path):
    """Save comprehensive text report."""
    with open(output_path, 'w') as f:
        f.write("# COMPREHENSIVE MODEL & PROVIDER ANALYSIS\n")
        f.write(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("=" * 80 + "\n\n")

        # Overall stats
        f.write("## OVERALL STATISTICS\n\n")
        f.write(f"**Total Models:** {stats['n_models']}\n")
        f.write(f"**High-Sophistication:** {stats['n_high_soph']}\n")
        f.write(f"**Low-Sophistication:** {stats['n_low_soph']}\n\n")

        f.write("### Models by Provider:\n\n")
        for provider, count in sorted(stats['providers'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{provider}**: {count} models\n")

        f.write("\n### Overall Dimension Means:\n\n")
        f.write("| Dimension | Mean | Std |\n")
        f.write("|-----------|------|-----|\n")
        for dim in ['sophistication'] + DIMENSIONS:
            mean = stats['overall_means'][dim]
            std = stats['overall_stds'][dim]
            f.write(f"| {dim.capitalize()} | {mean:.2f} | {std:.2f} |\n")

        # Correlations
        f.write("\n" + "=" * 80 + "\n\n")
        f.write("## SOPHISTICATION → DISINHIBITION CORRELATIONS\n\n")
        f.write("### Overall (All Models)\n\n")
        f.write("| Dimension | r |\n")
        f.write("|-----------|---|\n")
        for dim, corr in correlations['overall'].items():
            f.write(f"| {dim.capitalize()} | {corr:+.3f} |\n")

        f.write("\n### By Provider\n\n")
        for provider, corrs in sorted(correlations['by_provider'].items()):
            f.write(f"**{provider}:**\n\n")
            f.write("| Dimension | r |\n")
            f.write("|-----------|---|\n")
            for dim, corr in corrs.items():
                f.write(f"| {dim.capitalize()} | {corr:+.3f} |\n")
            f.write("\n")

    print(f"Saved: {output_path}")

def main():
    print("Loading behavioral profiles...")
    profiles = load_profiles()

    print(f"Loaded {len(profiles)} profiles")

    print("Calculating sophistication composite...")
    calculate_sophistication(profiles)

    print("Creating dataframe...")
    df = create_dataframe(profiles)

    print("\nAnalyzing overall statistics...")
    overall_stats = analyze_overall(df)

    print("Analyzing by provider...")
    provider_stats = analyze_by_provider(df)

    print("Analyzing by sophistication group...")
    sophistication_stats = analyze_by_sophistication_group(df)

    print("Calculating correlations...")
    correlations = calculate_correlations(df)

    # Save comprehensive stats to JSON
    output_data = {
        'overall': overall_stats,
        'by_provider': provider_stats,
        'by_sophistication_group': sophistication_stats,
        'correlations': correlations
    }

    stats_file = OUTPUT_DIR / "comprehensive_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved: {stats_file}")

    # Save CSV of all models
    csv_file = OUTPUT_DIR / "all_models_data.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved: {csv_file}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    # NOTE: Provider summary (counts, sophistication, H1) now generated by create_provider_summary.py
    # plot_provider_breakdown(df, OUTPUT_DIR / "provider_model_counts.png")  # DEPRECATED
    # plot_provider_sophistication(df, OUTPUT_DIR / "provider_sophistication_means.png")  # DEPRECATED
    plot_all_dimensions_by_provider(df, OUTPUT_DIR / "all_dimensions_by_provider.png")
    plot_provider_heatmap(df, OUTPUT_DIR / "provider_dimensions_heatmap.png")

    # Save comprehensive report
    print("\nGenerating comprehensive report...")
    save_comprehensive_report(overall_stats, correlations,
                             OUTPUT_DIR / "COMPREHENSIVE_STATS_REPORT.txt")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nTotal Models: {len(df)}")
    print(f"Providers: {len(df['provider'].unique())}")
    print(f"\nProvider breakdown:")
    for provider, count in sorted(overall_stats['providers'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {provider}: {count}")
    print(f"\nOutputs saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
