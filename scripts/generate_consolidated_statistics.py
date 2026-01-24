#!/usr/bin/env python3
"""
Generate CONSOLIDATED_STATISTICS.md from all source JSON files.

Produces a single document with all hard statistics across conditions.
No narrative, no insights - just numbers with labels.

Usage:
    python3 scripts/generate_consolidated_statistics.py

Output:
    outputs/behavioral_profiles/research_synthesis/CONSOLIDATED_STATISTICS.md
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Paths
BASE_DIR = Path("outputs/behavioral_profiles")
RESEARCH_DIR = BASE_DIR / "research_synthesis"
OUTPUT_FILE = RESEARCH_DIR / "CONSOLIDATED_STATISTICS.md"

# Conditions to include
CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder", "naturalistic"]
CONDITIONS_WITH_ALL = CONDITIONS + ["all_combined"]

# Sections that should include all_combined
# H1/H2, Outliers, Dimension means, Provider counts, Composite ranges all have all_combined data


def load_json(path: Path) -> Optional[dict]:
    """Load JSON file, return None if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def fmt_p(p: float) -> str:
    """Format p-value."""
    if p < 0.0001:
        return f"{p:.2e}"
    return f"{p:.4f}"


def fmt_r(r: float) -> str:
    """Format correlation coefficient."""
    return f"{r:.3f}"


def fmt_d(d: float) -> str:
    """Format Cohen's d."""
    import math
    if math.isnan(d):
        return "N/A"
    return f"{d:.2f}"


def fmt_float(f: float, decimals: int = 3) -> str:
    """Format float, handling NaN."""
    import math
    if math.isnan(f):
        return "N/A"
    return f"{f:.{decimals}f}"


def gather_global_summary() -> dict:
    """Gather global summary statistics."""
    summary = {
        "n_conditions": len(CONDITIONS_WITH_ALL),
        "condition_names": CONDITIONS_WITH_ALL,
        "total_models": 0,
        "total_evaluations": 0,
        "total_bert_evaluations": 0,
        "unique_providers": set(),
        "models_per_condition": {}
    }

    # Count from median_split files (all conditions including all_combined)
    for cond in CONDITIONS_WITH_ALL:
        ms_path = BASE_DIR / cond / "median_split_classification.json"
        data = load_json(ms_path)
        if data:
            n = data.get("n_high_sophistication", 0) + data.get("n_low_sophistication", 0)
            summary["models_per_condition"][cond] = n
            if n > summary["total_models"]:
                summary["total_models"] = n  # Max across conditions

    # Count evaluations from judge_agreement (individual conditions only, not all_combined to avoid double-counting)
    for cond in CONDITIONS:
        ja_path = BASE_DIR / cond / "judge_agreement" / "judge_agreement_audit.json"
        data = load_json(ja_path)
        if data:
            n_evals = data.get("summary", {}).get("n_evaluations", 0)
            summary["total_evaluations"] += n_evals

    # BERT evaluations - sum from per-condition results (not all_combined to match judge counting)
    for cond in CONDITIONS:
        bert_path = RESEARCH_DIR / "bert_validation" / cond / "bert_validation_results.json"
        data = load_json(bert_path)
        if data:
            # Sum n_scored from each model's results
            n_bert = sum(m.get("n_scored", m.get("n_responses", 0)) for m in data.get("model_results", []))
            summary["total_bert_evaluations"] += n_bert

    # Providers from baseline comprehensive_stats
    cs_path = BASE_DIR / "baseline" / "comprehensive_stats.json"
    data = load_json(cs_path)
    if data and "by_provider" in data:
        summary["unique_providers"] = set(data["by_provider"].keys())

    return summary


