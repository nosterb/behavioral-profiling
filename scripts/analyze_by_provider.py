#!/usr/bin/env python3
"""
Provider-specific analysis of sophistication vs boundary dimensions.
Creates separate visualizations and statistics for Anthropic, OpenAI, Grok, and Gemini.
"""

import json
from pathlib import Path
from collections import defaultdict


def load_all_profiles(profile_dir):
    """Load all personality profiles from JSON files."""
    profiles = []
    profile_dir = Path(profile_dir)

    for profile_file in profile_dir.glob("*.json"):
        with open(profile_file, 'r') as f:
            data = json.load(f)

        profile = {
            'model_name': data['model_name'],
            'total_evaluations': data.get('total_evaluations', 0)
        }

        for dim, values in data['dimensions'].items():
            profile[dim] = values['average']

        profiles.append(profile)

    return profiles


def classify_provider(model_name):
    """Classify model by provider."""
    name_lower = model_name.lower()

    if 'claude' in name_lower:
        return 'Anthropic'
    elif 'gpt' in name_lower or 'o1' in name_lower or 'o3' in name_lower:
        return 'OpenAI'
    elif 'gemini' in name_lower:
        return 'Google'
    elif 'grok' in name_lower:
        return 'xAI'
    elif 'llama' in name_lower:
        return 'Meta'
    else:
        return 'Other'


def classify_model_version(model_name):
    """Classify model by specific version for ordering."""
    name_lower = model_name.lower()

    # Anthropic/Claude
    if 'claude' in name_lower:
        if 'claude-4.5' in name_lower or 'claude-4-5' in name_lower:
            return ('Anthropic', 'Claude 4.5', 6)
        elif 'claude-4.1' in name_lower or 'claude-4-1' in name_lower:
            return ('Anthropic', 'Claude 4.1', 5)
        elif 'claude-4' in name_lower:
            return ('Anthropic', 'Claude 4.0', 4)
        elif 'claude-3.7' in name_lower or 'claude-3-7' in name_lower:
            return ('Anthropic', 'Claude 3.7', 3)
        elif 'claude-3.5' in name_lower or 'claude-3-5' in name_lower:
            return ('Anthropic', 'Claude 3.5', 2)
        elif 'claude-3' in name_lower:
            return ('Anthropic', 'Claude 3.0', 1)

    # OpenAI (progression: GPT-4.1 → O3 → GPT-5.1)
    if 'gpt-oss' in name_lower:
        return ('OpenAI', 'OpenAI-OSS', 0)
    elif 'gpt-5.1' in name_lower or 'gpt-5-1' in name_lower:
        return ('OpenAI', 'GPT-5.1', 3)
    elif 'o3' in name_lower:
        return ('OpenAI', 'O3', 2)
    elif 'gpt-4.1' in name_lower or 'gpt-4-1' in name_lower or 'gpt-4' in name_lower or 'o1' in name_lower:
        return ('OpenAI', 'GPT-4.1', 1)

    # Google/Gemini
    if 'gemini' in name_lower:
        if 'gemini-3' in name_lower:
            return ('Google', 'Gemini 3.0', 3)
        elif 'gemini-2' in name_lower:
            return ('Google', 'Gemini 2.5', 2)
        elif 'gemini-1.5' in name_lower or 'gemini-1-5' in name_lower:
            return ('Google', 'Gemini 1.5', 1)

    # xAI/Grok
    if 'grok' in name_lower:
        if 'grok-4' in name_lower:
            return ('xAI', 'Grok 4', 3)
        elif 'grok-3' in name_lower:
            return ('xAI', 'Grok 3', 2)
        elif 'grok-2' in name_lower:
            return ('xAI', 'Grok 2', 1)

    # Meta/Llama
    if 'llama' in name_lower:
        if 'llama-4' in name_lower or 'llama-3.4' in name_lower or 'llama-3-4' in name_lower:
            return ('Meta', 'Llama 4.x', 3)
        elif 'llama-3.3' in name_lower or 'llama-3-3' in name_lower:
            return ('Meta', 'Llama 3.3', 2)
        elif 'llama-3' in name_lower:
            return ('Meta', 'Llama 3.x', 1)

    return ('Other', 'Unknown', 0)


