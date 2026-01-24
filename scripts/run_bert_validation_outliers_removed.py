#!/usr/bin/env python3
"""
Run BERT validation with outliers removed for specified conditions.

Uses existing BERT validation results and filters out models identified
as outliers in the outliers_removed analysis. Recalculates correlations
and produces audit files with full provenance.

Usage:
    python3 scripts/run_bert_validation_outliers_removed.py --condition baseline
    python3 scripts/run_bert_validation_outliers_removed.py --condition naturalistic
    python3 scripts/run_bert_validation_outliers_removed.py --all
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

    # Check if this is a thinking model BEFORE normalizing
    is_thinking = "thinking" in n

    # Normalize thinking indicators to consistent format
    n = n.replace("-thinking", "").replace("_(thinking)", "").replace(" (thinking)", "")
    n = n.replace("-global", "").replace("_global", "")

    # Remove version timestamps
    n = re.sub(r'-\d{8}.*', '', n)
    n = re.sub(r'_\d{8}.*', '', n)

    # Normalize separators
    n = n.replace(" ", "-").replace("_", "-")

    # Remove trailing dashes
    n = n.strip("-")

    # Re-add thinking suffix if it was a thinking model
    if is_thinking:
        n = n + "-thinking"

    return n


def run_bert_validation_outliers_removed(condition: str) -> dict:
    """
    Run BERT validation on outliers-removed dataset for a condition.

    Returns results dict with correlations and audit info.
    """
    print(f"\n{'='*70}")
    print(f"BERT Validation - Outliers Removed [{condition}]")
    print(f"{'='*70}")

    # Paths
    bert_results_path = Path(f"outputs/behavioral_profiles/research_synthesis/bert_validation/{condition}/bert_validation_results.json")
    outlier_info_path = Path(f"outputs/behavioral_profiles/{condition}/outliers_removed/outlier_removal_info.json")
    output_dir = Path(f"outputs/behavioral_profiles/{condition}/outliers_removed")

    # Validate inputs exist
    if not bert_results_path.exists():
        print(f"ERROR: BERT results not found: {bert_results_path}")
        return None

    if not outlier_info_path.exists():
        print(f"ERROR: Outlier removal info not found: {outlier_info_path}")
        return None

    # Load existing BERT validation results
    print(f"\n[1/4] Loading BERT validation results from {bert_results_path}")
    with open(bert_results_path) as f:
        bert_data = json.load(f)

    original_n = len(bert_data["model_results"])
    print(f"  Original N: {original_n} models")

    # Load outlier removal info
    print(f"\n[2/4] Loading outlier removal info from {outlier_info_path}")
    with open(outlier_info_path) as f:
        outlier_info = json.load(f)

    models_retained = set(normalize_model_name(m) for m in outlier_info["models_retained"])
    outliers_removed = outlier_info.get("outliers_removed", [])
    n_outliers = len(outliers_removed)

    print(f"  Models retained: {len(models_retained)}")
    print(f"  Outliers removed: {n_outliers}")
    for o in outliers_removed:
        print(f"    - {o['model_id']} ({o['sd_from_line']:.2f} SD)")

    # Filter model results to retained models only
    print(f"\n[3/4] Filtering BERT results to retained models...")
    filtered_results = []
    for result in bert_data["model_results"]:
        model_norm = normalize_model_name(result["model_id"])
        if model_norm in models_retained:
            filtered_results.append(result)

    print(f"  Filtered N: {len(filtered_results)} models")

    if len(filtered_results) < 10:
        print("ERROR: Not enough models for valid correlation analysis")
        return None

    # Extract values for correlation
    aggression_vals = np.array([r["aggression"] for r in filtered_results])
    toxicity_vals = np.array([r["bert_toxicity"] for r in filtered_results])
    insult_vals = np.array([r["bert_insult"] for r in filtered_results])

    # Calculate correlations
    print(f"\n[4/4] Calculating correlations...")
    r_tox, p_tox = stats.pearsonr(aggression_vals, toxicity_vals)
    r_ins, p_ins = stats.pearsonr(aggression_vals, insult_vals)

    # Linear regression for additional stats
    slope_tox, intercept_tox, _, _, std_err_tox = stats.linregress(aggression_vals, toxicity_vals)
    slope_ins, intercept_ins, _, _, std_err_ins = stats.linregress(aggression_vals, insult_vals)

    # Results
    print(f"\n{'='*70}")
    print("RESULTS - OUTLIERS REMOVED")
    print(f"{'='*70}")
    print(f"\nN = {len(filtered_results)} models (removed {n_outliers} outliers)")
    print(f"\n--- Correlations with Judge Aggression ---")
    print(f"BERT Toxicity:  r = {r_tox:.3f}, p = {p_tox:.2e}")
    print(f"BERT Insult:    r = {r_ins:.3f}, p = {p_ins:.2e}")

    # Compare with original
    orig_r_tox = bert_data["correlations"]["toxicity"]["r"]
    orig_r_ins = bert_data["correlations"]["insult"]["r"]
    print(f"\n--- Change from Original ---")
    print(f"Toxicity: {orig_r_tox:.3f} -> {r_tox:.3f} ({r_tox - orig_r_tox:+.3f})")
    print(f"Insult:   {orig_r_ins:.3f} -> {r_ins:.3f} ({r_ins - orig_r_ins:+.3f})")

    # Build comprehensive audit file
    audit_data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "analysis": f"BERT Validation - Outliers Removed ({condition})",
            "bert_model": bert_data["metadata"]["bert_model"],
            "bert_model_url": bert_data["metadata"]["bert_model_url"]
        },
        "provenance": {
            "source_files": {
                "bert_validation_results": str(bert_results_path),
                "outlier_removal_info": str(outlier_info_path)
            },
            "methodology": {
                "outlier_detection": "Regression residuals > 2.0 SD from sophistication~disinhibition regression line",
                "correlation_method": "Pearson product-moment correlation",
                "filter_logic": "Exclude models identified as outliers in H1/H2 analysis"
            }
        },
        "sample": {
            "n_original": original_n,
            "n_removed": n_outliers,
            "n_final": len(filtered_results),
            "outliers_removed": [
                {
                    "model_id": o["model_id"],
                    "sophistication": o["sophistication"],
                    "disinhibition": o["disinhibition"],
                    "sd_from_line": o["sd_from_line"]
                }
                for o in outliers_removed
            ]
        },
        "correlations": {
            "toxicity": {
                "r": float(r_tox),
                "p": float(p_tox),
                "r_squared": float(r_tox ** 2),
                "interpretation": "large" if abs(r_tox) >= 0.5 else "medium" if abs(r_tox) >= 0.3 else "small"
            },
            "insult": {
                "r": float(r_ins),
                "p": float(p_ins),
                "r_squared": float(r_ins ** 2),
                "interpretation": "large" if abs(r_ins) >= 0.5 else "medium" if abs(r_ins) >= 0.3 else "small"
            }
        },
        "regression": {
            "toxicity": {
                "slope": float(slope_tox),
                "intercept": float(intercept_tox),
                "std_err": float(std_err_tox)
            },
            "insult": {
                "slope": float(slope_ins),
                "intercept": float(intercept_ins),
                "std_err": float(std_err_ins)
            }
        },
        "comparison_with_original": {
            "toxicity": {
                "r_original": float(orig_r_tox),
                "r_outliers_removed": float(r_tox),
                "delta": float(r_tox - orig_r_tox)
            },
            "insult": {
                "r_original": float(orig_r_ins),
                "r_outliers_removed": float(r_ins),
                "delta": float(r_ins - orig_r_ins)
            }
        },
        "model_data": [
            {
                "model_id": r["model_id"],
                "aggression": float(r["aggression"]),
                "bert_toxicity": float(r["bert_toxicity"]),
                "bert_insult": float(r["bert_insult"])
            }
            for r in filtered_results
        ]
    }

    # Save audit file
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "bert_validation_outliers_removed_audit.json"
    with open(audit_path, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nSaved: {audit_path}")

    # Generate brief markdown report
    brief_content = f"""# BERT Validation - Outliers Removed ({condition})

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

