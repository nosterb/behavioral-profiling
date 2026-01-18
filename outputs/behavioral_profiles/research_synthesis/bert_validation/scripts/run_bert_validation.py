#!/usr/bin/env python3
"""
Run BERT toxicity validation against baseline aggression scores.

Extracts model responses from baseline job outputs, scores them with BERT,
and calculates correlation with judge-assigned aggression scores.

Usage:
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --condition authority
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py --limit 50
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
import sys
from datetime import datetime

# Add project root to path (5 levels up from scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


MODEL_NAME = "unitary/toxic-bert"
JOBS_DIR = Path("outputs/single_prompt_jobs")

# Intervention suffixes for job filtering
INTERVENTION_SUFFIXES = ["_authority", "_urgency", "_reminder", "_telemetry", "_minimal_steering"]


def load_model():
    """Load toxic-bert model."""
    print(f"Loading BERT model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return model, tokenizer


def get_toxicity_scores(text: str, model, tokenizer, max_length: int = 512) -> dict:
    """Get toxicity scores from BERT."""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.sigmoid(outputs.logits).squeeze().tolist()

    labels = ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack"]
    if isinstance(probs, float):
        probs = [probs]
    return dict(zip(labels[:len(probs)], probs))


def normalize_model_name(name: str) -> str:
    """Normalize model name for matching. Preserves thinking variant distinction."""
    import re
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


def load_aggression_scores(condition: str = "baseline") -> dict:
    """Load aggression scores from condition-specific profiles."""
    profiles_dir = Path(f"outputs/behavioral_profiles/{condition}/profiles")
    aggression_by_model = {}
    normalized_to_original = {}

    if not profiles_dir.exists():
        print(f"ERROR: {profiles_dir} not found")
        return {}, {}

    for profile_file in profiles_dir.glob("*.json"):
        with open(profile_file) as f:
            profile = json.load(f)

        model_id = profile.get("model_id", profile_file.stem)
        dims = profile.get("dimensions", {})
        aggression = dims.get("aggression", {}).get("average")

        if aggression is not None:
            aggression_by_model[model_id] = aggression
            norm = normalize_model_name(model_id)
            normalized_to_original[norm] = model_id

    return aggression_by_model, normalized_to_original


def extract_responses_from_jobs(condition: str = "baseline", limit: int = None) -> dict:
    """
    Extract model responses from job outputs for a specific condition.

    Returns: {model_id: [list of responses]}
    """
    responses_by_model = defaultdict(list)

    # Find jobs for this condition
    # Structure: outputs/single_prompt_jobs/baseline_*/job_*_YYYYMMDD/job_*.json
    job_files = []
    for suite_dir in JOBS_DIR.glob("baseline_*"):
        if not suite_dir.is_dir():
            continue
        for job_dir in suite_dir.iterdir():
            if not job_dir.is_dir():
                continue
            name = job_dir.name

            if condition == "baseline":
                # Baseline = no intervention suffix
                if any(x in name for x in INTERVENTION_SUFFIXES):
                    continue
            else:
                # Non-baseline = must have the condition suffix
                # Map condition name to suffix
                suffix_map = {
                    "authority": "_authority",
                    "urgency": "_urgency",
                    "reminder": "_reminder",
                    "telemetryV3": "_telemetry",
                    "minimal_steering": "_minimal_steering"
                }
                required_suffix = suffix_map.get(condition, f"_{condition}")
                if required_suffix not in name:
                    continue

            # Find JSON file inside
            for job_file in job_dir.glob("*.json"):
                job_files.append(job_file)

    if limit:
        job_files = job_files[:limit]

    print(f"Found {len(job_files)} baseline job files")

    for job_file in job_files:
        try:
            with open(job_file) as f:
                job_data = json.load(f)

            models = job_data.get("models", [])
            for model_entry in models:
                # Use display_name for matching with profiles
                display_name = model_entry.get("display_name", "")
                response = model_entry.get("response", "")

                if display_name and response:
                    responses_by_model[display_name].append(response)

        except Exception as e:
            print(f"  Warning: Could not process {job_file}: {e}")

    return dict(responses_by_model)


def run_validation(condition: str = "baseline", limit: int = None):
    """Main validation pipeline."""
    print("=" * 70)
    print(f"BERT Toxicity vs. Judge Aggression Validation [{condition}]")
    print("=" * 70)

    # Load aggression scores
    print(f"\n[1/4] Loading aggression scores from {condition} profiles...")
    aggression_scores, profile_norm_map = load_aggression_scores(condition)
    print(f"  Found {len(aggression_scores)} models with aggression scores")

    if not aggression_scores:
        print(f"ERROR: No aggression scores found. Run {condition} H1/H2 analysis first.")
        return

    # Extract responses
    print(f"\n[2/4] Extracting responses from {condition} jobs...")
    responses = extract_responses_from_jobs(condition, limit)
    print(f"  Found responses for {len(responses)} models")

    # Build normalized response map
    response_norm_map = {}
    for model_id in responses.keys():
        norm = normalize_model_name(model_id)
        response_norm_map[norm] = model_id

    # Find overlap via normalized names
    common_norms = set(profile_norm_map.keys()) & set(response_norm_map.keys())
    print(f"  Models with both scores and responses (normalized match): {len(common_norms)}")

    if len(common_norms) < 10:
        print("ERROR: Not enough overlapping models for validation")
        return

    # Load BERT
    print("\n[3/4] Loading BERT model...")
    model, tokenizer = load_model()

    # Score responses
    print("\n[4/4] Scoring responses with BERT...")
    results = []

    for i, norm in enumerate(sorted(common_norms)):
        profile_id = profile_norm_map[norm]
        response_id = response_norm_map[norm]
        model_responses = responses[response_id]
        aggression = aggression_scores[profile_id]

        # Average BERT toxicity across all responses for this model
        toxicity_scores = []
        insult_scores = []
        all_scores = []

        n_to_score = len(model_responses)  # Score ALL responses
        for j, resp in enumerate(model_responses[:n_to_score]):
            scores = get_toxicity_scores(resp, model, tokenizer)
            toxicity_scores.append(scores.get("toxicity", 0))
            insult_scores.append(scores.get("insult", 0))
            all_scores.append(scores)
            print(f"  [{i+1}/{len(common_norms)}] {profile_id} response {j+1}/{n_to_score}: toxicity={scores.get('toxicity', 0):.4f}, insult={scores.get('insult', 0):.4f}")

        avg_toxicity = np.mean(toxicity_scores) if toxicity_scores else 0
        avg_insult = np.mean(insult_scores) if insult_scores else 0

        results.append({
            "model_id": profile_id,
            "aggression": aggression,
            "bert_toxicity": avg_toxicity,
            "bert_insult": avg_insult,
            "n_responses": len(model_responses),
            "n_scored": len(toxicity_scores),
            "all_toxicity_scores": toxicity_scores,
            "all_insult_scores": insult_scores
        })

        print(f"  [{i+1}/{len(common_norms)}] {profile_id} COMPLETE: avg_toxicity={avg_toxicity:.4f}, avg_insult={avg_insult:.4f}, aggression={aggression:.2f}")

    # Calculate correlations
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    aggression_vals = np.array([r["aggression"] for r in results])
    toxicity_vals = np.array([r["bert_toxicity"] for r in results])
    insult_vals = np.array([r["bert_insult"] for r in results])
    model_ids = [r["model_id"] for r in results]

    # Pearson correlations
    r_tox, p_tox = stats.pearsonr(aggression_vals, toxicity_vals)
    r_ins, p_ins = stats.pearsonr(aggression_vals, insult_vals)

    # Linear regression for toxicity
    slope_tox, intercept_tox, r_val_tox, p_val_tox, std_err_tox = stats.linregress(aggression_vals, toxicity_vals)
    slope_ins, intercept_ins, r_val_ins, p_val_ins, std_err_ins = stats.linregress(aggression_vals, insult_vals)

    print(f"\nN = {len(results)} models")
    print(f"\nAggression range: {min(aggression_vals):.2f} - {max(aggression_vals):.2f}")
    print(f"BERT Toxicity range: {min(toxicity_vals):.4f} - {max(toxicity_vals):.4f}")
    print(f"BERT Insult range: {min(insult_vals):.4f} - {max(insult_vals):.4f}")

    print(f"\n--- Correlations with Judge Aggression ---")
    print(f"BERT Toxicity:  r = {r_tox:.3f}, p = {p_tox:.4f}")
    print(f"BERT Insult:    r = {r_ins:.3f}, p = {p_ins:.4f}")

    print(f"\n--- Regression (Toxicity ~ Aggression) ---")
    print(f"Slope: {slope_tox:.4f}, Intercept: {intercept_tox:.4f}, SE: {std_err_tox:.4f}")

    # Interpretation
    print(f"\n--- Interpretation ---")
    if abs(r_tox) >= 0.5:
        interp = "Strong validation - BERT toxicity validates aggression measure"
        print(f"Strong correlation (r = {r_tox:.2f}): {interp}")
    elif abs(r_tox) >= 0.3:
        interp = "Moderate validation - Partial overlap between constructs"
        print(f"Moderate correlation (r = {r_tox:.2f}): {interp}")
    else:
        interp = "Weak validation - Aggression captures something distinct from toxicity"
        print(f"Weak correlation (r = {r_tox:.2f}): {interp}")

    # Output directory (condition-specific subfolder)
    output_dir = Path(__file__).parent.parent / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate scatter plots
    print(f"\n--- Generating Scatter Plots ---")
    pattern_info = generate_scatter_plots(
        aggression_vals, toxicity_vals, insult_vals, model_ids,
        r_tox, p_tox, r_ins, p_ins,
        slope_tox, intercept_tox, slope_ins, intercept_ins,
        output_dir,
        condition=condition
    )

    # Save comprehensive results JSON for downstream use
    profiles_dir = Path(f"outputs/behavioral_profiles/{condition}/profiles")
    output = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "bert_model": MODEL_NAME,
            "bert_model_url": "https://huggingface.co/unitary/toxic-bert",
            "training_data": "Jigsaw Toxic Comment Classification Challenge",
            "training_data_url": "https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge",
            "source_condition": condition,
            "source_profiles": str(profiles_dir),
            "source_jobs": str(JOBS_DIR)
        },
        "sample": {
            "n_models": len(results),
            "aggression_range": [float(min(aggression_vals)), float(max(aggression_vals))],
            "toxicity_range": [float(min(toxicity_vals)), float(max(toxicity_vals))],
            "insult_range": [float(min(insult_vals)), float(max(insult_vals))]
        },
        "correlations": {
            "toxicity": {
                "r": float(r_tox),
                "p": float(p_tox),
                "interpretation": "large" if abs(r_tox) >= 0.5 else "medium" if abs(r_tox) >= 0.3 else "small"
            },
            "insult": {
                "r": float(r_ins),
                "p": float(p_ins),
                "interpretation": "large" if abs(r_ins) >= 0.5 else "medium" if abs(r_ins) >= 0.3 else "small"
            }
        },
        "regression": {
            "toxicity": {
                "slope": float(slope_tox),
                "intercept": float(intercept_tox),
                "std_err": float(std_err_tox),
                "r_squared": float(r_tox ** 2)
            },
            "insult": {
                "slope": float(slope_ins),
                "intercept": float(intercept_ins),
                "std_err": float(std_err_ins),
                "r_squared": float(r_ins ** 2)
            }
        },
        "interpretation": interp,
        "patterns": {
            "toxicity": {
                "outliers": [{"model_id": o["model_id"], "residual": float(o["residual"]), "sd_from_line": float(o["sd_from_line"])} for o in pattern_info["toxicity"]["outliers"]],
                "constrained": [{"model_id": c["model_id"], "residual": float(c["residual"]), "sd_from_line": float(c["sd_from_line"])} for c in pattern_info["toxicity"]["constrained"]],
                "residual_std": pattern_info["toxicity"]["residual_std"]
            },
            "insult": {
                "outliers": [{"model_id": o["model_id"], "residual": float(o["residual"]), "sd_from_line": float(o["sd_from_line"])} for o in pattern_info["insult"]["outliers"]],
                "constrained": [{"model_id": c["model_id"], "residual": float(c["residual"]), "sd_from_line": float(c["sd_from_line"])} for c in pattern_info["insult"]["constrained"]],
                "residual_std": pattern_info["insult"]["residual_std"]
            }
        },
        "model_results": results,
        "output_files": {
            "results_json": "bert_validation_results.json",
            "scatter_toxicity": "scatter_toxicity_vs_aggression.png",
            "scatter_insult": "scatter_insult_vs_aggression.png",
            "scatter_combined": "scatter_combined.png",
            "report": "VALIDATION_REPORT.md"
        }
    }

    output_file = output_dir / "bert_validation_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Update validation report
    generate_validation_report(output, output_dir)

    return output


def generate_scatter_plots(aggression, toxicity, insult, model_ids,
                           r_tox, p_tox, r_ins, p_ins,
                           slope_tox, intercept_tox, slope_ins, intercept_ins,
                           output_dir, condition="baseline"):
    """Generate scatter plots with regression lines (research_synthesis styling)."""

    # =============================================================================
    # CONFIGURABLE THRESHOLDS (matching research_synthesis)
    # =============================================================================
    OUTLIER_SD_THRESHOLD = 2.0  # Statistical outliers: residuals > 2 SD
    # Constrained: high aggression but below-predicted toxicity
    # (analogous to high-sophistication but low-disinhibition in H2)
    CONSTRAINED_AGG_THRESHOLD = 1.6  # Top ~25% of aggression range (1.13-2.18)
    CONSTRAINED_RESIDUAL_THRESHOLD = -0.005  # Below prediction by this much

    # =============================================================================
    # Identify statistical patterns
    # =============================================================================
    def identify_patterns(x_vals, y_vals, ids, slope, intercept):
        """Identify outliers and constrained models from regression."""
        predicted = slope * np.array(x_vals) + intercept
        residuals = np.array(y_vals) - predicted
        residual_std = np.std(residuals)

        outliers = []
        constrained = []

        for i in range(len(x_vals)):
            # Outlier: |residual| > threshold * SD
            if abs(residuals[i]) > OUTLIER_SD_THRESHOLD * residual_std:
                outliers.append({
                    'idx': i,
                    'model_id': ids[i],
                    'residual': residuals[i],
                    'sd_from_line': residuals[i] / residual_std
                })

            # Constrained: high aggression but below-predicted toxicity
            if x_vals[i] > CONSTRAINED_AGG_THRESHOLD and residuals[i] < CONSTRAINED_RESIDUAL_THRESHOLD:
                constrained.append({
                    'idx': i,
                    'model_id': ids[i],
                    'residual': residuals[i],
                    'sd_from_line': residuals[i] / residual_std
                })

        return outliers, constrained, residuals, residual_std

    # Get patterns for toxicity
    outliers_tox, constrained_tox, residuals_tox, residual_std_tox = identify_patterns(
        aggression, toxicity, model_ids, slope_tox, intercept_tox)

    # Get patterns for insult
    outliers_ins, constrained_ins, residuals_ins, residual_std_ins = identify_patterns(
        aggression, insult, model_ids, slope_ins, intercept_ins)

    # Sort indices for extreme model identification
    sorted_by_aggression = sorted(range(len(aggression)), key=lambda i: aggression[i])
    sorted_by_toxicity = sorted(range(len(toxicity)), key=lambda i: toxicity[i])
    sorted_by_insult = sorted(range(len(insult)), key=lambda i: insult[i])

    def get_extreme_labels(x_vals, y_vals, ids, sorted_x, sorted_y, y_name, outliers, constrained):
        """Get extreme models for labeling with tags (including outliers)."""
        models_to_label = {}
        outlier_ids = {o['model_id'] for o in outliers}
        constrained_ids = {c['model_id'] for c in constrained}

        # Min/max x (aggression) - top 2 each
        for i in sorted_x[:2]:
            if ids[i] not in models_to_label:
                models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
            models_to_label[ids[i]]['tags'].append(f"min-agg={x_vals[i]:.2f}")
            models_to_label[ids[i]]['priority'] += 10

        for i in sorted_x[-2:]:
            if ids[i] not in models_to_label:
                models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
            models_to_label[ids[i]]['tags'].append(f"max-agg={x_vals[i]:.2f}")
            models_to_label[ids[i]]['priority'] += 10

        # Min/max y - top 2 each
        for i in sorted_y[:2]:
            if ids[i] not in models_to_label:
                models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
            models_to_label[ids[i]]['tags'].append(f"min-{y_name}={y_vals[i]:.4f}")
            models_to_label[ids[i]]['priority'] += 5

        for i in sorted_y[-2:]:
            if ids[i] not in models_to_label:
                models_to_label[ids[i]] = {'idx': i, 'tags': [], 'priority': 0}
            models_to_label[ids[i]]['tags'].append(f"max-{y_name}={y_vals[i]:.4f}")
            models_to_label[ids[i]]['priority'] += 5

        # Add ALL outliers with residual info (so every red ring has a label)
        for o in outliers:
            mid = o['model_id']
            if mid not in models_to_label:
                models_to_label[mid] = {'idx': o['idx'], 'tags': [], 'priority': 0}
            models_to_label[mid]['tags'].append(f"outlier({o['sd_from_line']:+.1f}σ)")
            models_to_label[mid]['priority'] += 20

        # Add constrained models
        for c in constrained:
            mid = c['model_id']
            if mid not in models_to_label:
                models_to_label[mid] = {'idx': c['idx'], 'tags': [], 'priority': 0}
            models_to_label[mid]['priority'] += 15  # Priority for labeling

        return models_to_label

    # =========================================================================
    # Plot 1: Toxicity vs Aggression (main validation plot)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    # Main scatter with research_synthesis styling
    ax.scatter(aggression, toxicity, alpha=0.7, s=150,
               c='#2ecc71', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})',
               zorder=3)

    # Regression line (dashed black)
    x_line = np.linspace(min(aggression), max(aggression), 100)
    y_line = slope_tox * x_line + intercept_tox
    ax.plot(x_line, y_line, 'k--', alpha=0.5, linewidth=2,
            label='Best Fit', zorder=1)

    # Highlight statistical outliers with red circles
    if outliers_tox:
        for o in outliers_tox:
            ax.scatter([aggression[o['idx']]], [toxicity[o['idx']]],
                      s=400, facecolors='none', edgecolors='red',
                      linewidth=3, zorder=5)
    # Legend entry for outliers (even if n=0)
    ax.scatter([], [], s=400, facecolors='none', edgecolors='red',
              linewidth=3, label=f'Statistical Outliers (n={len(outliers_tox)})')

    # Highlight constrained models with cyan diamonds
    if constrained_tox:
        for c in constrained_tox:
            ax.scatter([aggression[c['idx']]], [toxicity[c['idx']]],
                      marker='D', s=200, color='#00CED1', alpha=0.9,
                      edgecolors='blue', linewidth=2.5, zorder=6)
    # Legend entry for constrained (even if n=0)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5,
              label=f'Constrained (n={len(constrained_tox)})')

    # Label extreme models (deduplicated with tags)
    tox_labels = get_extreme_labels(aggression, toxicity, model_ids,
                                    sorted_by_aggression, sorted_by_toxicity, 'tox',
                                    outliers_tox, constrained_tox)

    for j, (mid, info) in enumerate(sorted(tox_labels.items(), key=lambda x: -x[1]['priority'])):
        i = info['idx']
        tags = info['tags']

        # Shorten model name
        label_name = mid.replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 18:
            label_name = label_name[:15] + '...'

        tag_text = '\n'.join(tags[:2])
        full_label = f"{label_name}\n{tag_text}"

        # Smart positioning
        x_offset = -70 if aggression[i] < np.median(aggression) else 70
        y_offset = -40 if toxicity[i] < np.median(toxicity) else 40
        y_offset += (j % 3) * 15

        ax.annotate(full_label,
                   xy=(aggression[i], toxicity[i]),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=6.5, fontweight='bold', color='navy',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                            alpha=0.85, edgecolor='navy'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                 color='navy', lw=1.3),
                   zorder=9)

    # Stats text box (wheat background) - includes pattern counts
    r_sq = r_tox ** 2
    p_str = f"{p_tox:.6f}" if p_tox >= 0.0001 else "< .0001"
    stats_text = (
        f'Validation: BERT Toxicity ~ Judge Aggression\n'
        f'r = {r_tox:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {"Large" if abs(r_tox) >= 0.5 else "Medium" if abs(r_tox) >= 0.3 else "Small"}\n'
        f'N = {len(aggression)} models\n\n'
        f'Outliers: {len(outliers_tox)} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(constrained_tox)} (high-agg, low-tox)'
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95),
            zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Toxicity Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Toxicity vs. Judge Aggression\n'
                 '(Independent Validation with Outlier & Constrained Detection)',
                 fontsize=15, fontweight='bold', pad=20)

    # Condition label as suptitle
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold',
                 y=0.995, color='#666666')

    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_dir / "scatter_toxicity_vs_aggression.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_toxicity_vs_aggression.png")
    print(f"    - Outliers: {len(outliers_tox)}")
    print(f"    - Constrained: {len(constrained_tox)}")

    # =========================================================================
    # Plot 2: Insult vs Aggression
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(aggression, insult, alpha=0.7, s=150,
               c='#e74c3c', edgecolors='black', linewidth=1.5,
               label=f'Models (n={len(aggression)})',
               zorder=3)

    y_line = slope_ins * x_line + intercept_ins
    ax.plot(x_line, y_line, 'k--', alpha=0.5, linewidth=2,
            label='Best Fit', zorder=1)

    # Highlight outliers
    if outliers_ins:
        for o in outliers_ins:
            ax.scatter([aggression[o['idx']]], [insult[o['idx']]],
                      s=400, facecolors='none', edgecolors='red',
                      linewidth=3, zorder=5)
    ax.scatter([], [], s=400, facecolors='none', edgecolors='red',
              linewidth=3, label=f'Statistical Outliers (n={len(outliers_ins)})')

    # Highlight constrained
    if constrained_ins:
        for c in constrained_ins:
            ax.scatter([aggression[c['idx']]], [insult[c['idx']]],
                      marker='D', s=200, color='#00CED1', alpha=0.9,
                      edgecolors='blue', linewidth=2.5, zorder=6)
    ax.scatter([], [], marker='D', s=200, color='#00CED1', alpha=0.9,
              edgecolors='blue', linewidth=2.5,
              label=f'Constrained (n={len(constrained_ins)})')

    # Label extreme models
    ins_labels = get_extreme_labels(aggression, insult, model_ids,
                                    sorted_by_aggression, sorted_by_insult, 'ins',
                                    outliers_ins, constrained_ins)

    for j, (mid, info) in enumerate(sorted(ins_labels.items(), key=lambda x: -x[1]['priority'])):
        i = info['idx']
        tags = info['tags']

        label_name = mid.replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 18:
            label_name = label_name[:15] + '...'

        tag_text = '\n'.join(tags[:2])
        full_label = f"{label_name}\n{tag_text}"

        x_offset = -70 if aggression[i] < np.median(aggression) else 70
        y_offset = -40 if insult[i] < np.median(insult) else 40
        y_offset += (j % 3) * 15

        ax.annotate(full_label,
                   xy=(aggression[i], insult[i]),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=6.5, fontweight='bold', color='navy',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                            alpha=0.85, edgecolor='navy'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                                 color='navy', lw=1.3),
                   zorder=9)

    r_sq = r_ins ** 2
    p_str = f"{p_ins:.6f}" if p_ins >= 0.0001 else "< .0001"
    stats_text = (
        f'Validation: BERT Insult ~ Judge Aggression\n'
        f'r = {r_ins:.3f}, p = {p_str}\n'
        f'R² = {r_sq:.3f} ({r_sq*100:.1f}% variance explained)\n\n'
        f'Effect Size: {"Large" if abs(r_ins) >= 0.5 else "Medium" if abs(r_ins) >= 0.3 else "Small"}\n'
        f'N = {len(aggression)} models\n\n'
        f'Outliers: {len(outliers_ins)} (|residual| > {OUTLIER_SD_THRESHOLD} SD)\n'
        f'Constrained: {len(constrained_ins)} (high-agg, low-ins)'
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95),
            zorder=7)

    ax.set_xlabel('Judge Aggression Score (1-10)', fontsize=13, fontweight='bold')
    ax.set_ylabel('BERT Insult Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('BERT Insult vs. Judge Aggression\n'
                 '(Independent Validation with Outlier & Constrained Detection)',
                 fontsize=15, fontweight='bold', pad=20)

    # Condition label as suptitle
    fig.suptitle(f'Condition: {condition}', fontsize=11, fontweight='bold',
                 y=0.995, color='#666666')

    ax.legend(loc='lower right', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_dir / "scatter_insult_vs_aggression.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_insult_vs_aggression.png")
    print(f"    - Outliers: {len(outliers_ins)}")
    print(f"    - Constrained: {len(constrained_ins)}")

    # =========================================================================
    # Plot 3: Combined 2-panel
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Toxicity panel
    axes[0].scatter(aggression, toxicity, alpha=0.7, s=120,
                    c='#2ecc71', edgecolors='black', linewidth=1.5, zorder=3)
    axes[0].plot(x_line, slope_tox * x_line + intercept_tox, 'k--', alpha=0.5, linewidth=2, zorder=1)

    # Outliers on combined
    for o in outliers_tox:
        axes[0].scatter([aggression[o['idx']]], [toxicity[o['idx']]],
                       s=300, facecolors='none', edgecolors='red', linewidth=2.5, zorder=5)
        # Label outlier
        label_name = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 15:
            label_name = label_name[:12] + '...'
        axes[0].annotate(f"{label_name}\n({o['sd_from_line']:+.1f}σ)",
                        xy=(aggression[o['idx']], toxicity[o['idx']]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=6, fontweight='bold', color='red',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='red'),
                        zorder=10)

    axes[0].text(0.05, 0.95,
                f'r = {r_tox:.3f}\nR² = {r_tox**2:.3f}\np < .0001\nOutliers: {len(outliers_tox)}',
                transform=axes[0].transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    axes[0].set_xlabel('Judge Aggression (1-10)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('BERT Toxicity (0-1)', fontsize=12, fontweight='bold')
    axes[0].set_title('Toxicity Validation', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_axisbelow(True)

    # Insult panel
    axes[1].scatter(aggression, insult, alpha=0.7, s=120,
                    c='#e74c3c', edgecolors='black', linewidth=1.5, zorder=3)
    axes[1].plot(x_line, slope_ins * x_line + intercept_ins, 'k--', alpha=0.5, linewidth=2, zorder=1)

    # Outliers on combined
    for o in outliers_ins:
        axes[1].scatter([aggression[o['idx']]], [insult[o['idx']]],
                       s=300, facecolors='none', edgecolors='red', linewidth=2.5, zorder=5)
        # Label outlier
        label_name = model_ids[o['idx']].replace('Claude-', 'C-').replace('GPT-', 'G-')
        if len(label_name) > 15:
            label_name = label_name[:12] + '...'
        axes[1].annotate(f"{label_name}\n({o['sd_from_line']:+.1f}σ)",
                        xy=(aggression[o['idx']], insult[o['idx']]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=6, fontweight='bold', color='red',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='red'),
                        zorder=10)

    axes[1].text(0.05, 0.95,
                f'r = {r_ins:.3f}\nR² = {r_ins**2:.3f}\np < .0001\nOutliers: {len(outliers_ins)}',
                transform=axes[1].transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    axes[1].set_xlabel('Judge Aggression (1-10)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('BERT Insult (0-1)', fontsize=12, fontweight='bold')
    axes[1].set_title('Insult Validation', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_axisbelow(True)

    # Condition label as suptitle, then main title
    fig.text(0.5, 0.998, f'Condition: {condition}', ha='center', va='top',
             fontsize=11, fontweight='bold', color='#666666')
    fig.suptitle(f'BERT Validation: Independent Measure vs. Judge Aggression (N={len(aggression)})',
                 fontsize=15, fontweight='bold', y=0.97)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(output_dir / "scatter_combined.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: scatter_combined.png")

    # Return pattern info for JSON storage
    return {
        'toxicity': {
            'outliers': outliers_tox,
            'constrained': constrained_tox,
            'residual_std': float(residual_std_tox)
        },
        'insult': {
            'outliers': outliers_ins,
            'constrained': constrained_ins,
            'residual_std': float(residual_std_ins)
        }
    }


def generate_validation_report(data, output_dir):
    """Generate markdown validation report."""
    report = f"""# BERT Toxicity Validation Report

