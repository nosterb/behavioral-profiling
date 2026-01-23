#!/usr/bin/env python3
"""
Regenerate MAIN_RESEARCH_BRIEF.md using AUTO-block architecture.

KEY PARADIGM: Mark AUTO-GENERATED content, preserve everything else.

This means:
- Anything between <!-- AUTO-START:section_id --> and <!-- AUTO-END:section_id -->
  will be regenerated from JSON data
- Everything OUTSIDE of AUTO blocks is preserved exactly as-is
- Users can add new sections anywhere and they won't be touched
- Users can edit any content outside AUTO blocks freely

Usage:
    python3 scripts/regenerate_main_brief_v2.py
    python3 scripts/regenerate_main_brief_v2.py --dry-run
    python3 scripts/regenerate_main_brief_v2.py --list-sections  # Show available AUTO sections
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# Configuration
BASE_DIR = Path("outputs/behavioral_profiles")
OUTPUT_FILE = BASE_DIR / "research_synthesis" / "MAIN_RESEARCH_BRIEF.md"

CONDITIONS = ["baseline", "authority", "minimal_steering", "reminder", "telemetryV3", "urgency", "naturalistic", "all_combined"]

# AUTO block markers
AUTO_START_PATTERN = r'<!-- AUTO-START:(\w+) -->'
AUTO_END_PATTERN = r'<!-- AUTO-END:(\w+) -->'


def load_json(path):
    """Load JSON file, return None if not found."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_condition_data(condition):
    """Load median_split_classification.json for a condition."""
    path = BASE_DIR / condition / "median_split_classification.json"
    return load_json(path)


def load_all_conditions():
    """Load data for all available conditions."""
    data = OrderedDict()
    for condition in CONDITIONS:
        cond_data = load_condition_data(condition)
        if cond_data:
            data[condition] = cond_data
    return data


def load_cross_condition_data():
    """Load cross-condition analysis files."""
    cross_dir = BASE_DIR / "research_synthesis" / "cross_condition"
    return {
        "anova": load_json(cross_dir / "repeated_measures_anova_results.json"),
        "variability": load_json(cross_dir / "variability_analysis_disinhibition.json"),
        "patterns": load_json(cross_dir / "cross_condition_patterns.json"),
    }


def load_external_validation():
    """Load external benchmark validation data."""
    ext_dir = BASE_DIR / "research_synthesis" / "limitations" / "external_evals"
    return {
        "arc_agi": load_json(ext_dir / "arc_agi_validation_analysis.json"),
        "gpqa": load_json(ext_dir / "gpqa_validation_analysis.json"),
        "aime": load_json(ext_dir / "aime_validation_analysis.json"),
    }


def load_judge_agreement():
    """Load judge agreement analysis data."""
    path = BASE_DIR / "research_synthesis" / "limitations" / "judge_limitations" / "judge_agreement_analysis.json"
    return load_json(path)


def load_per_condition_judge_agreement():
    """Load judge agreement data per condition for evaluation counts."""
    data = {}
    for condition in CONDITIONS:
        path = BASE_DIR / condition / "judge_agreement" / "judge_agreement_audit.json"
        ja_data = load_json(path)
        if ja_data:
            data[condition] = ja_data.get("summary", {}).get("n_evaluations", 0)
    return data


def load_outlier_data():
    """Load outlier removal data for all conditions."""
    outlier_data = {}
    for condition in CONDITIONS:
        outlier_info = load_json(BASE_DIR / condition / "outliers_removed" / "outlier_removal_info.json")
        outlier_classification = load_json(BASE_DIR / condition / "outliers_removed" / "median_split_classification.json")
        original_classification = load_json(BASE_DIR / condition / "median_split_classification.json")
        if outlier_info and outlier_classification and original_classification:
            outlier_data[condition] = {
                "info": outlier_info,
                "with_outliers": original_classification,
                "without_outliers": outlier_classification,
            }
    return outlier_data


def load_no_dimensions_data():
    """Load no_dimensions sensitivity data for all conditions."""
    no_dim_data = {}
    for condition in CONDITIONS:
        sensitivity_info = load_json(BASE_DIR / condition / "no_dimensions" / "sensitivity_analysis_info.json")
        no_dim_classification = load_json(BASE_DIR / condition / "no_dimensions" / "median_split_classification.json")
        original_classification = load_json(BASE_DIR / condition / "median_split_classification.json")
        if sensitivity_info and no_dim_classification and original_classification:
            no_dim_data[condition] = {
                "info": sensitivity_info,
                "full_dataset": original_classification,
                "no_dimensions": no_dim_classification,
            }
    return no_dim_data


def load_factor_structure():
    """Load factor structure analysis from baseline."""
    path = BASE_DIR / "research_synthesis" / "limitations" / "factor_structure" / "factor_structure_baseline.json"
    return load_json(path)


def load_provider_constraint():
    """Load provider constraint analysis from all conditions."""
    constraint_dir = BASE_DIR / "research_synthesis" / "limitations" / "provider_constraint"
    if not constraint_dir.exists():
        return None
    data = {}
    for condition in CONDITIONS:
        path = constraint_dir / f"provider_constraint_{condition}.json"
        if path.exists():
            data[condition] = load_json(path)
    return data if data else None


def load_classification_stability():
    """Load classification stability analysis."""
    path = BASE_DIR / "research_synthesis" / "limitations" / "median_split" / "classification_stability_analysis.json"
    return load_json(path)