| Metric | Original | Outliers Removed | Delta |
|--------|----------|------------------|-------|
| N | {original_n} | {len(filtered_results)} | -{n_outliers} |
| r (Toxicity) | {orig_r_tox:.3f} | {r_tox:.3f} | {r_tox - orig_r_tox:+.3f} |
| r (Insult) | {orig_r_ins:.3f} | {r_ins:.3f} | {r_ins - orig_r_ins:+.3f} |

## Outliers Removed

| Model | Sophistication | Disinhibition | SD from Line |
|-------|----------------|---------------|--------------|
"""
    for o in outliers_removed:
        brief_content += f"| {o['model_id']} | {o['sophistication']:.2f} | {o['disinhibition']:.2f} | {o['sd_from_line']:.2f} |\n"

    brief_content += f"""
## Correlations (Outliers Removed)

| Measure | r | p | R² | Effect Size |
|---------|---|---|----|----|
| BERT Toxicity | {r_tox:.3f} | {p_tox:.2e} | {r_tox**2:.3f} | {audit_data['correlations']['toxicity']['interpretation']} |
| BERT Insult | {r_ins:.3f} | {p_ins:.2e} | {r_ins**2:.3f} | {audit_data['correlations']['insult']['interpretation']} |

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `{bert_results_path}` | Original BERT validation results |
| `{outlier_info_path}` | H1/H2 outlier detection info |

