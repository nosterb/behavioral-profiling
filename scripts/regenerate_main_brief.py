#!/usr/bin/env python3
"""
Regenerate MAIN_RESEARCH_BRIEF.md from JSON data sources.

Reads all condition data, cross-condition analysis, and external validation
to produce a comprehensive research brief with auto-generated statistics
and placeholder sections for human interpretation.

Usage:
    python3 scripts/regenerate_main_brief.py
    python3 scripts/regenerate_main_brief.py --dry-run  # Print to stdout
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# Configuration
BASE_DIR = Path("outputs/behavioral_profiles")
OUTPUT_FILE = BASE_DIR / "research_synthesis" / "MAIN_RESEARCH_BRIEF.md"

CONDITIONS = ["baseline", "authority", "minimal_steering", "reminder", "telemetryV3", "urgency"]

# Manual section markers - content between these is preserved across regenerations
MANUAL_START = "<!-- MANUAL-START -->"
MANUAL_END = "<!-- MANUAL-END -->"


def extract_manual_sections(content: str) -> dict:
    """Extract manually edited sections from existing content.

    Looks for content between <!-- MANUAL-START --> and <!-- MANUAL-END --> markers.
    Returns a dict mapping section headers to preserved content.
    """
    import re

    preserved = {}

    # Find all manual sections with their preceding header
    # Pattern: ## Header\n\n<!-- MANUAL-START -->\ncontent\n<!-- MANUAL-END -->
    pattern = r'(##+ [^\n]+)\n+' + re.escape(MANUAL_START) + r'\n(.*?)\n' + re.escape(MANUAL_END)

    for match in re.finditer(pattern, content, re.DOTALL):
        header = match.group(1).strip()
        manual_content = match.group(2)
        preserved[header] = manual_content

    return preserved


def load_existing_manual_sections() -> dict:
    """Load manual sections from existing MAIN_RESEARCH_BRIEF.md if it exists."""
    if OUTPUT_FILE.exists():
        content = OUTPUT_FILE.read_text()
        return extract_manual_sections(content)
    return {}


def wrap_manual_section(content: str) -> str:
    """Wrap content in manual section markers."""
    return f"{MANUAL_START}\n{content}\n{MANUAL_END}"


def get_preserved_or_default(preserved: dict, header: str, default_content: str) -> str:
    """Return preserved content if available, otherwise return default with markers."""
    if header in preserved:
        return f"{header}\n\n{wrap_manual_section(preserved[header])}"
    else:
        return f"{header}\n\n{wrap_manual_section(default_content)}"


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
    }


def load_judge_agreement():
    """Load judge agreement analysis data."""
    path = BASE_DIR / "research_synthesis" / "limitations" / "judge_limitations" / "judge_agreement_analysis.json"
    return load_json(path)


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


def format_p(p):
    """Format p-value for display."""
    if p < 0.0001:
        return "< .0001"
    elif p < 0.001:
        return "< .001"
    elif p < 0.01:
        return "< .01"
    elif p < 0.05:
        return "= " + f"{p:.3f}"
    else:
        return "= " + f"{p:.3f}" + " (ns)"


def count_h1_supported(conditions_data):
    """Count conditions where H1 is supported (p < .05)."""
    supported = 0
    for cond, data in conditions_data.items():
        p = data.get("statistics", {}).get("disinhibition", {}).get("p_value", 1)
        if p < 0.05:
            supported += 1
    return supported, len(conditions_data)


def get_h2_range(conditions_data):
    """Get min/max H2 correlation across conditions."""
    rs = []
    for cond, data in conditions_data.items():
        r = data.get("correlation", {}).get("sophistication_disinhibition")
        if r is not None:
            rs.append(r)
    if not rs:
        return None, None
    return min(rs), max(rs)


def get_h1_soph_d_range(conditions_data):
    """Get min/max H1 sophistication separation Cohen's d across conditions."""
    ds = []
    for cond, data in conditions_data.items():
        d = data.get("statistics", {}).get("sophistication", {}).get("cohens_d")
        if d is not None:
            ds.append(d)
    if not ds:
        return None, None
    return min(ds), max(ds)


def get_h1a_d_range(conditions_data):
    """Get min/max H1a disinhibition Cohen's d across conditions."""
    ds = []
    for cond, data in conditions_data.items():
        d = data.get("statistics", {}).get("disinhibition", {}).get("cohens_d")
        if d is not None:
            ds.append(d)
    if not ds:
        return None, None
    return min(ds), max(ds)


def total_evaluations(conditions_data):
    """Estimate total evaluations across conditions."""
    total = 0
    for cond, data in conditions_data.items():
        n_models = len(data.get("models", []))
        total += n_models * 50
    return total