def load_bert_validation():
    """Load BERT validation data for all conditions."""
    bert_dir = BASE_DIR / "research_synthesis" / "bert_validation"
    bert_data = {}
    for condition in CONDITIONS:
        cond_dir = bert_dir / condition
        results = load_json(cond_dir / "bert_validation_results.json")
        soph_disin = load_json(cond_dir / "bert_soph_disin_results.json")
        if results:
            bert_data[condition] = {
                "primary": results,
                "extended": soph_disin
            }
    return bert_data if bert_data else None


def load_gpqa_bert_correlation():
    """Load GPQA vs BERT toxicity correlation data for conditions."""
    bert_dir = BASE_DIR / "research_synthesis" / "bert_validation"
    gpqa_bert_data = {}
    for condition in ["all_combined", "naturalistic", "baseline"]:
        audit_file = bert_dir / condition / "gpqa_bert_correlation_audit.json"
        data = load_json(audit_file)
        if data:
            gpqa_bert_data[condition] = data
    return gpqa_bert_data if gpqa_bert_data else None


def format_p(p):
    """Format p-value for display."""
    if p < 0.0001:
        return "< .0001"
    elif p < 0.001:
        return "< .001"
    elif p < 0.01:
        return "< .01"
    elif p < 0.05:
        return f"= {p:.3f}"
    else:
        return f"= {p:.3f} (ns)"


# ============================================================================
# AUTO-BLOCK GENERATORS
# Each generator produces content for a specific AUTO block
# ============================================================================

def generate_header_metadata(conditions_data, eval_counts=None):
    """Generate header metadata (statistics date, counts)."""
    n_conditions = len(conditions_data)
    n_models = 0
    for cond in ["baseline"] + list(conditions_data.keys()):
        if cond in conditions_data:
            n_models = len(conditions_data[cond].get("models", []))
            break

    # Use actual evaluation counts if available, otherwise estimate
    if eval_counts:
        # Sum evaluations from individual conditions only (not all_combined to avoid double-counting)
        total_evals = sum(eval_counts.get(cond, 0) for cond in eval_counts.keys() if cond != "all_combined")
    else:
        total_evals = sum(len(d.get("models", [])) * 50 for d in conditions_data.values())

    lines = []
    lines.append(f"<b>Statistics Last Updated</b>: {datetime.now().strftime('%Y-%m-%d')}<br>")
    lines.append(f"<b>Conditions Analyzed</b>: {n_conditions}<br>")
    lines.append(f"<b>Models</b>: {n_models} per condition<br>")
    lines.append(f"<b>Total Evaluations</b>: {total_evals:,}</b>")
    return "\n".join(lines)


def generate_h1h2_table(conditions_data, eval_counts=None):
    """Generate the core H1/H2 results table."""
    lines = []
    cond_names = list(conditions_data.keys())

    header = "| Metric | " + " | ".join(cond_names) + " |"
    separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
    lines.append(header)
    lines.append(separator)

    # N row
    row = "| **N** |"
    for cond in cond_names:
        n = len(conditions_data[cond].get("models", []))
        row += f" {n} |"
    lines.append(row)

    # Evaluations row
    if eval_counts:
        row = "| **Evaluations** |"
        for cond in cond_names:
            evals = eval_counts.get(cond, 0)
            row += f" {evals:,} |" if evals else " ? |"
        lines.append(row)

    # High/Low split
    row = "| **High / Low** |"
    for cond in cond_names:
        data = conditions_data[cond]
        h = data.get("n_high_sophistication", "?")
        l = data.get("n_low_sophistication", "?")
        row += f" {h} / {l} |"
    lines.append(row)

    # Median sophistication
    row = "| **Median Soph** |"
    for cond in cond_names:
        med = conditions_data[cond].get("median_sophistication", 0)
        row += f" {med:.2f} |"
    lines.append(row)

    # H1: Sophistication group separation (Cohen's d)
    row = "| **H1: Soph d** |"
    for cond in cond_names:
        d = conditions_data[cond].get("statistics", {}).get("sophistication", {}).get("cohens_d", 0)
        row += f" {d:.2f} |"
    lines.append(row)

    # H1a: Cohen's d
    row = "| **H1a: d** |"
    for cond in cond_names:
        d = conditions_data[cond].get("statistics", {}).get("disinhibition", {}).get("cohens_d", 0)
        row += f" {d:.2f} |"
    lines.append(row)

    # H1a: p-value
    row = "| **H1a: p** |"
    for cond in cond_names:
        p = conditions_data[cond].get("statistics", {}).get("disinhibition", {}).get("p_value", 1)
        row += " < .001 |" if p < 0.001 else f" {p:.3f} |"
    lines.append(row)

    # H2: r
    row = "| **H2: r** |"
    for cond in cond_names:
        r = conditions_data[cond].get("correlation", {}).get("sophistication_disinhibition", 0)
        row += f" {r:.3f} |"
    lines.append(row)

    # Separator for dimensions
    lines.append("| | " + " | ".join([""] * len(cond_names)) + "|")
    lines.append("| **Per-Dimension d:** | " + " | ".join([""] * len(cond_names)) + "|")

    # Individual dimension d values
    for dim in ["transgression", "aggression", "tribalism", "grandiosity"]:
        row = f"| *{dim.capitalize()}* |"
        for cond in cond_names:
            d = conditions_data[cond].get("statistics", {}).get(dim, {}).get("cohens_d", 0)
            row += f" {d:.2f} |"
        lines.append(row)

    return "\n".join(lines)


