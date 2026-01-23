#!/usr/bin/env python3
"""
Generate research brief using template-based system v2.

This script separates:
1. DATA sections - Pure algorithmic population
2. INTERPRET sections - Rule-based text generation (algorithmic, following template rules)
3. COMMENTARY sections - Optional insights (only added when data warrants)

The template rules are applied algorithmically to ensure narrative always matches data.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy import stats as sp_stats
from typing import Dict, List, Any, Optional, Tuple


# ==============================================================================
# EFFECT SIZE HELPERS
# ==============================================================================

def format_p(p: float) -> str:
    """Format p-value following APA conventions."""
    if p < 0.001:
        return "p < .001"
    elif p < 0.01:
        return "p < .01"
    elif p < 0.05:
        return f"p < .05"
    else:
        return f"p = {p:.3f}"


def effect_size_d(d: float) -> str:
    """Classify Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


def effect_size_r(r: float) -> str:
    """Classify Pearson r effect size."""
    abs_r = abs(r)
    if abs_r < 0.10:
        return "negligible"
    elif abs_r < 0.30:
        return "small"
    elif abs_r < 0.50:
        return "medium"
    else:
        return "large"


def count_to_words(count: int, total: int = 4) -> str:
    """Convert count to words for describing dimensions."""
    if count == total:
        return f"All {total}"
    elif count == 0:
        return f"None of the {total}"
    else:
        return f"{['Zero', 'One', 'Two', 'Three', 'Four'][count]} of {total}"


# ==============================================================================
# DATA FRESHNESS VALIDATION
# ==============================================================================

def validate_outlier_data_freshness(profile_dir: Path, median_split_path: Path) -> bool:
    """
    Check if outlier data is fresh (newer than median split data).

    Returns True if data is fresh or doesn't exist, False if stale.
    Prints warning if stale data detected.
    """
    outlier_info_path = profile_dir / 'outliers_removed' / 'outlier_removal_info.json'

    if not outlier_info_path.exists():
        return True  # No outlier data yet - will be skipped anyway

    if not median_split_path.exists():
        return True  # No median split - something else is wrong

    median_mtime = median_split_path.stat().st_mtime
    outlier_mtime = outlier_info_path.stat().st_mtime

    if outlier_mtime < median_mtime:
        print(f"⚠️  WARNING: Outlier data is STALE (older than median split)")
        print(f"   Outlier file: {outlier_info_path}")
        print(f"   Run: python3 scripts/analyze_outliers_removed.py {profile_dir.name} --force")
        print(f"   Or the pipeline will use outdated outlier statistics in the research brief.")
        return False

    return True


# ==============================================================================
# SCALE DETECTION
# ==============================================================================

def detect_scale(median_soph: float) -> Tuple[int, float]:
    """
    Detect scoring scale and return (scale, scale_factor).

    Returns:
        (scale, factor): e.g., (10, 1.0) for 1-10 scale, (50, 5.0) for 1-50 scale
    """
    if median_soph > 15:
        return 50, 5.0
    else:
        return 10, 1.0


def get_scaled_thresholds(median_soph: float) -> Dict[str, float]:
    """Get thresholds scaled appropriately for the scoring scale."""
    scale, factor = detect_scale(median_soph)
    return {
        'borderline': 0.15 * factor,
        'constrained_soph': 6.5 * factor,
        'constrained_residual': -0.15 * factor,
        'outlier_sd': 2.0,  # SD threshold doesn't scale
        'scale': scale,
        'factor': factor
    }


# ==============================================================================
# DATA EXTRACTION
# ==============================================================================

def extract_correlations(models: List[Dict]) -> Dict[str, Tuple[float, float]]:
    """Calculate correlations between sophistication and each dimension."""
    soph_values = [m['sophistication'] for m in models]

    correlations = {}
    dimensions = ['transgression', 'aggression', 'tribalism', 'grandiosity', 'disinhibition']

    for dim in dimensions:
        if dim == 'disinhibition':
            dim_values = [m['disinhibition'] for m in models]
        else:
            dim_values = [m['scores'][dim] for m in models]

        r, p = sp_stats.pearsonr(soph_values, dim_values)
        correlations[dim] = (r, p)

    return correlations


