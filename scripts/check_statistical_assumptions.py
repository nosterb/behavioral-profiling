#!/usr/bin/env python3
"""
Statistical Assumptions & Quality Control Analysis

Validates assumptions for parametric tests (Pearson correlation, t-tests):
- Normality of variables (Shapiro-Wilk)
- Correlation robustness (Pearson vs Spearman comparison)
- Residual normality (with/without outliers)

Usage:
    python3 scripts/check_statistical_assumptions.py --condition naturalistic
    python3 scripts/check_statistical_assumptions.py --condition baseline
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def load_all_models_data(condition: str, base_dir: str = 'outputs/behavioral_profiles') -> pd.DataFrame:
    """Load the all_models_data.csv for a condition."""
    csv_path = Path(f'{base_dir}/{condition}/all_models_data.csv')
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    df = pd.read_csv(csv_path)

    # Compute disinhibition composite if not present
    disin_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']
    if 'disinhibition' not in df.columns:
        if all(d in df.columns for d in disin_dims):
            df['disinhibition'] = df[disin_dims].mean(axis=1)
            print(f"Computed disinhibition composite from: {disin_dims}")
        else:
            missing = [d for d in disin_dims if d not in df.columns]
            raise ValueError(f"Cannot compute disinhibition - missing columns: {missing}")

    return df


def calculate_descriptive_stats(series: pd.Series) -> dict:
    """Calculate descriptive statistics for a series."""
    return {
        'mean': round(float(series.mean()), 4),
        'sd': round(float(series.std()), 4),
        'min': round(float(series.min()), 4),
        'max': round(float(series.max()), 4),
        'median': round(float(series.median()), 4),
        'skewness': round(float(stats.skew(series)), 4),
        'kurtosis': round(float(stats.kurtosis(series)), 4)
    }


def shapiro_wilk_test(series: pd.Series) -> dict:
    """Run Shapiro-Wilk normality test."""
    stat, p = stats.shapiro(series)
    return {
        'shapiro_wilk_w': round(float(stat), 4),
        'shapiro_wilk_p': float(p),
        'normal_at_05': bool(p > 0.05)  # Convert numpy bool to Python bool
    }


def correlation_robustness(x: pd.Series, y: pd.Series) -> dict:
    """Compare Pearson and Spearman correlations."""
    pearson_r, pearson_p = stats.pearsonr(x, y)
    spearman_rho, spearman_p = stats.spearmanr(x, y)
    diff = abs(spearman_rho - pearson_r)

    return {
        'pearson_r': round(float(pearson_r), 4),
        'pearson_p': float(pearson_p),
        'spearman_rho': round(float(spearman_rho), 4),
        'spearman_p': float(spearman_p),
        'difference': round(float(diff), 4),
        'methods_agree': bool(diff < 0.05)  # Convert numpy bool to Python bool
    }


def residual_analysis(x: pd.Series, y: pd.Series, outlier_threshold: float = 2.0) -> tuple:
    """Analyze residuals from linear regression, with/without outliers.

    Returns: (full_result, clean_result, outlier_indices, std_residuals, outlier_mask)
    """
    # Fit linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    predicted = slope * x + intercept
    residuals = y - predicted

    # Standardize residuals
    residual_std = residuals.std()
    std_residuals = residuals / residual_std

    # Identify outliers
    outlier_mask = np.abs(std_residuals) > outlier_threshold
    outlier_indices = x.index[outlier_mask].tolist()

    # Full sample residual normality
    full_shapiro = stats.shapiro(residuals)
    full_result = {
        'n': int(len(residuals)),
        'shapiro_wilk_w': round(float(full_shapiro[0]), 4),
        'shapiro_wilk_p': round(float(full_shapiro[1]), 4),
        'skewness': round(float(stats.skew(residuals)), 4),
        'kurtosis': round(float(stats.kurtosis(residuals)), 4),
        'normal_at_05': bool(full_shapiro[1] > 0.05)
    }

    # Without outliers
    if outlier_mask.sum() > 0:
        clean_x = x[~outlier_mask]
        clean_y = y[~outlier_mask]
        slope_c, intercept_c, r_c, p_c, std_err_c = stats.linregress(clean_x, clean_y)
        predicted_c = slope_c * clean_x + intercept_c
        residuals_c = clean_y - predicted_c

        clean_shapiro = stats.shapiro(residuals_c)
        clean_result = {
            'n': int(len(residuals_c)),
            'n_removed': int(outlier_mask.sum()),
            'shapiro_wilk_w': round(float(clean_shapiro[0]), 4),
            'shapiro_wilk_p': round(float(clean_shapiro[1]), 4),
            'skewness': round(float(stats.skew(residuals_c)), 4),
            'kurtosis': round(float(stats.kurtosis(residuals_c)), 4),
            'normal_at_05': bool(clean_shapiro[1] > 0.05),
            'correlation_r': round(float(r_c), 4)
        }
    else:
        clean_result = {
            'n': int(len(residuals)),
            'n_removed': 0,
            'note': 'No outliers detected',
            'correlation_r': round(float(r_value), 4)
        }

    return full_result, clean_result, outlier_indices, std_residuals, outlier_mask


def create_distribution_plots(df: pd.DataFrame, output_dir: Path, condition: str):
    """Create distribution visualizations."""

    # Plot 1: Composite distributions
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    for ax, col, title in zip(axes, ['sophistication', 'disinhibition'],
                               ['Sophistication', 'Disinhibition']):
        data = df[col].dropna()
        ax.hist(data, bins=15, alpha=0.7, edgecolor='black')
        ax.axvline(data.mean(), color='red', linestyle='--', label=f'Mean={data.mean():.2f}')
        ax.axvline(data.median(), color='green', linestyle=':', label=f'Median={data.median():.2f}')

        # Shapiro-Wilk
        stat, p = stats.shapiro(data)
        skew = stats.skew(data)
        ax.set_title(f'{title}\nW={stat:.3f}, p={p:.4f}, skew={skew:.2f}')
        ax.set_xlabel(title)
        ax.set_ylabel('Frequency')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'distribution_composites.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Plot 2: Disinhibition dimensions
    dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    for ax, col in zip(axes.flatten(), dims):
        if col in df.columns:
            data = df[col].dropna()
            ax.hist(data, bins=15, alpha=0.7, edgecolor='black')
            stat, p = stats.shapiro(data)
            skew = stats.skew(data)
            ax.set_title(f'{col.title()}\nW={stat:.3f}, p={p:.4f}, skew={skew:.2f}')
            ax.set_xlabel(col.title())
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'distribution_disinhibition_dims.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Plot 3: Q-Q plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Condition: {condition} - Q-Q Plots', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    for ax, col in zip(axes.flatten(), ['sophistication', 'disinhibition', 'transgression', 'aggression']):
        if col in df.columns:
            data = df[col].dropna()
            stats.probplot(data, dist="norm", plot=ax)
            ax.set_title(f'{col.title()} Q-Q Plot')
            ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'distribution_qq_plots.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_residual_plots(df: pd.DataFrame, std_residuals: pd.Series, outlier_indices: list,
                          output_dir: Path, condition: str):
    """Create residual analysis plots."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'Condition: {condition} - Residual Analysis', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    # Residual distribution
    ax = axes[0]
    ax.hist(std_residuals, bins=15, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', label='Zero')
    ax.axvline(-2, color='orange', linestyle=':', label='±2 SD')
    ax.axvline(2, color='orange', linestyle=':')
    stat, p = stats.shapiro(std_residuals)
    ax.set_title(f'Standardized Residuals\nShapiro-Wilk W={stat:.3f}, p={p:.4f}')
    ax.set_xlabel('Standardized Residual')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Residual vs Fitted
    ax = axes[1]
    slope, intercept, _, _, _ = stats.linregress(df['sophistication'], df['disinhibition'])
    fitted = slope * df['sophistication'] + intercept

    ax.scatter(fitted, std_residuals, alpha=0.7, s=50)
    ax.axhline(0, color='red', linestyle='--')
    ax.axhline(2, color='orange', linestyle=':')
    ax.axhline(-2, color='orange', linestyle=':')

    # Mark outliers
    if outlier_indices:
        for idx in outlier_indices:
            if idx in df.index:
                ax.scatter(fitted.loc[idx], std_residuals.loc[idx],
                          color='red', s=200, facecolors='none', linewidths=2)
                model_name = df.loc[idx, 'model'] if 'model' in df.columns else str(idx)
                ax.annotate(model_name, (fitted.loc[idx], std_residuals.loc[idx]),
                           fontsize=8, color='red',
                           xytext=(5, 5), textcoords='offset points')

    ax.set_title('Residuals vs Fitted Values')
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Standardized Residual')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'distribution_residuals.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_correlation_plot(df: pd.DataFrame, output_dir: Path, condition: str):
    """Create correlation robustness plot."""
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold', y=0.995, color='#666666')

    x = df['sophistication']
    y = df['disinhibition']

    # Scatter with regression
    ax.scatter(x, y, alpha=0.7, s=60, c='steelblue')

    # Regression line
    slope, intercept, r, p, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.7,
            label=f'Regression (r={r:.3f})')

    # Spearman
    rho, p_spearman = stats.spearmanr(x, y)

    # Stats box
    stats_text = f'Pearson r = {r:.4f}\nSpearman ρ = {rho:.4f}\nΔ = {abs(r-rho):.4f}'
    agree = "✅ Agree" if abs(r - rho) < 0.05 else "❌ Differ"
    stats_text += f'\n{agree}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    ax.set_xlabel('Sophistication', fontsize=12)
    ax.set_ylabel('Disinhibition', fontsize=12)
    ax.set_title('Correlation Robustness: Pearson vs Spearman')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_robustness.png', dpi=150, bbox_inches='tight')
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Check statistical assumptions for parametric tests')
    parser.add_argument('--condition', required=True, help='Condition name (e.g., baseline, naturalistic)')
    parser.add_argument('--base-dir', type=str, default='outputs/behavioral_profiles',
                        help='Base directory for behavioral profiles (default: outputs/behavioral_profiles)')
    args = parser.parse_args()

    condition = args.condition
    base_dir = args.base_dir

    # Load data
    print(f"\n{'='*60}")
    print(f"STATISTICAL ASSUMPTIONS ANALYSIS: {condition.upper()}")
    print(f"{'='*60}\n")

    try:
        df = load_all_models_data(condition, base_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"Loaded data: N = {len(df)} models")

    # Create output directory
    output_dir = Path(f'{base_dir}/{condition}/statistical_assumptions')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate descriptive statistics
    print("\n--- Descriptive Statistics ---")
    variables = ['sophistication', 'disinhibition', 'depth', 'authenticity',
                 'transgression', 'aggression', 'tribalism', 'grandiosity']

    descriptive_stats = {}
    for var in variables:
        if var in df.columns:
            descriptive_stats[var] = calculate_descriptive_stats(df[var])
            print(f"{var}: M={descriptive_stats[var]['mean']:.2f}, SD={descriptive_stats[var]['sd']:.2f}, skew={descriptive_stats[var]['skewness']:.2f}")

    # Normality tests
    print("\n--- Normality Tests (Shapiro-Wilk) ---")
    normality_tests = {}
    passing_count = 0
    for var in variables:
        if var in df.columns:
            normality_tests[var] = shapiro_wilk_test(df[var])
            status = "✅ normal" if normality_tests[var]['normal_at_05'] else "❌ non-normal"
            if normality_tests[var]['normal_at_05']:
                passing_count += 1
            print(f"{var}: W={normality_tests[var]['shapiro_wilk_w']:.3f}, p={normality_tests[var]['shapiro_wilk_p']:.4f} {status}")

    print(f"\nVariables passing normality: {passing_count}/{len(normality_tests)}")

    # Check sophistication symmetry
    soph_skew = descriptive_stats['sophistication']['skewness']
    soph_symmetric = abs(soph_skew) < 0.5
    print(f"\nSophistication symmetry: skew={soph_skew:.3f} {'✅ symmetric' if soph_symmetric else '❌ skewed'}")

    # Correlation robustness
    print("\n--- Correlation Robustness ---")
    corr_robust = correlation_robustness(df['sophistication'], df['disinhibition'])
    print(f"Pearson r = {corr_robust['pearson_r']:.4f} (p = {corr_robust['pearson_p']:.4e})")
    print(f"Spearman ρ = {corr_robust['spearman_rho']:.4f} (p = {corr_robust['spearman_p']:.4e})")
    print(f"Difference: Δ = {corr_robust['difference']:.4f}")
    agree_status = "✅ Methods agree (Δ < 0.05)" if corr_robust['methods_agree'] else "❌ Methods differ (Δ ≥ 0.05)"
    print(agree_status)

    # Residual analysis
    print("\n--- Residual Analysis ---")
    full_residual, clean_residual, outlier_indices, std_residuals, outlier_mask = residual_analysis(
        df['sophistication'], df['disinhibition']
    )

    print(f"Full sample (N={full_residual['n']}): W={full_residual['shapiro_wilk_w']:.3f}, p={full_residual['shapiro_wilk_p']:.4f}")

    # Identify outliers
    outliers = []
    if outlier_indices:
        print(f"\nOutliers detected: {len(outlier_indices)}")
        for idx in outlier_indices:
            model_name = df.loc[idx, 'model'] if 'model' in df.columns else str(idx)
            provider = df.loc[idx, 'provider'] if 'provider' in df.columns else 'Unknown'
            soph = df.loc[idx, 'sophistication']
            disin = df.loc[idx, 'disinhibition']
            std_res = std_residuals.loc[idx]
            print(f"  - {model_name}: soph={soph:.2f}, disin={disin:.2f}, residual={std_res:.2f} SD")
            outliers.append({
                'model': model_name,
                'provider': provider,
                'sophistication': round(float(soph), 4),
                'disinhibition': round(float(disin), 4),
                'std_residual': round(float(std_res), 4)
            })

    print(f"\nWithout outliers (N={clean_residual['n']}): W={clean_residual.get('shapiro_wilk_w', 'N/A')}, p={clean_residual.get('shapiro_wilk_p', 'N/A')}")
    if 'correlation_r' in clean_residual:
        print(f"Correlation after outlier removal: r = {clean_residual['correlation_r']:.4f}")

    # Correlation robustness WITHOUT outliers
    print("\n--- Correlation Robustness (Without Outliers) ---")
    if outlier_indices:
        clean_df = df[~outlier_mask]
        corr_robust_clean = correlation_robustness(clean_df['sophistication'], clean_df['disinhibition'])
        print(f"Pearson r = {corr_robust_clean['pearson_r']:.4f}")
        print(f"Spearman ρ = {corr_robust_clean['spearman_rho']:.4f}")
        print(f"Difference: Δ = {corr_robust_clean['difference']:.4f}")
        agree_status_clean = "✅ Methods agree (Δ < 0.05)" if corr_robust_clean['methods_agree'] else "❌ Methods differ (Δ ≥ 0.05)"
        print(agree_status_clean)
    else:
        corr_robust_clean = corr_robust.copy()
        corr_robust_clean['note'] = 'Same as full sample (no outliers removed)'
        print("No outliers to remove - same as full sample")

    # Determine overall recommendation
    print("\n--- Summary ---")
    residuals_normal_clean = clean_residual.get('normal_at_05', False)

    # Parametric methods appropriate if:
    # 1. Sophistication is symmetric (|skew| < 0.5), AND
    # 2. Pearson/Spearman agree (Δ < 0.05)
    parametric_ok = soph_symmetric and corr_robust['methods_agree']

    if parametric_ok:
        recommendation = "✅ Parametric methods appropriate"
        rationale = "Sophistication is symmetric; Pearson/Spearman agree"
        if outliers:
            rationale += f"; residuals normal after removing {len(outliers)} outlier(s)"
    else:
        recommendation = "⚠️ CAUTION with parametric methods"
        issues = []
        if not soph_symmetric:
            issues.append("sophistication skewed")
        if not corr_robust['methods_agree']:
            issues.append(f"Pearson/Spearman differ by {corr_robust['difference']:.3f}")
        rationale = "; ".join(issues)

    print(f"{recommendation}")
    print(f"Rationale: {rationale}")

    # Create visualizations
    print("\n--- Creating Visualizations ---")
    create_distribution_plots(df, output_dir, condition)
    create_residual_plots(df, std_residuals, outlier_indices, output_dir, condition)
    create_correlation_plot(df, output_dir, condition)
    print("Saved: distribution_composites.png, distribution_disinhibition_dims.png")
    print("Saved: distribution_qq_plots.png, distribution_residuals.png")
    print("Saved: correlation_robustness.png")

    # Build audit JSON
    audit = {
        'schema_version': '1.0',
        'metadata': {
            'generated': datetime.now().isoformat(),
            'analysis': 'Statistical Assumptions & Quality Control',
            'condition': condition,
            'n_models': int(len(df))
        },
        'provenance': {
            'source_files': {
                'behavioral_profiles': f'{base_dir}/{condition}/all_models_data.csv'
            },
            'methodology': {
                'normality_test': 'Shapiro-Wilk',
                'correlation_comparison': 'Pearson vs Spearman',
                'outlier_threshold': '2.0 standard deviations from regression line'
            }
        },
        'results': {
            'descriptive_statistics': descriptive_stats,
            'normality_tests': normality_tests,
            'correlation_robustness': {
                'full_sample': corr_robust,
                'outliers_removed': corr_robust_clean
            },
            'residual_analysis': {
                'full_sample': full_residual,
                'outliers_removed': clean_residual
            },
            'outliers': outliers,
            'summary': {
                'variables_passing_normality': f'{passing_count}/{len(normality_tests)}',
                'sophistication_symmetric': bool(soph_symmetric),
                'correlation_methods_agree_full': bool(corr_robust['methods_agree']),
                'correlation_methods_agree_clean': bool(corr_robust_clean['methods_agree']),
                'residuals_normal_without_outliers': bool(residuals_normal_clean),
                'parametric_methods_appropriate': bool(parametric_ok),
                'rationale': rationale
            }
        },
        'output_files': [
            'distribution_composites.png',
            'distribution_disinhibition_dims.png',
            'distribution_residuals.png',
            'distribution_qq_plots.png',
            'correlation_robustness.png'
        ]
    }

    # Save audit JSON
    audit_path = output_dir / 'normality_audit.json'
    with open(audit_path, 'w') as f:
        json.dump(audit, f, indent=2)
    print(f"Saved: normality_audit.json")

    # Load job audit data if available
    job_audit_path = Path(f'{base_dir}/{condition}/job_audit.json')
    job_audit = None
    if job_audit_path.exists():
        with open(job_audit_path) as f:
            job_audit = json.load(f)

    # Create markdown report
    md_content = f"""# Statistical Assumptions Analysis: {condition.title()}

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Condition**: {condition}
**N**: {len(df)} models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | {len(df)} |
"""

    if job_audit:
        summary = job_audit.get('summary', {})
        md_content += f"""| Unique Prompts | {summary.get('n_unique_prompts', 'N/A')} |
| Total Evaluations | {summary.get('total_valid_3judge', 'N/A'):,} |
| Judges | {', '.join(summary.get('judges_used', ['N/A']))} |
| Judge Count | {summary.get('n_judges', 'N/A')} |
| Jobs Complete | {summary.get('n_jobs_complete', 'N/A')}/{summary.get('n_jobs', 'N/A')} ({summary.get('completeness_rate', 0)*100:.0f}%) |
"""

    # Add outlier info to Data Summary
    outlier_models = ', '.join([o['model'] for o in outliers]) if outliers else 'None'
    md_content += f"""| Outliers Detected | {len(outliers)} ({outlier_models}) |
"""

    md_content += f"""
---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = {soph_skew:.3f} | {'✅' if soph_symmetric else '❌'} |
| Correlation Methods Agree (Full) | Δ = {corr_robust['difference']:.3f} | {'✅' if corr_robust['methods_agree'] else '❌'} |
| Correlation Methods Agree (Clean) | Δ = {corr_robust_clean['difference']:.3f} | {'✅' if corr_robust_clean['methods_agree'] else '❌'} |
| Residuals Normal (without outliers) | p = {clean_residual.get('shapiro_wilk_p', 'N/A')} | {'✅' if residuals_normal_clean else '❌'} |
| **Parametric Methods** | {rationale} | **{'✅ OK' if parametric_ok else '⚠️ CAUTION'}** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)
"""

    if outliers:
        md_content += f"""
**Outliers Detected**: {len(outliers)}

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
"""
        for o in outliers:
            direction = "Above" if o['std_residual'] > 0 else "Below"
            md_content += f"| {o['model']} | {o['provider']} | {o['sophistication']:.2f} | {o['disinhibition']:.2f} | {o['std_residual']:.2f} SD | {direction} |\n"

        md_content += f"""
**Impact of Outlier Removal**:
- Pearson r: {corr_robust['pearson_r']:.3f} → {corr_robust_clean['pearson_r']:.3f} ({corr_robust_clean['pearson_r'] - corr_robust['pearson_r']:+.3f})
- Pearson/Spearman Δ: {corr_robust['difference']:.3f} → {corr_robust_clean['difference']:.3f}
- Methods Agree: {'❌ → ✅' if not corr_robust['methods_agree'] and corr_robust_clean['methods_agree'] else '✅ → ✅' if corr_robust['methods_agree'] else '❌ → ❌'}
"""
    else:
        md_content += """
**Outliers Detected**: 0

No models exceed the 2.0 SD threshold from the regression line.
"""

    md_content += f"""

---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
"""

    for var in variables:
        if var in normality_tests:
            nt = normality_tests[var]
            status = '✅' if nt['normal_at_05'] else '❌'
            md_content += f"| {var.title()} | {nt['shapiro_wilk_w']:.4f} | {nt['shapiro_wilk_p']:.4f} | {status} |\n"

    md_content += f"""
**{passing_count}/{len(normality_tests)} variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = {len(df)})

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | {corr_robust['pearson_r']:.4f} | {corr_robust['pearson_p']:.4e} |
| Spearman ρ | {corr_robust['spearman_rho']:.4f} | {corr_robust['spearman_p']:.4e} |
| Difference | {corr_robust['difference']:.4f} | - |

**Methods {'agree' if corr_robust['methods_agree'] else 'DO NOT agree'} (threshold: Δ < 0.05)**

### Without Outliers (N = {clean_residual['n']})

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | {corr_robust_clean['pearson_r']:.4f} | {corr_robust_clean['pearson_p']:.4e} |
| Spearman ρ | {corr_robust_clean['spearman_rho']:.4f} | {corr_robust_clean['spearman_p']:.4e} |
| Difference | {corr_robust_clean['difference']:.4f} | - |

**Methods {'agree' if corr_robust_clean['methods_agree'] else 'DO NOT agree'} (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | {corr_robust['pearson_r']:.4f} | {corr_robust_clean['pearson_r']:.4f} | {corr_robust_clean['pearson_r'] - corr_robust['pearson_r']:+.4f} |
| Spearman ρ | {corr_robust['spearman_rho']:.4f} | {corr_robust_clean['spearman_rho']:.4f} | {corr_robust_clean['spearman_rho'] - corr_robust['spearman_rho']:+.4f} |
| Δ (difference) | {corr_robust['difference']:.4f} | {corr_robust_clean['difference']:.4f} | {corr_robust_clean['difference'] - corr_robust['difference']:+.4f} |
| Methods Agree | {'✅' if corr_robust['methods_agree'] else '❌'} | {'✅' if corr_robust_clean['methods_agree'] else '❌'} | - |

---

## Residual Analysis

### Full Sample (N = {full_residual['n']})
- Shapiro-Wilk W = {full_residual['shapiro_wilk_w']:.4f}, p = {full_residual['shapiro_wilk_p']:.4f}
- Skewness = {full_residual['skewness']:.4f}, Kurtosis = {full_residual['kurtosis']:.4f}

"""

    if outliers:
        md_content += f"""### Without Outliers (N = {clean_residual['n']})
- Shapiro-Wilk W = {clean_residual.get('shapiro_wilk_w', 'N/A')}, p = {clean_residual.get('shapiro_wilk_p', 'N/A')}
- Correlation r = {clean_residual.get('correlation_r', 'N/A')}

"""
    else:
        md_content += """### Residuals
- No outliers detected; residual statistics same as full sample

"""

    md_content += f"""---

## Recommendation

**{recommendation}**

{rationale}

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `{base_dir}/{condition}/all_models_data.csv`
**Audit File**: `normality_audit.json`
"""

    md_path = output_dir / 'STATISTICAL_ASSUMPTIONS_BRIEF.md'
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"Saved: STATISTICAL_ASSUMPTIONS_BRIEF.md")

    print(f"\n{'='*60}")
    print(f"Analysis complete. Outputs in: {output_dir}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
