#!/usr/bin/env python3
"""
Analyze whether certain providers show systematically more constrained behavior
(high sophistication but below-predicted disinhibition).

Statistical approach:
1. Fit overall regression: disinhibition ~ sophistication
2. Calculate residuals for each model
3. Compare mean residuals by provider (ANOVA + post-hoc)
4. Chi-square test on constrained classification proportions

Usage:
    python3 scripts/analyze_provider_constraint.py [condition]
    python3 scripts/analyze_provider_constraint.py baseline
    python3 scripts/analyze_provider_constraint.py --all
"""

import json
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from scipy import stats as scipy_stats

BASE_DIR = Path("outputs/behavioral_profiles")

# Provider mapping (model name patterns -> provider)
PROVIDER_PATTERNS = {
    "Anthropic": ["claude-", "Claude-"],
    "OpenAI": ["gpt-", "GPT-", "o3", "O3"],
    "Google": ["gemini-", "Gemini-"],
    "Meta": ["llama-", "Llama-"],
    "xAI": ["grok-", "Grok-"],
    "AWS": ["nova-", "Nova-"],
    "Mistral": ["mistral-", "Mistral-", "mixtral-", "Mixtral-"],
    "DeepSeek": ["deepseek-", "DeepSeek-"],
    "Alibaba": ["qwen", "Qwen"],
}


def get_provider(model_name: str) -> str:
    """Determine provider from model name."""
    for provider, patterns in PROVIDER_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in model_name.lower():
                return provider
    return "Other"


def load_condition_data(condition: str) -> dict:
    """Load median split classification data."""
    path = BASE_DIR / condition / "median_split_classification.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def calculate_residuals(models: list) -> list:
    """Calculate residuals from sophistication-disinhibition regression."""
    sophistication = np.array([m["sophistication"] for m in models])
    disinhibition = np.array([m["disinhibition"] for m in models])

    # Linear regression
    slope, intercept, r, p, se = scipy_stats.linregress(sophistication, disinhibition)
    predicted = slope * sophistication + intercept
    residuals = disinhibition - predicted

    # Add residuals to models
    for i, m in enumerate(models):
        m["residual"] = residuals[i]
        m["predicted"] = predicted[i]
        m["provider"] = get_provider(m["model_id"])

    return models, {"slope": slope, "intercept": intercept, "r": r, "p": p}


def analyze_by_provider(models: list) -> dict:
    """Analyze residuals by provider."""
    # Group by provider
    by_provider = defaultdict(list)
    for m in models:
        by_provider[m["provider"]].append(m)

    # Calculate stats per provider
    provider_stats = {}
    for provider, provider_models in by_provider.items():
        residuals = [m["residual"] for m in provider_models]
        sophistication = [m["sophistication"] for m in provider_models]
        disinhibition = [m["disinhibition"] for m in provider_models]

        # Count constrained (high soph, negative residual)
        constrained = sum(1 for m in provider_models
                        if m["sophistication"] > 6.5 and m["residual"] < -0.15)

        provider_stats[provider] = {
            "n": len(provider_models),
            "mean_residual": np.mean(residuals),
            "std_residual": np.std(residuals, ddof=1) if len(residuals) > 1 else 0,
            "min_residual": min(residuals),
            "max_residual": max(residuals),
            "mean_sophistication": np.mean(sophistication),
            "mean_disinhibition": np.mean(disinhibition),
            "n_constrained": constrained,
            "pct_constrained": constrained / len(provider_models) * 100 if provider_models else 0,
            "models": [m["model_id"] for m in provider_models]
        }

    return provider_stats


def run_anova(provider_stats: dict) -> dict:
    """Run one-way ANOVA on residuals by provider."""
    # Filter providers with n >= 3
    valid_providers = {p: s for p, s in provider_stats.items() if s["n"] >= 3}

    if len(valid_providers) < 2:
        return {"error": "Not enough providers with n >= 3"}

    # Get residual lists
    groups = []
    group_names = []
    for provider, prov_data in sorted(valid_providers.items()):
        # Reconstruct residuals from stats (we need the actual values)
        groups.append(prov_data.get("residual_values", []))
        group_names.append(provider)

    # ANOVA
    if all(len(g) >= 2 for g in groups):
        F, p = scipy_stats.f_oneway(*groups)

        # Effect size (eta-squared)
        # Between-group SS / Total SS
        all_residuals = [r for g in groups for r in g]
        grand_mean = np.mean(all_residuals)
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        ss_total = sum((r - grand_mean)**2 for r in all_residuals)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        return {
            "F": F,
            "p": p,
            "df_between": len(groups) - 1,
            "df_within": len(all_residuals) - len(groups),
            "eta_squared": eta_sq,
            "providers_included": group_names,
            "significant": p < 0.05
        }

    return {"error": "Insufficient data for ANOVA"}