def identify_special_models(models: List[Dict], median_soph: float) -> Dict[str, List[Dict]]:
    """Identify borderline, constrained, and outlier models."""
    thresholds = get_scaled_thresholds(median_soph)

    # Borderline models
    borderline = [m for m in models
                  if abs(m['sophistication'] - median_soph) < thresholds['borderline']]

    # Calculate regression for constrained/outlier detection
    soph_values = [m['sophistication'] for m in models]
    disinhib_values = [m['disinhibition'] for m in models]

    z = np.polyfit(soph_values, disinhib_values, 1)
    p_func = np.poly1d(z)
    predicted = p_func(np.array(soph_values))
    residuals = np.array(disinhib_values) - predicted
    residual_std = np.std(residuals)

    # Constrained models: high soph but below-predicted disinhibition
    constrained = []
    for i, model in enumerate(models):
        if (model['sophistication'] > thresholds['constrained_soph'] and
            residuals[i] < thresholds['constrained_residual']):
            constrained.append({
                'model': model,
                'residual': residuals[i]
            })

    # Outlier models: residual > 2 SD
    outliers = []
    for i, model in enumerate(models):
        if abs(residuals[i]) > thresholds['outlier_sd'] * residual_std:
            outliers.append({
                'model': model,
                'residual': residuals[i],
                'sd_from_line': residuals[i] / residual_std
            })

    return {
        'borderline': sorted(borderline, key=lambda x: x['sophistication']),
        'constrained': sorted(constrained, key=lambda x: x['residual']),
        'outliers': sorted(outliers, key=lambda x: abs(x['residual']), reverse=True)
    }


# ==============================================================================
# INTERPRET SECTION GENERATORS
# ==============================================================================

def interpret_h1(soph_d: float) -> str:
    """Generate H1 interpretation following template rules."""
    if soph_d >= 1.5:
        return "The median split produces two well-separated sophistication groups, supporting H1."
    elif soph_d >= 0.8:
        return "The median split produces moderately separated sophistication groups, supporting H1."
    else:
        return "The median split shows limited group separation. H1 requires further investigation."


def interpret_h1a(disinhib_d: float, p_value: float) -> str:
    """Generate H1a interpretation following template rules."""
    if p_value < 0.05 and disinhib_d >= 0.5:
        return "High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a."
    elif p_value < 0.05 and disinhib_d < 0.5:
        return "High-sophistication models showed significantly but modestly higher disinhibition than low-sophistication models. H1a is partially supported."
    else:
        return "No significant difference in disinhibition between groups. H1a is not supported."


def interpret_h1a_dimensions(dim_stats: Dict[str, Dict]) -> str:
    """Generate H1a dimensions summary following template rules."""
    dimensions = ['transgression', 'aggression', 'tribalism', 'grandiosity']

    # Count large effects
    large_effects = []
    other_effects = []

    for dim in dimensions:
        d = dim_stats[dim]['cohens_d']
        effect = effect_size_d(d)
        if effect == 'large':
            large_effects.append((dim, d))
        else:
            other_effects.append((dim, d, effect))

    # Find dimension with largest d
    all_dims = [(dim, dim_stats[dim]['cohens_d']) for dim in dimensions]
    largest = max(all_dims, key=lambda x: abs(x[1]))

    # Build interpretation
    count_str = count_to_words(len(large_effects))

    parts = []

    if len(large_effects) == 4:
        parts.append(f"{count_str} disinhibition dimensions showed large effects (d >= 0.8), with {largest[0]} showing the largest effect (d = {largest[1]:.2f}).")
    elif len(large_effects) > 0:
        parts.append(f"{count_str} disinhibition dimensions showed large effects (d >= 0.8), with {largest[0]} showing the largest effect (d = {largest[1]:.2f}).")

        # Note dimensions that didn't meet threshold
        for dim, d, effect in other_effects:
            parts.append(f"{dim.capitalize()} showed a {effect} effect (d = {d:.2f}).")
    else:
        parts.append(f"No disinhibition dimensions showed large effects (d >= 0.8). {largest[0].capitalize()} showed the strongest association (d = {largest[1]:.2f}, {effect_size_d(largest[1])}).")

    return " ".join(parts)


def interpret_h2(r: float, p: float) -> str:
    """Generate H2 interpretation following template rules."""
    if r >= 0.5 and p < 0.001:
        return "Model sophistication strongly predicted disinhibition composite scores, supporting H2."
    elif r >= 0.3 and p < 0.05:
        return "Model sophistication moderately predicted disinhibition composite scores, supporting H2."
    else:
        return "The sophistication-disinhibition relationship was weak or not significant. H2 requires further investigation."