def gather_h1h2_core() -> list[dict]:
    """Gather H1/H2 core statistics from median_split_classification.json."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        path = BASE_DIR / cond / "median_split_classification.json"
        data = load_json(path)
        if not data:
            continue

        n_high = data.get("n_high_sophistication", 0)
        n_low = data.get("n_low_sophistication", 0)
        n = n_high + n_low

        stats = data.get("statistics", {}).get("disinhibition", {})
        corr = data.get("correlation", {}).get("sophistication_disinhibition", 0)
        # corr might be a float directly or a dict with "r" key
        h2_r = corr if isinstance(corr, (int, float)) else corr.get("r", 0)

        results.append({
            "condition": cond,
            "n": n,
            "median_soph": data.get("median_sophistication", 0),
            "n_high": n_high,
            "n_low": n_low,
            "h1_d": stats.get("cohens_d", 0),
            "h1_p": stats.get("p_value", 1),
            "h2_r": h2_r
        })
    return results


def gather_h1h2_outliers_removed() -> list[dict]:
    """Gather H1/H2 statistics with outliers removed."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        # Get original N
        orig_path = BASE_DIR / cond / "median_split_classification.json"
        orig_data = load_json(orig_path)
        n_orig = 0
        if orig_data:
            n_orig = orig_data.get("n_high_sophistication", 0) + orig_data.get("n_low_sophistication", 0)

        # Get outliers removed
        or_path = BASE_DIR / cond / "outliers_removed" / "median_split_classification.json"
        data = load_json(or_path)
        if not data:
            continue

        n_high = data.get("n_high_sophistication", 0)
        n_low = data.get("n_low_sophistication", 0)
        n_final = n_high + n_low

        stats = data.get("statistics", {}).get("disinhibition", {})
        corr = data.get("correlation", {}).get("sophistication_disinhibition", 0)
        h2_r = corr if isinstance(corr, (int, float)) else corr.get("r", 0)

        results.append({
            "condition": cond,
            "n_orig": n_orig,
            "n_removed": n_orig - n_final,
            "n_final": n_final,
            "h1_d": stats.get("cohens_d", 0),
            "h1_p": stats.get("p_value", 1),
            "h2_r": h2_r
        })
    return results


def gather_bert_validation() -> list[dict]:
    """Gather BERT validation statistics (toxicity vs aggression)."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        path = RESEARCH_DIR / "bert_validation" / cond / "bert_validation_results.json"
        data = load_json(path)
        if not data:
            continue

        meta = data.get("metadata", {})
        corr = data.get("correlations", {})
        model_results = data.get("model_results", [])

        # Get evaluation count - try metadata first, then sum from model_results
        n_evals = meta.get("total_evaluations", 0)
        if not n_evals and model_results:
            n_evals = sum(m.get("n_scored", m.get("n_responses", 0)) for m in model_results)

        results.append({
            "condition": cond,
            "n": len(model_results) or meta.get("n_models", 0),
            "evaluations": n_evals,
            "r_tox": corr.get("toxicity", {}).get("r", 0),
            "p_tox": corr.get("toxicity", {}).get("p", 1),
            "r_ins": corr.get("insult", {}).get("r", 0),
            "p_ins": corr.get("insult", {}).get("p", 1)
        })
    return results


def gather_bert_outliers_removed() -> list[dict]:
    """Gather BERT validation (toxicity vs aggression) with outliers removed."""
    results = []
    # Include baseline, naturalistic, and all_combined
    for cond in ["baseline", "naturalistic", "all_combined"]:
        # Try condition-specific outliers_removed folder first
        path = BASE_DIR / cond / "outliers_removed" / "bert_validation_outliers_removed_audit.json"
        data = load_json(path)
        if not data:
            continue

        sample = data.get("sample", {})
        corr = data.get("correlations", {})

        results.append({
            "condition": cond,
            "n": sample.get("n_final", 0),
            "n_removed": sample.get("n_removed", 0),
            "r_tox": corr.get("toxicity_vs_aggression", {}).get("r", 0),
            "p_tox": corr.get("toxicity_vs_aggression", {}).get("p", 1),
            "r_ins": corr.get("insult_vs_aggression", {}).get("r", 0),
            "p_ins": corr.get("insult_vs_aggression", {}).get("p", 1)
        })
    return results


def gather_bert_soph_disin() -> list[dict]:
    """Gather BERT vs sophistication/disinhibition correlations."""
    results = []
    for cond in CONDITIONS:
        path = RESEARCH_DIR / "bert_validation" / cond / "bert_soph_disin_results.json"
        data = load_json(path)
        if not data:
            continue

        corr = data.get("correlations", {})

        results.append({
            "condition": cond,
            "r_tox_soph": corr.get("toxicity_vs_sophistication", {}).get("r", 0),
            "p_tox_soph": corr.get("toxicity_vs_sophistication", {}).get("p", 1),
            "r_tox_disin": corr.get("toxicity_vs_disinhibition", {}).get("r", 0),
            "p_tox_disin": corr.get("toxicity_vs_disinhibition", {}).get("p", 1),
            "r_ins_soph": corr.get("insult_vs_sophistication", {}).get("r", 0),
            "p_ins_soph": corr.get("insult_vs_sophistication", {}).get("p", 1),
            "r_ins_disin": corr.get("insult_vs_disinhibition", {}).get("r", 0),
            "p_ins_disin": corr.get("insult_vs_disinhibition", {}).get("p", 1)
        })
    return results


def gather_bert_soph_disin_outliers_removed() -> list[dict]:
    """Gather BERT vs sophistication/disinhibition with outliers removed."""
    results = []
    # Include baseline, naturalistic, and all_combined
    for cond in ["baseline", "naturalistic", "all_combined"]:
        path = BASE_DIR / cond / "outliers_removed" / "bert_soph_disin_outliers_removed_audit.json"
        data = load_json(path)
        if not data:
            continue

        sample = data.get("sample", {})
        corr = data.get("correlations", {})

        results.append({
            "condition": cond,
            "n": sample.get("n_final", 0),
            "n_removed": sample.get("n_removed", 0),
            "r_tox_soph": corr.get("toxicity_vs_sophistication", {}).get("r", 0),
            "p_tox_soph": corr.get("toxicity_vs_sophistication", {}).get("p", 1),
            "r_tox_disin": corr.get("toxicity_vs_disinhibition", {}).get("r", 0),
            "p_tox_disin": corr.get("toxicity_vs_disinhibition", {}).get("p", 1),
            "r_ins_soph": corr.get("insult_vs_sophistication", {}).get("r", 0),
            "p_ins_soph": corr.get("insult_vs_sophistication", {}).get("p", 1),
            "r_ins_disin": corr.get("insult_vs_disinhibition", {}).get("r", 0),
            "p_ins_disin": corr.get("insult_vs_disinhibition", {}).get("p", 1)
        })
    return results


def gather_judge_agreement() -> list[dict]:
    """Gather judge agreement ICC values."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        path = BASE_DIR / cond / "judge_agreement" / "judge_agreement_audit.json"
        data = load_json(path)
        if not data:
            continue

        summary = data.get("summary", {})
        by_dim = data.get("by_dimension", {})

        results.append({
            "condition": cond,
            "n_evals": summary.get("n_evaluations", 0),
            "overall": data.get("overall", {}).get("icc_avg", 0),
            "warm": by_dim.get("warmth", {}).get("icc_avg", 0),
            "form": by_dim.get("formality", {}).get("icc_avg", 0),
            "hedge": by_dim.get("hedging", {}).get("icc_avg", 0),
            "aggr": by_dim.get("aggression", {}).get("icc_avg", 0),
            "trans": by_dim.get("transgression", {}).get("icc_avg", 0),
            "grand": by_dim.get("grandiosity", {}).get("icc_avg", 0),
            "trib": by_dim.get("tribalism", {}).get("icc_avg", 0),
            "depth": by_dim.get("depth", {}).get("icc_avg", 0),
            "auth": by_dim.get("authenticity", {}).get("icc_avg", 0)
        })
    return results