def run_pairwise_tests(models: list, provider_stats: dict) -> list:
    """Run pairwise t-tests between providers."""
    # Group residuals by provider
    residuals_by_provider = defaultdict(list)
    for m in models:
        residuals_by_provider[m["provider"]].append(m["residual"])

    # Filter providers with n >= 3
    valid = {p: r for p, r in residuals_by_provider.items() if len(r) >= 3}

    results = []
    providers = sorted(valid.keys())
    n_comparisons = len(providers) * (len(providers) - 1) // 2

    for i, p1 in enumerate(providers):
        for p2 in providers[i+1:]:
            t, p = scipy_stats.ttest_ind(valid[p1], valid[p2])
            d = (np.mean(valid[p1]) - np.mean(valid[p2])) / np.sqrt(
                ((len(valid[p1])-1)*np.var(valid[p1], ddof=1) +
                 (len(valid[p2])-1)*np.var(valid[p2], ddof=1)) /
                (len(valid[p1]) + len(valid[p2]) - 2)
            ) if np.var(valid[p1], ddof=1) + np.var(valid[p2], ddof=1) > 0 else 0

            results.append({
                "comparison": f"{p1} vs {p2}",
                "provider_1": p1,
                "provider_2": p2,
                "mean_1": np.mean(valid[p1]),
                "mean_2": np.mean(valid[p2]),
                "n_1": len(valid[p1]),
                "n_2": len(valid[p2]),
                "t": t,
                "p": p,
                "p_bonferroni": min(p * n_comparisons, 1.0),
                "cohens_d": d,
                "significant_bonferroni": p * n_comparisons < 0.05,
                "direction": "more_constrained" if np.mean(valid[p1]) < np.mean(valid[p2]) else "less_constrained"
            })

    return sorted(results, key=lambda x: x["p"])


def run_chi_square(provider_stats: dict) -> dict:
    """Chi-square test on constrained vs non-constrained proportions."""
    # Build contingency table
    providers = [p for p, s in provider_stats.items() if s["n"] >= 3]

    if len(providers) < 2:
        return {"error": "Not enough providers"}

    # Constrained vs not constrained
    constrained = []
    not_constrained = []

    for p in providers:
        s = provider_stats[p]
        constrained.append(s["n_constrained"])
        not_constrained.append(s["n"] - s["n_constrained"])

    contingency = np.array([constrained, not_constrained])

    # Check for zero rows/columns
    if np.any(np.sum(contingency, axis=1) == 0) or np.any(np.sum(contingency, axis=0) == 0):
        return {
            "test": "skipped",
            "error": "Zero row or column in contingency table",
            "significant": False,
            "contingency_table": {
                "providers": providers,
                "constrained": constrained,
                "not_constrained": not_constrained
            }
        }

    # Chi-square (or Fisher's exact if expected counts low)
    if np.min(contingency) < 5:
        # Use Fisher's exact for 2x2, otherwise chi-square with warning
        if len(providers) == 2:
            odds, p = scipy_stats.fisher_exact(contingency.T)
            return {
                "test": "fisher_exact",
                "odds_ratio": odds,
                "p": p,
                "significant": p < 0.05,
                "warning": "Small expected counts"
            }

    try:
        chi2, p, dof, expected = scipy_stats.chi2_contingency(contingency)
    except ValueError as e:
        return {
            "test": "skipped",
            "error": str(e),
            "significant": False
        }

    return {
        "test": "chi_square",
        "chi2": chi2,
        "p": p,
        "dof": dof,
        "significant": p < 0.05,
        "contingency_table": {
            "providers": providers,
            "constrained": constrained,
            "not_constrained": not_constrained
        }
    }


def analyze_condition(condition: str) -> dict:
    """Run full provider constraint analysis for a condition."""
    data = load_condition_data(condition)
    if not data:
        return None

    models = data.get("models", [])
    if len(models) < 10:
        return None

    # Calculate residuals
    models, regression = calculate_residuals(models)

    # Analyze by provider
    provider_stats = analyze_by_provider(models)

    # Store residual values for ANOVA
    residuals_by_provider = defaultdict(list)
    for m in models:
        residuals_by_provider[m["provider"]].append(m["residual"])
    for p in provider_stats:
        provider_stats[p]["residual_values"] = residuals_by_provider[p]

    # Statistical tests
    anova = run_anova(provider_stats)
    pairwise = run_pairwise_tests(models, provider_stats)
    chi_sq = run_chi_square(provider_stats)

    # Remove residual_values from output (too verbose)
    for p in provider_stats:
        del provider_stats[p]["residual_values"]

    return {
        "condition": condition,
        "n_models": len(models),
        "regression": regression,
        "provider_stats": provider_stats,
        "anova": anova,
        "pairwise_comparisons": pairwise,
        "chi_square": chi_sq,
        "generated": datetime.now().isoformat()
    }