def interpret_h2_dimensions(correlations: Dict[str, Tuple[float, float]]) -> str:
    """Generate H2 dimensions summary following template rules."""
    dimensions = ['transgression', 'aggression', 'tribalism', 'grandiosity']

    # Classify each dimension
    large = []
    medium = []
    small = []

    for dim in dimensions:
        r, p = correlations[dim]
        abs_r = abs(r)
        if abs_r >= 0.50:
            large.append((dim, r, p))
        elif abs_r >= 0.30:
            medium.append((dim, r, p))
        else:
            small.append((dim, r, p))

    # Find dimension with highest r
    all_dims = [(dim, correlations[dim][0]) for dim in dimensions]
    highest = max(all_dims, key=lambda x: abs(x[1]))

    # Build interpretation
    parts = []

    if len(large) == 4:
        parts.append(f"All four disinhibition dimensions showed large correlations (r >= 0.50) with sophistication, with {highest[0]} (r = {highest[1]:.3f}) showing the strongest association.")
    elif len(large) >= 1:
        count_str = count_to_words(len(large))
        large_dims = ", ".join([d[0] for d in large])
        parts.append(f"{count_str} disinhibition dimensions showed large correlations (r >= 0.50) with sophistication, with {highest[0]} (r = {highest[1]:.3f}) showing the strongest association.")

        # Note dimensions that didn't reach large threshold
        for dim, r, p in medium:
            parts.append(f"{dim.capitalize()} showed a medium correlation (r = {r:.3f}).")
        for dim, r, p in small:
            parts.append(f"{dim.capitalize()} showed a smaller but significant correlation (r = {r:.3f}).")
    else:
        # No large correlations
        if len(medium) > 0:
            count_str = count_to_words(len(medium))
            parts.append(f"{count_str} dimensions showed medium correlations (r >= 0.30), with {highest[0]} (r = {highest[1]:.3f}) showing the strongest.")
        else:
            parts.append(f"No dimensions showed medium or large correlations. {highest[0].capitalize()} showed the strongest association (r = {highest[1]:.3f}, {effect_size_r(highest[1])}).")

    return " ".join(parts)


def interpret_other_dimensions(dim_stats: Dict[str, Dict]) -> str:
    """Generate other dimensions interpretation."""
    dimensions = ['warmth', 'formality', 'hedging']

    significant = []
    for dim in dimensions:
        stat = dim_stats[dim]
        if stat['p_value'] < 0.05:
            # difference = High - Low
            # If difference > 0: High-soph scored higher
            # If difference < 0: Low-soph scored higher
            if stat['difference'] > 0:
                group = "High-sophistication"
                direction = "higher"
            else:
                group = "Low-sophistication"
                direction = "higher"  # Low-soph is higher when difference is negative
            d = abs(stat['cohens_d'])
            significant.append((dim, group, direction, d, stat['difference']))

    if not significant:
        return "No significant differences were observed for warmth, formality, or hedging."

    parts = []
    for dim, group, direction, d, diff in significant:
        effect = effect_size_d(d)
        parts.append(f"{group} models showed {direction} {dim} (d = {d:.2f}, {effect} effect).")

    return " ".join(parts)


def interpret_borderline(models: List[Dict], n: int) -> str:
    """Generate borderline models interpretation."""
    if n == 0:
        return "No models fell within the borderline threshold."

    model_list = ", ".join([m['display_name'] for m in models[:5]])  # List up to 5
    if n > 5:
        model_list += f", and {n - 5} others"

    return f"{n} models were within the borderline threshold: {model_list}. These could have been classified either way, making them important for sensitivity analysis."


def interpret_constrained(models: List[Dict], n: int) -> str:
    """Generate constrained models interpretation."""
    if n == 0:
        return "No models met the constrained criteria in this condition."

    model_names = [c['model']['display_name'] for c in models]
    model_list = ", ".join(model_names[:5])

    return f"{n} model(s) showed high sophistication but below-predicted disinhibition: {model_list}."


def interpret_outliers(outliers: List[Dict], n: int) -> str:
    """Generate outliers interpretation."""
    if n == 0:
        return "No models exceeded the 2 SD outlier threshold."

    parts = []
    for o in outliers[:3]:  # Show up to 3
        model = o['model']
        direction = "above" if o['residual'] > 0 else "below"
        parts.append(f"{model['display_name']} ({o['sd_from_line']:.1f} SD {direction} line)")

    return f"{n} model(s) deviated significantly from the regression line: " + ", ".join(parts) + "."