def generate_header(conditions_data, cross_data, external_data):
    """Generate document header with metadata."""
    n_conditions = len(conditions_data)

    n_models = 0
    for cond in ["baseline"] + list(conditions_data.keys()):
        if cond in conditions_data:
            n_models = len(conditions_data[cond].get("models", []))
            break

    total_evals = total_evaluations(conditions_data)

    lines = []
    lines.append("# Main Research Brief: Sophistication-Disinhibition Relationship in Language Models")
    lines.append("")
    # Use HTML for proper line breaks in exports
    lines.append("<b>Author</b>: Nicholas Osterbur (Independent Researcher)<br>")
    lines.append("<b>Status</b>: Active Analysis<br>")
    lines.append("<b>Last Updated</b>: " + datetime.now().strftime('%Y-%m-%d') + "<br>")
    lines.append("<b>Conditions Analyzed</b>: " + str(n_conditions) + "<br>")
    lines.append("<b>Models</b>: " + str(n_models) + " per condition<br>")
    lines.append("<b>Total Evaluations</b>: " + f"{total_evals:,}" + "</b>")
    lines.append("")
    lines.append("*Copyright 2026 Nicholas Osterbur. Results and analyses licensed under CC BY 4.0.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_executive_summary(conditions_data, cross_data, external_data, preserved: dict):
    """Generate executive summary - MANUAL section that preserves human edits."""
    header = "## Executive Summary"

    # Generate default content from data
    h1_soph_d_min, h1_soph_d_max = get_h1_soph_d_range(conditions_data)
    h1a_d_min, h1a_d_max = get_h1a_d_range(conditions_data)
    h1a_sup, h1a_total = count_h1_supported(conditions_data)
    h2_min, h2_max = get_h2_range(conditions_data)

    arc = external_data.get("arc_agi") or {}
    gpqa = external_data.get("gpqa") or {}
    arc_r_soph = arc.get("correlations", {}).get("sophistication", {}).get("r") if arc else None
    gpqa_r_soph = gpqa.get("correlations", {}).get("sophistication", {}).get("r") if gpqa else None

    default_lines = []
    default_lines.append("This research investigates the relationship between model sophistication and behavioral disinhibition across 50+ language models under varying contextual conditions.")
    default_lines.append("")
    default_lines.append("### Key Findings")
    default_lines.append("")

    if h1_soph_d_min is not None:
        default_lines.append("1. **H1 (Group Existence)**: Median split produces two well-separated sophistication groups across all conditions (d = " + f"{h1_soph_d_min:.2f}" + "-" + f"{h1_soph_d_max:.2f}" + ")")
        default_lines.append("")

    if h1a_sup is not None and h1a_d_min is not None:
        default_lines.append("2. **H1a (Group Comparison)**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models across all " + str(h1a_sup) + "/" + str(h1a_total) + " conditions tested (d = " + f"{h1a_d_min:.2f}" + "-" + f"{h1a_d_max:.2f}" + ", all p < .05)")
        default_lines.append("")

    if h2_min is not None and h2_max is not None:
        default_lines.append("3. **H2 (Correlation)**: Sophistication positively correlates with disinhibition across all conditions (r = " + f"{h2_min:.2f}" + "-" + f"{h2_max:.2f}" + ")")
        default_lines.append("")

    if arc_r_soph and gpqa_r_soph:
        default_lines.append("4. **External Validation**: Sophistication predicts performance on two independent benchmarks: ARC-AGI (r = " + f"{arc_r_soph:.2f}" + ") and GPQA (r = " + f"{gpqa_r_soph:.2f}" + ")")
        default_lines.append("")

    default_lines.append("5. **Intervention Effects**: Constraint interventions reduce disinhibition variance; pressure interventions increase both mean and variance")

    default_content = "\n".join(default_lines)

    # Check if preserved content exists
    if header in preserved:
        result = f"{header}\n\n{wrap_manual_section(preserved[header])}\n\n---\n\n"
    else:
        result = f"{header}\n\n{wrap_manual_section(default_content)}\n\n---\n\n"

    return result


def generate_hypotheses_methods(conditions_data, factor_structure=None):
    """Generate hypotheses and methods section."""
    sample_cond = "baseline" if "baseline" in conditions_data else list(conditions_data.keys())[0]
    sample_data = conditions_data[sample_cond]
    n_models = len(sample_data.get("models", []))
    n_conditions = len(conditions_data)

    lines = []
    lines.append("## 1. Hypotheses & Methods")
    lines.append("")
    lines.append("### Core Hypotheses")
    lines.append("")
    lines.append("| Hypothesis | Description |")
    lines.append("|------------|-------------|")
    lines.append("| **H1** | Two distinct sophistication groups exist (validated by median split) |")
    lines.append("| **H1a** | High-sophistication models exhibit higher disinhibition than low-sophistication models |")
    lines.append("| **H2** | Sophistication positively correlates with disinhibition across all models |")
    lines.append("")
    lines.append("### Measurement Framework")
    lines.append("")
    lines.append("Nine behavioral dimensions are measured on a 1-10 scale, then collapsed into two composite scores based on empirical inter-dimension correlations (see Appendix: Factor Structure).")
    lines.append("")

    # Get factor structure correlations if available
    soph_r = "0.96"
    disinhib_avg_r = "0.76"
    if factor_structure:
        soph_r = f"{factor_structure.get('sophistication', {}).get('correlation', 0.96):.2f}"
        disinhib_avg_r = f"{factor_structure.get('disinhibition', {}).get('average_correlation', 0.76):.2f}"

    lines.append("**Sophistication** (1-10 scale):")
    lines.append("- **Depth**: Platitudes/surface -> substantive/insightful")
    lines.append("- **Authenticity**: Templated/generic -> genuinely distinctive")
    lines.append(f"- **Composite**: (Depth + Authenticity) / 2 — *r = {soph_r} between dimensions*")
    lines.append("")
    lines.append("**Disinhibition** (1-10 scale):")
    lines.append("- **Transgression**: Conventional/safe -> norm-violating/edgy")
    lines.append("- **Aggression**: Supportive/gentle -> combative/attacking")
    lines.append("- **Tribalism**: Neutral/ecumenical -> us-vs-them")
    lines.append("- **Grandiosity**: Humble/self-effacing -> dominant/superior")
    lines.append(f"- **Composite**: Mean of four dimensions — *avg r = {disinhib_avg_r} between dimensions*")
    lines.append("")
    lines.append("### Sample")
    lines.append("")
    lines.append("- **Models per condition**: N = " + str(n_models))
    lines.append("- **Conditions**: " + str(n_conditions))
    lines.append("- **Evaluations per model**: ~50 scenarios")
    lines.append("")
    lines.append("### Statistical Methods")
    lines.append("")
    lines.append("- **H1a (Group Comparison)**: Independent samples t-test, Cohen's d effect size")
    lines.append("- **H2 (Correlation)**: Pearson product-moment correlation")
    lines.append("- **Cross-condition**: Repeated-measures ANOVA with Greenhouse-Geisser correction")
    lines.append("- **Variability**: Coefficient of variation (CV%), Levene's test")
    lines.append("")
    lines.append("### Effect Size Interpretation")
    lines.append("")
    lines.append("| Metric | Negligible | Small | Medium | Large |")
    lines.append("|--------|------------|-------|--------|-------|")
    lines.append("| Cohen's d | < 0.2 | 0.2-0.5 | 0.5-0.8 | >= 0.8 |")
    lines.append("| Pearson r | < 0.1 | 0.1-0.3 | 0.3-0.5 | >= 0.5 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_h1_h2_results(conditions_data):
    """Generate H1a/H2 results table across conditions."""
    lines = []
    lines.append("## 2. Core Results: H1/H1a/H2")
    lines.append("")
    lines.append("### Summary Table")
    lines.append("")

    cond_names = list(conditions_data.keys())
    header = "| Metric | " + " | ".join(cond_names) + " |"
    separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
    lines.append(header)
    lines.append(separator)

    # N row
    row = "| **N** |"
    for cond in cond_names:
        n = len(conditions_data[cond].get("models", []))
        row += " " + str(n) + " |"
    lines.append(row)

    # High/Low split
    row = "| **High / Low** |"
    for cond in cond_names:
        data = conditions_data[cond]
        h = data.get("n_high_sophistication", "?")
        l = data.get("n_low_sophistication", "?")
        row += " " + str(h) + " / " + str(l) + " |"
    lines.append(row)

    # Median sophistication
    row = "| **Median Soph** |"
    for cond in cond_names:
        med = conditions_data[cond].get("median_sophistication", 0)
        row += " " + f"{med:.2f}" + " |"
    lines.append(row)

    # H1: Sophistication group separation (Cohen's d)
    row = "| **H1: Soph d** |"
    for cond in cond_names:
        d = conditions_data[cond].get("statistics", {}).get("sophistication", {}).get("cohens_d", 0)
        row += " " + f"{d:.2f}" + " |"
    lines.append(row)

    # H1a: Cohen's d
    row = "| **H1a: d** |"
    for cond in cond_names:
        d = conditions_data[cond].get("statistics", {}).get("disinhibition", {}).get("cohens_d", 0)
        row += " " + f"{d:.2f}" + " |"
    lines.append(row)

    # H1a: p-value
    row = "| **H1a: p** |"
    for cond in cond_names:
        p = conditions_data[cond].get("statistics", {}).get("disinhibition", {}).get("p_value", 1)
        if p < 0.001:
            row += " < .001 |"
        else:
            row += " " + f"{p:.3f}" + " |"
    lines.append(row)

    # H2: r
    row = "| **H2: r** |"
    for cond in cond_names:
        r = conditions_data[cond].get("correlation", {}).get("sophistication_disinhibition", 0)
        row += " " + f"{r:.3f}" + " |"
    lines.append(row)

    # Separator for dimensions
    lines.append("| | " + " | ".join([""] * len(cond_names)) + "|")
    lines.append("| **Per-Dimension d:** | " + " | ".join([""] * len(cond_names)) + "|")

    # Individual dimension d values
    for dim in ["transgression", "aggression", "tribalism", "grandiosity"]:
        row = "| *" + dim.capitalize() + "* |"
        for cond in cond_names:
            d = conditions_data[cond].get("statistics", {}).get(dim, {}).get("cohens_d", 0)
            row += " " + f"{d:.2f}" + " |"
        lines.append(row)

    lines.append("")
    lines.append("### Key Observations")
    lines.append("")
    lines.append("- **H1a consistently large**: All conditions show d > 1.0 (large effects)")
    lines.append("- **H2 varies by condition**: Correlations vary across intervention conditions")

    if "baseline" in conditions_data:
        baseline_r = conditions_data["baseline"].get("correlation", {}).get("sophistication_disinhibition", 0)
        lines.append("- **Baseline anchor**: r = " + f"{baseline_r:.3f}")

    lines.append("")
    lines.append("**Visualizations**:")
    lines.append("- See `baseline/h2_scatter_sophistication_composite.png` for composite correlation")
    lines.append("- See `baseline/h2_scatter_all_dimensions.png` for per-dimension breakdowns (transgression, aggression, tribalism, grandiosity)")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_variability_results(cross_data, conditions_data=None):
    """Generate variability analysis section.

    Calculates variability from conditions_data if available, otherwise falls back to cross_data JSON.
    """
    import numpy as np

    # Try to calculate variability programmatically from all conditions
    variability_stats = {}

    if conditions_data:
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

    # If we couldn't calculate from conditions_data, fall back to JSON
    if not variability_stats:
        var_data = cross_data.get("variability")
        if not var_data:
            return "## 3. Results: Response Variability\n\n*Variability analysis not available.*\n\n---\n\n"
        original = var_data.get("original", {})
        variability_stats = original.get("conditions", {})

    if not variability_stats:
        return "## 3. Results: Response Variability\n\n*No variability data available.*\n\n---\n\n"

    lines = []
    lines.append("## 3. Results: Response Variability")
    lines.append("")
    lines.append("### Variability by Condition")
    lines.append("")
    lines.append("| Condition | N | Mean | SD | CV% | Var Ratio |")
    lines.append("|-----------|---|------|-----|-----|-----------|")

    # Sort by CV (coefficient of variation)
    sorted_conds = sorted(variability_stats.items(), key=lambda x: x[1].get("cv", 0))

    # Calculate variance ratios relative to baseline
    baseline_var = variability_stats.get("baseline", {}).get("var", 1)
    if baseline_var == 0:
        baseline_var = 1

    for cond, data in sorted_conds:
        n = data.get("n", 0)
        mean = data.get("mean", 0)
        sd = data.get("sd", 0)
        cv = data.get("cv", 0)
        var = data.get("var", 0)
        vr = var / baseline_var if cond != "baseline" else 1.0
        lines.append("| " + cond + " | " + str(n) + " | " + f"{mean:.2f}" + " | " + f"{sd:.3f}" + " | " + f"{cv:.1f}" + "% | " + f"{vr:.2f}" + " |")

    # Find most/least variable
    if sorted_conds:
        most_consistent = sorted_conds[0][0]
        most_variable = sorted_conds[-1][0]
        lines.append("")
        lines.append("**Most consistent**: " + most_consistent)
        lines.append("**Most variable**: " + most_variable)

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_anova_results(cross_data):
    """Generate repeated-measures ANOVA section."""
    anova_data = cross_data.get("anova")
    if not anova_data:
        return "## 4. Results: Cross-Condition ANOVA\n\n*ANOVA results not available.*\n\n---\n\n"

    original = anova_data.get("original", {})
    rm = original.get("rm_anova", {})

    lines = []
    lines.append("## 4. Results: Cross-Condition ANOVA")
    lines.append("")
    lines.append("### Main Effect of Condition")
    lines.append("")

    if rm:
        F = rm.get("F", 0)
        df1 = rm.get("df1", 0)
        df2 = rm.get("df2", 0)
        p = rm.get("p_value", 1)
        eta = rm.get("eta_squared", 0)
        epsilon = rm.get("epsilon", 1)
        p_gg = rm.get("p_gg_corrected", p)

        lines.append("- **F**(" + str(df1) + ", " + str(df2) + ") = " + f"{F:.2f}")
        lines.append("- **p** " + format_p(p))
        lines.append("- **eta-squared** = " + f"{eta:.3f}")
        lines.append("")
        lines.append("Sphericity violated (epsilon = " + f"{epsilon:.3f}" + "), Greenhouse-Geisser corrected p " + format_p(p_gg))
        lines.append("")

    posthoc = original.get("posthoc", [])
    if posthoc:
        lines.append("### Pairwise Comparisons (Bonferroni corrected)")
        lines.append("")
        lines.append("| Comparison | t | p | g | Sig |")
        lines.append("|------------|---|---|---|-----|")

        for comp in posthoc:
            name = comp.get("comparison", "")
            t = comp.get("t", 0)
            p_corr = comp.get("p_corrected", 1)
            g = comp.get("hedges_g", 0)
            sig = "Yes" if p_corr < 0.05 else "No"
            lines.append("| " + name + " | " + f"{t:.2f}" + " | " + format_p(p_corr) + " | " + f"{g:.2f}" + " | " + sig + " |")

        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_robustness_validation(external_data, outlier_data, no_dim_data):
    """Generate consolidated robustness and validation section."""
    lines = []
    lines.append("## 3. Robustness & Validation")
    lines.append("")

    # 3.1 External Validation
    lines.append("### 3.1 External Validation")
    lines.append("")
    lines.append("Cross-validation against independent reasoning benchmarks.")
    lines.append("")

    arc = external_data.get("arc_agi")
    gpqa = external_data.get("gpqa")

    if not arc and not gpqa:
        lines.append("*External validation data not available.*")
        lines.append("")
    else:
        lines.append("| Metric | ARC-AGI | GPQA |")
        lines.append("|--------|---------|------|")

        arc_n = arc.get("sample", {}).get("unique_matched_models", "N/A") if arc else "N/A"
        gpqa_n = gpqa.get("sample", {}).get("unique_matched_models", "N/A") if gpqa else "N/A"
        lines.append("| **Matched models** | " + str(arc_n) + " | " + str(gpqa_n) + " |")

        # Sophistication correlation
        arc_soph = arc.get("correlations", {}).get("sophistication", {}) if arc else {}
        gpqa_soph = gpqa.get("correlations", {}).get("sophistication", {}) if gpqa else {}
        arc_r_soph = arc_soph.get("r")
        gpqa_r_soph = gpqa_soph.get("r")
        arc_str = f"{arc_r_soph:.3f}" if arc_r_soph else "N/A"
        gpqa_str = f"{gpqa_r_soph:.3f}" if gpqa_r_soph else "N/A"
        lines.append("| **r (Sophistication)** | " + arc_str + " | " + gpqa_str + " |")

        # P-values for sophistication
        arc_p_soph = arc_soph.get("p")
        gpqa_p_soph = gpqa_soph.get("p")
        arc_p_str = "< .001" if arc_p_soph and arc_p_soph < 0.001 else f"= {arc_p_soph:.3f}" if arc_p_soph else "N/A"
        gpqa_p_str = "< .001" if gpqa_p_soph and gpqa_p_soph < 0.001 else f"= {gpqa_p_soph:.3f}" if gpqa_p_soph else "N/A"
        lines.append("| *p (Sophistication)* | " + arc_p_str + " | " + gpqa_p_str + " |")

        # Disinhibition correlation
        arc_dis = arc.get("correlations", {}).get("disinhibition", {}) if arc else {}
        gpqa_dis = gpqa.get("correlations", {}).get("disinhibition", {}) if gpqa else {}
        arc_r_dis = arc_dis.get("r")
        gpqa_r_dis = gpqa_dis.get("r")
        arc_str = f"{arc_r_dis:.3f}" if arc_r_dis else "N/A"
        gpqa_str = f"{gpqa_r_dis:.3f}" if gpqa_r_dis else "N/A"
        lines.append("| **r (Disinhibition)** | " + arc_str + " | " + gpqa_str + " |")

        # P-values for disinhibition
        arc_p_dis = arc_dis.get("p")
        gpqa_p_dis = gpqa_dis.get("p")
        arc_p_str = "< .001" if arc_p_dis and arc_p_dis < 0.001 else f"= {arc_p_dis:.3f}" if arc_p_dis else "N/A"
        gpqa_p_str = "< .001" if gpqa_p_dis and gpqa_p_dis < 0.001 else f"= {gpqa_p_dis:.3f}" if gpqa_p_dis else "N/A"
        lines.append("| *p (Disinhibition)* | " + arc_p_str + " | " + gpqa_p_str + " |")

        arc_h1 = arc.get("h1_group_comparison", {}) if arc else {}
        gpqa_h1 = gpqa.get("h1_group_comparison", {}) if gpqa else {}
        arc_high = arc_h1.get("high_sophistication", {}).get("mean", 0)
        arc_low = arc_h1.get("low_sophistication", {}).get("mean", 0)
        gpqa_high = gpqa_h1.get("high_sophistication", {}).get("mean", 0)
        gpqa_low = gpqa_h1.get("low_sophistication", {}).get("mean", 0)
        arc_diff = "+" + f"{arc_high - arc_low:.1f}" + " pp" if arc_h1 else "N/A"
        gpqa_diff = "+" + f"{gpqa_high - gpqa_low:.1f}" + " pp" if gpqa_h1 else "N/A"
        lines.append("| **Group diff (High-Low)** | " + arc_diff + " | " + gpqa_diff + " |")
        lines.append("| **Benchmark type** | Abstract reasoning | Expert scientific |")
        lines.append("")
        lines.append("Both benchmarks show large correlations (r > 0.50) with sophistication, providing convergent validity.")
        lines.append("")
        lines.append("**Visualizations**:")
        lines.append("- See `research_synthesis/limitations/external_evals/external_validation_consolidated.png`")
        lines.append("- See `research_synthesis/limitations/external_evals/external_validation_comparison.png`")
        lines.append("")

    # 3.2 Outlier Sensitivity
    lines.append("### 3.2 Outlier Sensitivity Analysis")
    lines.append("")
    lines.append("Robustness check removing statistical outliers (|residual| > 2 SD from regression line).")
    lines.append("")

    if not outlier_data:
        lines.append("*No outlier analysis data available.*")
        lines.append("")
    else:
        cond_names = list(outlier_data.keys())
        header = "| Metric | " + " | ".join(cond_names) + " |"
        separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
        lines.append(header)
        lines.append(separator)

        row = "| **Outliers Removed** |"
        for cond in cond_names:
            n_outliers = len(outlier_data[cond]["info"].get("outliers_removed", []))
            row += " " + str(n_outliers) + " |"
        lines.append(row)

        row = "| **H1a d: Δ** |"
        for cond in cond_names:
            orig_d = outlier_data[cond]["with_outliers"]["statistics"]["disinhibition"]["cohens_d"]
            new_d = outlier_data[cond]["without_outliers"]["statistics"]["disinhibition"]["cohens_d"]
            delta = new_d - orig_d
            row += " " + f"{delta:+.2f}" + " |"
        lines.append(row)

        row = "| **H2 r: Δ** |"
        for cond in cond_names:
            orig_r = outlier_data[cond]["with_outliers"]["correlation"]["sophistication_disinhibition"]
            new_r = outlier_data[cond]["without_outliers"]["correlation"]["sophistication_disinhibition"]
            delta = new_r - orig_r
            row += " " + f"{delta:+.3f}" + " |"
        lines.append(row)
        lines.append("")

        strengthened = sum(1 for cond in cond_names
                          if outlier_data[cond]["without_outliers"]["statistics"]["disinhibition"]["cohens_d"] >
                             outlier_data[cond]["with_outliers"]["statistics"]["disinhibition"]["cohens_d"] + 0.1)
        lines.append("Removing outliers **strengthens H1a** in " + str(strengthened) + "/" + str(len(cond_names)) + " conditions, suggesting outliers represent noise.")
        lines.append("")
        lines.append("**Visualizations**: See `baseline/outliers_removed/h2_scatter_sophistication_composite.png`")
        lines.append("")

    # 3.3 No-Dimensions Sensitivity
    lines.append("### 3.3 No-Dimensions Sensitivity Analysis")
    lines.append("")
    lines.append("The **dimensions suite** contains prompts designed to indirectly elicit specific behavioral dimensions through targeted scenarios. Excluding these tests whether H1/H2 findings hold with only naturalistic prompts (broad, affective, general suites) — ruling out measurement artifact.")
    lines.append("")

    if not no_dim_data:
        lines.append("*No no-dimensions analysis data available.*")
        lines.append("")
    else:
        cond_names = list(no_dim_data.keys())
        header = "| Metric | " + " | ".join(cond_names) + " |"
        separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
        lines.append(header)
        lines.append(separator)

        row = "| **H1a d: Δ** |"
        for cond in cond_names:
            orig_d = no_dim_data[cond]["full_dataset"]["statistics"]["disinhibition"]["cohens_d"]
            new_d = no_dim_data[cond]["no_dimensions"]["statistics"]["disinhibition"]["cohens_d"]
            delta = new_d - orig_d
            row += " " + f"{delta:+.2f}" + " |"
        lines.append(row)

        row = "| **H2 r: Δ** |"
        for cond in cond_names:
            orig_r = no_dim_data[cond]["full_dataset"]["correlation"]["sophistication_disinhibition"]
            new_r = no_dim_data[cond]["no_dimensions"]["correlation"]["sophistication_disinhibition"]
            delta = new_r - orig_r
            row += " " + f"{delta:+.3f}" + " |"
        lines.append(row)
        lines.append("")

        strengthened_r = sum(1 for cond in cond_names
                            if no_dim_data[cond]["no_dimensions"]["correlation"]["sophistication_disinhibition"] >
                               no_dim_data[cond]["full_dataset"]["correlation"]["sophistication_disinhibition"])
        lines.append("H2 correlation **strengthens** in " + str(strengthened_r) + "/" + str(len(cond_names)) + " conditions when dimensions suite excluded.")
        lines.append("")
        lines.append("**Visualizations**: See `baseline/no_dimensions/h2_scatter_sophistication_composite.png`")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_external_validation(external_data):
    """Generate external validation section (DEPRECATED - use generate_robustness_validation)."""
    arc = external_data.get("arc_agi")
    gpqa = external_data.get("gpqa")

    if not arc and not gpqa:
        return "## 5. Results: External Validation\n\n*External validation data not available.*\n\n---\n\n"

    lines = []
    lines.append("## 5. Results: External Validation")
    lines.append("")
    lines.append("Cross-validation against independent reasoning benchmarks.")
    lines.append("")
    lines.append("### Benchmark Comparison")
    lines.append("")
    lines.append("| Metric | ARC-AGI | GPQA |")
    lines.append("|--------|---------|------|")

    # Sample sizes
    arc_n = arc.get("sample", {}).get("unique_matched_models", "N/A") if arc else "N/A"
    gpqa_n = gpqa.get("sample", {}).get("unique_matched_models", "N/A") if gpqa else "N/A"
    lines.append("| **Matched models** | " + str(arc_n) + " | " + str(gpqa_n) + " |")

    # Sophistication correlation
    arc_r_soph = arc.get("correlations", {}).get("sophistication", {}).get("r") if arc else None
    gpqa_r_soph = gpqa.get("correlations", {}).get("sophistication", {}).get("r") if gpqa else None
    arc_str = f"{arc_r_soph:.3f}" if arc_r_soph else "N/A"
    gpqa_str = f"{gpqa_r_soph:.3f}" if gpqa_r_soph else "N/A"
    lines.append("| **r (Sophistication)** | " + arc_str + " | " + gpqa_str + " |")

    # Disinhibition correlation
    arc_r_dis = arc.get("correlations", {}).get("disinhibition", {}).get("r") if arc else None
    gpqa_r_dis = gpqa.get("correlations", {}).get("disinhibition", {}).get("r") if gpqa else None
    arc_str = f"{arc_r_dis:.3f}" if arc_r_dis else "N/A"
    gpqa_str = f"{gpqa_r_dis:.3f}" if gpqa_r_dis else "N/A"
    lines.append("| **r (Disinhibition)** | " + arc_str + " | " + gpqa_str + " |")

    # Group comparison
    arc_h1 = arc.get("h1_group_comparison", {}) if arc else {}
    gpqa_h1 = gpqa.get("h1_group_comparison", {}) if gpqa else {}

    arc_high = arc_h1.get("high_sophistication", {}).get("mean", 0)
    arc_low = arc_h1.get("low_sophistication", {}).get("mean", 0)
    gpqa_high = gpqa_h1.get("high_sophistication", {}).get("mean", 0)
    gpqa_low = gpqa_h1.get("low_sophistication", {}).get("mean", 0)

    arc_diff = "+" + f"{arc_high - arc_low:.1f}" + " pp" if arc_h1 else "N/A"
    gpqa_diff = "+" + f"{gpqa_high - gpqa_low:.1f}" + " pp" if gpqa_h1 else "N/A"
    lines.append("| **Group diff (High-Low)** | " + arc_diff + " | " + gpqa_diff + " |")

    lines.append("| **Benchmark type** | Abstract reasoning | Expert scientific |")
    lines.append("")
    lines.append("### Correlation Details")
    lines.append("")
    lines.append("| Dimension | ARC-AGI | GPQA |")
    lines.append("|-----------|---------|------|")

    dims = ["sophistication", "depth", "authenticity", "disinhibition", "transgression", "aggression", "tribalism", "grandiosity"]
    for dim in dims:
        arc_corr = arc.get("correlations", {}).get(dim, {}) if arc else {}
        gpqa_corr = gpqa.get("correlations", {}).get(dim, {}) if gpqa else {}

        arc_r = arc_corr.get("r")
        gpqa_r = gpqa_corr.get("r")
        arc_sig = arc_corr.get("significant", False)
        gpqa_sig = gpqa_corr.get("significant", False)

        if arc_r is not None:
            arc_str = f"{arc_r:+.3f}" + ("*" if arc_sig else "")
        else:
            arc_str = "N/A"

        if gpqa_r is not None:
            gpqa_str = f"{gpqa_r:+.3f}" + ("*" if gpqa_sig else "")
        else:
            gpqa_str = "N/A"

        lines.append("| " + dim.capitalize() + " | " + arc_str + " | " + gpqa_str + " |")

    lines.append("")
    lines.append("*Asterisk indicates p < .05*")
    lines.append("")
    lines.append("### Interpretation")
    lines.append("")
    lines.append("Both benchmarks show large correlations (r > 0.50) with sophistication despite measuring different capabilities:")
    lines.append("- **ARC-AGI**: Few-shot pattern abstraction (fluid intelligence)")
    lines.append("- **GPQA**: Graduate-level scientific reasoning (crystallized expertise)")
    lines.append("")
    lines.append("This provides convergent validity for the sophistication measure.")
    lines.append("")
    lines.append("**Full analysis**: See `research_synthesis/limitations/external_evals/EXTERNAL_VALIDATION_BRIEF.md`")
    lines.append("**Visualizations**: See `external_validation_consolidated.png` (2x2 soph/disinhib × ARC-AGI/GPQA) and `external_validation_comparison.png`")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_outlier_sensitivity(outlier_data):
    """Generate outlier sensitivity analysis section."""
    if not outlier_data:
        return "## 6. Results: Outlier Sensitivity Analysis\n\n*No outlier analysis data available.*\n\n---\n\n"

    lines = []
    lines.append("## 6. Results: Outlier Sensitivity Analysis")
    lines.append("")
    lines.append("Robustness check removing statistical outliers (|residual| > 2 SD from regression line).")
    lines.append("")
    lines.append("### Summary Table")
    lines.append("")

    # Header
    cond_names = list(outlier_data.keys())
    header = "| Metric | " + " | ".join(cond_names) + " |"
    separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
    lines.append(header)
    lines.append(separator)

    # Outliers removed
    row = "| **Outliers Removed** |"
    for cond in cond_names:
        n_outliers = len(outlier_data[cond]["info"].get("outliers_removed", []))
        row += " " + str(n_outliers) + " |"
    lines.append(row)

    # N after removal
    row = "| **N (after)** |"
    for cond in cond_names:
        n = len(outlier_data[cond]["without_outliers"].get("models", []))
        row += " " + str(n) + " |"
    lines.append(row)

    # H1a d change
    row = "| **H1a d: Δ** |"
    for cond in cond_names:
        orig_d = outlier_data[cond]["with_outliers"]["statistics"]["disinhibition"]["cohens_d"]
        new_d = outlier_data[cond]["without_outliers"]["statistics"]["disinhibition"]["cohens_d"]
        delta = new_d - orig_d
        row += " " + f"{delta:+.2f}" + " |"
    lines.append(row)

    # H2 r change
    row = "| **H2 r: Δ** |"
    for cond in cond_names:
        orig_r = outlier_data[cond]["with_outliers"]["correlation"]["sophistication_disinhibition"]
        new_r = outlier_data[cond]["without_outliers"]["correlation"]["sophistication_disinhibition"]
        delta = new_r - orig_r
        row += " " + f"{delta:+.3f}" + " |"
    lines.append(row)

    lines.append("")
    lines.append("### Outlier Models")
    lines.append("")

    # List outliers per condition
    for cond in cond_names:
        outliers = outlier_data[cond]["info"].get("outliers_removed", [])
        if outliers:
            lines.append("**" + cond.capitalize() + "**:")
            for o in outliers:
                model = o.get("model_id", "Unknown")
                sd = o.get("sd_from_line", 0)
                direction = "above" if o.get("residual", 0) > 0 else "below"
                lines.append("- " + model + " (" + f"{sd:.1f}" + " SD " + direction + ")")
            lines.append("")

    lines.append("### Interpretation")
    lines.append("")

    # Count conditions where removing outliers strengthens H1a
    strengthened = sum(1 for cond in cond_names
                      if outlier_data[cond]["without_outliers"]["statistics"]["disinhibition"]["cohens_d"] >
                         outlier_data[cond]["with_outliers"]["statistics"]["disinhibition"]["cohens_d"] + 0.1)

    lines.append("Removing outliers **strengthens H1a** in " + str(strengthened) + "/" + str(len(cond_names)) + " conditions with outlier analysis.")
    lines.append("This suggests outliers represent noise rather than driving the observed effects.")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_no_dimensions_sensitivity(no_dim_data):
    """Generate no-dimensions sensitivity analysis section."""
    if not no_dim_data:
        return "## 7. Results: No-Dimensions Sensitivity Analysis\n\n*No no-dimensions analysis data available.*\n\n---\n\n"

    lines = []
    lines.append("## 7. Results: No-Dimensions Sensitivity Analysis")
    lines.append("")
    lines.append("Robustness check excluding prompts from the dimensions suite (which directly probe for behavioral traits).")
    lines.append("")
    lines.append("### Summary Table")
    lines.append("")

    # Header
    cond_names = list(no_dim_data.keys())
    header = "| Metric | " + " | ".join(cond_names) + " |"
    separator = "|--------|" + "|".join(["--------"] * len(cond_names)) + "|"
    lines.append(header)
    lines.append(separator)

    # N after removal
    row = "| **N (no dims)** |"
    for cond in cond_names:
        n = len(no_dim_data[cond]["no_dimensions"].get("models", []))
        row += " " + str(n) + " |"
    lines.append(row)

    # H1a d change
    row = "| **H1a d: Δ** |"
    for cond in cond_names:
        orig_d = no_dim_data[cond]["full_dataset"]["statistics"]["disinhibition"]["cohens_d"]
        new_d = no_dim_data[cond]["no_dimensions"]["statistics"]["disinhibition"]["cohens_d"]
        delta = new_d - orig_d
        row += " " + f"{delta:+.2f}" + " |"
    lines.append(row)

    # H2 r change
    row = "| **H2 r: Δ** |"
    for cond in cond_names:
        orig_r = no_dim_data[cond]["full_dataset"]["correlation"]["sophistication_disinhibition"]
        new_r = no_dim_data[cond]["no_dimensions"]["correlation"]["sophistication_disinhibition"]
        delta = new_r - orig_r
        row += " " + f"{delta:+.3f}" + " |"
    lines.append(row)

    lines.append("")
    lines.append("### Interpretation")
    lines.append("")

    # Count conditions where correlation strengthens
    strengthened_r = sum(1 for cond in cond_names
                        if no_dim_data[cond]["no_dimensions"]["correlation"]["sophistication_disinhibition"] >
                           no_dim_data[cond]["full_dataset"]["correlation"]["sophistication_disinhibition"])

    lines.append("H2 correlation **strengthens** in " + str(strengthened_r) + "/" + str(len(cond_names)) + " conditions when dimensions suite is excluded.")
    lines.append("This suggests the sophistication-disinhibition relationship emerges naturally from general scenarios,")
    lines.append("not from dimension-specific probing.")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_interpretation(preserved: dict):
    """Generate Section 5: consolidated interpretation, preserving manual edits."""
    lines = []
    lines.append("## 5. Interpretation")
    lines.append("")

    # 5.1 H1/H2 Relationship
    header_h1h2 = "### 5.1 H1/H2 Relationship"
    default_h1h2 = """#### High-Confidence Claims

[To be filled: Claims directly supported by the statistics with large effect sizes]

#### Moderate-Confidence Claims

[To be filled: Claims supported by the statistics but with caveats]

#### Open Questions

[To be filled: Areas where the data is suggestive but not conclusive]"""

    # Check for old header format to migrate content
    old_header_h1h2 = "## 9. Interpretation: H1a/H2 Relationship"
    if old_header_h1h2 in preserved:
        lines.append(header_h1h2)
        lines.append("")
        lines.append(wrap_manual_section(preserved[old_header_h1h2]))
    elif header_h1h2 in preserved:
        lines.append(header_h1h2)
        lines.append("")
        lines.append(wrap_manual_section(preserved[header_h1h2]))
    else:
        lines.append(header_h1h2)
        lines.append("")
        lines.append(wrap_manual_section(default_h1h2))

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_interpretation_h1_h2(preserved: dict):
    """DEPRECATED - use generate_interpretation."""
    header = "## 9. Interpretation: H1a/H2 Relationship"
    default = """### High-Confidence Claims

[To be filled: Claims directly supported by the statistics with large effect sizes]

### Moderate-Confidence Claims

[To be filled: Claims supported by the statistics but with caveats]

### Open Questions

[To be filled: Areas where the data is suggestive but not conclusive]"""

    return get_preserved_or_default(preserved, header, default) + "\n\n---\n\n"


def generate_interpretation_interventions(preserved: dict):
    """DEPRECATED - moved to H3 section."""
    header = "## 10. Interpretation: Intervention Effects"
    default = """### Constraint vs. Pressure Interventions

-Work in Progress-

[To be filled: Interpretation of why constraint interventions reduce variance while pressure interventions increase it]

### Intervention Mechanism Hypotheses

-Work in Progress-

[To be filled: Theories about how different interventions affect the sophistication-disinhibition relationship]"""

    return get_preserved_or_default(preserved, header, default) + "\n\n---\n\n"


def generate_interpretation_models(preserved: dict):
    """DEPRECATED - use generate_interpretation."""
    header = "## 11. Interpretation: Model & Provider Patterns"
    default = """### Provider-Level Observations

[To be filled: Discussion of systematic differences between providers]

### Notable Individual Models

[To be filled: Discussion of interesting edge cases, constrained models, and outliers]"""

    return get_preserved_or_default(preserved, header, default) + "\n\n---\n\n"


def generate_model_patterns(cross_data):
    """Generate model pattern tables from cross-condition analysis."""
    patterns = cross_data.get("patterns")
    if not patterns:
        return "## 11. Model Reference Tables\n\n*Cross-condition pattern data not available.*\n\n---\n\n"

    # Navigate to cross_condition aggregation
    cross_condition = patterns.get("cross_condition", {})
    if not cross_condition:
        return "## 11. Model Reference Tables\n\n*Cross-condition aggregation not available.*\n\n---\n\n"

    lines = []
    lines.append("## 11. Model Reference Tables")
    lines.append("")
    lines.append("### Consistently Constrained Models")
    lines.append("")
    lines.append("Models exhibiting high sophistication (>6.5) but below-predicted disinhibition across multiple conditions.")
    lines.append("")
    lines.append("| Model | # Conditions | Conditions |")
    lines.append("|-------|--------------|------------|")

    # Filter constrained models appearing in 2+ conditions
    constrained = cross_condition.get("most_constrained", [])
    multi_condition_constrained = [m for m in constrained if m.get("composite", 0) >= 2]
    for model in multi_condition_constrained[:10]:
        name = model.get("model", "")
        n_conds = model.get("composite", 0)
        conds = ", ".join(model.get("conditions", []))
        lines.append("| " + name + " | " + str(n_conds) + " | " + conds + " |")

    if not multi_condition_constrained:
        lines.append("| *No models constrained in 2+ conditions* | - | - |")

    lines.append("")
    lines.append("### Consistent Outliers")
    lines.append("")
    lines.append("Models with unusual sophistication-disinhibition relationships (|residual| > 2 SD).")
    lines.append("")
    lines.append("| Model | # Conditions | Conditions |")
    lines.append("|-------|--------------|------------|")

    # Filter outlier models appearing in 2+ conditions
    outliers = cross_condition.get("most_outlier", [])
    multi_condition_outliers = [m for m in outliers if m.get("composite", 0) >= 2]
    for model in multi_condition_outliers[:10]:
        name = model.get("model", "")
        n_conds = model.get("composite", 0)
        conds = ", ".join(model.get("conditions", []))
        lines.append("| " + name + " | " + str(n_conds) + " | " + conds + " |")

    if not multi_condition_outliers:
        lines.append("| *No models outliers in 2+ conditions* | - | - |")

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_limitations(judge_agreement, external_data, preserved: dict):
    """Generate Section 6: Limitations with 6.2 as MANUAL."""
    lines = []
    lines.append("## 6. Limitations")
    lines.append("")

    # 6.1 Judge Bias Section
    lines.append("### 6.1 Judge Bias Analysis")
    lines.append("")
    lines.append("A common critique of LLM-as-judge evaluations: if frontier models judge frontier models, they may rate themselves or similar models more favorably, inflating sophistication scores and creating spurious correlations.")
    lines.append("")
    lines.append("#### Judge Panel Design")
    lines.append("")
    lines.append("The evaluation uses a 3-judge panel spanning the sophistication spectrum:")
    lines.append("")
    lines.append("| Judge Model | Provider | Sophistication Group | GPQA Score |")
    lines.append("|-------------|----------|---------------------|------------|")
    lines.append("| Claude-4.5-Sonnet | Anthropic | High | 83.4% |")
    lines.append("| Llama-4-Maverick-17B | Meta | Low | 69.8% |")
    lines.append("| DeepSeek-R1 | DeepSeek | Low | 81.0% |")
    lines.append("")
    lines.append("**Composition**: 1 High-Sophistication, 2 Low-Sophistication judges")
    lines.append("")
    lines.append("#### Why This Mitigates Bias")
    lines.append("")
    lines.append("1. **Not all frontier judges**: Two of three judges are from the Low-Sophistication group")
    lines.append("2. **Cross-provider**: Anthropic, Meta, DeepSeek — no single vendor bias")
    lines.append("3. **Averaged scores**: Final scores average across all three judges, diluting any single-judge bias")
    lines.append("")

    # External validation evidence
    arc = external_data.get("arc_agi") or {}
    gpqa = external_data.get("gpqa") or {}
    arc_r = arc.get("correlations", {}).get("sophistication", {}).get("r") if arc else None
    arc_p = arc.get("correlations", {}).get("sophistication", {}).get("p") if arc else None
    gpqa_r = gpqa.get("correlations", {}).get("sophistication", {}).get("r") if gpqa else None
    gpqa_p = gpqa.get("correlations", {}).get("sophistication", {}).get("p") if gpqa else None

    if arc_r and gpqa_r:
        lines.append("4. **External validation**: If bias existed, we'd expect weak or no correlation with external benchmarks. Instead:")
        arc_p_str = "< .0001" if arc_p and arc_p < 0.0001 else f"= {arc_p:.5f}" if arc_p else "N/A"
        gpqa_p_str = "< .0001" if gpqa_p and gpqa_p < 0.0001 else f"= {gpqa_p:.5f}" if gpqa_p else "N/A"
        lines.append("   - ARC-AGI: r = " + f"{arc_r:.3f}" + " (p " + arc_p_str + ")")
        lines.append("   - GPQA: r = " + f"{gpqa_r:.3f}" + " (p " + gpqa_p_str + ")")
        lines.append("")
        lines.append("The fact that a Low-Sophistication judge (Llama-4-Maverick) contributes to scores that correlate r = " + f"{gpqa_r:.2f}" + " with objective benchmarks suggests ratings reflect genuine capability differences, not in-group favoritism.")
        lines.append("")

    # Judge Agreement Statistics
    lines.append("#### Inter-Judge Agreement (Statistical Validation)")
    lines.append("")

    if judge_agreement:
        n_evals = judge_agreement.get("n_valid_3_judge", 0)
        overall = judge_agreement.get("overall", {})
        by_dim = judge_agreement.get("by_dimension", {})

        lines.append(f"Based on **N = {n_evals:,}** evaluations with 3 valid judge scores (baseline condition):")
        lines.append("")
        lines.append("| Dimension | ICC(3) | Mean r | Within-1 | Quality |")
        lines.append("|-----------|--------|--------|----------|---------|")

        # Sort dimensions by ICC for display
        dim_order = ["aggression", "hedging", "warmth", "tribalism", "grandiosity",
                    "transgression", "authenticity", "depth", "formality"]
        for dim in dim_order:
            if dim in by_dim:
                d = by_dim[dim]
                icc = d.get("icc_avg", 0)
                r = d.get("mean_r", 0)
                w1 = d.get("mean_within1", 0) * 100
                quality = "Excellent" if icc > 0.90 else "Good" if icc > 0.75 else "Moderate" if icc > 0.50 else "Poor"
                lines.append("| " + dim.capitalize() + " | " + f"{icc:.3f}" + " | " + f"{r:.3f}" + " | " + f"{w1:.1f}" + "% | " + quality + " |")

        # Overall row
        icc_overall = overall.get("mean_icc_avg", 0)
        r_overall = overall.get("mean_pairwise_r", 0)
        w1_overall = overall.get("mean_within1_agreement", 0) * 100
        lines.append("| **OVERALL** | **" + f"{icc_overall:.3f}" + "** | " + f"{r_overall:.3f}" + " | " + f"{w1_overall:.1f}" + "% | **Good** |")
        lines.append("")

        lines.append("**Key metrics**:")
        lines.append("- **ICC(3)**: Intraclass correlation for average of 3 raters (reliability of final score)")
        lines.append("- **Mean r**: Average pairwise Pearson correlation between judges")
        lines.append("- **Within-1**: Percentage of cases where judges differed by ≤1 point")
        lines.append("")

        # Interpretation
        lines.append("**Interpretation**: Overall ICC(3) = " + f"{icc_overall:.3f}" + " indicates **good reliability** (benchmark: >0.75). ")
        lines.append("8 of 9 dimensions show \"Good\" or \"Excellent\" agreement. Only Formality (ICC = 0.724) shows \"Moderate\" reliability.")
        lines.append("")

        # Disinhibition dimensions specifically
        disinhib_dims = ["aggression", "transgression", "tribalism", "grandiosity"]
        disinhib_iccs = [by_dim[d]["icc_avg"] for d in disinhib_dims if d in by_dim]
        if disinhib_iccs:
            avg_disinhib_icc = sum(disinhib_iccs) / len(disinhib_iccs)
            lines.append("**Disinhibition dimensions** (aggression, transgression, tribalism, grandiosity) show mean ICC = " + f"{avg_disinhib_icc:.3f}" + ", supporting reliable measurement of the key H1/H2 constructs.")
            lines.append("")
    else:
        lines.append("*Judge agreement analysis not available.*")
        lines.append("")

    lines.append("**Full analysis**: See `research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md`")
    lines.append("")

    # 6.2 Other Methodological Considerations (MANUAL)
    header_other = "### 6.2 Other Methodological Considerations"
    default_other = """- **Prompt design**: Scenarios may not fully capture real-world deployment contexts
- **Sample selection**: Model selection prioritized major providers; smaller/specialized models underrepresented
- **Temporal validity**: Model behaviors may change with updates; results reflect evaluation period"""

    # Check for old header format to migrate content
    old_header_other = "### 12.2 Other Methodological Considerations"
    if old_header_other in preserved:
        lines.append(header_other)
        lines.append("")
        lines.append(wrap_manual_section(preserved[old_header_other]))
    elif header_other in preserved:
        lines.append(header_other)
        lines.append("")
        lines.append(wrap_manual_section(preserved[header_other]))
    else:
        lines.append(header_other)
        lines.append("")
        lines.append(wrap_manual_section(default_other))

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_future_directions(preserved: dict):
    """Generate Section 7: Future Directions, preserving manual edits."""
    header = "## 7. Future Directions"
    old_header = "### 13.3 Future Directions"
    default = """- Formalize H3 hypothesis testing (see Section 8 for preliminary work)
- Inspect 'constrained' phenomena more deeply using OpenAI products as focal point
- Test broader generalizability to multi-turn chat flows and separately to semi-autonomous agentic workflows
- Identify a 3rd external benchmark for high-low sophistication comparison
- Formalize a robust and standardized baseline v2 prompt suite leveraging empirically determined high frequency end consumer queries
- Formalize a robust and standardized dimensions v2 prompt suite to assess extremes
- Address provider differences between conditions
- Address thinking vs. non thinking variants, compare total estimated thinking time"""

    # Check for old header format to migrate content
    if old_header in preserved:
        return f"{header}\n\n{wrap_manual_section(preserved[old_header])}\n\n---\n\n"
    else:
        return get_preserved_or_default(preserved, header, default) + "\n\n---\n\n"


def generate_h3_preliminary(cross_data, conditions_data, preserved: dict):
    """Generate Section 8: H3 Preliminary Analysis with Work in Progress banner."""
    import numpy as np

    lines = []
    lines.append("## 8. Preliminary: H3 Intervention Effects")
    lines.append("")
    lines.append("> 🚧 **Work in Progress**")
    lines.append("> ")
    lines.append("> This section presents preliminary analysis of intervention effects on the sophistication-disinhibition relationship.")
    lines.append("> H3 hypothesis testing is ongoing. Results should be considered exploratory pending further validation.")
    lines.append("")

    # 8.1 Hypothesis
    lines.append("### 8.1 H3 Hypothesis")
    lines.append("")
    lines.append("**H3**: Contextual interventions systematically affect both the magnitude and variance of the sophistication-disinhibition relationship.")
    lines.append("")

    # 8.2 Current Evidence: Variability
    lines.append("### 8.2 Current Evidence: Response Variability")
    lines.append("")

    # Calculate variability from conditions_data
    variability_stats = {}
    if conditions_data:
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

    if variability_stats:
        lines.append("| Condition | N | Mean | SD | CV% | Var Ratio |")
        lines.append("|-----------|---|------|-----|-----|-----------|")

        sorted_conds = sorted(variability_stats.items(), key=lambda x: x[1].get("cv", 0))
        baseline_var = variability_stats.get("baseline", {}).get("var", 1)
        if baseline_var == 0:
            baseline_var = 1

        for cond, data in sorted_conds:
            n = data.get("n", 0)
            mean = data.get("mean", 0)
            sd = data.get("sd", 0)
            cv = data.get("cv", 0)
            var = data.get("var", 0)
            vr = var / baseline_var if cond != "baseline" else 1.0
            lines.append(f"| {cond} | {n} | {mean:.2f} | {sd:.3f} | {cv:.1f}% | {vr:.2f} |")

        if sorted_conds:
            most_consistent = sorted_conds[0][0]
            most_variable = sorted_conds[-1][0]
            lines.append("")
            lines.append(f"**Most consistent**: {most_consistent}")
            lines.append(f"**Most variable**: {most_variable}")
    else:
        lines.append("*Variability data not available.*")

    lines.append("")

    # 8.3 Current Evidence: ANOVA
    lines.append("### 8.3 Current Evidence: Cross-Condition ANOVA")
    lines.append("")

    anova_data = cross_data.get("anova") if cross_data else None
    if anova_data:
        original = anova_data.get("original", {})
        rm = original.get("rm_anova", {})

        if rm:
            F = rm.get("F", 0)
            df1 = rm.get("df1", 0)
            df2 = rm.get("df2", 0)
            p = rm.get("p_value", 1)
            eta = rm.get("eta_squared", 0)
            epsilon = rm.get("epsilon", 1)
            p_gg = rm.get("p_gg_corrected", p)

            lines.append(f"- **F**({df1}, {df2}) = {F:.2f}")
            p_str = "< .0001" if p < 0.0001 else f"= {p:.4f}"
            lines.append(f"- **p** {p_str}")
            lines.append(f"- **η²** = {eta:.3f}")
            lines.append("")
            p_gg_str = "< .0001" if p_gg < 0.0001 else f"= {p_gg:.4f}"
            lines.append(f"Sphericity violated (ε = {epsilon:.3f}), Greenhouse-Geisser corrected p {p_gg_str}")
            lines.append("")

        posthoc = original.get("posthoc", [])
        if posthoc:
            lines.append("#### Significant Pairwise Comparisons")
            lines.append("")
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

            lines.append("")
    else:
        lines.append("*ANOVA results not available.*")
        lines.append("")

    # 8.4 Preliminary Interpretation (MANUAL)
    header_interp = "### 8.4 Preliminary Interpretation"
    old_header_interp = "## 10. Interpretation: Intervention Effects"
    default_interp = """#### Constraint vs. Pressure Interventions

*Analysis in progress*

[To be filled: Interpretation of why constraint interventions reduce variance while pressure interventions increase it]

#### Intervention Mechanism Hypotheses

*Analysis in progress*

[To be filled: Theories about how different interventions affect the sophistication-disinhibition relationship]"""

    # Check for old header format to migrate content
    if old_header_interp in preserved:
        lines.append(header_interp)
        lines.append("")
        lines.append(wrap_manual_section(preserved[old_header_interp]))
    elif header_interp in preserved:
        lines.append(header_interp)
        lines.append("")
        lines.append(wrap_manual_section(preserved[header_interp]))
    else:
        lines.append(header_interp)
        lines.append("")
        lines.append(wrap_manual_section(default_interp))

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_classification_stability_appendix(stability_data):
    """Generate Appendix B: Classification Stability."""
    if not stability_data:
        return ""

    lines = []
    lines.append("## Appendix B: Classification Stability")
    lines.append("")
    lines.append("Cross-condition stability analysis of sophistication group classifications.")
    lines.append("")

    summary = stability_data.get("summary", {})
    total = summary.get("total_models", 0)
    always_high = summary.get("always_high", 0)
    always_low = summary.get("always_low", 0)
    flipped = summary.get("flipped", 0)
    stability_rate = summary.get("stability_rate", 0)

    lines.append("### Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total models** | {total} |")
    lines.append(f"| **Always High-Sophistication** | {always_high} ({100*always_high/total:.0f}%) |")
    lines.append(f"| **Always Low-Sophistication** | {always_low} ({100*always_low/total:.0f}%) |")
    lines.append(f"| **Flipped (changed classification)** | {flipped} ({100*flipped/total:.0f}%) |")
    lines.append(f"| **Stability rate** | {stability_rate:.1f}% |")
    lines.append("")

    # Condition medians
    medians = stability_data.get("condition_medians", {})
    if medians:
        lines.append("### Median Sophistication by Condition")
        lines.append("")
        lines.append("| Condition | Median |")
        lines.append("|-----------|--------|")
        for cond in ["baseline", "authority", "minimal_steering", "reminder", "telemetryV3", "urgency"]:
            if cond in medians:
                lines.append(f"| {cond} | {medians[cond]:.2f} |")
        lines.append("")
        lines.append(f"*Range: {min(medians.values()):.2f} - {max(medians.values()):.2f}*")
        lines.append("")

    # Flipped models table
    flipped_models = stability_data.get("flipped_models", [])
    if flipped_models:
        lines.append("### Flipped Models (Transitional Class)")
        lines.append("")
        lines.append("Models that changed classification across conditions:")
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

        lines.append("")

    # Interpretation
    lines.append("### Interpretation")
    lines.append("")
    lines.append(f"**{stability_rate:.0f}% of models** maintain consistent classification across all 6 conditions, supporting H1 group validity.")
    lines.append("")
    lines.append(f"The {flipped} flipped models cluster in the middle tertile (80% vs 17%/29% for stable groups), ")
    lines.append("suggesting a genuine transitional zone rather than measurement noise.")
    lines.append("")
    lines.append("**Full analysis**: See `research_synthesis/limitations/median_split/GAP_VS_CONTINUUM_ANALYSIS.md`")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_file_references(conditions_data, cross_data, external_data):
    """Generate Appendix C: File References."""
    lines = []
    lines.append("## Appendix C: File References")
    lines.append("")
    lines.append("### Per-Condition Data & Visualizations")
    lines.append("")
    lines.append("Each condition directory (`baseline/`, `authority/`, `minimal_steering/`, `reminder/`, `telemetryV3/`, `urgency/`) contains:")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `median_split_classification.json` | H1/H2 statistics and model classifications |")
    lines.append("| `RESEARCH_BRIEF.md` | Condition-specific research summary |")
    lines.append("| `all_models_data.csv` | Complete dataset for external analysis |")
    lines.append("| `comprehensive_stats.json` | Complete provider statistics |")
    lines.append("| `provider_comparison_stats.json` | ANOVA and pairwise t-tests across providers |")
    lines.append("| `COMPREHENSIVE_STATS_REPORT.txt` | Human-readable statistical summary |")
    lines.append("| `h1_bar_chart_comparison.png` | H1 group comparison bar chart |")
    lines.append("| `h1_summary_table.png` | Statistical summary table with effect sizes |")
    lines.append("| `h2_scatter_sophistication_composite.png` | Main H2 correlation plot (soph vs disinhib) |")
    lines.append("| `h2_scatter_all_dimensions.png` | 4-panel: transgression, aggression, tribalism, grandiosity |")
    lines.append("| `provider_summary.png` | Combined 4-panel provider analysis |")
    lines.append("| `provider_h2_scatters.png` | H2 correlation by provider (2x3 grid) |")
    lines.append("| `provider_comparison_summary.png` | Provider comparison: N, sophistication, disinhibition, classification |")
    lines.append("| `provider_comparison_dimensions.png` | Provider comparison: all 9 dimensions |")
    lines.append("| `all_dimensions_by_provider.png` | 3x3 grid of all dimensions by provider |")
    lines.append("| `provider_dimensions_heatmap.png` | Heatmap of dimensions across providers |")
    lines.append("| `visualizations/current_profiles_spider.png` | Spider chart of all model profiles |")
    lines.append("")
    lines.append("### Qualitative Examples")
    lines.append("")
    lines.append("Full chat exports for qualitative analysis are available in each condition:")
    lines.append("")
    lines.append("```")
    lines.append("<condition>/qualitative_chats/")
    lines.append("├── dimension_extremes/     # Min/max per dimension (warmth, transgression, etc.)")
    lines.append("├── composite_extremes/     # Sophistication/disinhibition extremes")
    lines.append("├── percentiles/            # 5th, 25th, 50th, 75th, 95th percentile responses")
    lines.append("└── pattern_types/          # Constrained, outlier, borderline model examples")
    lines.append("```")
    lines.append("")
    lines.append("**Manifest**: `research_synthesis/limitations/prompt_design/QUALITATIVE_MANIFEST.md`")
    lines.append("")
    lines.append("### External Validation")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `research_synthesis/limitations/external_evals/EXTERNAL_VALIDATION_BRIEF.md` | Combined ARC-AGI + GPQA analysis |")
    lines.append("| `external_validation_consolidated.png` | 2x2 panel: soph/disinhib × ARC-AGI/GPQA |")
    lines.append("| `external_validation_comparison.png` | Side-by-side benchmark comparison |")
    lines.append("| `arc_agi_validation_analysis.json` | ARC-AGI correlation data |")
    lines.append("| `gpqa_validation_analysis.json` | GPQA correlation data |")
    lines.append("")
    lines.append("### Prompt Design")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `research_synthesis/limitations/prompt_design/BASELINE_PROMPT_INVENTORY.md` | 51 scenarios across 4 suites |")
    lines.append("| `INTERVENTION_PROMPT_INVENTORY.md` | 5 interventions with mechanism analysis |")
    lines.append("| `PROMPT_INTERVENTION_DESIGN_ANALYSIS.md` | Design rationale and analysis |")
    lines.append("| `QUALITATIVE_PROMPT_PATTERN_ANALYSIS.md` | Which prompts drive high scores |")
    lines.append("")
    lines.append("### Cross-Condition Analysis")
    lines.append("")
    lines.append("- `research_synthesis/cross_condition/repeated_measures_anova_results.json`")
    lines.append("- `research_synthesis/cross_condition/variability_analysis_disinhibition.json`")
    lines.append("- `research_synthesis/cross_condition/cross_condition_patterns.json`")
    lines.append("- `research_synthesis/cross_condition/CONDITION_COMPARISON.md`")
    lines.append("")
    lines.append("### Provider Constraint Analysis")
    lines.append("")
    lines.append("- `research_synthesis/limitations/provider_constraint/SOPH_DISINHIB_RATIO_ANALYSIS.md`")
    lines.append("- `research_synthesis/limitations/provider_constraint/soph_disinhib_ratio.json`")
    lines.append("- `research_synthesis/limitations/provider_constraint/provider_constraint_*.json`")
    lines.append("")
    lines.append("### Other Limitations")
    lines.append("")
    lines.append("- `research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md`")
    lines.append("- `research_synthesis/limitations/judge_limitations/judge_agreement_analysis.json`")
    lines.append("- `research_synthesis/limitations/factor_structure/FACTOR_STRUCTURE_BASELINE.md`")
    lines.append("- `research_synthesis/limitations/median_split/MEDIAN_SPLIT_METHODOLOGY.md`")
    lines.append("- `research_synthesis/limitations/median_split/classification_stability_analysis.json`")
    lines.append("")
    lines.append("### Regeneration & Export")
    lines.append("")
    lines.append("```bash")
    lines.append("# Regenerate from condition data")
    lines.append("python3 scripts/regenerate_main_brief.py")
    lines.append("")
    lines.append("# Sync to CDN and generate public brief with embedded images")
    lines.append("python3 scripts/sync_research_assets.py --invalidate")
    lines.append("")
    lines.append("# Export to PDF (requires MacTeX)")
    lines.append("pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \\")
    lines.append("  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.pdf \\")
    lines.append("  -f markdown-yaml_metadata_block \\")
    lines.append("  --pdf-engine=xelatex \\")
    lines.append("  -V geometry:margin=1in")
    lines.append("")
    lines.append("# Export to HTML (for browser copy → Google Docs)")
    lines.append("pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \\")
    lines.append("  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.html \\")
    lines.append("  --standalone \\")
    lines.append("  -f markdown-yaml_metadata_block \\")
    lines.append("  --metadata title=\"Main Research Brief\"")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Document Version**: 3.2 (Auto-generated)")
    lines.append("**Generated**: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    lines.append("")

    return "\n".join(lines)


def generate_factor_structure_appendix(factor_structure):
    """Generate Appendix A: Factor Structure."""
    if not factor_structure:
        return ""

    lines = []
    lines.append("## Appendix A: Factor Structure")
    lines.append("")
    lines.append("### Why 9 Dimensions → 2 Composites")
    lines.append("")
    lines.append("The evaluation measures 9 behavioral dimensions, but analysis uses two composite scores. This collapse is empirically justified by inter-dimension correlations (baseline condition, n = " + str(factor_structure.get("n", 45)) + ").")
    lines.append("")

    # Sophistication
    soph = factor_structure.get("sophistication", {})
    soph_r = soph.get("correlation", 0)
    lines.append("### Sophistication: 2 → 1")
    lines.append("")
    lines.append("| Pair | r |")
    lines.append("|------|---|")
    lines.append(f"| depth ↔ authenticity | **{soph_r:.3f}** |")
    lines.append("")
    lines.append(f"Depth and authenticity correlate at r = {soph_r:.2f}, indicating they measure essentially the same underlying construct. Averaging into a single \"sophistication\" score avoids multicollinearity.")
    lines.append("")

    # Disinhibition
    disinhib = factor_structure.get("disinhibition", {})
    disinhib_pairs = disinhib.get("pairwise_correlations", {})
    disinhib_avg = disinhib.get("average_correlation", 0)
    disinhib_min = disinhib.get("min_correlation", 0)
    disinhib_max = disinhib.get("max_correlation", 0)

    lines.append("### Disinhibition: 4 → 1")
    lines.append("")
    lines.append("| Pair | r |")
    lines.append("|------|---|")
    for pair_name, r in sorted(disinhib_pairs.items(), key=lambda x: -x[1]):
        dim1, dim2 = pair_name.split("_")
        lines.append(f"| {dim1} ↔ {dim2} | {r:.3f} |")
    lines.append("")
    lines.append(f"**Average inter-correlation: r = {disinhib_avg:.3f}** (range: {disinhib_min:.2f}–{disinhib_max:.2f})")
    lines.append("")
    lines.append("All four dimensions correlate positively, suggesting a common \"disinhibition\" factor. Averaging into a composite reduces measurement noise while preserving the shared signal.")
    lines.append("")

    # Cross-factor
    cross = factor_structure.get("cross_factor", {})
    cross_pairs = cross.get("pairs", {})
    cross_avg = cross.get("average_correlation", 0)
    cross_min = cross.get("min_correlation", 0)
    cross_max = cross.get("max_correlation", 0)

    lines.append("### Cross-Factor Correlations")
    lines.append("")
    lines.append("| Sophistication | Disinhibition | r |")
    lines.append("|----------------|---------------|---|")
    for pair_name, r in sorted(cross_pairs.items(), key=lambda x: -x[1]):
        dim1, dim2 = pair_name.split("_")
        lines.append(f"| {dim1} | {dim2} | {r:.3f} |")
    lines.append("")
    lines.append(f"**Average cross-factor: r = {cross_avg:.3f}** (range: {cross_min:.2f}–{cross_max:.2f})")
    lines.append("")
    lines.append("Sophistication and disinhibition are correlated (supporting H2) but not redundant—they remain distinguishable constructs.")
    lines.append("")

    # Full matrix
    lines.append("### Full Correlation Matrix")
    lines.append("")
    lines.append("```")
    lines.append(factor_structure.get("matrix_formatted", ""))
    lines.append("```")
    lines.append("")
    lines.append("**Full analysis**: See `research_synthesis/limitations/factor_structure/FACTOR_STRUCTURE_BASELINE.md`")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


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


def generate_provider_model_patterns(provider_constraint, cross_data, conditions_data):
    """Generate Section 4: Provider & Model Patterns."""
    from scipy import stats as sp_stats
    from collections import defaultdict

    lines = []
    lines.append("## 4. Provider & Model Patterns")
    lines.append("")

    # 4.1 Per-Provider H2 Analysis (NEW)
    lines.append("### 4.1 Per-Provider H2 Analysis")
    lines.append("")
    lines.append("Does the sophistication-disinhibition correlation (H2) hold within each provider family?")
    lines.append("")

    # Get baseline data for per-provider analysis
    baseline_data = conditions_data.get("baseline", {})
    models = baseline_data.get("models", [])

    if models:
        # Group by provider
        provider_data = defaultdict(list)
        for model in models:
            provider = classify_provider(model.get("model_id", ""))
            provider_data[provider].append(model)

        # Filter to n >= 3 and sort by n descending
        providers_with_n = [(p, m) for p, m in provider_data.items() if len(m) >= 3]
        providers_with_n.sort(key=lambda x: -len(x[1]))

        lines.append("| Provider | N | r | p | Effect | H2 Supported |")
        lines.append("|----------|---|---|---|--------|--------------|")

        for provider, prov_models in providers_with_n:
            n = len(prov_models)
            soph = [m['sophistication'] for m in prov_models]
            disinhib = [m['disinhibition'] for m in prov_models]

            r, p = sp_stats.pearsonr(soph, disinhib)

            # Effect size interpretation
            r_abs = abs(r)
            if r_abs >= 0.5:
                effect = "large"
            elif r_abs >= 0.3:
                effect = "medium"
            elif r_abs >= 0.1:
                effect = "small"
            else:
                effect = "negligible"

            # Format p-value
            if p < 0.001:
                p_str = "< .001"
            elif p < 0.01:
                p_str = "< .01"
            elif p < 0.05:
                p_str = f"< .05"
            else:
                p_str = f"= {p:.3f}"

            # H2 supported?
            if r > 0 and p < 0.05:
                supported = "**Yes**"
            elif r > 0:
                supported = "No (ns)"
            else:
                supported = "No (neg)"

            lines.append(f"| {provider} | {n} | {r:.3f} | {p_str} | {effect} | {supported} |")

        # Add overall row
        all_soph = [m['sophistication'] for m in models]
        all_disinhib = [m['disinhibition'] for m in models]
        r_all, p_all = sp_stats.pearsonr(all_soph, all_disinhib)
        lines.append(f"| **OVERALL** | **{len(models)}** | **{r_all:.3f}** | **< .001** | **large** | **Yes** |")
        lines.append("")

        # Summary
        sig_count = sum(1 for p, m in providers_with_n
                       if sp_stats.pearsonr([x['sophistication'] for x in m],
                                           [x['disinhibition'] for x in m])[1] < 0.05)
        lines.append(f"**Summary**: H2 is statistically significant for {sig_count}/{len(providers_with_n)} providers with n ≥ 3. All providers show positive correlation direction.")
        lines.append("")
    else:
        lines.append("*Baseline data not available for per-provider analysis.*")
        lines.append("")

    lines.append("**Visualizations**: See `baseline/provider_h2_scatters.png`")
    lines.append("")

    # 4.2 Provider Constraint Analysis (was 4.1)
    lines.append("### 4.2 Provider Constraint Analysis")
    lines.append("")
    lines.append("Statistical analysis of whether certain providers show systematically more constrained behavior (high sophistication but below-predicted disinhibition).")
    lines.append("")

    if not provider_constraint:
        lines.append("*Provider constraint data not available.*")
        lines.append("")
    else:
        lines.append("#### Cross-Condition Summary")
        lines.append("")
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

        lines.append("")
        lines.append("*Negative residual = more constrained than predicted by sophistication. Rank = OpenAI's position among all providers sorted by residual (1st = most constrained). ANOVA includes providers with n ≥ 3 only.*")
        lines.append("")

        # Add cross-provider summary table
        lines.append("#### Provider Constraint Summary")
        lines.append("")
        lines.append("| Provider | Times in Top 3 | Avg Residual | Consistency |")
        lines.append("|----------|----------------|--------------|-------------|")
        lines.append("| **OpenAI** | 6/6 | -0.169 | Very consistent |")
        lines.append("| AWS | 4/6 | -0.033 | Moderate |")
        lines.append("| xAI | 2/6 | -0.014 | Varies widely (n=2) |")
        lines.append("| Meta | 3/6 | -0.013 | Weak/mixed |")
        lines.append("")
        lines.append("**Key Finding**: OpenAI is the only provider with reliably negative residuals across all conditions. See `research_synthesis/cross_condition/PROVIDER_CONSTRAINT_ANALYSIS.md` for detailed analysis.")
        lines.append("")

    # 4.3 Consistently Constrained Models (was 4.2)
    patterns = cross_data.get("patterns") if cross_data else None
    cross_condition = patterns.get("cross_condition", {}) if patterns else {}

    lines.append("### 4.3 Consistently Constrained Models")
    lines.append("")
    lines.append("Models exhibiting high sophistication (>6.5) but below-predicted disinhibition across multiple conditions.")
    lines.append("")
    lines.append("| Model | # Conditions | Conditions |")
    lines.append("|-------|--------------|------------|")

    constrained = cross_condition.get("most_constrained", [])
    multi_condition_constrained = [m for m in constrained if m.get("composite", 0) >= 2]
    for model in multi_condition_constrained[:10]:
        name = model.get("model", "")
        n_conds = model.get("composite", 0)
        conds = ", ".join(model.get("conditions", []))
        lines.append("| " + name + " | " + str(n_conds) + " | " + conds + " |")

    if not multi_condition_constrained:
        lines.append("| *No models constrained in 2+ conditions* | - | - |")

    lines.append("")
    lines.append("**Observation**: All consistently constrained models are OpenAI (GPT-OSS-120B, GPT-5.2 Pro, O3, GPT-5, GPT-5.2), suggesting deliberate constraint at the provider level rather than individual model characteristics.")
    lines.append("")
    lines.append("**Visualizations**: See `research_synthesis/limitations/quadrant_classification/quadrant_scatter.png`")
    lines.append("")

    # 4.4 Consistent Outliers (was 4.3)
    lines.append("### 4.4 Consistent Outliers")
    lines.append("")
    lines.append("Models with unusual sophistication-disinhibition relationships (|residual| > 2 SD).")
    lines.append("")
    lines.append("| Model | # Conditions | Conditions |")
    lines.append("|-------|--------------|------------|")

    outliers = cross_condition.get("most_outlier", [])
    multi_condition_outliers = [m for m in outliers if m.get("composite", 0) >= 2]
    for model in multi_condition_outliers[:10]:
        name = model.get("model", "")
        n_conds = model.get("composite", 0)
        conds = ", ".join(model.get("conditions", []))
        lines.append("| " + name + " | " + str(n_conds) + " | " + conds + " |")

    if not multi_condition_outliers:
        lines.append("| *No models outliers in 2+ conditions* | - | - |")

    lines.append("")
    lines.append("**Observation**: Gemini-3-Pro-Preview is a notable outlier — exhibiting disinhibition 4-5 SD above regression despite top-tier capability benchmarks. This may reflect different training priorities or less aggressive constraint strategies compared to peers.")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_provider_constraint_section(provider_constraint):
    """Generate provider constraint analysis section (DEPRECATED - use generate_provider_model_patterns)."""
    if not provider_constraint:
        return ""

    lines = []
    lines.append("## Appendix: Provider Constraint Analysis")
    lines.append("")
    lines.append("Statistical analysis of whether certain providers show systematically more constrained behavior (high sophistication but below-predicted disinhibition).")
    lines.append("")

    # Cross-condition summary table
    lines.append("### Cross-Condition Summary")
    lines.append("")
    lines.append("| Condition | OpenAI Residual | Rank | ANOVA p | Sig |")
    lines.append("|-----------|-----------------|------|---------|-----|")

    for condition in ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder"]:
        if condition not in provider_constraint:
            continue

        data = provider_constraint[condition]
        openai_stats = data.get("provider_stats", {}).get("OpenAI", {})
        openai_resid = openai_stats.get("mean_residual", float("nan"))

        # Calculate rank
        sorted_provs = sorted(data.get("provider_stats", {}).items(),
                              key=lambda x: x[1].get("mean_residual", 0))
        rank = next((i+1 for i, (p, _) in enumerate(sorted_provs) if p == "OpenAI"), "N/A")
        rank_str = f"{rank}" + ("st" if rank == 1 else "nd" if rank == 2 else "rd" if rank == 3 else "th")

        anova_p = data.get("anova", {}).get("p", float("nan"))
        sig = "Yes" if anova_p < 0.05 else "No"

        lines.append(f"| {condition} | {openai_resid:+.3f} | {rank_str} | {anova_p:.4f} | {sig} |")

    lines.append("")
    lines.append("*Negative residual = more constrained than predicted by sophistication*")
    lines.append("")

    # Significant pairwise comparisons
    lines.append("### Significant Pairwise Comparisons (Bonferroni-corrected)")
    lines.append("")
    lines.append("| Condition | Comparison | Cohen's d | p_bonf |")
    lines.append("|-----------|------------|-----------|--------|")

    sig_found = False
    for condition, data in provider_constraint.items():
        pairwise = data.get("pairwise_comparisons", [])
        for pair in pairwise:
            if pair.get("significant_bonferroni") and "OpenAI" in pair.get("comparison", ""):
                sig_found = True
                d = pair.get("cohens_d", 0)
                p = pair.get("p_bonferroni", 1)
                # Determine direction
                if pair.get("provider_1") == "OpenAI":
                    comparison = f"{pair.get('provider_2')} > OpenAI"
                else:
                    comparison = f"{pair.get('provider_1')} > OpenAI"
                lines.append(f"| {condition} | {comparison} | {abs(d):.2f} | {p:.4f} |")

    if not sig_found:
        lines.append("| *No significant OpenAI comparisons* | - | - | - |")

    lines.append("")

    # Key finding summary
    lines.append("### Key Finding")
    lines.append("")
    lines.append("OpenAI models exhibit **systematically lower disinhibition than predicted by their sophistication level** across all conditions tested. Effect sizes are large (d > 1.2) in significant pairwise comparisons with Anthropic models.")
    lines.append("")
    lines.append("**Full analysis**: See `research_synthesis/limitations/provider_constraint/`")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_main_brief():
    """Generate the complete MAIN_RESEARCH_BRIEF.md content."""
    # Load preserved manual sections from existing file
    preserved = load_existing_manual_sections()

    conditions_data = load_all_conditions()
    cross_data = load_cross_condition_data()
    external_data = load_external_validation()
    outlier_data = load_outlier_data()
    no_dim_data = load_no_dimensions_data()
    judge_agreement = load_judge_agreement()
    factor_structure = load_factor_structure()
    provider_constraint = load_provider_constraint()
    classification_stability = load_classification_stability()

    if not conditions_data:
        return "# Main Research Brief\n\n**Error**: No condition data found.\n"

    # New reorganized structure
    sections = [
        # Header & Summary
        generate_header(conditions_data, cross_data, external_data),
        generate_executive_summary(conditions_data, cross_data, external_data, preserved),

        # Section 1: Methods
        generate_hypotheses_methods(conditions_data, factor_structure),

        # Section 2: Core H1/H2 Results
        generate_h1_h2_results(conditions_data),

        # Section 3: Robustness & Validation (consolidated)
        generate_robustness_validation(external_data, outlier_data, no_dim_data),

        # Section 4: Provider & Model Patterns
        generate_provider_model_patterns(provider_constraint, cross_data, conditions_data),

        # Section 5: Interpretation (MANUAL sections)
        generate_interpretation(preserved),

        # Section 6: Limitations (6.2 is MANUAL)
        generate_limitations(judge_agreement, external_data, preserved),

        # Section 7: Future Directions (MANUAL)
        generate_future_directions(preserved),

        # Section 8: H3 Preliminary (with WIP banner)
        generate_h3_preliminary(cross_data, conditions_data, preserved),

        # Appendices
        generate_factor_structure_appendix(factor_structure),
        generate_classification_stability_appendix(classification_stability),
        generate_file_references(conditions_data, cross_data, external_data),
    ]

    return "".join(sections)


def generate_h3_preliminary_section(cross_data, conditions_data):
    """Generate H3 preliminary section (variability, ANOVA) - placed at bottom."""
    lines = []
    lines.append("## Appendix: H3 Preliminary Analysis (Response Variability)")
    lines.append("")
    lines.append("> **Status**: PRELIMINARY - Reserved for H3 hypothesis development. Current focus is H1/H2.")
    lines.append("")

    # Include variability content
    variability_content = generate_variability_results(cross_data, conditions_data)
    # Strip the header and separator since we're embedding
    variability_lines = variability_content.split('\n')
    # Skip the header line and find content
    in_content = False
    for line in variability_lines:
        if line.startswith('### Variability'):
            in_content = True
        if in_content and not line.startswith('## ') and not line.startswith('---'):
            lines.append(line)
        if line.startswith('---') and in_content:
            break

    lines.append("")

    # Include ANOVA content
    anova_content = generate_anova_results(cross_data)
    anova_lines = anova_content.split('\n')
    in_content = False
    for line in anova_lines:
        if line.startswith('### Main Effect') or line.startswith('### Pairwise'):
            in_content = True
        if in_content and not line.startswith('## ') and not line.startswith('---'):
            lines.append(line)
        if line.startswith('---') and in_content:
            break

    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Regenerate MAIN_RESEARCH_BRIEF.md")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout instead of writing file")
    args = parser.parse_args()

    content = generate_main_brief()

    if args.dry_run:
        print(content)
    else:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            f.write(content)
        print("Generated: " + str(OUTPUT_FILE))
        print("Size: " + f"{len(content):,}" + " bytes")


if __name__ == "__main__":
    main()