def print_results(results: dict):
    """Print analysis results."""
    print(f"\n{'='*70}")
    print(f"Provider Constraint Analysis: {results['condition']}")
    print(f"{'='*70}")
    print(f"N = {results['n_models']} models")
    print(f"Regression: disinhibition = {results['regression']['slope']:.3f} × sophistication + {results['regression']['intercept']:.3f}")
    print(f"           r = {results['regression']['r']:.3f}, p = {results['regression']['p']:.4f}")

    # Provider stats sorted by mean residual
    print(f"\n{'─'*70}")
    print("Provider Statistics (sorted by mean residual, negative = more constrained)")
    print(f"{'─'*70}")
    print(f"{'Provider':<12} {'N':>4} {'Mean Resid':>11} {'Constrained':>12} {'Mean Soph':>10} {'Mean Dis':>10}")
    print(f"{'─'*70}")

    sorted_providers = sorted(results["provider_stats"].items(),
                              key=lambda x: x[1]["mean_residual"])

    for provider, stats in sorted_providers:
        print(f"{provider:<12} {stats['n']:>4} {stats['mean_residual']:>+11.3f} "
              f"{stats['n_constrained']:>5}/{stats['n']:<2} ({stats['pct_constrained']:>4.0f}%) "
              f"{stats['mean_sophistication']:>10.2f} {stats['mean_disinhibition']:>10.2f}")

    # ANOVA
    print(f"\n{'─'*70}")
    print("One-Way ANOVA: Residuals by Provider")
    print(f"{'─'*70}")
    anova = results["anova"]
    if "error" not in anova:
        print(f"F({anova['df_between']}, {anova['df_within']}) = {anova['F']:.2f}, p = {anova['p']:.4f}")
        print(f"η² = {anova['eta_squared']:.3f}")
        print(f"Significant: {'Yes' if anova['significant'] else 'No'}")
    else:
        print(f"Error: {anova['error']}")

    # Significant pairwise comparisons
    print(f"\n{'─'*70}")
    print("Pairwise Comparisons (Bonferroni corrected)")
    print(f"{'─'*70}")

    sig_pairs = [p for p in results["pairwise_comparisons"] if p["significant_bonferroni"]]
    if sig_pairs:
        for pair in sig_pairs:
            direction = "more" if pair["mean_1"] < pair["mean_2"] else "less"
            print(f"{pair['provider_1']} vs {pair['provider_2']}: "
                  f"t = {pair['t']:.2f}, p_bonf = {pair['p_bonferroni']:.4f}, d = {pair['cohens_d']:.2f}")
            print(f"  → {pair['provider_1']} is {direction} constrained than {pair['provider_2']}")
    else:
        print("No significant pairwise differences after Bonferroni correction")

    # Chi-square
    print(f"\n{'─'*70}")
    print("Chi-Square: Constrained Classification by Provider")
    print(f"{'─'*70}")
    chi = results["chi_square"]
    if "error" not in chi:
        if chi["test"] == "chi_square":
            print(f"χ²({chi['dof']}) = {chi['chi2']:.2f}, p = {chi['p']:.4f}")
        else:
            print(f"Fisher's exact: OR = {chi['odds_ratio']:.2f}, p = {chi['p']:.4f}")
        print(f"Significant: {'Yes' if chi['significant'] else 'No'}")
    else:
        print(f"Error: {chi['error']}")


def main():
    parser = argparse.ArgumentParser(description="Analyze provider constraint patterns")
    parser.add_argument("condition", nargs="?", default="baseline", help="Condition to analyze")
    parser.add_argument("--all", action="store_true", help="Analyze all conditions")
    parser.add_argument("--output-json", action="store_true", help="Save JSON results")
    args = parser.parse_args()

    conditions = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder"] if args.all else [args.condition]

    all_results = {}

    for condition in conditions:
        results = analyze_condition(condition)
        if results:
            print_results(results)
            all_results[condition] = results

            if args.output_json:
                output_dir = BASE_DIR / "research_synthesis" / "limitations" / "provider_constraint"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"provider_constraint_{condition}.json"
                with open(output_path, "w") as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"\nSaved: {output_path}")

    # Cross-condition summary if multiple
    if len(all_results) > 1:
        print(f"\n{'='*70}")
        print("Cross-Condition Summary: OpenAI Constraint Pattern")
        print(f"{'='*70}")
        print(f"{'Condition':<20} {'OpenAI Resid':>12} {'OpenAI Rank':>12} {'ANOVA p':>10}")
        print(f"{'─'*70}")

        for cond, res in all_results.items():
            openai_stats = res["provider_stats"].get("OpenAI", {})
            openai_resid = openai_stats.get("mean_residual", float("nan"))

            # Rank (1 = most constrained)
            sorted_provs = sorted(res["provider_stats"].items(),
                                  key=lambda x: x[1]["mean_residual"])
            rank = next((i+1 for i, (p, _) in enumerate(sorted_provs) if p == "OpenAI"), "N/A")

            anova_p = res["anova"].get("p", float("nan"))

            print(f"{cond:<20} {openai_resid:>+12.3f} {rank:>12} {anova_p:>10.4f}")


if __name__ == "__main__":
    main()