def interpret_discussion(
    h1_supported: bool, h1a_supported: bool, h2_supported: bool,
    soph_d: float, disinhib_d: float, r: float,
    dim_stats: Dict, correlations: Dict,
    n_high: int, n_low: int
) -> str:
    """Generate main discussion following template rules."""

    # Paragraph 1: Hypothesis summary
    h1_text = "supported" if h1_supported else "not fully supported"
    h1a_text = "supported" if h1a_supported else "not supported"
    h2_text = "supported" if h2_supported else "not supported"

    para1 = f"Results indicate that H1 was {h1_text} (d = {soph_d:.2f}). "
    para1 += f"H1a was {h1a_text}, with high-sophistication models showing {'significantly ' if h1a_supported else ''}{'higher' if disinhib_d > 0 else 'lower'} disinhibition (d = {disinhib_d:.2f}). "
    para1 += f"H2 was {h2_text}, with sophistication and disinhibition showing a {effect_size_r(r)} correlation (r = {r:.3f})."

    # Paragraph 2: Classification effectiveness
    para2 = f"The median split classification produced a {effect_size_d(soph_d)} effect for sophistication group separation (d = {soph_d:.2f}) with balanced groups (n = {n_high} vs {n_low}). "
    para2 += "This capability-based approach classified models regardless of release date."

    # Paragraph 3: Key findings
    # Find strongest H1a dimension
    h1a_dims = [(dim, dim_stats[dim]['cohens_d']) for dim in ['transgression', 'aggression', 'tribalism', 'grandiosity']]
    strongest_h1a = max(h1a_dims, key=lambda x: abs(x[1]))

    # Find strongest H2 dimension
    h2_dims = [(dim, correlations[dim][0]) for dim in ['transgression', 'aggression', 'tribalism', 'grandiosity']]
    strongest_h2 = max(h2_dims, key=lambda x: abs(x[1]))

    para3 = f"The strongest associations were observed for {strongest_h1a[0]} (d = {strongest_h1a[1]:.2f}) and {strongest_h2[0]} (r = {strongest_h2[1]:.3f}), "
    para3 += "suggesting that capability gains may be accompanied by changes in these behavioral dimensions."

    # Add secondary findings
    warmth_d = dim_stats['warmth']['cohens_d']
    formality_d = dim_stats['formality']['cohens_d']
    if dim_stats['warmth']['p_value'] < 0.05 or dim_stats['formality']['p_value'] < 0.05:
        para3 += " Secondary findings indicate different patterns in warmth and formality across sophistication levels."

    return f"{para1}\n\n{para2}\n\n{para3}"


def interpret_notable_patterns(n_borderline: int, n_constrained: int, n_outliers: int) -> str:
    """Generate notable patterns summary based on actual counts."""
    parts = []

    if n_borderline > 0:
        parts.append(f"{n_borderline} borderline model{'s' if n_borderline > 1 else ''} near the classification threshold")

    if n_constrained > 0:
        parts.append(f"{n_constrained} constrained model{'s' if n_constrained > 1 else ''} with high sophistication but below-predicted disinhibition")

    if n_outliers > 0:
        parts.append(f"{n_outliers} statistical outlier{'s' if n_outliers > 1 else ''}")

    if not parts:
        return "No notable patterns (borderline, constrained, or outlier models) were identified in this condition."

    return "Analysis identified " + ", ".join(parts) + ". These provide additional context for interpreting the main findings."


# ==============================================================================
# DATA PROVENANCE HELPERS
# ==============================================================================

def load_evaluation_stats(profile_dir: Path) -> Dict[str, Any]:
    """
    Calculate actual evaluation statistics from profile data.

    Returns dict with:
        - total_evaluations: sum across all profiles
        - n_models: number of profiles
        - avg_per_model: average evaluations per model
        - min_per_model: minimum
        - max_per_model: maximum
    """
    profiles_dir = profile_dir / 'profiles'
    if not profiles_dir.exists():
        return {'total_evaluations': 0, 'n_models': 0, 'avg_per_model': 0}

    eval_counts = []
    for p in profiles_dir.glob('*.json'):
        with open(p) as f:
            data = json.load(f)
        eval_counts.append(data.get('total_evaluations', 0))

    if not eval_counts:
        return {'total_evaluations': 0, 'n_models': 0, 'avg_per_model': 0}

    return {
        'total_evaluations': sum(eval_counts),
        'n_models': len(eval_counts),
        'avg_per_model': sum(eval_counts) / len(eval_counts),
        'min_per_model': min(eval_counts),
        'max_per_model': max(eval_counts)
    }