def gather_dimension_effect_sizes() -> list[dict]:
    """Gather per-dimension H1 effect sizes (Cohen's d)."""
    results = []

    for cond in CONDITIONS_WITH_ALL:
        path = BASE_DIR / cond / "median_split_classification.json"
        data = load_json(path)
        if not data:
            continue

        stats = data.get("statistics", {})
        row = {"condition": cond}

        # Map dimension names - note: sophistication and disinhibition (not _composite)
        dim_map = {
            "warmth": "warmth", "formality": "formality", "hedging": "hedging",
            "aggression": "aggression", "transgression": "transgression",
            "grandiosity": "grandiosity", "tribalism": "tribalism",
            "depth": "depth", "authenticity": "authenticity",
            "sophistication": "sophistication",
            "disinhibition": "disinhibition"
        }

        for dim_key, dim_short in dim_map.items():
            d_val = stats.get(dim_key, {}).get("cohens_d", 0)
            row[dim_short] = d_val

        results.append(row)
    return results


def gather_dimension_means() -> list[dict]:
    """Gather dimension means across all models."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        path = BASE_DIR / cond / "comprehensive_stats.json"
        data = load_json(path)
        if not data:
            continue

        # Calculate overall means from by_provider data
        by_provider = data.get("by_provider", {})
        row = {"condition": cond}

        dims = ["warmth", "formality", "hedging", "aggression", "transgression",
                "grandiosity", "tribalism", "depth", "authenticity"]

        for dim in dims:
            # Weighted average across providers
            total_weighted = 0
            total_n = 0
            for prov, pdata in by_provider.items():
                n = pdata.get("n", 0)
                mean = pdata.get("means", {}).get(dim, 0)
                total_weighted += n * mean
                total_n += n
            row[dim] = total_weighted / total_n if total_n > 0 else 0

        results.append(row)
    return results


def gather_provider_counts() -> list[dict]:
    """Gather model counts by provider."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        path = BASE_DIR / cond / "comprehensive_stats.json"
        data = load_json(path)
        if not data:
            continue

        by_provider = data.get("by_provider", {})
        row = {"condition": cond, "n": sum(p.get("n", 0) for p in by_provider.values())}

        # Known providers - use "n" not "count"
        for provider in ["Anthropic", "OpenAI", "Meta", "Google", "xAI", "Mistral", "DeepSeek", "Alibaba", "AWS"]:
            row[provider] = by_provider.get(provider, {}).get("n", 0)

        results.append(row)
    return results


