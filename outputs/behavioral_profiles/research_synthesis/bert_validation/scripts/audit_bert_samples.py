#!/usr/bin/env python3
"""
BERT Validation Audit Script

Extracts 5 sample responses per condition, runs them through BERT,
validates against existing results, and generates a certification statement.

Usage:
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/audit_bert_samples.py
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

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


def extract_sample_responses(condition: str, n_samples: int = 5) -> list:
    """Extract n sample responses from a condition's job outputs."""
    samples = []

    # Find jobs for this condition
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

    # Extract samples from different jobs/models for diversity
    seen_models = set()
    for job_file in job_files:
        if len(samples) >= n_samples:
            break

        try:
            with open(job_file) as f:
                job_data = json.load(f)

            prompt = job_data.get("prompt", "")
            models = job_data.get("models", [])

            for model_entry in models:
                if len(samples) >= n_samples:
                    break

                display_name = model_entry.get("display_name", "")
                response = model_entry.get("response", "")

                # Get diverse models
                if display_name and response and display_name not in seen_models:
                    seen_models.add(display_name)
                    samples.append({
                        "model_id": display_name,
                        "prompt": prompt[:500] + ("..." if len(prompt) > 500 else ""),
                        "response": response,
                        "response_length": len(response),
                        "source_file": str(job_file.name)
                    })

        except Exception as e:
            continue

    return samples


def load_existing_results(condition: str) -> dict:
    """Load existing BERT validation results for a condition."""
    results_file = BERT_VALIDATION_DIR / condition / "bert_validation_results.json"
    if results_file.exists():
        with open(results_file) as f:
            return json.load(f)
    return None