**Generated**: {data['metadata']['date'][:10]}
**Experiment**: Independent validation of LLM-as-judge aggression scores

---

## Summary

| Metric | Value |
|--------|-------|
| **N (models)** | {data['sample']['n_models']} |
| **BERT Toxicity vs. Aggression** | r = {data['correlations']['toxicity']['r']:.3f}, p = {data['correlations']['toxicity']['p']:.4f} |
| **BERT Insult vs. Aggression** | r = {data['correlations']['insult']['r']:.3f}, p = {data['correlations']['insult']['p']:.4f} |
| **Interpretation** | {data['interpretation']} |

---

## Visualizations

### BERT Toxicity vs. Judge Aggression
![Toxicity Scatter](scatter_toxicity_vs_aggression.png)

### BERT Insult vs. Judge Aggression
![Insult Scatter](scatter_insult_vs_aggression.png)

### Combined View
![Combined Scatter](scatter_combined.png)

---

## Data Trail

### 1. BERT Model

| Field | Value |
|-------|-------|
| **Model Name** | `{data['metadata']['bert_model']}` |
| **Hosted On** | Hugging Face (downloaded locally) |
| **Model URL** | {data['metadata']['bert_model_url']} |
| **Architecture** | BERT (bert-base-uncased), 110M parameters |
| **Training Data** | {data['metadata']['training_data']} |
| **Training Data URL** | {data['metadata']['training_data_url']} |
| **Output Labels** | toxicity, severe_toxicity, obscene, threat, insult, identity_attack |
| **Max Sequence Length** | 512 tokens |
| **Execution** | Local inference (no API calls) |