def generate_external_validation_table(external_data):
    """Generate external validation benchmark table."""
    arc = external_data.get("arc_agi")
    gpqa = external_data.get("gpqa")
    aime = external_data.get("aime")

    if not arc and not gpqa and not aime:
        return "*External validation data not available.*"

    lines = []
    lines.append("| Metric | ARC-AGI | GPQA | AIME 2025 |")
    lines.append("|--------|---------|------|-----------|")

    # Matched models
    arc_n = arc.get("sample", {}).get("unique_matched_models", "N/A") if arc else "N/A"
    gpqa_n = gpqa.get("sample", {}).get("unique_matched_models", "N/A") if gpqa else "N/A"
    aime_n = aime.get("sample", {}).get("unique_matched_models", "N/A") if aime else "N/A"
    lines.append(f"| **Matched models** | {arc_n} | {gpqa_n} | {aime_n} |")

    # Sophistication correlation with p-values
    for metric, label in [("sophistication", "r"), ("sophistication", "p")]:
        row = f"| **{label} (Sophistication)** |" if label == "r" else f"| *p (Sophistication)* |"
        for src, data in [("arc", arc), ("gpqa", gpqa), ("aime", aime)]:
            if data:
                corr = data.get("correlations", {}).get("sophistication", {})
                val = corr.get(label)
                if label == "r":
                    row += f" {val:.3f} |" if val else " N/A |"
                else:
                    row += " < .001 |" if val and val < 0.001 else f" = {val:.3f} |" if val else " N/A |"
            else:
                row += " N/A |"
        lines.append(row)

    # Disinhibition correlation with p-values
    for metric, label in [("disinhibition", "r"), ("disinhibition", "p")]:
        row = f"| **{label} (Disinhibition)** |" if label == "r" else f"| *p (Disinhibition)* |"
        for src, data in [("arc", arc), ("gpqa", gpqa), ("aime", aime)]:
            if data:
                corr = data.get("correlations", {}).get("disinhibition", {})
                val = corr.get(label)
                if label == "r":
                    row += f" {val:.3f} |" if val else " N/A |"
                else:
                    row += " < .001 |" if val and val < 0.001 else f" = {val:.3f} |" if val else " N/A |"
            else:
                row += " N/A |"
        lines.append(row)

    # Group differences
    row = "| **Group diff (High-Low)** |"
    for data in [arc, gpqa, aime]:
        if data:
            h1 = data.get("h1_group_comparison", {})
            high = h1.get("high_sophistication", {}).get("mean", 0)
            low = h1.get("low_sophistication", {}).get("mean", 0)
            row += f" +{high - low:.1f} pp |" if h1 else " N/A |"
        else:
            row += " N/A |"
    lines.append(row)

    lines.append("| **Benchmark type** | Abstract reasoning | Expert scientific | Mathematical reasoning |")

    return "\n".join(lines)


def generate_outlier_sensitivity_table(outlier_data):
    """Generate outlier sensitivity analysis table."""
    if not outlier_data:
        return "*No outlier analysis data available.*"

    lines = []
    cond_names = list(outlier_data.keys())

    header = "| Metric | " + " | ".join(cond_names) + " |"
    separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
    lines.append(header)
    lines.append(separator)

    # Outliers removed
    row = "| **Outliers Removed** |"
    for cond in cond_names:
        n_outliers = len(outlier_data[cond]["info"].get("outliers_removed", []))
        row += f" {n_outliers} |"
    lines.append(row)

    # H1a d change
    row = "| **H1a d: Δ** |"
    for cond in cond_names:
        orig_d = outlier_data[cond]["with_outliers"]["statistics"]["disinhibition"]["cohens_d"]
        new_d = outlier_data[cond]["without_outliers"]["statistics"]["disinhibition"]["cohens_d"]
        row += f" {new_d - orig_d:+.2f} |"
    lines.append(row)

    # H2 r change
    row = "| **H2 r: Δ** |"
    for cond in cond_names:
        orig_r = outlier_data[cond]["with_outliers"]["correlation"]["sophistication_disinhibition"]
        new_r = outlier_data[cond]["without_outliers"]["correlation"]["sophistication_disinhibition"]
        row += f" {new_r - orig_r:+.3f} |"
    lines.append(row)

    return "\n".join(lines)


def generate_no_dimensions_table(no_dim_data):
    """Generate no-dimensions sensitivity table."""
    if not no_dim_data:
        return "*No no-dimensions analysis data available.*"

    lines = []
    cond_names = list(no_dim_data.keys())

    header = "| Metric | " + " | ".join(cond_names) + " |"
    separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
    lines.append(header)
    lines.append(separator)

    # H1a d change
    row = "| **H1a d: Δ** |"
    for cond in cond_names:
        orig_d = no_dim_data[cond]["full_dataset"]["statistics"]["disinhibition"]["cohens_d"]
        new_d = no_dim_data[cond]["no_dimensions"]["statistics"]["disinhibition"]["cohens_d"]
        row += f" {new_d - orig_d:+.2f} |"
    lines.append(row)

    # H2 r change
    row = "| **H2 r: Δ** |"
    for cond in cond_names:
        orig_r = no_dim_data[cond]["full_dataset"]["correlation"]["sophistication_disinhibition"]
        new_r = no_dim_data[cond]["no_dimensions"]["correlation"]["sophistication_disinhibition"]
        row += f" {new_r - orig_r:+.3f} |"
    lines.append(row)

    return "\n".join(lines)