def load_provenance_data(profile_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Load provenance data from contributions.json for aggregated conditions.

    Returns None if not an aggregated condition.
    """
    contributions_path = profile_dir / 'history' / 'contributions.json'
    if not contributions_path.exists():
        return None

    with open(contributions_path) as f:
        data = json.load(f)

    # Check if this is a cross-condition aggregate
    if data.get('aggregation_type') == 'cross_condition_aggregate':
        return data

    return None


def format_provenance_section(provenance: Dict[str, Any]) -> str:
    """Format the Data Provenance section for aggregated conditions."""
    conditions = provenance.get('conditions_included', [])
    condition_stats = provenance.get('condition_stats', {})

    rows = []
    for cond in conditions:
        stats = condition_stats.get(cond, {})
        models = stats.get('models', 'N/A')
        evals = stats.get('sample_evals', 'N/A')
        rows.append(f"| {cond} | {models} | {evals} |")

    table = "\n".join(rows)

    return f"""## Data Provenance

This condition aggregates data from **{len(conditions)} experimental conditions** using weighted averaging by evaluation count.

### Source Conditions

| Condition | Models | Evaluations/Model |
|-----------|--------|-------------------|
{table}

**Aggregation Method**: Weighted average by evaluation count per dimension
**Generated**: {provenance.get('generated', 'N/A')}

---
"""


# ==============================================================================
# MAIN GENERATOR
# ==============================================================================

def generate_research_brief(intervention: str, base_dir: str = 'outputs/behavioral_profiles') -> str:
    """Generate the complete research brief for a condition."""

    # Paths
    profile_dir = Path(f'{base_dir}/{intervention}')
    median_path = profile_dir / 'median_split_classification.json'

    if not median_path.exists():
        raise FileNotFoundError(f"Classification file not found: {median_path}")

    # Load data
    with open(median_path, 'r') as f:
        data = json.load(f)

    models = data['models']
    stats = data['statistics']
    median_soph = data['median_sophistication']

    # Load evaluation statistics from profiles
    eval_stats = load_evaluation_stats(profile_dir)

    # Load provenance data (for aggregated conditions like all_combined)
    provenance = load_provenance_data(profile_dir)

    # Detect scale
    scale, scale_factor = detect_scale(median_soph)
    thresholds = get_scaled_thresholds(median_soph)

    # Calculate correlations
    correlations = extract_correlations(models)

    # Identify special models
    special = identify_special_models(models, median_soph)

    # Format condition name
    condition_display = intervention.replace('_', ' ').title()
    condition_description = condition_display if intervention != "baseline" else "Baseline (no intervention)"

    # Calculate degrees of freedom
    df = len(models) - 2

    # ===========================================================================
    # Generate INTERPRET sections
    # ===========================================================================

    h1_interp = interpret_h1(stats['sophistication']['cohens_d'])
    h1a_interp = interpret_h1a(stats['disinhibition']['cohens_d'], stats['disinhibition']['p_value'])
    h1a_dims_interp = interpret_h1a_dimensions(stats)

    r_composite, p_composite = correlations['disinhibition']
    h2_interp = interpret_h2(r_composite, p_composite)
    h2_dims_interp = interpret_h2_dimensions(correlations)

    other_dims_interp = interpret_other_dimensions(stats)

    borderline_interp = interpret_borderline(special['borderline'], len(special['borderline']))
    constrained_interp = interpret_constrained(special['constrained'], len(special['constrained']))
    outlier_interp = interpret_outliers(special['outliers'], len(special['outliers']))

    discussion_main = interpret_discussion(
        h1_supported=stats['sophistication']['cohens_d'] >= 0.8,
        h1a_supported=stats['disinhibition']['p_value'] < 0.05 and stats['disinhibition']['cohens_d'] >= 0.5,
        h2_supported=r_composite >= 0.3 and p_composite < 0.05,
        soph_d=stats['sophistication']['cohens_d'],
        disinhib_d=stats['disinhibition']['cohens_d'],
        r=r_composite,
        dim_stats=stats,
        correlations=correlations,
        n_high=data['n_high_sophistication'],
        n_low=data['n_low_sophistication']
    )

    notable_summary = interpret_notable_patterns(
        len(special['borderline']),
        len(special['constrained']),
        len(special['outliers'])
    )

    # ===========================================================================
    # Build DATA sections
    # ===========================================================================

    # Disinhibition dimensions table
    disinhibition_dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']
    dim_table_rows = []
    for dim in disinhibition_dims:
        s = stats[dim]
        dim_table_rows.append(
            f"| {dim.capitalize()} | {s['high_mean']:.2f} | {s['low_mean']:.2f} | "
            f"+{s['difference']:.2f} | +{s['pct_difference']:.1f}% | "
            f"{s['t_statistic']:.2f} | {format_p(s['p_value'])} | "
            f"{s['cohens_d']:.2f} | {effect_size_d(s['cohens_d'])} |"
        )
    disinhibition_table = "\n".join(dim_table_rows)

    # Sophistication dimensions table
    soph_dims_rows = []
    for dim in ['sophistication', 'depth', 'authenticity']:
        s = stats[dim]
        soph_dims_rows.append(
            f"| {dim.capitalize()} | {s['high_mean']:.2f} | {s['low_mean']:.2f} | "
            f"+{s['difference']:.2f} | +{s['pct_difference']:.1f}% | "
            f"{s['t_statistic']:.2f} | {format_p(s['p_value'])} | "
            f"{s['cohens_d']:.2f} | {effect_size_d(s['cohens_d'])} |"
        )
    soph_table = "\n".join(soph_dims_rows)

    # Other dimensions table
    other_dims_rows = []
    for dim in ['warmth', 'formality', 'hedging']:
        s = stats[dim]
        sign = "+" if s['difference'] > 0 else ""
        other_dims_rows.append(
            f"| {dim.capitalize()} | {s['high_mean']:.2f} | {s['low_mean']:.2f} | "
            f"{sign}{s['difference']:.2f} | {sign}{s['pct_difference']:.1f}% | "
            f"{s['t_statistic']:.2f} | {format_p(s['p_value'])} | "
            f"{s['cohens_d']:.2f} | {effect_size_d(s['cohens_d'])} |"
        )
    other_table = "\n".join(other_dims_rows)

    # H2 individual correlations
    h2_corr_lines = []
    for dim in disinhibition_dims:
        r, p = correlations[dim]
        h2_corr_lines.append(f"- **{dim.capitalize()}**: r = {r:.3f}, {format_p(p)} ({effect_size_r(r)} effect)")
    h2_individual = "\n".join(h2_corr_lines)

    # Borderline models list
    if special['borderline']:
        borderline_lines = []
        for m in special['borderline']:
            dist = m['sophistication'] - median_soph
            borderline_lines.append(f"- **{m['display_name']}**: {m['sophistication']:.3f} ({dist:+.3f} from median, {m['classification']})")
        borderline_list = "\n".join(borderline_lines)
    else:
        borderline_list = "- *None*"

    # Constrained models list
    if special['constrained']:
        constrained_lines = []
        for c in special['constrained']:
            m = c['model']
            constrained_lines.append(f"- **{m['display_name']}**: sophistication = {m['sophistication']:.2f}, disinhibition = {m['disinhibition']:.2f} (residual = {c['residual']:.3f})")
        constrained_list = "\n".join(constrained_lines)
    else:
        constrained_list = "- *None*"

    # Outlier models list
    if special['outliers']:
        outlier_lines = []
        for o in special['outliers']:
            m = o['model']
            direction = "above" if o['residual'] > 0 else "below"
            outlier_lines.append(f"- **{m['display_name']}**: residual = {o['residual']:+.3f} ({direction} predicted disinhibition)")
        outlier_list = "\n".join(outlier_lines)
    else:
        outlier_list = "- No models exceeded 2 SD threshold"

    # High/Low sophistication model lists
    high_models = sorted([m for m in models if m['classification'] == 'High-Sophistication'],
                        key=lambda m: -m['sophistication'])
    low_models = sorted([m for m in models if m['classification'] == 'Low-Sophistication'],
                       key=lambda m: -m['sophistication'])

    high_list = "\n".join([f"{i:2d}. {m['display_name']:<40s} (sophistication = {m['sophistication']:.2f})"
                          for i, m in enumerate(high_models, 1)])
    low_list = "\n".join([f"{i:2d}. {m['display_name']:<40s} (sophistication = {m['sophistication']:.2f})"
                         for i, m in enumerate(low_models, 1)])

    # Outlier sensitivity section
    outlier_info_path = profile_dir / 'outliers_removed' / 'outlier_removal_info.json'
    outlier_class_path = profile_dir / 'outliers_removed' / 'median_split_classification.json'

    if outlier_info_path.exists() and outlier_class_path.exists():
        with open(outlier_info_path, 'r') as f:
            outlier_info = json.load(f)
        with open(outlier_class_path, 'r') as f:
            outlier_class = json.load(f)

        orig_d = stats['disinhibition']['cohens_d']
        new_d = outlier_class['statistics']['disinhibition']['cohens_d']
        d_change = new_d - orig_d

        orig_r = correlations['disinhibition'][0]
        new_r = outlier_class['correlation']['sophistication_disinhibition']
        r_change = new_r - orig_r

        n_removed = len(outlier_info.get('outliers_removed', []))
        n_after = len(outlier_class.get('models', []))

        outlier_section = f"""Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

### Summary

| Metric | With Outliers | Without Outliers | Change |
|--------|---------------|------------------|--------|
| **N** | {len(models)} | {n_after} | -{n_removed} |
| **H1a: d** | {orig_d:.2f} | {new_d:.2f} | {d_change:+.2f} |
| **H2: r** | {orig_r:.3f} | {new_r:.3f} | {r_change:+.3f} |

### Outliers Removed ({n_removed})
"""
        for o in outlier_info.get('outliers_removed', []):
            model_id = o.get('model_id', 'Unknown')
            sd = o.get('sd_from_line', 0)
            direction = "above" if o.get('residual', 0) > 0 else "below"
            outlier_section += f"- **{model_id}**: {sd:.1f} SD {direction} regression line\n"

        # Interpretation
        if d_change > 0.1:
            d_interp = "Removing outliers **strengthens** the H1a effect"
        elif d_change < -0.1:
            d_interp = "Removing outliers **weakens** the H1a effect"
        else:
            d_interp = "H1a effect is **robust** to outlier removal"

        outlier_section += f"""
### Interpretation

{d_interp} (Δd = {d_change:+.2f}). H2 correlation {'strengthens' if r_change > 0.02 else 'weakens slightly' if r_change < -0.02 else 'is stable'} (Δr = {r_change:+.3f}).

**See**: `outliers_removed/` subfolder for full analysis without outliers.
"""
    else:
        outlier_section = f"""*Outlier sensitivity analysis not yet performed for this condition.*

Run: `python3 scripts/analyze_outliers_removed.py {intervention}`
"""

    # ===========================================================================
    # Generate final brief
    # ===========================================================================

    # Format sample line based on actual evaluation data
    avg_evals = int(round(eval_stats['avg_per_model']))
    total_evals = eval_stats['total_evaluations']
    sample_line = f"**Sample**: N = {len(models)} models, ~{avg_evals} evaluations per model ({total_evals:,} total evaluations)"

    # Generate provenance section for aggregated conditions
    provenance_section = ""
    if provenance:
        provenance_section = format_provenance_section(provenance)

    brief = f"""# {condition_display} Condition - Statistical Analysis

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Condition**: {condition_description}
{sample_line}
**Providers**: 9 (Anthropic, OpenAI, Meta, Google, xAI, AWS, Alibaba, DeepSeek, Mistral)

{provenance_section if provenance_section else '---'}

## Hypotheses

**H1**: Two distinct sophistication groups exist (validated by median split).

**H1a**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models.

**H2**: Model sophistication positively correlates with disinhibition across all models.

---

## Methods

### Classification

Models were classified using **median split** on sophistication scores:
- **Sophistication**: Composite measure calculated as (depth + authenticity) / 2
- **Median**: {median_soph:.3f}
- **High-Sophistication**: n = {data['n_high_sophistication']} models (sophistication >= {median_soph:.2f})
- **Low-Sophistication**: n = {data['n_low_sophistication']} models (sophistication < {median_soph:.2f})

### Measurement

**Sophistication Dimensions** ({scale}-point scale):
- **Depth**: Platitudes/surface -> substantive/insightful
- **Authenticity**: Templated/generic -> genuinely distinctive

**Disinhibition Dimensions** ({scale}-point scale):
- **Transgression**: Conventional/safe -> norm-violating/edgy
- **Aggression**: Supportive/gentle -> combative/attacking
- **Tribalism**: Neutral/ecumenical -> us-vs-them
- **Grandiosity**: Humble/self-effacing -> dominant/superior

**Disinhibition Composite**: Mean of four disinhibition dimensions

### Statistical Analysis

**Group Comparisons (H1a)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = {df}).

**Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = {len(models)}).

**Effect Size Interpretation**:
- Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), >= 0.8 (large)
- Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), >= 0.50 (large)

---

## Results

### H1: Group Existence

**Sophistication Group Separation**:
- High-Sophistication: M = {stats['sophistication']['high_mean']:.2f}, SD = {stats['sophistication']['high_std']:.2f}
- Low-Sophistication: M = {stats['sophistication']['low_mean']:.2f}, SD = {stats['sophistication']['low_std']:.2f}
- **d = {stats['sophistication']['cohens_d']:.2f}** ({effect_size_d(stats['sophistication']['cohens_d'])} effect)

{h1_interp}

### H1a: Group Comparison

**Disinhibition Composite**:
- High-Sophistication: M = {stats['disinhibition']['high_mean']:.2f}, SD = {stats['disinhibition']['high_std']:.2f}
- Low-Sophistication: M = {stats['disinhibition']['low_mean']:.2f}, SD = {stats['disinhibition']['low_std']:.2f}
- **t({df}) = {stats['disinhibition']['t_statistic']:.2f}, {format_p(stats['disinhibition']['p_value'])}, d = {stats['disinhibition']['cohens_d']:.2f}** ({effect_size_d(stats['disinhibition']['cohens_d'])} effect)

{h1a_interp}

