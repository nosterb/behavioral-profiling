#!/usr/bin/env python3
"""
Cross-provider statistical comparisons for behavioral profiles.
Runs ANOVA and pairwise t-tests between providers with n≥3.
"""

import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
MIN_PROVIDER_N = 3  # Minimum models per provider

# Behavioral dimensions
DIMENSIONS = [
    "warmth", "formality", "hedging", "aggression", "transgression",
    "grandiosity", "tribalism", "depth", "authenticity"
]

DISINHIBITION_DIMS = ["transgression", "aggression", "tribalism", "grandiosity"]
SOPHISTICATION_DIMS = ["depth", "authenticity"]


def load_data(condition: str) -> pd.DataFrame:
    """Load all_models_data.csv for a condition."""
    csv_path = Path(f"outputs/behavioral_profiles/{condition}/all_models_data.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    return pd.read_csv(csv_path)


def filter_providers(df: pd.DataFrame, min_n: int = MIN_PROVIDER_N) -> pd.DataFrame:
    """Filter to providers with at least min_n models."""
    provider_counts = df['provider'].value_counts()
    valid_providers = provider_counts[provider_counts >= min_n].index.tolist()
    return df[df['provider'].isin(valid_providers)].copy()


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def interpret_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


def interpret_eta2(eta2: float) -> str:
    """Interpret eta-squared effect size."""
    if eta2 < 0.01:
        return "negligible"
    elif eta2 < 0.06:
        return "small"
    elif eta2 < 0.14:
        return "medium"
    else:
        return "large"


def run_anova(df: pd.DataFrame, dimension: str) -> dict:
    """Run one-way ANOVA for a dimension across providers."""
    groups = [group[dimension].values for name, group in df.groupby('provider')]

    # One-way ANOVA
    f_stat, p_value = stats.f_oneway(*groups)

    # Calculate eta-squared
    grand_mean = df[dimension].mean()
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    ss_total = sum((df[dimension] - grand_mean)**2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    # Degrees of freedom
    k = len(groups)  # number of groups
    N = len(df)      # total observations
    df_between = k - 1
    df_within = N - k

    return {
        'F': float(f_stat),
        'p': float(p_value),
        'eta_squared': float(eta_squared),
        'eta_squared_interp': interpret_eta2(eta_squared),
        'df_between': int(df_between),
        'df_within': int(df_within),
        'n_groups': int(k),
        'N': int(N)
    }


def run_pairwise_ttests(df: pd.DataFrame, dimension: str) -> list:
    """Run pairwise t-tests between all providers."""
    providers = sorted(df['provider'].unique())
    results = []

    for i, prov1 in enumerate(providers):
        for prov2 in providers[i+1:]:
            group1 = df[df['provider'] == prov1][dimension].values
            group2 = df[df['provider'] == prov2][dimension].values

            # Welch's t-test (unequal variances)
            t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
            d = cohens_d(group1, group2)

            results.append({
                'provider_1': prov1,
                'provider_2': prov2,
                'n1': int(len(group1)),
                'n2': int(len(group2)),
                'mean1': float(np.mean(group1)),
                'mean2': float(np.mean(group2)),
                'diff': float(np.mean(group1) - np.mean(group2)),
                't': float(t_stat),
                'p': float(p_value),
                'cohens_d': float(d),
                'd_interp': interpret_d(d)
            })

    return results


def apply_bonferroni(pairwise_results: list, alpha: float = 0.05) -> list:
    """Apply Bonferroni correction to pairwise results."""
    n_comparisons = len(pairwise_results)
    adjusted_alpha = alpha / n_comparisons

    for result in pairwise_results:
        result['p_bonferroni'] = float(min(result['p'] * n_comparisons, 1.0))
        result['significant_bonferroni'] = bool(result['p'] < adjusted_alpha)

    return pairwise_results


def format_p_value(p: float) -> str:
    """Format p-value in APA style."""
    if p < 0.001:
        return "< .001"
    elif p < 0.01:
        return f"= {p:.3f}"
    else:
        return f"= {p:.3f}"


def analyze_dimension(df: pd.DataFrame, dimension: str) -> dict:
    """Full analysis of a single dimension."""
    anova = run_anova(df, dimension)
    pairwise = run_pairwise_ttests(df, dimension)
    pairwise = apply_bonferroni(pairwise)

    # Provider means
    provider_stats = df.groupby('provider')[dimension].agg(['mean', 'std', 'count'])
    provider_stats = provider_stats.sort_values('mean', ascending=False)

    # Convert to native Python types
    provider_stats_dict = {}
    for provider, row in provider_stats.iterrows():
        provider_stats_dict[provider] = {
            'mean': float(row['mean']),
            'std': float(row['std']) if not pd.isna(row['std']) else None,
            'count': int(row['count'])
        }

    return {
        'dimension': dimension,
        'anova': anova,
        'pairwise': pairwise,
        'provider_stats': provider_stats_dict
    }


def create_comparison_visualization(df: pd.DataFrame, results: dict, output_path: Path, condition: str = "baseline"):
    """Create visualization of provider comparisons."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Sort providers by mean disinhibition for consistent ordering
    df['disinhibition'] = df[DISINHIBITION_DIMS].mean(axis=1)
    provider_order = df.groupby('provider')['disinhibition'].mean().sort_values(ascending=False).index.tolist()

    # 1. Disinhibition composite by provider
    ax1 = axes[0, 0]
    sns.boxplot(data=df, x='provider', y='disinhibition', order=provider_order, ax=ax1, palette='Set2')
    ax1.set_xlabel('Provider', fontsize=11)
    ax1.set_ylabel('Disinhibition Composite', fontsize=11)
    ax1.set_title('Disinhibition by Provider', fontsize=13, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)

    # Add ANOVA result
    anova_disinhibition = results.get('disinhibition', {}).get('anova', {})
    if anova_disinhibition:
        f_val = anova_disinhibition.get('F', 0)
        p_val = anova_disinhibition.get('p', 1)
        eta2 = anova_disinhibition.get('eta_squared', 0)
        ax1.text(0.02, 0.98, f'F = {f_val:.2f}, p {format_p_value(p_val)}\nη² = {eta2:.3f} ({anova_disinhibition.get("eta_squared_interp", "")})',
                transform=ax1.transAxes, fontsize=9, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # 2. Sophistication composite by provider
    df['sophistication'] = df[SOPHISTICATION_DIMS].mean(axis=1)
    ax2 = axes[0, 1]
    provider_order_soph = df.groupby('provider')['sophistication'].mean().sort_values(ascending=False).index.tolist()
    sns.boxplot(data=df, x='provider', y='sophistication', order=provider_order_soph, ax=ax2, palette='Set2')
    ax2.set_xlabel('Provider', fontsize=11)
    ax2.set_ylabel('Sophistication Composite', fontsize=11)
    ax2.set_title('Sophistication by Provider', fontsize=13, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)

    # Add ANOVA result
    anova_soph = results.get('sophistication', {}).get('anova', {})
    if anova_soph:
        f_val = anova_soph.get('F', 0)
        p_val = anova_soph.get('p', 1)
        eta2 = anova_soph.get('eta_squared', 0)
        ax2.text(0.02, 0.98, f'F = {f_val:.2f}, p {format_p_value(p_val)}\nη² = {eta2:.3f} ({anova_soph.get("eta_squared_interp", "")})',
                transform=ax2.transAxes, fontsize=9, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # 3. Heatmap of effect sizes (Cohen's d) between providers for disinhibition
    ax3 = axes[1, 0]
    pairwise_disinhibition = results.get('disinhibition', {}).get('pairwise', [])
    if pairwise_disinhibition:
        # Create matrix
        providers = sorted(df['provider'].unique())
        d_matrix = pd.DataFrame(0.0, index=providers, columns=providers)
        for comp in pairwise_disinhibition:
            p1, p2 = comp['provider_1'], comp['provider_2']
            d_matrix.loc[p1, p2] = comp['cohens_d']
            d_matrix.loc[p2, p1] = -comp['cohens_d']

        # Reorder by mean disinhibition
        d_matrix = d_matrix.loc[provider_order, provider_order]

        mask = np.triu(np.ones_like(d_matrix, dtype=bool), k=1)
        sns.heatmap(d_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                   vmin=-2, vmax=2, ax=ax3, cbar_kws={'label': "Cohen's d"})
        ax3.set_title('Pairwise Effect Sizes (Disinhibition)', fontsize=13, fontweight='bold')

    # 4. Significance matrix
    ax4 = axes[1, 1]
    if pairwise_disinhibition:
        sig_matrix = pd.DataFrame('', index=providers, columns=providers)
        for comp in pairwise_disinhibition:
            p1, p2 = comp['provider_1'], comp['provider_2']
            p_val = comp['p_bonferroni']
            d_val = abs(comp['cohens_d'])

            if p_val < 0.001:
                sig = '***'
            elif p_val < 0.01:
                sig = '**'
            elif p_val < 0.05:
                sig = '*'
            else:
                sig = 'ns'

            # Add effect size descriptor
            if d_val >= 0.8:
                sig += ' (L)'
            elif d_val >= 0.5:
                sig += ' (M)'
            elif d_val >= 0.2:
                sig += ' (S)'

            sig_matrix.loc[p1, p2] = sig
            sig_matrix.loc[p2, p1] = sig

        sig_matrix = sig_matrix.loc[provider_order, provider_order]

        # Create color coding
        color_map = {'': 0, 'ns': 1, 'ns (S)': 1.5, '* (S)': 2, '* (M)': 2.5, '* (L)': 3,
                    '** (S)': 3.5, '** (M)': 4, '** (L)': 4.5, '*** (S)': 5, '*** (M)': 5.5, '*** (L)': 6}
        color_matrix = sig_matrix.applymap(lambda x: color_map.get(x, 0))

        mask = np.triu(np.ones_like(color_matrix, dtype=bool), k=1)
        sns.heatmap(color_matrix.astype(float), mask=mask, annot=sig_matrix, fmt='',
                   cmap='YlOrRd', ax=ax4, cbar=False)
        ax4.set_title('Significance (Bonferroni)\n* p<.05, ** p<.01, *** p<.001\n(S)mall (M)edium (L)arge effect',
                     fontsize=11, fontweight='bold')

    plt.suptitle(f'Provider Comparison Summary\nCondition: {condition}', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def create_dimension_comparison_grid(df: pd.DataFrame, results: dict, output_path: Path, condition: str = "baseline"):
    """Create grid showing all 9 dimensions by provider with ANOVA stats."""
    fig, axes = plt.subplots(3, 3, figsize=(16, 14))
    axes = axes.flatten()

    provider_order = df.groupby('provider')['sophistication'].mean().sort_values(ascending=False).index.tolist()

    for i, dim in enumerate(DIMENSIONS):
        ax = axes[i]
        sns.boxplot(data=df, x='provider', y=dim, order=provider_order, ax=ax, palette='Set2')
        ax.set_xlabel('')
        ax.set_ylabel('Score', fontsize=9)
        ax.tick_params(axis='x', rotation=45, labelsize=8)

        # Add ANOVA result
        anova = results.get(dim, {}).get('anova', {})
        if anova:
            f_val = anova.get('F', 0)
            p_val = anova.get('p', 1)
            eta2 = anova.get('eta_squared', 0)
            interp = anova.get('eta_squared_interp', '')

            sig_marker = ''
            if p_val < 0.001:
                sig_marker = '***'
            elif p_val < 0.01:
                sig_marker = '**'
            elif p_val < 0.05:
                sig_marker = '*'

            title_color = 'red' if p_val < 0.05 else 'black'
            ax.set_title(f'{dim.capitalize()} {sig_marker}\nF={f_val:.2f}, η²={eta2:.2f} ({interp})',
                        fontsize=10, fontweight='bold', color=title_color)

    plt.suptitle(f'All Dimensions by Provider (n≥3)\n* p<.05, ** p<.01, *** p<.001\nCondition: {condition}',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def print_summary_report(results: dict, df: pd.DataFrame, condition: str):
    """Print comprehensive summary report."""
    providers = sorted(df['provider'].unique())

    print("\n" + "=" * 80)
    print(f"CROSS-PROVIDER COMPARISON: {condition.upper()}")
    print("=" * 80)

    # Provider sample sizes
    print(f"\n{'PROVIDER SAMPLE SIZES':^40}")
    print("-" * 40)
    for provider in providers:
        n = len(df[df['provider'] == provider])
        print(f"  {provider}: n = {n}")
    print(f"  {'Total':}: N = {len(df)}")

    # ANOVA results for key composites
    print(f"\n{'ANOVA RESULTS - KEY COMPOSITES':^60}")
    print("-" * 60)
    print(f"{'Measure':<20} {'F':>8} {'p':>12} {'η²':>8} {'Effect':>12}")
    print("-" * 60)

    for measure in ['disinhibition', 'sophistication']:
        anova = results.get(measure, {}).get('anova', {})
        if anova:
            f_val = anova.get('F', 0)
            p_val = anova.get('p', 1)
            eta2 = anova.get('eta_squared', 0)
            interp = anova.get('eta_squared_interp', '')
            print(f"{measure.capitalize():<20} {f_val:>8.2f} {format_p_value(p_val):>12} {eta2:>8.3f} {interp:>12}")

    # ANOVA results for all dimensions
    print(f"\n{'ANOVA RESULTS - ALL DIMENSIONS':^60}")
    print("-" * 60)
    print(f"{'Dimension':<20} {'F':>8} {'p':>12} {'η²':>8} {'Effect':>12}")
    print("-" * 60)

    for dim in DIMENSIONS:
        anova = results.get(dim, {}).get('anova', {})
        if anova:
            f_val = anova.get('F', 0)
            p_val = anova.get('p', 1)
            eta2 = anova.get('eta_squared', 0)
            interp = anova.get('eta_squared_interp', '')
            sig = '*' if p_val < 0.05 else ' '
            print(f"{dim.capitalize():<20} {f_val:>8.2f} {format_p_value(p_val):>12} {eta2:>8.3f} {interp:>12} {sig}")

    # Significant pairwise comparisons for disinhibition
    print(f"\n{'SIGNIFICANT PAIRWISE COMPARISONS (DISINHIBITION)':^60}")
    print("-" * 60)
    print(f"{'Comparison':<25} {'d':>8} {'p (Bonf)':>12} {'Effect':>10}")
    print("-" * 60)

    pairwise = results.get('disinhibition', {}).get('pairwise', [])
    sig_pairs = [p for p in pairwise if p['p_bonferroni'] < 0.05]
    sig_pairs.sort(key=lambda x: abs(x['cohens_d']), reverse=True)

    if sig_pairs:
        for comp in sig_pairs:
            name = f"{comp['provider_1']} vs {comp['provider_2']}"
            d = comp['cohens_d']
            p = comp['p_bonferroni']
            interp = comp['d_interp']
            print(f"{name:<25} {d:>+8.2f} {format_p_value(p):>12} {interp:>10}")
    else:
        print("  No significant pairwise differences after Bonferroni correction")

    # Provider rankings
    print(f"\n{'PROVIDER RANKINGS':^50}")
    print("-" * 50)

    for measure in ['disinhibition', 'sophistication']:
        provider_means = df.groupby('provider')[measure].mean().sort_values(ascending=False)
        print(f"\n{measure.capitalize()}:")
        for i, (provider, mean) in enumerate(provider_means.items(), 1):
            print(f"  {i}. {provider}: {mean:.2f}")

    print("\n" + "=" * 80)


def main():
    # Get condition from command line
    if len(sys.argv) > 1:
        condition = sys.argv[1]
    else:
        condition = "baseline"

    print(f"\nRunning cross-provider comparisons for: {condition}")
    print("-" * 50)

    # Load data
    try:
        df = load_data(condition)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Loaded {len(df)} models")

    # Filter providers
    df_filtered = filter_providers(df, MIN_PROVIDER_N)
    excluded = set(df['provider'].unique()) - set(df_filtered['provider'].unique())

    print(f"Filtered to providers with n≥{MIN_PROVIDER_N}")
    print(f"Retained: {len(df_filtered)} models from {df_filtered['provider'].nunique()} providers")
    if excluded:
        print(f"Excluded providers (n<{MIN_PROVIDER_N}): {', '.join(excluded)}")

    # Calculate composites
    df_filtered['disinhibition'] = df_filtered[DISINHIBITION_DIMS].mean(axis=1)
    df_filtered['sophistication'] = df_filtered[SOPHISTICATION_DIMS].mean(axis=1)

    # Run analyses
    print("\nRunning analyses...")
    results = {}

    # Analyze composites
    for measure in ['disinhibition', 'sophistication']:
        results[measure] = analyze_dimension(df_filtered, measure)

    # Analyze all dimensions
    for dim in DIMENSIONS:
        results[dim] = analyze_dimension(df_filtered, dim)

    # Output directory
    output_dir = Path(f"outputs/behavioral_profiles/{condition}")

    # Save results JSON
    # Convert provider_stats DataFrames to dicts for JSON serialization
    results_json = {}
    for key, value in results.items():
        results_json[key] = {
            'dimension': value['dimension'],
            'anova': value['anova'],
            'pairwise': value['pairwise'],
            'provider_stats': value['provider_stats']
        }

    json_path = output_dir / "provider_comparison_stats.json"
    with open(json_path, 'w') as f:
        json.dump(results_json, f, indent=2)
    print(f"Saved: {json_path}")

    # Create visualizations
    print("\nGenerating visualizations...")
    create_comparison_visualization(df_filtered, results, output_dir / "provider_comparison_summary.png", condition=condition)
    create_dimension_comparison_grid(df_filtered, results, output_dir / "provider_comparison_dimensions.png", condition=condition)

    # Print summary report
    print_summary_report(results, df_filtered, condition)

    print(f"\nOutputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