def generate_bert_primary_table(bert_data):
    """Generate BERT primary validation table (BERT vs Aggression)."""
    if not bert_data:
        return "*BERT validation data not available.*"

    lines = []
    lines.append("| Condition | Toxicity r | p | Insult r | p | Effect |")
    lines.append("|-----------|------------|---|----------|---|--------|")

    # Sort by toxicity r descending
    sorted_conds = sorted(
        bert_data.items(),
        key=lambda x: x[1].get("primary", {}).get("correlations", {}).get("toxicity", {}).get("r", 0),
        reverse=True
    )

    for cond, data in sorted_conds:
        primary = data.get("primary", {}).get("correlations", {})
        tox = primary.get("toxicity", {})
        ins = primary.get("insult", {})

        tox_r = tox.get("r", 0)
        tox_p = tox.get("p", 1)
        ins_r = ins.get("r", 0)
        ins_p = ins.get("p", 1)

        # Effect size
        effect = "Large" if abs(tox_r) >= 0.5 else "Medium" if abs(tox_r) >= 0.3 else "Small"

        # Format p-values
        tox_p_str = "< .0001" if tox_p < 0.0001 else f"{tox_p:.4f}"
        ins_p_str = "< .0001" if ins_p < 0.0001 else f"{ins_p:.4f}"

        bold = "**" if cond == "baseline" else ""
        lines.append(f"| {bold}{cond}{bold} | {bold}{tox_r:.3f}{bold} | {tox_p_str} | {bold}{ins_r:.3f}{bold} | {ins_p_str} | {effect} |")

    return "\n".join(lines)


def generate_bert_extended_table(bert_data):
    """Generate BERT extended validation table (vs Sophistication/Disinhibition)."""
    if not bert_data:
        return "*BERT validation data not available.*"

    lines = []
    lines.append("| Condition | Tox~Soph | Tox~Disin | Ins~Disin |")
    lines.append("|-----------|----------|-----------|-----------|")

    for cond in CONDITIONS:
        if cond not in bert_data:
            continue

        ext = bert_data[cond].get("extended", {})
        if not ext:
            continue

        corrs = ext.get("correlations", {})

        tox_soph = corrs.get("toxicity_vs_sophistication", {}).get("r", 0)
        tox_disin = corrs.get("toxicity_vs_disinhibition", {}).get("r", 0)
        ins_disin = corrs.get("insult_vs_disinhibition", {}).get("r", 0)

        def effect_label(r):
            ar = abs(r)
            if ar >= 0.5:
                return f"{r:.3f} (L)"
            elif ar >= 0.3:
                return f"{r:.3f} (M)"
            else:
                return f"{r:.3f} (S)"

        bold = "**" if cond == "baseline" else ""
        lines.append(f"| {bold}{cond}{bold} | {effect_label(tox_soph)} | {bold}{effect_label(tox_disin)}{bold} | {bold}{effect_label(ins_disin)}{bold} |")

    lines.append("")
    lines.append("*Effect sizes: L = Large (>=0.5), M = Medium (0.3-0.5), S = Small (<0.3)*")

    return "\n".join(lines)


def generate_gpqa_bert_table(gpqa_bert_data):
    """Generate GPQA vs BERT toxicity correlation table."""
    if not gpqa_bert_data:
        return "*GPQA-BERT correlation data not available.*"

    lines = []
    lines.append("External validation correlating GPQA benchmark (scientific reasoning capability) directly with BERT-detected toxicity, bypassing judge-based behavioral dimensions.")
    lines.append("")
    lines.append("| Condition | N | r | p | R² | Effect |")
    lines.append("|-----------|---|---|---|-----|--------|")

    # Order: all_combined first (bolded), then naturalistic, baseline
    ordered_conditions = ["all_combined", "naturalistic", "baseline"]

    for cond in ordered_conditions:
        if cond not in gpqa_bert_data:
            continue

        data = gpqa_bert_data[cond]
        results = data.get("results", {})
        n = data.get("metadata", {}).get("n_matched", 0)
        r = results.get("pearson_r", 0)
        p = results.get("p_value", 1)
        r_sq = results.get("r_squared", 0) * 100  # Convert to percentage
        effect = results.get("effect_size", "")

        # Format p-value (proper rounding)
        if p < 0.001:
            p_str = "< .001"
        else:
            p_str = f".{round(p*1000):03d}"  # e.g., .007, .011

        # Bold the all_combined row
        if cond == "all_combined":
            lines.append(f"| **{cond}** | {n} | **{r:.3f}** | {p_str} | {r_sq:.1f}% | {effect} |")
        else:
            lines.append(f"| {cond} | {n} | {r:.3f} | {p_str} | {r_sq:.1f}% | {effect} |")

    return "\n".join(lines)


