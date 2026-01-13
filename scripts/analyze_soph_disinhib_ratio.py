#!/usr/bin/env python3
"""
Analyze sophistication/disinhibition ratio per model and provider.

Compares baseline vs cross-condition aggregate data.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict


def load_baseline_data(csv_path: Path) -> list[dict]:
    """Load baseline all_models_data.csv."""
    models = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Calculate disinhibition composite
            disinhib = (
                float(row['transgression']) +
                float(row['aggression']) +
                float(row['tribalism']) +
                float(row['grandiosity'])
            ) / 4

            models.append({
                'model': row['model'],
                'provider': row['provider'],
                'sophistication': float(row['sophistication']),
                'disinhibition': disinhib,
                'n_evaluations': int(row['n_evaluations']),
            })
    return models


def load_aggregate_profiles(profiles_dir: Path) -> list[dict]:
    """Load cross-condition aggregate profiles."""
    models = []

    # Provider mapping based on model name patterns
    def get_provider(model_id: str) -> str:
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
        elif 'qwen' in model_lower:
            return 'Alibaba'
        elif 'deepseek' in model_lower:
            return 'DeepSeek'
        else:
            return 'Other'

    for profile_path in profiles_dir.glob('*.json'):
        with open(profile_path) as f:
            data = json.load(f)

        dims = data.get('dimensions', {})
        if not dims:
            continue

        # Extract averages from nested dimension structure
        def get_dim_avg(dim_name, default=5):
            dim_data = dims.get(dim_name, {})
            if isinstance(dim_data, dict):
                return dim_data.get('average', default)
            return dim_data if dim_data else default

        # Calculate composites
        depth = get_dim_avg('depth', 5)
        authenticity = get_dim_avg('authenticity', 5)
        sophistication = (depth + authenticity) / 2

        transgression = get_dim_avg('transgression', 1)
        aggression = get_dim_avg('aggression', 1)
        tribalism = get_dim_avg('tribalism', 1)
        grandiosity = get_dim_avg('grandiosity', 1)
        disinhibition = (transgression + aggression + tribalism + grandiosity) / 4

        models.append({
            'model': data.get('model_id', profile_path.stem),
            'provider': get_provider(data.get('model_id', profile_path.stem)),
            'sophistication': sophistication,
            'disinhibition': disinhibition,
            'n_evaluations': data.get('evaluation_count', 0),
        })

    return models


def calculate_ratios(models: list[dict]) -> tuple[list[dict], dict]:
    """Calculate soph/disinhib ratio for models and providers."""

    # Model-level ratios
    model_ratios = []
    for m in models:
        ratio = m['sophistication'] / m['disinhibition'] if m['disinhibition'] > 0 else 0
        model_ratios.append({
            'model': m['model'],
            'provider': m['provider'],
            'sophistication': m['sophistication'],
            'disinhibition': m['disinhibition'],
            'ratio': ratio,
            'n_evaluations': m['n_evaluations'],
        })

    # Sort by ratio descending
    model_ratios.sort(key=lambda x: x['ratio'], reverse=True)

    # Provider-level aggregation
    provider_data = defaultdict(lambda: {'soph_sum': 0, 'disinhib_sum': 0, 'count': 0, 'n_evals': 0})
    for m in models:
        p = m['provider']
        provider_data[p]['soph_sum'] += m['sophistication']
        provider_data[p]['disinhib_sum'] += m['disinhibition']
        provider_data[p]['count'] += 1
        provider_data[p]['n_evals'] += m['n_evaluations']

    provider_ratios = {}
    for provider, data in provider_data.items():
        avg_soph = data['soph_sum'] / data['count']
        avg_disinhib = data['disinhib_sum'] / data['count']
        ratio = avg_soph / avg_disinhib if avg_disinhib > 0 else 0
        provider_ratios[provider] = {
            'avg_sophistication': avg_soph,
            'avg_disinhibition': avg_disinhib,
            'ratio': ratio,
            'n_models': data['count'],
            'n_evaluations': data['n_evals'],
        }

    return model_ratios, provider_ratios


def generate_markdown_report(
    baseline_models: list[dict],
    baseline_providers: dict,
    aggregate_models: list[dict],
    aggregate_providers: dict,
    output_path: Path,
):
    """Generate markdown report with side-by-side comparison."""

    lines = [
        "# Sophistication / Disinhibition Ratio Analysis",
        "",
        "**Generated**: 2026-01-12",
        "**Purpose**: Measure capability-to-risk ratio across models and providers",
        "",
        "> **Interpretation**: Higher ratio = more sophistication per unit disinhibition (more \"constrained\" behavior relative to capability)",
        "",
        "---",
        "",
        "## Provider Summary (Side-by-Side)",
        "",
        "| Provider | Baseline Ratio | Aggregate Ratio | Δ | Baseline Soph | Agg Soph | Baseline Dis | Agg Dis | N (Baseline) |",
        "|----------|---------------|-----------------|---|---------------|----------|--------------|---------|--------------|",
    ]

    # Get all providers
    all_providers = sorted(set(baseline_providers.keys()) | set(aggregate_providers.keys()))

    for provider in all_providers:
        b = baseline_providers.get(provider, {})
        a = aggregate_providers.get(provider, {})

        b_ratio = b.get('ratio', 0)
        a_ratio = a.get('ratio', 0)
        delta = a_ratio - b_ratio if b_ratio and a_ratio else 0

        b_soph = b.get('avg_sophistication', 0)
        a_soph = a.get('avg_sophistication', 0)
        b_dis = b.get('avg_disinhibition', 0)
        a_dis = a.get('avg_disinhibition', 0)
        n = b.get('n_models', 0)

        delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"

        lines.append(
            f"| {provider} | {b_ratio:.2f} | {a_ratio:.2f} | {delta_str} | "
            f"{b_soph:.2f} | {a_soph:.2f} | {b_dis:.2f} | {a_dis:.2f} | {n} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Model Rankings: Baseline",
        "",
        "### Top 10 (Highest Ratio - Most Constrained)",
        "",
        "| Rank | Model | Provider | Soph | Disinhib | Ratio |",
        "|------|-------|----------|------|----------|-------|",
    ])

    for i, m in enumerate(baseline_models[:10], 1):
        lines.append(
            f"| {i} | {m['model']} | {m['provider']} | "
            f"{m['sophistication']:.2f} | {m['disinhibition']:.2f} | **{m['ratio']:.2f}** |"
        )

    lines.extend([
        "",
        "### Bottom 10 (Lowest Ratio - Least Constrained)",
        "",
        "| Rank | Model | Provider | Soph | Disinhib | Ratio |",
        "|------|-------|----------|------|----------|-------|",
    ])

    for i, m in enumerate(baseline_models[-10:][::-1], 1):
        rank = len(baseline_models) - i + 1
        lines.append(
            f"| {rank} | {m['model']} | {m['provider']} | "
            f"{m['sophistication']:.2f} | {m['disinhibition']:.2f} | **{m['ratio']:.2f}** |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Model Rankings: Cross-Condition Aggregate",
        "",
        "### Top 10 (Highest Ratio - Most Constrained)",
        "",
        "| Rank | Model | Provider | Soph | Disinhib | Ratio |",
        "|------|-------|----------|------|----------|-------|",
    ])

    for i, m in enumerate(aggregate_models[:10], 1):
        lines.append(
            f"| {i} | {m['model']} | {m['provider']} | "
            f"{m['sophistication']:.2f} | {m['disinhibition']:.2f} | **{m['ratio']:.2f}** |"
        )

    lines.extend([
        "",
        "### Bottom 10 (Lowest Ratio - Least Constrained)",
        "",
        "| Rank | Model | Provider | Soph | Disinhib | Ratio |",
        "|------|-------|----------|------|----------|-------|",
    ])

    for i, m in enumerate(aggregate_models[-10:][::-1], 1):
        rank = len(aggregate_models) - i + 1
        lines.append(
            f"| {rank} | {m['model']} | {m['provider']} | "
            f"{m['sophistication']:.2f} | {m['disinhibition']:.2f} | **{m['ratio']:.2f}** |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Full Model Table (Baseline)",
        "",
        "| Model | Provider | Sophistication | Disinhibition | Ratio |",
        "|-------|----------|----------------|---------------|-------|",
    ])

    for m in baseline_models:
        lines.append(
            f"| {m['model']} | {m['provider']} | "
            f"{m['sophistication']:.3f} | {m['disinhibition']:.3f} | {m['ratio']:.3f} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Methodology",
        "",
        "- **Sophistication**: (depth + authenticity) / 2",
        "- **Disinhibition**: (transgression + aggression + tribalism + grandiosity) / 4",
        "- **Ratio**: sophistication / disinhibition",
        "",
        "### Interpretation",
        "",
        "| Ratio Range | Interpretation |",
        "|-------------|----------------|",
        "| > 5.0 | Highly constrained (high capability, very low disinhibition) |",
        "| 4.0 - 5.0 | Moderately constrained |",
        "| 3.5 - 4.0 | Balanced |",
        "| 3.0 - 3.5 | Moderately unconstrained |",
        "| < 3.0 | Least constrained (capability tracks disinhibition) |",
        "",
        "---",
        "",
        "## Data Sources",
        "",
        "- **Baseline**: `baseline/all_models_data.csv`",
        "- **Aggregate**: `profiles/*.json` (cross-condition weighted average)",
        "",
    ])

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Saved: {output_path}")


def save_json_artifact(
    baseline_models: list[dict],
    baseline_providers: dict,
    aggregate_models: list[dict],
    aggregate_providers: dict,
    output_path: Path,
):
    """Save JSON data artifact."""

    artifact = {
        "generated": "2026-01-12",
        "baseline": {
            "models": baseline_models,
            "providers": baseline_providers,
        },
        "aggregate": {
            "models": aggregate_models,
            "providers": aggregate_providers,
        },
    }

    with open(output_path, 'w') as f:
        json.dump(artifact, f, indent=2)

    print(f"Saved: {output_path}")


def main():
    base_dir = Path(__file__).parent.parent

    # Load data
    print("Loading baseline data...")
    baseline_csv = base_dir / "outputs/behavioral_profiles/baseline/all_models_data.csv"
    baseline_data = load_baseline_data(baseline_csv)

    print("Loading aggregate profiles...")
    profiles_dir = base_dir / "outputs/behavioral_profiles/profiles"
    aggregate_data = load_aggregate_profiles(profiles_dir)

    # Calculate ratios
    print("Calculating ratios...")
    baseline_models, baseline_providers = calculate_ratios(baseline_data)
    aggregate_models, aggregate_providers = calculate_ratios(aggregate_data)

    # Output directory
    output_dir = base_dir / "outputs/behavioral_profiles/research_synthesis/limitations/provider_constraint"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate reports
    print("Generating reports...")
    generate_markdown_report(
        baseline_models, baseline_providers,
        aggregate_models, aggregate_providers,
        output_dir / "SOPH_DISINHIB_RATIO_ANALYSIS.md"
    )

    save_json_artifact(
        baseline_models, baseline_providers,
        aggregate_models, aggregate_providers,
        output_dir / "soph_disinhib_ratio.json"
    )

    # Print summary
    print("\n" + "=" * 60)
    print("PROVIDER SUMMARY (Baseline)")
    print("=" * 60)
    for provider in sorted(baseline_providers.keys()):
        p = baseline_providers[provider]
        print(f"{provider:12} | Ratio: {p['ratio']:.2f} | Soph: {p['avg_sophistication']:.2f} | Dis: {p['avg_disinhibition']:.2f} | N: {p['n_models']}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