### 2. Source Data

| Field | Value |
|-------|-------|
| **Condition** | {data['metadata']['source_condition']} |
| **Profiles Path** | `{data['metadata']['source_profiles']}` |
| **Jobs Path** | `{data['metadata']['source_jobs']}` |
| **Models Evaluated** | {data['sample']['n_models']} |

### 3. Statistical Results

#### Correlations

| Measure | r | p-value | Effect Size |
|---------|---|---------|-------------|
| BERT Toxicity | {data['correlations']['toxicity']['r']:.4f} | {data['correlations']['toxicity']['p']:.6f} | {data['correlations']['toxicity']['interpretation']} |
| BERT Insult | {data['correlations']['insult']['r']:.4f} | {data['correlations']['insult']['p']:.6f} | {data['correlations']['insult']['interpretation']} |

#### Regression: Toxicity ~ Aggression

| Parameter | Value |
|-----------|-------|
| Slope | {data['regression']['toxicity']['slope']:.6f} |
| Intercept | {data['regression']['toxicity']['intercept']:.6f} |
| R² | {data['regression']['toxicity']['r_squared']:.4f} |
| Standard Error | {data['regression']['toxicity']['std_err']:.6f} |

#### Regression: Insult ~ Aggression

| Parameter | Value |
|-----------|-------|
| Slope | {data['regression']['insult']['slope']:.6f} |
| Intercept | {data['regression']['insult']['intercept']:.6f} |
| R² | {data['regression']['insult']['r_squared']:.4f} |
| Standard Error | {data['regression']['insult']['std_err']:.6f} |

