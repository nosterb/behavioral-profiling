#!/usr/bin/env python3
"""
Full BERT Validation with Audit Trail

Runs the complete BERT validation pipeline across all conditions,
storing the first 5 raw responses per condition for audit purposes,
and validates against existing results.

Usage:
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_full_audit.py
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from scipy import stats

MODEL_NAME = "unitary/toxic-bert"
JOBS_DIR = Path("outputs/single_prompt_jobs")
BERT_VALIDATION_DIR = Path("outputs/behavioral_profiles/research_synthesis/bert_validation")
CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder"]
SAMPLES_PER_CONDITION = 5

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


def load_aggression_scores(condition: str) -> tuple:
    """Load aggression scores from condition profiles."""
    profiles_dir = Path(f"outputs/behavioral_profiles/{condition}/profiles")
    aggression_by_model = {}
    normalized_to_original = {}

    if not profiles_dir.exists():
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


def normalize_model_name(name: str) -> str:
    """Normalize model name for matching."""
    import re
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


def extract_responses_from_jobs(condition: str) -> dict:
    """Extract ALL model responses from job outputs."""
    responses_by_model = defaultdict(list)

    job_files = []
    for suite_dir in JOBS_DIR.glob("baseline_*"):
        if not suite_dir.is_dir():
            continue
        for job_dir in suite_dir.iterdir():
            if not job_dir.is_dir():
                continue
            name = job_dir.name

            if condition == "baseline":
                if any(x in name for x in INTERVENTION_SUFFIXES):
                    continue
            else:
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

            for job_file in job_dir.glob("*.json"):
                job_files.append(job_file)

    for job_file in job_files:
        try:
            with open(job_file) as f:
                job_data = json.load(f)

            prompt = job_data.get("prompt", "")
            models = job_data.get("models", [])

            for model_entry in models:
                display_name = model_entry.get("display_name", "")
                response = model_entry.get("response", "")

                if display_name and response:
                    responses_by_model[display_name].append({
                        "response": response,
                        "prompt": prompt,
                        "source": job_file.name
                    })

        except Exception:
            continue

    return dict(responses_by_model)


def load_existing_results(condition: str) -> dict:
    """Load existing BERT validation results."""
    results_file = BERT_VALIDATION_DIR / condition / "bert_validation_results.json"
    if results_file.exists():
        with open(results_file) as f:
            return json.load(f)
    return None


def run_full_audit():
    """Run full BERT validation with audit trail."""
    print("=" * 70)
    print("BERT FULL VALIDATION WITH AUDIT")
    print("=" * 70)
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Conditions: {', '.join(CONDITIONS)}")
    print(f"Audit samples per condition: {SAMPLES_PER_CONDITION}")
    print()

    # Load BERT model once
    bert_model, tokenizer = load_model()
    print()

    audit_data = {
        "metadata": {
            "audit_date": datetime.now().isoformat(),
            "bert_model": MODEL_NAME,
            "bert_model_url": "https://huggingface.co/unitary/toxic-bert",
            "conditions": CONDITIONS,
            "samples_per_condition": SAMPLES_PER_CONDITION
        },
        "audit_samples": {},
        "condition_summaries": {},
        "validation_results": {},
        "certification": None
    }

    total_responses_scored = 0
    all_validations = []

    for condition in CONDITIONS:
        print(f"\n{'='*70}")
        print(f"CONDITION: {condition}")
        print(f"{'='*70}")

        # Load existing results for validation
        existing = load_existing_results(condition)
        existing_model_scores = {}
        if existing:
            existing_model_scores = {r["model_id"]: r for r in existing.get("model_results", [])}

        # Load aggression scores
        aggression_scores, profile_norm_map = load_aggression_scores(condition)
        print(f"\n[1] Found {len(aggression_scores)} models with aggression scores")

        # Extract responses
        responses = extract_responses_from_jobs(condition)
        print(f"[2] Found responses for {len(responses)} models")

        # Build normalized map
        response_norm_map = {}
        for model_id in responses.keys():
            norm = normalize_model_name(model_id)
            response_norm_map[norm] = model_id

        # Find common models
        common_norms = set(profile_norm_map.keys()) & set(response_norm_map.keys())
        print(f"[3] Models with both scores and responses: {len(common_norms)}")

        # Collect audit samples (first 5 unique responses)
        audit_samples = []
        sample_count = 0

        # Score all responses
        print(f"\n[4] Scoring all responses with BERT...")
        model_results = []

        for i, norm in enumerate(sorted(common_norms)):
            profile_id = profile_norm_map[norm]
            response_id = response_norm_map[norm]
            model_responses = responses[response_id]
            aggression = aggression_scores[profile_id]

            toxicity_scores = []
            insult_scores = []

            for j, resp_data in enumerate(model_responses):
                scores = get_toxicity_scores(resp_data["response"], bert_model, tokenizer)
                toxicity_scores.append(scores["toxicity"])
                insult_scores.append(scores["insult"])
                total_responses_scored += 1

                # Capture audit samples (first 5 across condition)
                if sample_count < SAMPLES_PER_CONDITION:
                    audit_samples.append({
                        "sample_id": sample_count + 1,
                        "model_id": profile_id,
                        "prompt": resp_data["prompt"][:500] + ("..." if len(resp_data["prompt"]) > 500 else ""),
                        "response": resp_data["response"],
                        "response_length": len(resp_data["response"]),
                        "source_file": resp_data["source"],
                        "bert_scores": {
                            "toxicity": round(scores["toxicity"], 6),
                            "insult": round(scores["insult"], 6),
                            "severe_toxicity": round(scores.get("severe_toxicity", 0), 6),
                            "obscene": round(scores.get("obscene", 0), 6),
                            "threat": round(scores.get("threat", 0), 6),
                            "identity_attack": round(scores.get("identity_attack", 0), 6)
                        }
                    })
                    sample_count += 1

            avg_toxicity = np.mean(toxicity_scores)
            avg_insult = np.mean(insult_scores)

            model_results.append({
                "model_id": profile_id,
                "aggression": aggression,
                "bert_toxicity": avg_toxicity,
                "bert_insult": avg_insult,
                "n_responses": len(model_responses)
            })

            # Validate against existing
            if profile_id in existing_model_scores:
                existing_tox = existing_model_scores[profile_id].get("bert_toxicity", 0)
                tox_diff = abs(existing_tox - avg_toxicity)
                match = tox_diff < 0.0001

                all_validations.append({
                    "condition": condition,
                    "model_id": profile_id,
                    "existing_toxicity": existing_tox,
                    "audit_toxicity": avg_toxicity,
                    "diff": tox_diff,
                    "match": match
                })

                status = "✓" if match else "✗"
                print(f"  [{i+1}/{len(common_norms)}] {profile_id}: tox={avg_toxicity:.6f} {status}")
            else:
                print(f"  [{i+1}/{len(common_norms)}] {profile_id}: tox={avg_toxicity:.6f} (new)")

        # Store audit samples
        audit_data["audit_samples"][condition] = audit_samples

        # Compute correlations
        if len(model_results) >= 10:
            aggression_vals = np.array([r["aggression"] for r in model_results])
            toxicity_vals = np.array([r["bert_toxicity"] for r in model_results])
            r_tox, p_tox = stats.pearsonr(aggression_vals, toxicity_vals)

            audit_data["condition_summaries"][condition] = {
                "n_models": len(model_results),
                "n_responses_scored": sum(r["n_responses"] for r in model_results),
                "correlation_toxicity_aggression": {
                    "r": round(r_tox, 4),
                    "p": round(p_tox, 6)
                }
            }

            print(f"\n  Summary: N={len(model_results)}, r={r_tox:.3f}, p={p_tox:.4f}")

    # Generate certification
    print(f"\n{'='*70}")
    print("CERTIFICATION")
    print(f"{'='*70}")

    total_validated = len(all_validations)
    total_matched = sum(1 for v in all_validations if v["match"])
    all_passed = total_validated > 0 and total_matched == total_validated

    audit_data["validation_results"] = {
        "total_validated": total_validated,
        "total_matched": total_matched,
        "details": all_validations
    }

    if all_passed:
        certification = {
            "status": "PASSED",
            "statement": (
                f"BERT Validation Audit PASSED. "
                f"All {total_matched}/{total_validated} validated model scores matched existing results "
                f"within tolerance (< 0.0001). Pipeline is deterministic and reproducible. "
                f"Total responses scored: {total_responses_scored}."
            ),
            "audit_date": datetime.now().isoformat(),
            "bert_model": MODEL_NAME,
            "total_responses_scored": total_responses_scored,
            "total_models_validated": total_validated,
            "total_models_matched": total_matched
        }
        print(f"\n*** STATUS: PASSED ***")
    else:
        certification = {
            "status": "FAILED",
            "statement": (
                f"BERT Validation Audit FAILED. "
                f"Only {total_matched}/{total_validated} model scores matched. "
                f"Review mismatched models for data integrity issues."
            ),
            "audit_date": datetime.now().isoformat(),
            "bert_model": MODEL_NAME,
            "total_responses_scored": total_responses_scored,
            "total_models_validated": total_validated,
            "total_models_matched": total_matched,
            "mismatched_models": [v for v in all_validations if not v["match"]]
        }
        print(f"\n*** STATUS: FAILED ***")

    print(f"\n{certification['statement']}")

    audit_data["certification"] = certification

    # Save
    output_file = BERT_VALIDATION_DIR / "audit_samples.json"
    with open(output_file, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nSaved: {output_file}")

    # Generate report
    generate_audit_report(audit_data)

    return audit_data


def generate_audit_report(audit_data: dict):
    """Generate markdown audit report."""
    cert = audit_data["certification"]
    meta = audit_data["metadata"]

    report = f"""# BERT Validation Audit Report