def run_audit():
    """Main audit pipeline."""
    print("=" * 70)
    print("BERT VALIDATION AUDIT")
    print("=" * 70)
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Samples per condition: {SAMPLES_PER_CONDITION}")
    print(f"Conditions: {', '.join(CONDITIONS)}")
    print()

    # Load BERT model
    model, tokenizer = load_model()
    print()

    audit_data = {
        "metadata": {
            "audit_date": datetime.now().isoformat(),
            "bert_model": MODEL_NAME,
            "samples_per_condition": SAMPLES_PER_CONDITION,
            "conditions": CONDITIONS
        },
        "samples": {},
        "validation": {},
        "certification": None
    }

    all_validations_passed = True
    validation_details = []

    for condition in CONDITIONS:
        print(f"\n{'='*60}")
        print(f"CONDITION: {condition}")
        print(f"{'='*60}")

        # Extract samples
        print(f"\n[1] Extracting {SAMPLES_PER_CONDITION} sample responses...")
        samples = extract_sample_responses(condition, SAMPLES_PER_CONDITION)
        print(f"    Extracted {len(samples)} samples")

        # Score with BERT
        print(f"\n[2] Scoring with BERT...")
        for i, sample in enumerate(samples):
            scores = get_toxicity_scores(sample["response"], model, tokenizer)
            sample["bert_scores"] = {
                "toxicity": round(scores["toxicity"], 6),
                "insult": round(scores["insult"], 6),
                "severe_toxicity": round(scores["severe_toxicity"], 6),
                "obscene": round(scores["obscene"], 6),
                "threat": round(scores["threat"], 6),
                "identity_attack": round(scores["identity_attack"], 6)
            }
            print(f"    [{i+1}/{len(samples)}] {sample['model_id'][:30]}: "
                  f"toxicity={scores['toxicity']:.6f}, insult={scores['insult']:.6f}")

        audit_data["samples"][condition] = samples

        # Load existing results for validation
        print(f"\n[3] Validating against existing results...")
        existing = load_existing_results(condition)

        condition_validation = {
            "existing_results_found": existing is not None,
            "sample_validations": [],
            "passed": True
        }

        if existing:
            existing_model_scores = {r["model_id"]: r for r in existing.get("model_results", [])}

            for sample in samples:
                model_id = sample["model_id"]
                if model_id in existing_model_scores:
                    existing_toxicity = existing_model_scores[model_id].get("bert_toxicity", 0)
                    new_toxicity = sample["bert_scores"]["toxicity"]

                    # Allow small floating point differences (< 0.0001)
                    diff = abs(existing_toxicity - new_toxicity)
                    match = diff < 0.0001

                    validation_entry = {
                        "model_id": model_id,
                        "existing_toxicity": existing_toxicity,
                        "audit_toxicity": new_toxicity,
                        "difference": diff,
                        "match": match
                    }
                    condition_validation["sample_validations"].append(validation_entry)

                    if not match:
                        condition_validation["passed"] = False
                        all_validations_passed = False
                        print(f"    MISMATCH: {model_id} - existing={existing_toxicity:.6f}, audit={new_toxicity:.6f}")
                    else:
                        print(f"    MATCH: {model_id} - {existing_toxicity:.6f} == {new_toxicity:.6f}")
                else:
                    print(f"    SKIP: {model_id} not in existing results (different sample)")
        else:
            print(f"    WARNING: No existing results found for {condition}")
            condition_validation["passed"] = False
            all_validations_passed = False

        audit_data["validation"][condition] = condition_validation
        validation_details.append({
            "condition": condition,
            "passed": condition_validation["passed"],
            "n_validated": len(condition_validation["sample_validations"]),
            "n_matched": sum(1 for v in condition_validation["sample_validations"] if v["match"])
        })

    # Generate certification
    print(f"\n{'='*70}")
    print("CERTIFICATION")
    print(f"{'='*70}")

    total_validated = sum(v["n_validated"] for v in validation_details)
    total_matched = sum(v["n_matched"] for v in validation_details)

    if all_validations_passed and total_validated > 0:
        certification = {
            "status": "PASSED",
            "statement": (
                f"BERT Validation Audit PASSED. "
                f"All {total_matched}/{total_validated} validated samples produced identical toxicity scores "
                f"(within floating-point tolerance of 0.0001) when re-run through the BERT model. "
                f"This confirms that the BERT validation pipeline is deterministic and reproducible."
            ),
            "audit_date": datetime.now().isoformat(),
            "auditor": "automated_audit_script",
            "bert_model": MODEL_NAME,
            "conditions_audited": CONDITIONS,
            "total_samples": len(CONDITIONS) * SAMPLES_PER_CONDITION,
            "total_validated": total_validated,
            "total_matched": total_matched
        }
        print(f"\nSTATUS: PASSED")
        print(f"\n{certification['statement']}")
    else:
        certification = {
            "status": "FAILED",
            "statement": (
                f"BERT Validation Audit FAILED. "
                f"Only {total_matched}/{total_validated} validated samples matched existing results. "
                f"This may indicate data corruption, model version differences, or pipeline issues."
            ),
            "audit_date": datetime.now().isoformat(),
            "auditor": "automated_audit_script",
            "bert_model": MODEL_NAME,
            "conditions_audited": CONDITIONS,
            "total_samples": len(CONDITIONS) * SAMPLES_PER_CONDITION,
            "total_validated": total_validated,
            "total_matched": total_matched,
            "failed_conditions": [v["condition"] for v in validation_details if not v["passed"]]
        }
        print(f"\nSTATUS: FAILED")
        print(f"\n{certification['statement']}")

    audit_data["certification"] = certification

    # Save audit results
    output_file = BERT_VALIDATION_DIR / "audit_samples.json"
    with open(output_file, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nAudit results saved to: {output_file}")

    # Generate audit report markdown
    generate_audit_report(audit_data)

    return audit_data


def generate_audit_report(audit_data: dict):
    """Generate markdown audit report."""
    cert = audit_data["certification"]

    report = f"""# BERT Validation Audit Report

**Generated**: {cert['audit_date'][:10]}
**Status**: {cert['status']}

---

## Certification Statement

{cert['statement']}

---

## Audit Details

| Field | Value |
|-------|-------|
| **BERT Model** | `{cert['bert_model']}` |
| **Conditions Audited** | {len(cert['conditions_audited'])} |
| **Total Samples** | {cert['total_samples']} |
| **Samples Validated** | {cert['total_validated']} |
| **Samples Matched** | {cert['total_matched']} |

---

## Per-Condition Results

| Condition | Validated | Matched | Status |
|-----------|-----------|---------|--------|
"""

    for condition in CONDITIONS:
        v = audit_data["validation"].get(condition, {})
        n_validated = len(v.get("sample_validations", []))
        n_matched = sum(1 for s in v.get("sample_validations", []) if s.get("match", False))
        status = "PASS" if v.get("passed", False) else "FAIL"
        report += f"| {condition} | {n_validated} | {n_matched} | {status} |\n"

    report += f"""
---

## Sample Responses

Below are the raw responses sent to BERT for each condition.

"""

    for condition in CONDITIONS:
        samples = audit_data["samples"].get(condition, [])
        report += f"### {condition.upper()}\n\n"

        for i, sample in enumerate(samples[:3]):  # Show first 3 in report
            report += f"""**Sample {i+1}: {sample['model_id']}**

- **Source**: `{sample['source_file']}`
- **Response length**: {sample['response_length']} chars
- **BERT Toxicity**: {sample['bert_scores']['toxicity']:.6f}
- **BERT Insult**: {sample['bert_scores']['insult']:.6f}

<details>
<summary>Prompt (click to expand)</summary>

```
{sample['prompt']}
```

</details>

<details>
<summary>Response (click to expand)</summary>

```
{sample['response'][:1000]}{'...' if len(sample['response']) > 1000 else ''}
```

</details>

"""

    report += f"""---

## Reproducibility

```bash
# Re-run this audit
python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/audit_bert_samples.py
```

---

## Data Files

| File | Description |
|------|-------------|
| `audit_samples.json` | Complete audit data with all samples and BERT scores |
| `AUDIT_REPORT.md` | This report |

"""

    report_file = BERT_VALIDATION_DIR / "AUDIT_REPORT.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"Audit report saved to: {report_file}")


if __name__ == "__main__":
    run_audit()