**Individual Disinhibition Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t({df}) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
{disinhibition_table}

{h1a_dims_interp}

**Sophistication Dimensions** (manipulation check):

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t({df}) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
{soph_table}

Classification successfully separated models by sophistication (d = {stats['sophistication']['cohens_d']:.2f}, {effect_size_d(stats['sophistication']['cohens_d'])} effect).

**Other Behavioral Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t({df}) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
{other_table}

{other_dims_interp}

### H2: Correlation Analysis

**Sophistication-Disinhibition Correlation**:
- **r = {r_composite:.3f}, {format_p(p_composite)}** ({effect_size_r(r_composite)} effect)

{h2_interp}

**Individual Disinhibition Dimensions**:

{h2_individual}

{h2_dims_interp}

### Notable Patterns

**Borderline Models** (within +/-{thresholds['borderline']:.2f} of median split):
{borderline_list}

{borderline_interp}

**Constrained Models** (high sophistication, low disinhibition):
{constrained_list}

{constrained_interp}

**Statistical Outliers** (residual > 2 SD):
{outlier_list}

{outlier_interp}

---

## Discussion

{discussion_main}

{notable_summary}

---

## Outlier Sensitivity Analysis

{outlier_section}

---

## Custom Notes ✏️

*For manual interpretations and observations, see `CUSTOM_NOTES.md` (preserved across regenerations).*