**Generated**: {cert['audit_date'][:19]}
**Status**: **{cert['status']}**

---

## Certification Statement

> {cert['statement']}

---

## Audit Summary

| Field | Value |
|-------|-------|
| **BERT Model** | `{meta['bert_model']}` |
| **Total Responses Scored** | {cert['total_responses_scored']:,} |
| **Models Validated** | {cert['total_models_validated']} |
| **Models Matched** | {cert['total_models_matched']} |

---

## Per-Condition Summary

| Condition | Models | Responses | r (Tox~Agg) | p-value |
|-----------|--------|-----------|-------------|---------|
"""

    for condition in CONDITIONS:
        summary = audit_data["condition_summaries"].get(condition, {})
        n_models = summary.get("n_models", 0)
        n_responses = summary.get("n_responses_scored", 0)
        corr = summary.get("correlation_toxicity_aggression", {})
        r = corr.get("r", "N/A")
        p = corr.get("p", "N/A")
        report += f"| {condition} | {n_models} | {n_responses} | {r} | {p} |\n"

    report += f"""
---

## Raw Response Samples

These are the actual text responses sent to BERT for toxicity scoring.

"""

    for condition in CONDITIONS:
        samples = audit_data["audit_samples"].get(condition, [])
        report += f"### {condition.upper()} ({len(samples)} samples)\n\n"

        for sample in samples:
            scores = sample.get("bert_scores", {})
            report += f"""#### Sample {sample['sample_id']}: {sample['model_id']}

| Field | Value |
|-------|-------|
| **Source File** | `{sample['source_file']}` |
| **Response Length** | {sample['response_length']:,} chars |
| **BERT Toxicity** | {scores.get('toxicity', 'N/A')} |
| **BERT Insult** | {scores.get('insult', 'N/A')} |
| **BERT Severe Toxicity** | {scores.get('severe_toxicity', 'N/A')} |

**Prompt:**
```
{sample['prompt']}
```

**Response:**
```
{sample['response'][:2000]}{'...' if len(sample['response']) > 2000 else ''}
```

---

"""

    report += f"""
## Reproducibility

```bash
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_full_audit.py
```

## Output Files

| File | Description |
|------|-------------|
| `audit_samples.json` | Complete audit data with raw samples and validation |
| `AUDIT_REPORT.md` | This report |

"""

    report_file = BERT_VALIDATION_DIR / "AUDIT_REPORT.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"Saved: {report_file}")


if __name__ == "__main__":
    run_full_audit()