def create_provider_visualizations(profiles, output_dir):
    """Create provider-specific visualizations."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not available. Skipping visualizations.")
        return []

    created_files = []

    providers = ['Anthropic', 'OpenAI', 'Google', 'xAI', 'Meta']
    boundary_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']

    # Color schemes per provider
    provider_colors = {
        'Anthropic': ['#E63946', '#F77F00', '#06A77D', '#118AB2'],  # Red, orange, teal, blue
        'OpenAI': ['#10A37F', '#087F5B', '#1971C2', '#5F3DC4'],      # OpenAI green variants
        'Meta': ['#0668E1', '#0A7CFF', '#4267B2', '#1877F2'],        # Meta blue variants
        'Google': ['#EA4335', '#FBBC04', '#34A853', '#4285F4'],     # Google colors
        'xAI': ['#9B59B6', '#8E44AD', '#3498DB', '#2980B9']         # Purple/blue
    }

    # Version markers
    version_markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h']

    for provider in providers:
        provider_profiles = [p for p in profiles if classify_provider(p['model_name']) == provider]

        if not provider_profiles:
            continue

        # Create 2x2 subplot for this provider
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()

        for idx, dim in enumerate(boundary_dims):
            ax = axes[idx]

            # Group by version
            version_data = defaultdict(list)

            for p in provider_profiles:
                if 'depth' in p and 'authenticity' in p and dim in p:
                    prov, version, order = classify_model_version(p['model_name'])
                    soph = (p['depth'] + p['authenticity']) / 2
                    version_data[version].append({
                        'sophistication': soph,
                        'boundary': p[dim],
                        'model_name': p['model_name'],
                        'order': order
                    })

            # Sort versions by order
            sorted_versions = sorted(version_data.keys(), key=lambda v: version_data[v][0]['order'] if version_data[v] else 0)

            # Plot each version with different marker
            for vidx, version in enumerate(sorted_versions):
                data_points = version_data[version]
                if not data_points:
                    continue

                sophs = [d['sophistication'] for d in data_points]
                bounds = [d['boundary'] for d in data_points]

                marker = version_markers[vidx % len(version_markers)]
                color = provider_colors[provider][idx]

                ax.scatter(sophs, bounds,
                          marker=marker,
                          s=100,
                          color=color,
                          alpha=0.7,
                          edgecolors='black',
                          linewidth=1.5,
                          label=version)

            # Add trend line for all data
            all_sophs = []
            all_bounds = []
            for version_points in version_data.values():
                all_sophs.extend([d['sophistication'] for d in version_points])
                all_bounds.extend([d['boundary'] for d in version_points])

            if len(all_sophs) > 1:
                z = np.polyfit(all_sophs, all_bounds, 1)
                p = np.poly1d(z)
                x_line = np.linspace(min(all_sophs), max(all_sophs), 100)
                ax.plot(x_line, p(x_line), "k--", alpha=0.5, linewidth=2)

                # Calculate correlation
                from math import sqrt
                n = len(all_sophs)
                mean_x = sum(all_sophs) / n
                mean_y = sum(all_bounds) / n
                numerator = sum((all_sophs[i] - mean_x) * (all_bounds[i] - mean_y) for i in range(n))
                denom_x = sqrt(sum((all_sophs[i] - mean_x)**2 for i in range(n)))
                denom_y = sqrt(sum((all_bounds[i] - mean_y)**2 for i in range(n)))
                r = numerator / (denom_x * denom_y) if denom_x > 0 and denom_y > 0 else 0

                ax.text(0.05, 0.95, f'r = {r:.3f}\nn = {n}',
                       transform=ax.transAxes,
                       fontsize=11,
                       verticalalignment='top',
                       fontweight='bold',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

            ax.set_xlabel('Sophistication (Depth + Authenticity) / 2', fontsize=11, fontweight='bold')
            ax.set_ylabel(f'{dim.capitalize()} Score', fontsize=11, fontweight='bold')
            ax.set_title(f'Sophistication → {dim.capitalize()}', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='lower right', fontsize=9)

        plt.suptitle(f'{provider}: Sophistication vs Boundary Dimensions',
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout(rect=[0, 0, 1, 0.99])

        filename = output_dir / f'provider_{provider.lower()}_analysis.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(filename)
        print(f"Created: {filename}")

    return created_files


def analyze_provider_progressions(profiles):
    """Analyze version progressions for each provider."""
    providers = ['Anthropic', 'OpenAI', 'Google', 'xAI', 'Meta']
    dimensions = ['depth', 'authenticity', 'transgression', 'aggression', 'tribalism', 'grandiosity']

    print(f"\n{'='*120}")
    print("PROVIDER-SPECIFIC GENERATIONAL PROGRESSIONS")
    print(f"{'='*120}\n")

    for provider in providers:
        provider_profiles = [p for p in profiles if classify_provider(p['model_name']) == provider]

        if not provider_profiles:
            continue

        print(f"\n{'='*120}")
        print(f"{provider.upper()}")
        print(f"{'='*120}\n")

        # Group by version
        version_stats = defaultdict(lambda: defaultdict(list))

        for p in provider_profiles:
            prov, version, order = classify_model_version(p['model_name'])
            for dim in dimensions:
                if dim in p:
                    version_stats[version][dim].append(p[dim])

        # Sort by order
        sorted_versions = sorted(version_stats.keys(),
                                key=lambda v: min([classify_model_version(p['model_name'])[2]
                                                  for p in provider_profiles
                                                  if classify_model_version(p['model_name'])[1] == v], default=0))

        # Print table
        print(f"{'Version':<20s}  {'n':>3s}  " + "  ".join([f"{d.capitalize()[:6]:<8s}" for d in dimensions]))
        print("-" * 120)

        for version in sorted_versions:
            stats = version_stats[version]
            n_models = len([p for p in provider_profiles if classify_model_version(p['model_name'])[1] == version])

            row = f"{version:<20s}  {n_models:>3d}  "
            for dim in dimensions:
                if stats[dim]:
                    mean_val = sum(stats[dim]) / len(stats[dim])
                    row += f"{mean_val:<8.2f}  "
                else:
                    row += f"{'N/A':<8s}  "
            print(row)

        # Calculate correlations for this provider
        print(f"\n{provider} Correlations (Sophistication → Boundary Dimensions):")
        print("-" * 80)

        for dim in ['transgression', 'aggression', 'tribalism', 'grandiosity']:
            sophs = []
            bounds = []

            for p in provider_profiles:
                if 'depth' in p and 'authenticity' in p and dim in p:
                    soph = (p['depth'] + p['authenticity']) / 2
                    sophs.append(soph)
                    bounds.append(p[dim])

            if len(sophs) > 2:
                from math import sqrt
                n = len(sophs)
                mean_x = sum(sophs) / n
                mean_y = sum(bounds) / n
                numerator = sum((sophs[i] - mean_x) * (bounds[i] - mean_y) for i in range(n))
                denom_x = sqrt(sum((sophs[i] - mean_x)**2 for i in range(n)))
                denom_y = sqrt(sum((bounds[i] - mean_y)**2 for i in range(n)))
                r = numerator / (denom_x * denom_y) if denom_x > 0 and denom_y > 0 else 0

                effect = "very large" if abs(r) >= 0.7 else "large" if abs(r) >= 0.5 else "medium" if abs(r) >= 0.3 else "small"
                print(f"  {dim:15s}: r = {r:+.3f} ({effect:12s}) (n={n})")


def compare_provider_strategies(profiles):
    """Compare how providers differ in their capability-constraint tradeoffs."""
    print(f"\n{'='*120}")
    print("PROVIDER STRATEGY COMPARISON")
    print(f"{'='*120}\n")

    providers = ['Anthropic', 'OpenAI', 'Google', 'xAI', 'Meta']
    dimensions = ['depth', 'authenticity', 'transgression', 'aggression', 'tribalism', 'grandiosity']

    # Get latest version for each provider
    latest_models = {}

    for provider in providers:
        provider_profiles = [p for p in profiles if classify_provider(p['model_name']) == provider]
        if not provider_profiles:
            continue

        # Find models with highest order (latest versions)
        max_order = max([classify_model_version(p['model_name'])[2] for p in provider_profiles])
        latest = [p for p in provider_profiles if classify_model_version(p['model_name'])[2] == max_order]

        latest_models[provider] = latest

    # Print comparison table
    print("Latest versions from each provider:\n")
    print(f"{'Provider':<15s}  {'Version':<20s}  {'n':>3s}  " + "  ".join([f"{d.capitalize()[:6]:<8s}" for d in dimensions]))
    print("-" * 120)

    for provider in providers:
        if provider not in latest_models:
            continue

        models = latest_models[provider]
        version_name = classify_model_version(models[0]['model_name'])[1]

        row = f"{provider:<15s}  {version_name:<20s}  {len(models):>3d}  "

        for dim in dimensions:
            scores = [m[dim] for m in models if dim in m]
            if scores:
                mean_val = sum(scores) / len(scores)
                row += f"{mean_val:<8.2f}  "
            else:
                row += f"{'N/A':<8s}  "
        print(row)

    # Analyze strategies
    print(f"\n{'='*120}")
    print("STRATEGY ANALYSIS")
    print(f"{'='*120}\n")

    for provider in providers:
        if provider not in latest_models:
            continue

        models = latest_models[provider]

        # Calculate sophistication and disinhibition
        sophs = []
        trans = []
        aggr = []

        for m in models:
            if 'depth' in m and 'authenticity' in m:
                sophs.append((m['depth'] + m['authenticity']) / 2)
            if 'transgression' in m:
                trans.append(m['transgression'])
            if 'aggression' in m:
                aggr.append(m['aggression'])

        if sophs and trans and aggr:
            avg_soph = sum(sophs) / len(sophs)
            avg_trans = sum(trans) / len(trans)
            avg_aggr = sum(aggr) / len(aggr)

            print(f"{provider}:")
            print(f"  Sophistication: {avg_soph:.2f}")
            print(f"  Transgression:  {avg_trans:.2f}")
            print(f"  Aggression:     {avg_aggr:.2f}")

            # Calculate "disinhibition per sophistication"
            trans_ratio = avg_trans / avg_soph if avg_soph > 0 else 0
            aggr_ratio = avg_aggr / avg_soph if avg_soph > 0 else 0

            print(f"  Transgression/Sophistication ratio: {trans_ratio:.3f}")
            print(f"  Aggression/Sophistication ratio:    {aggr_ratio:.3f}")

            if trans_ratio < 0.35:
                print(f"  → Strategy: HIGH CONSTRAINT (low disinhibition relative to capability)")
            elif trans_ratio > 0.45:
                print(f"  → Strategy: LOW CONSTRAINT (high disinhibition relative to capability)")
            else:
                print(f"  → Strategy: MODERATE CONSTRAINT (balanced)")
            print()


def main():
    profile_dir = Path("outputs/behavioral_profiles/baseline/profiles")
    output_dir = Path("outputs/personality_profiles/visualizations")

    print(f"Loading profiles from {profile_dir}...")
    profiles = load_all_profiles(profile_dir)
    print(f"Loaded {len(profiles)} profiles\n")

    # Analyze provider progressions
    analyze_provider_progressions(profiles)

    # Compare provider strategies
    compare_provider_strategies(profiles)

    # Create visualizations
    print(f"\n{'='*120}")
    print("CREATING PROVIDER-SPECIFIC VISUALIZATIONS")
    print(f"{'='*120}\n")

    created_files = create_provider_visualizations(profiles, output_dir)

    print(f"\n{'='*120}")
    print("COMPLETE")
    print(f"{'='*120}\n")

    if created_files:
        print(f"Created {len(created_files)} visualizations:")
        for f in created_files:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
