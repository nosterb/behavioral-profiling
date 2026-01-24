#!/usr/bin/env python3
"""
Run BERT vs Sophistication/Disinhibition validation with outliers removed.

Uses existing BERT soph/disin results and filters out models identified
as outliers in the H1/H2 outliers_removed analysis.

Usage:
    python3 scripts/run_bert_soph_disin_outliers_removed.py --condition baseline
    python3 scripts/run_bert_soph_disin_outliers_removed.py --all
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy import stats
import re


def normalize_model_name(name: str) -> str:
    """Normalize model name for matching. Preserves thinking variant distinction."""
    n = name.lower()
    is_thinking = "thinking" in n
    n = n.replace("-thinking", "").replace("_(thinking)", "").replace(" (thinking)", "")
    n = n.replace("-global", "").replace("_global", "")
    n = re.sub(r'-\d{8}.*', '', n)
    n = re.sub(r'_\d{8}.*', '', n)
    n = n.replace(" ", "-").replace("_", "-")
    n = n.strip("-")
    if is_thinking:
        n = n + "-thinking"
    return n


def run_bert_soph_disin_outliers_removed(condition: str) -> dict:
    """
    Run BERT vs Soph/Disin validation on outliers-removed dataset.
    """
    print(f"\n{'='*70}")
    print(f"BERT vs Sophistication/Disinhibition - Outliers Removed [{condition}]")
    print(f"{'='*70}")

    # Paths
    bert_results_path = Path(f"outputs/behavioral_profiles/research_synthesis/bert_validation/{condition}/bert_soph_disin_results.json")
    outlier_info_path = Path(f"outputs/behavioral_profiles/{condition}/outliers_removed/outlier_removal_info.json")
    output_dir = Path(f"outputs/behavioral_profiles/{condition}/outliers_removed")

    # Validate inputs
    if not bert_results_path.exists():
        print(f"ERROR: BERT soph/disin results not found: {bert_results_path}")
        return None

    if not outlier_info_path.exists():
        print(f"ERROR: Outlier removal info not found: {outlier_info_path}")
        return None

    # Load BERT soph/disin results
    print(f"\n[1/4] Loading BERT soph/disin results...")
    with open(bert_results_path) as f:
        bert_data = json.load(f)

    original_n = bert_data["metadata"]["n_models"]
    print(f"  Original N: {original_n} models")

    # Load outlier removal info
    print(f"\n[2/4] Loading outlier removal info...")
    with open(outlier_info_path) as f:
        outlier_info = json.load(f)

    models_retained = set(normalize_model_name(m) for m in outlier_info["models_retained"])
    outliers_removed = outlier_info.get("outliers_removed", [])
    n_outliers = len(outliers_removed)

    print(f"  Models retained: {len(models_retained)}")
    print(f"  Outliers removed: {n_outliers}")
    for o in outliers_removed:
        print(f"    - {o['model_id']} ({o['sd_from_line']:.2f} SD)")

    # Filter model data to retained models only
    print(f"\n[3/4] Filtering to retained models...")
    filtered_data = []
    for model in bert_data["model_data"]:
        model_norm = normalize_model_name(model["model_id"])
        if model_norm in models_retained:
            filtered_data.append(model)

    print(f"  Filtered N: {len(filtered_data)} models")

    if len(filtered_data) < 10:
        print("ERROR: Not enough models for valid analysis")
        return None

    # Extract arrays (keys are "toxicity"/"insult" in bert_soph_disin_results.json)
    sophistication = np.array([m["sophistication"] for m in filtered_data])
    disinhibition = np.array([m["disinhibition"] for m in filtered_data])
    toxicity = np.array([m["toxicity"] for m in filtered_data])
    insult = np.array([m["insult"] for m in filtered_data])

    # Calculate correlations
    print(f"\n[4/4] Calculating correlations...")

    r_tox_soph, p_tox_soph = stats.pearsonr(sophistication, toxicity)
    r_tox_disin, p_tox_disin = stats.pearsonr(disinhibition, toxicity)
    r_ins_soph, p_ins_soph = stats.pearsonr(sophistication, insult)
    r_ins_disin, p_ins_disin = stats.pearsonr(disinhibition, insult)

    # Results
    print(f"\n{'='*70}")
    print("RESULTS - OUTLIERS REMOVED")
    print(f"{'='*70}")
    print(f"\nN = {len(filtered_data)} models (removed {n_outliers} outliers)")

    print(f"\n--- BERT Toxicity Correlations ---")
    print(f"vs Sophistication:  r = {r_tox_soph:.3f}, p = {p_tox_soph:.2e}")
    print(f"vs Disinhibition:   r = {r_tox_disin:.3f}, p = {p_tox_disin:.2e}")

    print(f"\n--- BERT Insult Correlations ---")
    print(f"vs Sophistication:  r = {r_ins_soph:.3f}, p = {p_ins_soph:.2e}")
    print(f"vs Disinhibition:   r = {r_ins_disin:.3f}, p = {p_ins_disin:.2e}")

    # Compare with original
    orig = bert_data["correlations"]
    print(f"\n--- Change from Original ---")
    print(f"Tox~Soph:   {orig['toxicity_vs_sophistication']['r']:.3f} -> {r_tox_soph:.3f} ({r_tox_soph - orig['toxicity_vs_sophistication']['r']:+.3f})")
    print(f"Tox~Disin:  {orig['toxicity_vs_disinhibition']['r']:.3f} -> {r_tox_disin:.3f} ({r_tox_disin - orig['toxicity_vs_disinhibition']['r']:+.3f})")
    print(f"Ins~Soph:   {orig['insult_vs_sophistication']['r']:.3f} -> {r_ins_soph:.3f} ({r_ins_soph - orig['insult_vs_sophistication']['r']:+.3f})")
    print(f"Ins~Disin:  {orig['insult_vs_disinhibition']['r']:.3f} -> {r_ins_disin:.3f} ({r_ins_disin - orig['insult_vs_disinhibition']['r']:+.3f})")

    def interpret(r):
        return "large" if abs(r) >= 0.5 else "medium" if abs(r) >= 0.3 else "small"

    # Build audit file
    audit_data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "analysis": f"BERT vs Sophistication/Disinhibition - Outliers Removed ({condition})",
            "bert_model": "unitary/toxic-bert"
        },
        "provenance": {
            "source_files": {
                "bert_soph_disin_results": str(bert_results_path),
                "outlier_removal_info": str(outlier_info_path)
            },
            "methodology": {
                "outlier_detection": "Regression residuals > 2.0 SD from sophistication~disinhibition regression",
                "correlation_method": "Pearson product-moment correlation",
                "filter_logic": "Exclude models identified as outliers in H1/H2 analysis"
            }
        },
        "sample": {
            "n_original": original_n,
            "n_removed": n_outliers,
            "n_final": len(filtered_data),
            "outliers_removed": [
                {"model_id": o["model_id"], "sd_from_line": o["sd_from_line"]}
                for o in outliers_removed
            ]
        },
        "correlations": {
            "toxicity_vs_sophistication": {
                "r": float(r_tox_soph),
                "p": float(p_tox_soph),
                "interpretation": interpret(r_tox_soph)
            },
            "toxicity_vs_disinhibition": {
                "r": float(r_tox_disin),
                "p": float(p_tox_disin),
                "interpretation": interpret(r_tox_disin)
            },
            "insult_vs_sophistication": {
                "r": float(r_ins_soph),
                "p": float(p_ins_soph),
                "interpretation": interpret(r_ins_soph)
            },
            "insult_vs_disinhibition": {
                "r": float(r_ins_disin),
                "p": float(p_ins_disin),
                "interpretation": interpret(r_ins_disin)
            }
        },
        "comparison_with_original": {
            "toxicity_vs_sophistication": {
                "r_original": orig["toxicity_vs_sophistication"]["r"],
                "r_outliers_removed": float(r_tox_soph),
                "delta": float(r_tox_soph - orig["toxicity_vs_sophistication"]["r"])
            },
            "toxicity_vs_disinhibition": {
                "r_original": orig["toxicity_vs_disinhibition"]["r"],
                "r_outliers_removed": float(r_tox_disin),
                "delta": float(r_tox_disin - orig["toxicity_vs_disinhibition"]["r"])
            },
            "insult_vs_sophistication": {
                "r_original": orig["insult_vs_sophistication"]["r"],
                "r_outliers_removed": float(r_ins_soph),
                "delta": float(r_ins_soph - orig["insult_vs_sophistication"]["r"])
            },
            "insult_vs_disinhibition": {
                "r_original": orig["insult_vs_disinhibition"]["r"],
                "r_outliers_removed": float(r_ins_disin),
                "delta": float(r_ins_disin - orig["insult_vs_disinhibition"]["r"])
            }
        },
        "model_data": [
            {
                "model_id": m["model_id"],
                "sophistication": float(m["sophistication"]),
                "disinhibition": float(m["disinhibition"]),
                "toxicity": float(m["toxicity"]),
                "insult": float(m["insult"])
            }
            for m in filtered_data
        ]
    }

    # Save audit file
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "bert_soph_disin_outliers_removed_audit.json"
    with open(audit_path, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nSaved: {audit_path}")

    return audit_data


def update_consolidated_statistics(results: dict):
    """
    Update CONSOLIDATED_STATISTICS.md with Section 6: BERT vs Soph/Disin - Outliers Removed.
    """
    stats_path = Path("outputs/behavioral_profiles/research_synthesis/CONSOLIDATED_STATISTICS.md")

    if not stats_path.exists():
        print(f"WARNING: {stats_path} not found")
        return

    print(f"\nUpdating {stats_path}...")

    with open(stats_path, "r") as f:
        content = f.read()

    # Build new table
    table_rows = [
        "| Condition | N | N_Removed | r_tox_soph | p | r_tox_disin | p | r_ins_soph | p | r_ins_disin | p |",
        "|-----------|---|-----------|------------|---|-------------|---|------------|---|-------------|---|"
    ]

    condition_order = ["baseline", "naturalistic", "all_combined"]
    for condition in condition_order:
        if condition in results:
            r = results[condition]
            n = r["sample"]["n_final"]
            n_rem = r["sample"]["n_removed"]
            c = r["correlations"]

            def fmt_p(p):
                return f"{p:.2e}" if p < 0.001 else f"{p:.4f}"

            table_rows.append(
                f"| {condition} | {n} | {n_rem} | "
                f"{c['toxicity_vs_sophistication']['r']:.3f} | {fmt_p(c['toxicity_vs_sophistication']['p'])} | "
                f"{c['toxicity_vs_disinhibition']['r']:.3f} | {fmt_p(c['toxicity_vs_disinhibition']['p'])} | "
                f"{c['insult_vs_sophistication']['r']:.3f} | {fmt_p(c['insult_vs_sophistication']['p'])} | "
                f"{c['insult_vs_disinhibition']['r']:.3f} | {fmt_p(c['insult_vs_disinhibition']['p'])} |"
            )

    new_section = "## 6. BERT vs SOPHISTICATION/DISINHIBITION - OUTLIERS REMOVED\n\n" + "\n".join(table_rows) + "\n\n---"

    # Check if section already exists
    if "## 6. BERT vs SOPHISTICATION/DISINHIBITION - OUTLIERS REMOVED" in content:
        # Replace existing
        pattern = r"## 6\. BERT vs SOPHISTICATION/DISINHIBITION - OUTLIERS REMOVED\n\n(\|[^\n]+\n)+\n---"
        content = re.sub(pattern, new_section, content)
    else:
        # Insert after Section 5 (before the old Section 6 / now Section 7)
        # Find "## 5. BERT vs SOPHISTICATION/DISINHIBITION" section end
        section5_end = content.find("## 5. BERT vs SOPHISTICATION/DISINHIBITION")
        if section5_end != -1:
            # Find the --- after Section 5
            next_section = content.find("\n---\n\n## ", section5_end)
            if next_section != -1:
                insert_point = next_section + 5  # After "\n---\n"
                content = content[:insert_point] + "\n" + new_section + "\n" + content[insert_point:]

                # Renumber subsequent sections
                content = content.replace("## 6. JUDGE AGREEMENT", "## 7. JUDGE AGREEMENT")
                content = content.replace("## 7. EXTERNAL VALIDATION", "## 8. EXTERNAL VALIDATION")
                content = content.replace("## 8. EXTERNAL VALIDATION", "## 8. EXTERNAL VALIDATION")  # Idempotent

    with open(stats_path, "w") as f:
        f.write(content)

    print(f"Updated: {stats_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", type=str,
                        choices=["baseline", "naturalistic", "all_combined"])
    parser.add_argument("--all", action="store_true",
                        help="Process baseline and naturalistic")
    parser.add_argument("--update-docs", action="store_true", default=True)
    parser.add_argument("--no-update-docs", action="store_false", dest="update_docs")

    args = parser.parse_args()

    if args.all:
        conditions = ["baseline", "naturalistic", "all_combined"]
    elif args.condition:
        conditions = [args.condition]
    else:
        parser.print_help()
        return

    results = {}

    for condition in conditions:
        result = run_bert_soph_disin_outliers_removed(condition)
        if result:
            results[condition] = result

    if args.update_docs and results:
        update_consolidated_statistics(results)

    print(f"\n{'='*70}")
    print("COMPLETE")
    print(f"{'='*70}")
    for condition, r in results.items():
        c = r["correlations"]
        print(f"  {condition}: N={r['sample']['n_final']}, r_tox_disin={c['toxicity_vs_disinhibition']['r']:.3f}")


if __name__ == "__main__":
    main()