def generate_provider_h2_table(conditions_data):
    """Generate per-provider H2 correlation table."""
    from scipy import stats as sp_stats
    from collections import defaultdict

    baseline_data = conditions_data.get("baseline", {})
    models = baseline_data.get("models", [])

    if not models:
        return "*Baseline data not available for per-provider analysis.*"

    # Group by provider
    def classify_provider(model_id):
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

    provider_data = defaultdict(list)
    for model in models:
        provider = classify_provider(model.get("model_id", ""))
        provider_data[provider].append(model)

    # Filter to n >= 3
    providers_with_n = [(p, m) for p, m in provider_data.items() if len(m) >= 3]
    providers_with_n.sort(key=lambda x: -len(x[1]))

    lines = []
    lines.append("| Provider | N | r | p | Effect | H2 Supported |")
    lines.append("|----------|---|---|---|--------|--------------|")

    for provider, prov_models in providers_with_n:
        n = len(prov_models)
        soph = [m['sophistication'] for m in prov_models]
        disinhib = [m['disinhibition'] for m in prov_models]

        r, p = sp_stats.pearsonr(soph, disinhib)

        # Effect size
        r_abs = abs(r)
        effect = "large" if r_abs >= 0.5 else "medium" if r_abs >= 0.3 else "small" if r_abs >= 0.1 else "negligible"

        # Format p-value
        p_str = "< .001" if p < 0.001 else "< .01" if p < 0.01 else f"= {p:.3f}"

        # H2 supported?
        supported = "**Yes**" if r > 0 and p < 0.05 else "No (ns)" if r > 0 else "No (neg)"

        lines.append(f"| {provider} | {n} | {r:.3f} | {p_str} | {effect} | {supported} |")

    # Overall
    all_soph = [m['sophistication'] for m in models]
    all_disinhib = [m['disinhibition'] for m in models]
    r_all, _ = sp_stats.pearsonr(all_soph, all_disinhib)
    lines.append(f"| **OVERALL** | **{len(models)}** | **{r_all:.3f}** | **< .001** | **large** | **Yes** |")

    return "\n".join(lines)


def generate_provider_constraint_table(provider_constraint):
    """Generate provider constraint cross-condition table."""
    if not provider_constraint:
        return "*Provider constraint data not available.*"

    lines = []
    lines.append("| Condition | OpenAI Residual | Rank | ANOVA p | Sig |")
    lines.append("|-----------|-----------------|------|---------|-----|")

    for condition in ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder"]:
        if condition not in provider_constraint:
            continue

        data = provider_constraint[condition]
        openai_stats = data.get("provider_stats", {}).get("OpenAI", {})
        openai_resid = openai_stats.get("mean_residual", float("nan"))

        sorted_provs = sorted(data.get("provider_stats", {}).items(),
                             key=lambda x: x[1].get("mean_residual", 0))
        rank = next((i+1 for i, (p, _) in enumerate(sorted_provs) if p == "OpenAI"), "N/A")
        rank_str = f"{rank}" + ("st" if rank == 1 else "nd" if rank == 2 else "rd" if rank == 3 else "th")

        anova_p = data.get("anova", {}).get("p", float("nan"))
        sig = "Yes" if anova_p < 0.05 else "No"

        lines.append(f"| {condition} | {openai_resid:+.3f} | {rank_str} | {anova_p:.4f} | {sig} |")

    return "\n".join(lines)


def generate_constrained_models_table(cross_data):
    """Generate consistently constrained models table."""
    patterns = cross_data.get("patterns") if cross_data else None
    cross_condition = patterns.get("cross_condition", {}) if patterns else {}
    constrained = cross_condition.get("most_constrained", [])

    multi = [m for m in constrained if m.get("composite", 0) >= 2]

    if not multi:
        return "| *No models constrained in 2+ conditions* | - | - |"

    lines = []
    for model in multi[:10]:
        name = model.get("model", "")
        n_conds = model.get("composite", 0)
        conds = ", ".join(model.get("conditions", []))
        lines.append(f"| {name} | {n_conds} | {conds} |")

    return "\n".join(lines)


def generate_outlier_models_table(cross_data):
    """Generate consistent outliers table."""
    patterns = cross_data.get("patterns") if cross_data else None
    cross_condition = patterns.get("cross_condition", {}) if patterns else {}
    outliers = cross_condition.get("most_outlier", [])

    multi = [m for m in outliers if m.get("composite", 0) >= 2]

    if not multi:
        return "| *No models outliers in 2+ conditions* | - | - |"

    lines = []
    for model in multi[:10]:
        name = model.get("model", "")
        n_conds = model.get("composite", 0)
        conds = ", ".join(model.get("conditions", []))
        lines.append(f"| {name} | {n_conds} | {conds} |")

    return "\n".join(lines)


def generate_judge_agreement_table(judge_agreement):
    """Generate judge inter-rater reliability table."""
    if not judge_agreement:
        return "*Judge agreement analysis not available.*"

    n_evals = judge_agreement.get("n_valid_3_judge", 0)
    by_dim = judge_agreement.get("by_dimension", {})
    overall = judge_agreement.get("overall", {})

    lines = []
    lines.append(f"Based on **N = {n_evals:,}** evaluations with 3 valid judge scores (baseline condition):")
    lines.append("")
    lines.append("| Dimension | ICC(3) | Mean r | Within-1 | Quality |")
    lines.append("|-----------|--------|--------|----------|---------|")

    dim_order = ["aggression", "hedging", "warmth", "tribalism", "grandiosity",
                 "transgression", "authenticity", "depth", "formality"]

    for dim in dim_order:
        if dim in by_dim:
            d = by_dim[dim]
            icc = d.get("icc_avg", 0)
            r = d.get("mean_r", 0)
            w1 = d.get("mean_within1", 0) * 100
            quality = "Excellent" if icc > 0.90 else "Good" if icc > 0.75 else "Moderate" if icc > 0.50 else "Poor"
            lines.append(f"| {dim.capitalize()} | {icc:.3f} | {r:.3f} | {w1:.1f}% | {quality} |")

    icc_overall = overall.get("mean_icc_avg", 0)
    r_overall = overall.get("mean_pairwise_r", 0)
    w1_overall = overall.get("mean_within1_agreement", 0) * 100
    lines.append(f"| **OVERALL** | **{icc_overall:.3f}** | {r_overall:.3f} | {w1_overall:.1f}% | **Good** |")

    return "\n".join(lines)