def gather_external_validation() -> dict:
    """Gather external validation statistics."""
    result = {}

    # Triangulated analysis
    tri_path = RESEARCH_DIR / "limitations" / "external_evals" / "reasoning_composite_triangulated_audit.json"
    tri_data = load_json(tri_path)
    if tri_data:
        result["triangulated"] = {
            "approach_1": tri_data.get("approach_1_observed_only", {}),
            "approach_1b": tri_data.get("approach_1b_observed_gpqa_aime", {}),
            "approach_1c": tri_data.get("approach_1c_gpqa_alone", {}),
            "approach_2": tri_data.get("approach_2_cross_benchmark", {}),
            "approach_3": tri_data.get("approach_3_multiple_imputation", {}),
            "summary": tri_data.get("summary", {})
        }

    # Per-benchmark validations
    for benchmark in ["gpqa", "aime", "arc_agi"]:
        bm_path = RESEARCH_DIR / "limitations" / "external_evals" / f"{benchmark}_validation_analysis.json"
        bm_data = load_json(bm_path)
        if bm_data:
            result[benchmark] = bm_data

    return result


def gather_provider_anova() -> dict:
    """Gather provider ANOVA statistics (baseline only)."""
    path = BASE_DIR / "baseline" / "provider_comparison_stats.json"
    data = load_json(path)
    if not data:
        return {}

    # Keys are "disinhibition" and "sophistication" (not _composite)
    return {
        "disinhibition": data.get("disinhibition", {}).get("anova", {}),
        "sophistication": data.get("sophistication", {}).get("anova", {})
    }


def gather_provider_means() -> list[dict]:
    """Gather provider means for baseline."""
    path = BASE_DIR / "baseline" / "comprehensive_stats.json"
    data = load_json(path)
    if not data:
        return []

    results = []
    by_provider = data.get("by_provider", {})

    for provider, pdata in by_provider.items():
        # Calculate disinhibition and sophistication from individual dims
        means = pdata.get("means", {})
        stds = pdata.get("stds", {})

        # Disinhibition = avg(aggression, transgression, grandiosity, tribalism)
        disin_dims = ["aggression", "transgression", "grandiosity", "tribalism"]
        disin_mean = sum(means.get(d, 0) for d in disin_dims) / len(disin_dims)
        disin_sd = sum(stds.get(d, 0) for d in disin_dims) / len(disin_dims)  # Approximation

        # Sophistication = avg(depth, authenticity)
        soph_dims = ["depth", "authenticity"]
        soph_mean = sum(means.get(d, 0) for d in soph_dims) / len(soph_dims)
        soph_sd = sum(stds.get(d, 0) for d in soph_dims) / len(soph_dims)  # Approximation

        results.append({
            "provider": provider,
            "n": pdata.get("n", 0),
            "disin_mean": disin_mean,
            "disin_sd": disin_sd,
            "soph_mean": soph_mean,
            "soph_sd": soph_sd
        })

    # Sort by disinhibition mean descending
    results.sort(key=lambda x: x["disin_mean"], reverse=True)
    return results


def gather_composite_ranges() -> list[dict]:
    """Gather composite score ranges per condition."""
    results = []
    for cond in CONDITIONS_WITH_ALL:
        path = BASE_DIR / cond / "median_split_classification.json"
        data = load_json(path)
        if not data:
            continue

        models = data.get("models", [])
        if not models:
            continue

        # Try multiple key names for composites
        soph_vals = []
        disin_vals = []
        for m in models:
            # Try different possible key names
            soph = m.get("sophistication_composite") or m.get("sophistication", 0)
            disin = m.get("disinhibition_composite") or m.get("disinhibition", 0)
            if soph:
                soph_vals.append(soph)
            if disin:
                disin_vals.append(disin)

        if soph_vals and disin_vals:
            results.append({
                "condition": cond,
                "soph_min": min(soph_vals),
                "soph_max": max(soph_vals),
                "disin_min": min(disin_vals),
                "disin_max": max(disin_vals)
            })
    return results