### 4. Score Ranges

| Measure | Min | Max |
|---------|-----|-----|
| Judge Aggression | {data['sample']['aggression_range'][0]:.2f} | {data['sample']['aggression_range'][1]:.2f} |
| BERT Toxicity | {data['sample']['toxicity_range'][0]:.4f} | {data['sample']['toxicity_range'][1]:.4f} |
| BERT Insult | {data['sample']['insult_range'][0]:.4f} | {data['sample']['insult_range'][1]:.4f} |

---

## Output Files

| File | Description |
|------|-------------|
| `bert_validation_results.json` | Complete results with per-model scores (for downstream use) |
| `scatter_toxicity_vs_aggression.png` | Toxicity correlation scatter plot |
| `scatter_insult_vs_aggression.png` | Insult correlation scatter plot |
| `scatter_combined.png` | Combined 2-panel visualization |
| `VALIDATION_REPORT.md` | This report |
| `full_run_log.txt` | Complete execution log with per-response scores |

---

## Interpretation

{data['interpretation']}

**Effect size thresholds** (Cohen's conventions):
- |r| < 0.10: Negligible
- |r| 0.10-0.30: Small
- |r| 0.30-0.50: Medium
- |r| ≥ 0.50: Large

---

## Reproducibility

```bash
# Activate virtual environment
source venv/bin/activate

# Run validation
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py

# With verbose logging
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py 2>&1 | tee outputs/behavioral_profiles/research_synthesis/bert_validation/full_run_log.txt
```

---

## References

1. Unitary AI toxic-bert: {data['metadata']['bert_model_url']}
2. Jigsaw Toxic Comment Challenge: {data['metadata']['training_data_url']}
3. BERT paper: Devlin et al. (2019) "BERT: Pre-training of Deep Bidirectional Transformers"
"""

    report_file = output_dir / "VALIDATION_REPORT.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"  Saved: VALIDATION_REPORT.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", type=str, default="baseline",
                        choices=["baseline", "authority", "urgency", "reminder", "telemetryV3", "minimal_steering"],
                        help="Condition to validate (default: baseline)")
    parser.add_argument("--limit", type=int, help="Limit number of job files to process")
    args = parser.parse_args()

    run_validation(condition=args.condition, limit=args.limit)