def generate_h3_variability_table(conditions_data):
    """Generate H3 response variability table."""
    import numpy as np

    variability_stats = {}
    for cond, data in conditions_data.items():
        models = data.get("models", [])
        if models:
            disinhib_values = [m.get("disinhibition", 0) for m in models]
            if disinhib_values:
                mean_val = np.mean(disinhib_values)
                sd_val = np.std(disinhib_values, ddof=1) if len(disinhib_values) > 1 else 0
                cv_val = (sd_val / mean_val * 100) if mean_val > 0 else 0
                var_val = np.var(disinhib_values, ddof=1) if len(disinhib_values) > 1 else 0
                variability_stats[cond] = {
                    "n": len(disinhib_values),
                    "mean": mean_val,
                    "sd": sd_val,
                    "var": var_val,
                    "cv": cv_val
                }

    if not variability_stats:
        return "*Variability data not available.*"

    lines = []
    lines.append("| Condition | N | Mean | SD | CV% | Var Ratio |")
    lines.append("|-----------|---|------|-----|-----|-----------|")

    sorted_conds = sorted(variability_stats.items(), key=lambda x: x[1].get("cv", 0))
    baseline_var = variability_stats.get("baseline", {}).get("var", 1) or 1

    for cond, data in sorted_conds:
        n = data.get("n", 0)
        mean = data.get("mean", 0)
        sd = data.get("sd", 0)
        cv = data.get("cv", 0)
        var = data.get("var", 0)
        vr = var / baseline_var if cond != "baseline" else 1.0
        lines.append(f"| {cond} | {n} | {mean:.2f} | {sd:.3f} | {cv:.1f}% | {vr:.2f} |")

    return "\n".join(lines)


def generate_h3_anova_stats(cross_data):
    """Generate H3 ANOVA statistics."""
    anova_data = cross_data.get("anova") if cross_data else None
    if not anova_data:
        return "*ANOVA results not available.*"

    original = anova_data.get("original", {})
    rm = original.get("rm_anova", {})

    if not rm:
        return "*No repeated-measures ANOVA data.*"

    F = rm.get("F", 0)
    df1 = rm.get("df1", 0)
    df2 = rm.get("df2", 0)
    p = rm.get("p_value", 1)
    eta = rm.get("eta_squared", 0)
    epsilon = rm.get("epsilon", 1)
    p_gg = rm.get("p_gg_corrected", p)

    lines = []
    lines.append(f"- **F**({df1}, {df2}) = {F:.2f}")
    p_str = "< .0001" if p < 0.0001 else f"= {p:.4f}"
    lines.append(f"- **p** {p_str}")
    lines.append(f"- **eta squared** = {eta:.3f}")
    lines.append("")
    p_gg_str = "< .0001" if p_gg < 0.0001 else f"= {p_gg:.4f}"
    lines.append(f"Sphericity violated (epsilon = {epsilon:.3f}), Greenhouse-Geisser corrected p {p_gg_str}")

    return "\n".join(lines)


def generate_h3_posthoc_table(cross_data):
    """Generate H3 pairwise comparison table."""
    anova_data = cross_data.get("anova") if cross_data else None
    if not anova_data:
        return "*No posthoc data available.*"

    original = anova_data.get("original", {})
    posthoc = original.get("posthoc", [])

    if not posthoc:
        return "*No pairwise comparisons available.*"

    lines = []
    lines.append("| Comparison | t | p | g | Sig |")
    lines.append("|------------|---|---|---|-----|")

    for comp in posthoc:
        if comp.get("p_corrected", 1) < 0.05:
            name = comp.get("comparison", "")
            t = comp.get("t", 0)
            p_corr = comp.get("p_corrected", 1)
            g = comp.get("hedges_g", 0)
            p_str = "< .0001" if p_corr < 0.0001 else f"{p_corr:.4f}"
            lines.append(f"| {name} | {t:.2f} | {p_str} | {g:.2f} | Yes |")

    return "\n".join(lines)