def generate_markdown() -> str:
    """Generate the full markdown document."""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d")

    # Header
    lines.append("# CONSOLIDATED STATISTICS")
    lines.append(f"Generated: {now}")
    lines.append("")

    # === SECTION 0: GLOBAL SUMMARY ===
    summary = gather_global_summary()
    lines.append("---")
    lines.append("")
    lines.append("## 0. GLOBAL SUMMARY")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Conditions | {summary['n_conditions']} |")
    lines.append(f"| Condition Names | {', '.join(summary['condition_names'])} |")
    lines.append(f"| Models (max per condition) | {summary['total_models']} |")
    lines.append(f"| Total Judge Evaluations | {summary['total_evaluations']:,} |")
    lines.append(f"| Total BERT Evaluations | {summary['total_bert_evaluations']:,} |")
    lines.append(f"| Unique Providers | {len(summary['unique_providers'])} ({', '.join(sorted(summary['unique_providers']))}) |")
    lines.append("")

    # === SECTION 1: H1/H2 CORE ===
    lines.append("---")
    lines.append("")
    lines.append("## 1. H1/H2 CORE STATISTICS")
    lines.append("")
    lines.append("| Condition | N | Median_Soph | N_High | N_Low | H1_d | H1_p | H2_r |")
    lines.append("|-----------|---|-------------|--------|-------|------|------|------|")
    for row in gather_h1h2_core():
        lines.append(f"| {row['condition']} | {row['n']} | {row['median_soph']:.3f} | {row['n_high']} | {row['n_low']} | {fmt_d(row['h1_d'])} | {fmt_p(row['h1_p'])} | {fmt_r(row['h2_r'])} |")
    lines.append("")

    # === SECTION 2: H1/H2 OUTLIERS REMOVED ===
    lines.append("---")
    lines.append("")
    lines.append("## 2. H1/H2 OUTLIERS REMOVED")
    lines.append("")
    lines.append("| Condition | N_Orig | N_Removed | N_Final | H1_d | H1_p | H2_r |")
    lines.append("|-----------|--------|-----------|---------|------|------|------|")
    for row in gather_h1h2_outliers_removed():
        lines.append(f"| {row['condition']} | {row['n_orig']} | {row['n_removed']} | {row['n_final']} | {fmt_d(row['h1_d'])} | {fmt_p(row['h1_p'])} | {fmt_r(row['h2_r'])} |")
    lines.append("")

    # === SECTION 3: BERT VALIDATION ===
    lines.append("---")
    lines.append("")
    lines.append("## 3. BERT VALIDATION - TOXICITY vs AGGRESSION")
    lines.append("")
    lines.append("| Condition | N | Evaluations | r_tox | p_tox | r_ins | p_ins |")
    lines.append("|-----------|---|-------------|-------|-------|-------|-------|")
    for row in gather_bert_validation():
        lines.append(f"| {row['condition']} | {row['n']} | {row['evaluations']:,} | {fmt_r(row['r_tox'])} | {fmt_p(row['p_tox'])} | {fmt_r(row['r_ins'])} | {fmt_p(row['p_ins'])} |")
    lines.append("")

    # === SECTION 4: BERT TOXICITY vs AGGRESSION - OUTLIERS REMOVED ===
    lines.append("---")
    lines.append("")
    lines.append("## 4. BERT TOXICITY vs AGGRESSION - OUTLIERS REMOVED")
    lines.append("")
    lines.append("| Condition | N | N_Removed | r_tox | p_tox | r_ins | p_ins |")
    lines.append("|-----------|---|-----------|-------|-------|-------|-------|")
    for row in gather_bert_outliers_removed():
        lines.append(f"| {row['condition']} | {row['n']} | {row['n_removed']} | {fmt_r(row['r_tox'])} | {fmt_p(row['p_tox'])} | {fmt_r(row['r_ins'])} | {fmt_p(row['p_ins'])} |")
    lines.append("")

    # === SECTION 5: BERT vs SOPH/DISIN ===
    lines.append("---")
    lines.append("")
    lines.append("## 5. BERT vs SOPHISTICATION/DISINHIBITION")
    lines.append("")
    lines.append("| Condition | r_tox_soph | p | r_tox_disin | p | r_ins_soph | p | r_ins_disin | p |")
    lines.append("|-----------|------------|---|-------------|---|------------|---|-------------|---|")
    for row in gather_bert_soph_disin():
        lines.append(f"| {row['condition']} | {fmt_r(row['r_tox_soph'])} | {fmt_p(row['p_tox_soph'])} | {fmt_r(row['r_tox_disin'])} | {fmt_p(row['p_tox_disin'])} | {fmt_r(row['r_ins_soph'])} | {fmt_p(row['p_ins_soph'])} | {fmt_r(row['r_ins_disin'])} | {fmt_p(row['p_ins_disin'])} |")
    lines.append("")

    # === SECTION 6: BERT vs SOPH/DISIN - OUTLIERS REMOVED ===
    lines.append("---")
    lines.append("")
    lines.append("## 6. BERT vs SOPHISTICATION/DISINHIBITION - OUTLIERS REMOVED")
    lines.append("")
    lines.append("| Condition | N | N_Removed | r_tox_soph | p | r_tox_disin | p | r_ins_soph | p | r_ins_disin | p |")
    lines.append("|-----------|---|-----------|------------|---|-------------|---|------------|---|-------------|---|")
    for row in gather_bert_soph_disin_outliers_removed():
        lines.append(f"| {row['condition']} | {row['n']} | {row['n_removed']} | {fmt_r(row['r_tox_soph'])} | {fmt_p(row['p_tox_soph'])} | {fmt_r(row['r_tox_disin'])} | {fmt_p(row['p_tox_disin'])} | {fmt_r(row['r_ins_soph'])} | {fmt_p(row['p_ins_soph'])} | {fmt_r(row['r_ins_disin'])} | {fmt_p(row['p_ins_disin'])} |")
    lines.append("")

    # === SECTION 7: JUDGE AGREEMENT ===
    lines.append("---")
    lines.append("")
    lines.append("## 7. JUDGE AGREEMENT - ICC(3)")
    lines.append("")
    lines.append("| Condition | N_Evals | Overall | warm | form | hedge | aggr | trans | grand | trib | depth | auth |")
    lines.append("|-----------|---------|---------|------|------|-------|------|-------|-------|------|-------|------|")
    for row in gather_judge_agreement():
        lines.append(f"| {row['condition']} | {row['n_evals']:,} | {row['overall']:.3f} | {row['warm']:.2f} | {row['form']:.2f} | {row['hedge']:.2f} | {row['aggr']:.2f} | {row['trans']:.2f} | {row['grand']:.2f} | {row['trib']:.2f} | {row['depth']:.2f} | {row['auth']:.2f} |")
    lines.append("")

    # === SECTION 8: DIMENSION EFFECT SIZES ===
    lines.append("---")
    lines.append("")
    lines.append("## 8. PER-DIMENSION H1 EFFECT SIZES (Cohen's d)")
    lines.append("")
    lines.append("| Condition | warm | form | hedge | aggr | trans | grand | trib | depth | auth | soph | disin |")
    lines.append("|-----------|------|------|-------|------|-------|-------|------|-------|------|------|-------|")
    for row in gather_dimension_effect_sizes():
        lines.append(f"| {row['condition']} | {fmt_d(row.get('warmth', 0))} | {fmt_d(row.get('formality', 0))} | {fmt_d(row.get('hedging', 0))} | {fmt_d(row.get('aggression', 0))} | {fmt_d(row.get('transgression', 0))} | {fmt_d(row.get('grandiosity', 0))} | {fmt_d(row.get('tribalism', 0))} | {fmt_d(row.get('depth', 0))} | {fmt_d(row.get('authenticity', 0))} | {fmt_d(row.get('sophistication', 0))} | {fmt_d(row.get('disinhibition', 0))} |")
    lines.append("")

    # === SECTION 9: DIMENSION MEANS ===
    lines.append("---")
    lines.append("")
    lines.append("## 9. DIMENSION MEANS (ALL MODELS)")
    lines.append("")
    lines.append("| Condition | warm | form | hedge | aggr | trans | grand | trib | depth | auth |")
    lines.append("|-----------|------|------|-------|------|-------|-------|------|-------|------|")
    for row in gather_dimension_means():
        lines.append(f"| {row['condition']} | {row.get('warmth', 0):.2f} | {row.get('formality', 0):.2f} | {row.get('hedging', 0):.2f} | {row.get('aggression', 0):.2f} | {row.get('transgression', 0):.2f} | {row.get('grandiosity', 0):.2f} | {row.get('tribalism', 0):.2f} | {row.get('depth', 0):.2f} | {row.get('authenticity', 0):.2f} |")
    lines.append("")

    # === SECTION 10: PROVIDER COUNTS ===
    lines.append("---")
    lines.append("")
    lines.append("## 10. MODEL COUNTS BY PROVIDER")
    lines.append("")
    lines.append("| Condition | N | Anthropic | OpenAI | Meta | Google | xAI | Mistral | DeepSeek | Alibaba | AWS |")
    lines.append("|-----------|---|-----------|--------|------|--------|-----|---------|----------|---------|-----|")
    for row in gather_provider_counts():
        lines.append(f"| {row['condition']} | {row['n']} | {row.get('Anthropic', 0)} | {row.get('OpenAI', 0)} | {row.get('Meta', 0)} | {row.get('Google', 0)} | {row.get('xAI', 0)} | {row.get('Mistral', 0)} | {row.get('DeepSeek', 0)} | {row.get('Alibaba', 0)} | {row.get('AWS', 0)} |")
    lines.append("")

    # === SECTION 11: EXTERNAL VALIDATION ===
    ext = gather_external_validation()
    lines.append("---")
    lines.append("")
    lines.append("## 11. EXTERNAL VALIDATION")
    lines.append("")

    # 11.1 Per-benchmark validations (most concrete, lead with this)
    lines.append("### 11.1 Per-Benchmark Correlations")
    lines.append("")
    lines.append("| Benchmark | N | r(BM→Soph) | p | r(BM→Disin) | p |")
    lines.append("|-----------|---|------------|---|-------------|---|")

    for bm_key, bm_name in [("gpqa", "GPQA"), ("aime", "AIME"), ("arc_agi", "ARC-AGI")]:
        bm_data = ext.get(bm_key, {})
        if bm_data:
            corrs = bm_data.get("correlations", {})
            # Get N from sophistication correlation or sample
            soph_corr = corrs.get("sophistication", {})
            disin_corr = corrs.get("disinhibition", {})
            n = soph_corr.get("n", bm_data.get("sample", {}).get("n_matched", "N/A"))

            r_soph = soph_corr.get("r", 0)
            p_soph = soph_corr.get("p", 1)
            r_disin = disin_corr.get("r", 0)
            p_disin = disin_corr.get("p", 1)

            lines.append(f"| {bm_name} | {n} | {fmt_r(r_soph)} | {fmt_p(p_soph)} | {fmt_r(r_disin)} | {fmt_p(p_disin)} |")
    lines.append("")

    # 11.2 Summary table of all approaches
    tri = ext.get("triangulated", {})
    if tri:
        lines.append("### 11.2 Triangulated Analysis Summary")
        lines.append("")
        lines.append("| Approach | N | r(R→D) | r(S→D) | Δr | r(R→S) | Sig |")
        lines.append("|----------|---|--------|--------|-----|--------|-----|")

        summary_table = tri.get("summary", {}).get("table", {})
        for approach_key, label in [
            ("approach_1", "3-benchmark observed"),
            ("approach_1b", "GPQA+AIME observed"),
            ("approach_1c", "GPQA only (BEST)"),
            ("approach_2", "Cross-benchmark imputed"),
            ("approach_3", "Multiple imputation")
        ]:
            row = summary_table.get(approach_key, {})
            if row:
                sig = "Yes" if row.get("significant", approach_key != "approach_1") else "No"
                lines.append(f"| {label} | {row.get('n', 'N/A')} | {fmt_r(row.get('r_RD', 0))} | {fmt_r(row.get('r_SD', 0))} | {fmt_r(row.get('delta_r', 0))} | {fmt_r(row.get('r_RS', 0))} | {sig} |")
        lines.append("")

    # 11.3 Best estimate detail (GPQA alone)
    a1c = tri.get("approach_1c", {})
    if a1c:
        lines.append("### 11.3 Best Estimate: GPQA Alone (N=35)")
        lines.append("")
        lines.append("| Correlation | r | p |")
        lines.append("|-------------|---|---|")
        for key in ["reasoning_to_disinhibition", "sophistication_to_disinhibition", "reasoning_to_sophistication"]:
            corr = a1c.get("correlations", {}).get(key, {})
            lines.append(f"| {key} | {fmt_r(corr.get('r', 0))} | {fmt_p(corr.get('p', 1))} |")
        lines.append("")

        # Range info
        rng = a1c.get("range", {})
        if rng:
            lines.append("| Variable | Min | Max | Mean |")
            lines.append("|----------|-----|-----|------|")
            for var in ["gpqa", "sophistication", "disinhibition"]:
                v = rng.get(var, {})
                lines.append(f"| {var} | {v.get('min', 0):.2f} | {v.get('max', 0):.2f} | {v.get('mean', 0):.2f} |")
            lines.append("")

    # === SECTION 12: PROVIDER ANOVA ===
    anova = gather_provider_anova()
    lines.append("---")
    lines.append("")
    lines.append("## 12. PROVIDER ANOVA (BASELINE)")
    lines.append("")

    if anova.get("disinhibition"):
        lines.append("### 12.1 Disinhibition")
        lines.append("")
        lines.append("| Statistic | Value |")
        lines.append("|-----------|-------|")
        d = anova["disinhibition"]
        lines.append(f"| F | {d.get('F', 0):.3f} |")
        lines.append(f"| p | {fmt_p(d.get('p', 1))} |")
        lines.append(f"| eta_squared | {d.get('eta_squared', 0):.3f} |")
        lines.append(f"| df_between | {d.get('df_between', 0)} |")
        lines.append(f"| df_within | {d.get('df_within', 0)} |")
        lines.append(f"| N | {d.get('N', 0)} |")
        lines.append("")

    if anova.get("sophistication"):
        lines.append("### 12.2 Sophistication")
        lines.append("")
        lines.append("| Statistic | Value |")
        lines.append("|-----------|-------|")
        s = anova["sophistication"]
        lines.append(f"| F | {s.get('F', 0):.3f} |")
        lines.append(f"| p | {fmt_p(s.get('p', 1))} |")
        lines.append(f"| eta_squared | {s.get('eta_squared', 0):.3f} |")
        lines.append(f"| df_between | {s.get('df_between', 0)} |")
        lines.append(f"| df_within | {s.get('df_within', 0)} |")
        lines.append(f"| N | {s.get('N', 0)} |")
        lines.append("")

    # === SECTION 13: PROVIDER MEANS ===
    lines.append("---")
    lines.append("")
    lines.append("## 13. PROVIDER MEANS (BASELINE)")
    lines.append("")
    lines.append("| Provider | N | Disin_Mean | Disin_SD | Soph_Mean | Soph_SD |")
    lines.append("|----------|---|------------|----------|-----------|---------|\n")
    for row in gather_provider_means():
        lines.append(f"| {row['provider']} | {row['n']} | {fmt_float(row['disin_mean'])} | {fmt_float(row['disin_sd'])} | {fmt_float(row['soph_mean'])} | {fmt_float(row['soph_sd'])} |")
    lines.append("")

    # === SECTION 14: COMPOSITE RANGES ===
    lines.append("---")
    lines.append("")
    lines.append("## 14. COMPOSITE RANGES")
    lines.append("")
    lines.append("| Condition | Soph_Min | Soph_Max | Disin_Min | Disin_Max |")
    lines.append("|-----------|----------|----------|-----------|-----------|\n")
    for row in gather_composite_ranges():
        lines.append(f"| {row['condition']} | {row['soph_min']:.2f} | {row['soph_max']:.2f} | {row['disin_min']:.2f} | {row['disin_max']:.2f} |")
    lines.append("")

    # === SECTION 15: EFFECT SIZE SUMMARY ===
    h1h2 = gather_h1h2_core()
    h1h2_or = gather_h1h2_outliers_removed()

    lines.append("---")
    lines.append("")
    lines.append("## 15. EFFECT SIZE SUMMARY")
    lines.append("")
    lines.append("| Condition | H1_d_Range | H2_r_Range | All_p < .05 |")
    lines.append("|-----------|------------|------------|-------------|")

    for row in h1h2:
        cond = row["condition"]
        or_row = next((r for r in h1h2_or if r["condition"] == cond), None)

        d_min = row["h1_d"]
        d_max = or_row["h1_d"] if or_row else row["h1_d"]
        if d_min > d_max:
            d_min, d_max = d_max, d_min

        r_min = row["h2_r"]
        r_max = or_row["h2_r"] if or_row else row["h2_r"]
        if r_min > r_max:
            r_min, r_max = r_max, r_min

        all_sig = row["h1_p"] < 0.05 and (or_row is None or or_row["h1_p"] < 0.05)

        lines.append(f"| {cond} | {fmt_d(d_min)} - {fmt_d(d_max)} | {fmt_r(r_min)} - {fmt_r(r_max)} | {'Yes' if all_sig else 'No'} |")
    lines.append("")

    # === DATA SOURCES ===
    lines.append("---")
    lines.append("")
    lines.append("## DATA SOURCES")
    lines.append("")
    lines.append("| Section | Source File |")
    lines.append("|---------|-------------|")
    lines.append("| H1/H2 Core | `<condition>/median_split_classification.json` |")
    lines.append("| Outliers Removed | `<condition>/outliers_removed/median_split_classification.json` |")
    lines.append("| BERT Validation | `bert_validation/<condition>/bert_validation_results.json` |")
    lines.append("| BERT Soph/Disin | `bert_validation/<condition>/bert_soph_disin_results.json` |")
    lines.append("| Judge Agreement | `<condition>/judge_agreement/judge_agreement_audit.json` |")
    lines.append("| External Validation | `limitations/external_evals/reasoning_composite_triangulated_audit.json` |")
    lines.append("| Per-Benchmark | `limitations/external_evals/{gpqa,aime,arc_agi}_validation_analysis.json` |")
    lines.append("| Provider ANOVA | `<condition>/provider_comparison_stats.json` |")
    lines.append("| Provider Means | `<condition>/comprehensive_stats.json` |")
    lines.append("")

    # === REPRODUCIBILITY ===
    lines.append("---")
    lines.append("")
    lines.append("## REPRODUCIBILITY")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/generate_consolidated_statistics.py")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    print("Generating CONSOLIDATED_STATISTICS.md...")

    content = generate_markdown()

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        f.write(content)

    print(f"Written to: {OUTPUT_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()