### Audit Files
| File | Description |
|------|-------------|
| `bert_validation_outliers_removed_audit.json` | Complete audit data with per-model scores |

### Reproducibility
```bash
python3 scripts/run_bert_validation_outliers_removed.py --condition {condition}
```
"""

    brief_path = output_dir / "BERT_VALIDATION_OUTLIERS_REMOVED_BRIEF.md"
    with open(brief_path, "w") as f:
        f.write(brief_content)
    print(f"Saved: {brief_path}")

    return audit_data


def update_consolidated_statistics(results: dict):
    """
    Update CONSOLIDATED_STATISTICS.md with BERT validation outliers-removed results.
    """
    stats_path = Path("outputs/behavioral_profiles/research_synthesis/CONSOLIDATED_STATISTICS.md")

    if not stats_path.exists():
        print(f"WARNING: {stats_path} not found, skipping update")
        return

    print(f"\nUpdating {stats_path}...")

    with open(stats_path, "r") as f:
        content = f.read()

    # Build the new table content
    table_rows = ["| Condition | N | N_Removed | r_tox | p_tox | r_ins | p_ins |",
                  "|-----------|---|-----------|-------|-------|-------|-------|"]

    # Sort conditions for consistent ordering
    condition_order = ["baseline", "naturalistic", "all_combined"]
    for condition in condition_order:
        if condition in results:
            r = results[condition]
            n = r["sample"]["n_final"]
            n_removed = r["sample"]["n_removed"]
            r_tox = r["correlations"]["toxicity"]["r"]
            p_tox = r["correlations"]["toxicity"]["p"]
            r_ins = r["correlations"]["insult"]["r"]
            p_ins = r["correlations"]["insult"]["p"]

            # Format p-values
            p_tox_str = f"{p_tox:.2e}" if p_tox < 0.001 else f"{p_tox:.4f}"
            p_ins_str = f"{p_ins:.2e}" if p_ins < 0.001 else f"{p_ins:.4f}"

            table_rows.append(f"| {condition} | {n} | {n_removed} | {r_tox:.3f} | {p_tox_str} | {r_ins:.3f} | {p_ins_str} |")

    new_table = "\n".join(table_rows)

    # Find and replace the BERT VALIDATION - OUTLIERS REMOVED section
    # Pattern: ## 4. BERT VALIDATION - OUTLIERS REMOVED ... until ---
    pattern = r"(## 4\. BERT VALIDATION - OUTLIERS REMOVED\n\n)(\|[^\n]+\n)+(\n---)"
    replacement = f"## 4. BERT VALIDATION - OUTLIERS REMOVED\n\n{new_table}\n\n---"

    if "## 4. BERT VALIDATION - OUTLIERS REMOVED" in content:
        # Replace existing section
        new_content = re.sub(pattern, replacement, content)
    else:
        # Insert after ## 3. BERT VALIDATION section
        insert_point = content.find("## 4.")
        if insert_point == -1:
            insert_point = content.find("## 5.")
        if insert_point != -1:
            new_content = content[:insert_point] + replacement + "\n\n" + content[insert_point:]
        else:
            new_content = content + "\n\n" + replacement

    with open(stats_path, "w") as f:
        f.write(new_content)

    print(f"Updated: {stats_path}")


def main():
    parser = argparse.ArgumentParser(description="Run BERT validation with outliers removed")
    parser.add_argument("--condition", type=str,
                        choices=["baseline", "naturalistic", "all_combined"],
                        help="Condition to process")
    parser.add_argument("--all", action="store_true",
                        help="Process all conditions (baseline, naturalistic)")
    parser.add_argument("--update-docs", action="store_true", default=True,
                        help="Update CONSOLIDATED_STATISTICS.md (default: True)")
    parser.add_argument("--no-update-docs", action="store_false", dest="update_docs",
                        help="Skip updating documentation")

    args = parser.parse_args()

    if args.all:
        conditions = ["baseline", "naturalistic"]
    elif args.condition:
        conditions = [args.condition]
    else:
        parser.print_help()
        return

    results = {}

    # Also load existing all_combined if it exists
    all_combined_audit = Path("outputs/behavioral_profiles/all_combined/outliers_removed/bert_validation_outliers_removed_audit.json")
    if all_combined_audit.exists():
        with open(all_combined_audit) as f:
            results["all_combined"] = json.load(f)

    for condition in conditions:
        result = run_bert_validation_outliers_removed(condition)
        if result:
            results[condition] = result

    if args.update_docs and results:
        update_consolidated_statistics(results)

    print(f"\n{'='*70}")
    print("COMPLETE")
    print(f"{'='*70}")
    print(f"Processed {len(results)} condition(s)")
    for condition, r in results.items():
        print(f"  {condition}: N={r['sample']['n_final']}, r_tox={r['correlations']['toxicity']['r']:.3f}")


if __name__ == "__main__":
    main()