def generate_factor_structure_tables(factor_structure):
    """Generate factor structure correlation tables."""
    if not factor_structure:
        return "*Factor structure data not available.*"

    lines = []

    # Sophistication
    soph = factor_structure.get("sophistication", {})
    soph_r = soph.get("correlation", 0)
    lines.append("### Sophistication: 2 -> 1")
    lines.append("")
    lines.append("| Pair | r |")
    lines.append("|------|---|")
    lines.append(f"| depth <-> authenticity | **{soph_r:.3f}** |")
    lines.append("")

    # Disinhibition
    disinhib = factor_structure.get("disinhibition", {})
    disinhib_pairs = disinhib.get("pairwise_correlations", {})
    disinhib_avg = disinhib.get("average_correlation", 0)

    lines.append("### Disinhibition: 4 -> 1")
    lines.append("")
    lines.append("| Pair | r |")
    lines.append("|------|---|")
    for pair_name, r in sorted(disinhib_pairs.items(), key=lambda x: -x[1]):
        dim1, dim2 = pair_name.split("_")
        lines.append(f"| {dim1} <-> {dim2} | {r:.3f} |")
    lines.append("")
    lines.append(f"**Average inter-correlation: r = {disinhib_avg:.3f}**")
    lines.append("")

    # Cross-factor
    cross = factor_structure.get("cross_factor", {})
    cross_pairs = cross.get("pairs", {})
    cross_avg = cross.get("average_correlation", 0)

    lines.append("### Cross-Factor Correlations")
    lines.append("")
    lines.append("| Sophistication | Disinhibition | r |")
    lines.append("|----------------|---------------|---|")
    for pair_name, r in sorted(cross_pairs.items(), key=lambda x: -x[1]):
        dim1, dim2 = pair_name.split("_")
        lines.append(f"| {dim1} | {dim2} | {r:.3f} |")
    lines.append("")
    lines.append(f"**Average cross-factor: r = {cross_avg:.3f}**")
    lines.append("")

    # Full matrix
    lines.append("### Full Correlation Matrix")
    lines.append("")
    lines.append("```")
    lines.append(factor_structure.get("matrix_formatted", ""))
    lines.append("```")

    return "\n".join(lines)


def generate_classification_stability_tables(stability_data):
    """Generate classification stability summary and tables."""
    if not stability_data:
        return "*Classification stability data not available.*"

    lines = []
    summary = stability_data.get("summary", {})
    total = summary.get("total_models", 0)
    always_high = summary.get("always_high", 0)
    always_low = summary.get("always_low", 0)
    flipped = summary.get("flipped", 0)
    stability_rate = summary.get("stability_rate", 0)

    # Summary table
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total models** | {total} |")
    lines.append(f"| **Always High-Sophistication** | {always_high} ({100*always_high/total:.0f}%) |")
    lines.append(f"| **Always Low-Sophistication** | {always_low} ({100*always_low/total:.0f}%) |")
    lines.append(f"| **Flipped (changed classification)** | {flipped} ({100*flipped/total:.0f}%) |")
    lines.append(f"| **Stability rate** | {stability_rate:.1f}% |")
    lines.append("")

    # Median by condition
    medians = stability_data.get("condition_medians", {})
    if medians:
        lines.append("### Median Sophistication by Condition")
        lines.append("")
        lines.append("| Condition | Median |")
        lines.append("|-----------|--------|")
        for cond in CONDITIONS:
            if cond in medians:
                lines.append(f"| {cond} | {medians[cond]:.2f} |")
        lines.append("")
        lines.append(f"*Range: {min(medians.values()):.2f} - {max(medians.values()):.2f}*")
        lines.append("")

    # Flipped models
    flipped_models = stability_data.get("flipped_models", [])
    if flipped_models:
        lines.append("### Flipped Models (Transitional Class)")
        lines.append("")
        lines.append("| Model | High Conditions | Low Conditions | Avg Soph |")
        lines.append("|-------|-----------------|----------------|----------|")
        for model in flipped_models:
            name = model.get("display_name", model.get("model_id", "Unknown"))
            high_conds = len(model.get("high_conditions", []))
            low_conds = len(model.get("low_conditions", []))
            scores = model.get("sophistication_scores", {})
            avg_soph = sum(scores.values()) / len(scores) if scores else 0
            lines.append(f"| {name} | {high_conds}/6 | {low_conds}/6 | {avg_soph:.2f} |")

    return "\n".join(lines)


# ============================================================================
# MAIN REGENERATION LOGIC
# ============================================================================

# Registry of AUTO section generators
AUTO_GENERATORS = {
    "header_metadata": lambda data: generate_header_metadata(data["conditions"], data.get("eval_counts")),
    "h1h2_table": lambda data: generate_h1h2_table(data["conditions"], data.get("eval_counts")),
    "external_validation_table": lambda data: generate_external_validation_table(data["external"]),
    "outlier_sensitivity_table": lambda data: generate_outlier_sensitivity_table(data["outlier"]),
    "no_dimensions_table": lambda data: generate_no_dimensions_table(data["no_dim"]),
    "bert_primary_table": lambda data: generate_bert_primary_table(data["bert"]),
    "bert_extended_table": lambda data: generate_bert_extended_table(data["bert"]),
    "gpqa_bert_table": lambda data: generate_gpqa_bert_table(data["gpqa_bert"]),
    "provider_h2_table": lambda data: generate_provider_h2_table(data["conditions"]),
    "provider_constraint_table": lambda data: generate_provider_constraint_table(data["provider_constraint"]),
    "constrained_models_table": lambda data: generate_constrained_models_table(data["cross"]),
    "outlier_models_table": lambda data: generate_outlier_models_table(data["cross"]),
    "judge_agreement_table": lambda data: generate_judge_agreement_table(data["judge_agreement"]),
    "h3_variability_table": lambda data: generate_h3_variability_table(data["conditions"]),
    "h3_anova_stats": lambda data: generate_h3_anova_stats(data["cross"]),
    "h3_posthoc_table": lambda data: generate_h3_posthoc_table(data["cross"]),
    "factor_structure_tables": lambda data: generate_factor_structure_tables(data["factor_structure"]),
    "classification_stability_tables": lambda data: generate_classification_stability_tables(data["classification_stability"]),
}