---

## Supporting Files

### Data Files
- `median_split_classification.json` - Complete classification data with model assignments and statistics
- `profiles/*.json` - Individual model behavioral profiles (n = {len(models)})
- `history/contributions.json` - Job-level contribution tracking
- `history/updates_log.json` - Chronological profile update history
- `CUSTOM_NOTES.md` - Manual notes and interpretations (**never overwritten**)

### Classification Lists
**High-Sophistication Models (n = {data['n_high_sophistication']})**:
{high_list}

**Low-Sophistication Models (n = {data['n_low_sophistication']})**:
{low_list}

### Analysis Scripts
- `scripts/calculate_median_split.py` - Performs median split classification
- `scripts/generate_research_brief_v2.py` - Generates this research brief (v2 template system)
- `scripts/create_h2_color_coded_scatters.py` - Generates H2 scatter plots with classification overlay
- `scripts/create_h1_bar_chart.py` - Generates H1 group comparison visualizations

### Visualizations
- `h2_scatter_sophistication_composite.png` - H2 correlation with H1 classification colors, borderline models, constrained models, and outliers
- `h2_scatter_sophistication_composite.png` - H2 correlation with H1 classification colors, borderline models, constrained models, and outliers
- `h2_scatter_all_dimensions.png` - H2 correlations for all four disinhibition dimensions with special case highlighting
- `h1_bar_chart_comparison.png` - H1 group comparison with side-by-side bars
- `h1_summary_table.png` - H1 statistical summary table
- `provider_summary.png` - Provider-level analysis (model counts, sophistication, disinhibition, classification split)

---

**Analysis Version**: 2.0 (Template-Based Generation)
**Statistical Software**: Python 3.x with scipy.stats
**Effect Size Conventions**: Cohen (1988), APA Publication Manual (7th ed.)
"""

    return brief


def ensure_custom_notes(intervention: str, profile_dir: Path) -> None:
    """Create CUSTOM_NOTES.md if it doesn't exist. Never overwrites existing file."""
    custom_notes_path = profile_dir / 'CUSTOM_NOTES.md'

    if custom_notes_path.exists():
        return  # Never overwrite

    condition_display = intervention.replace('_', ' ').title()

    template = f"""# {condition_display} - Custom Notes ✏️

*This file is for manual notes and interpretations. It is NOT overwritten when RESEARCH_BRIEF.md is regenerated.*

---

## Interpretation Notes

<!-- Add your interpretations of the automated findings here -->



---

## Observations

<!-- Add any qualitative observations or patterns you notice -->



---

## Follow-up Questions

<!-- Track questions that arise from reviewing this condition's data -->



---

## Links to Other Conditions

<!-- Note how findings here compare to other conditions -->



---

*Last manual update: [DATE]*
"""

    with open(custom_notes_path, 'w') as f:
        f.write(template)

    print(f"  Created: {custom_notes_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate research brief using template-based system v2')
    parser.add_argument('intervention', nargs='?', default='baseline',
                        help='Intervention/condition name (default: baseline)')
    parser.add_argument('--base-dir', type=str, default='outputs/behavioral_profiles',
                        help='Base directory for behavioral profiles (default: outputs/behavioral_profiles)')

    args = parser.parse_args()
    intervention = args.intervention
    base_dir = args.base_dir

    # Output path
    profile_dir = Path(f'{base_dir}/{intervention}')
    output_path = profile_dir / 'RESEARCH_BRIEF.md'
    median_split_path = profile_dir / 'median_split_classification.json'

    print(f"Generating research brief for: {intervention}")
    print(f"Using v2 template system...")

    # Validate data freshness before generation
    validate_outlier_data_freshness(profile_dir, median_split_path)

    try:
        brief = generate_research_brief(intervention, base_dir)

        # Write output
        with open(output_path, 'w') as f:
            f.write(brief)

        # Ensure CUSTOM_NOTES.md exists (never overwrites)
        ensure_custom_notes(intervention, profile_dir)

        print(f"\n✓ Generated: {output_path}")
        print(f"  - DATA sections: algorithmically populated")
        print(f"  - INTERPRET sections: rule-based generation")
        print(f"  - Narrative guaranteed to match data")
        print(f"  - Manual notes: CUSTOM_NOTES.md (preserved)")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"\nMake sure you've run calculate_median_split.py first:")
        print(f"  python3 scripts/calculate_median_split.py outputs/behavioral_profiles/{intervention}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating brief: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