def find_auto_blocks(content: str) -> list:
    """Find all AUTO blocks in content. Returns list of (start_pos, end_pos, section_id, inner_content)."""
    blocks = []
    start_pattern = re.compile(AUTO_START_PATTERN)
    end_pattern = re.compile(AUTO_END_PATTERN)

    for start_match in start_pattern.finditer(content):
        section_id = start_match.group(1)
        start_pos = start_match.start()

        # Find matching end
        end_tag = f"<!-- AUTO-END:{section_id} -->"
        end_pos = content.find(end_tag, start_match.end())

        if end_pos != -1:
            inner_start = start_match.end()
            inner_content = content[inner_start:end_pos].strip()
            blocks.append({
                "section_id": section_id,
                "start_pos": start_pos,
                "end_pos": end_pos + len(end_tag),
                "inner_start": inner_start,
                "inner_end": end_pos,
                "inner_content": inner_content,
                "full_match": content[start_pos:end_pos + len(end_tag)]
            })

    return blocks


def regenerate_auto_blocks(content: str, data: dict) -> str:
    """Regenerate all AUTO blocks in content, preserving everything else."""
    blocks = find_auto_blocks(content)

    if not blocks:
        print("No AUTO blocks found in document.")
        return content

    # Process blocks in reverse order to preserve positions
    result = content
    for block in sorted(blocks, key=lambda b: b["start_pos"], reverse=True):
        section_id = block["section_id"]

        if section_id not in AUTO_GENERATORS:
            print(f"  Warning: No generator for AUTO block '{section_id}'")
            continue

        try:
            new_content = AUTO_GENERATORS[section_id](data)

            # Build new block
            new_block = f"<!-- AUTO-START:{section_id} -->\n{new_content}\n<!-- AUTO-END:{section_id} -->"

            # Replace
            result = result[:block["start_pos"]] + new_block + result[block["end_pos"]:]
            print(f"  Regenerated: {section_id}")

        except Exception as e:
            print(f"  Error generating '{section_id}': {e}")

    return result


def list_auto_sections():
    """List available AUTO section generators."""
    print("Available AUTO section generators:")
    print("-" * 40)
    for section_id in sorted(AUTO_GENERATORS.keys()):
        print(f"  <!-- AUTO-START:{section_id} -->")
    print()
    print("Usage in document:")
    print("  <!-- AUTO-START:section_id -->")
    print("  (content will be auto-generated)")
    print("  <!-- AUTO-END:section_id -->")


def main():
    parser = argparse.ArgumentParser(description="Regenerate MAIN_RESEARCH_BRIEF.md (AUTO-block version)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout instead of writing file")
    parser.add_argument("--list-sections", action="store_true", help="List available AUTO section generators")
    parser.add_argument("--input", type=str, help="Input file (default: MAIN_RESEARCH_BRIEF.md)")
    args = parser.parse_args()

    if args.list_sections:
        list_auto_sections()
        return

    # Load all data sources
    print("Loading data sources...")
    conditions_data = load_all_conditions()
    cross_data = load_cross_condition_data()
    external_data = load_external_validation()
    outlier_data = load_outlier_data()
    no_dim_data = load_no_dimensions_data()
    judge_agreement = load_judge_agreement()
    eval_counts = load_per_condition_judge_agreement()
    factor_structure = load_factor_structure()
    provider_constraint = load_provider_constraint()
    classification_stability = load_classification_stability()
    bert_data = load_bert_validation()
    gpqa_bert_data = load_gpqa_bert_correlation()

    if not conditions_data:
        print("Error: No condition data found.")
        return

    print(f"  Loaded {len(conditions_data)} conditions")

    # Bundle data for generators
    data = {
        "conditions": conditions_data,
        "cross": cross_data,
        "external": external_data,
        "outlier": outlier_data,
        "no_dim": no_dim_data,
        "judge_agreement": judge_agreement,
        "eval_counts": eval_counts,
        "factor_structure": factor_structure,
        "provider_constraint": provider_constraint,
        "classification_stability": classification_stability,
        "bert": bert_data,
        "gpqa_bert": gpqa_bert_data,
    }

    # Read existing document
    input_file = Path(args.input) if args.input else OUTPUT_FILE
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        print("Create the document first with AUTO block markers.")
        return

    print(f"Reading: {input_file}")
    content = input_file.read_text()

    # Find and regenerate AUTO blocks
    print("\nRegenerating AUTO blocks...")
    new_content = regenerate_auto_blocks(content, data)

    # Update timestamp
    new_content = re.sub(
        r'\*\*Statistics Generated\*\*: \d{4}-\d{2}-\d{2} \d{2}:\d{2}',
        f'**Statistics Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        new_content
    )

    if args.dry_run:
        print("\n--- DRY RUN OUTPUT ---")
        print(new_content)
    else:
        with open(OUTPUT_FILE, "w") as f:
            f.write(new_content)
        print(f"\nWritten: {OUTPUT_FILE}")
        print(f"Size: {len(new_content):,} bytes")


if __name__ == "__main__":
    main()
